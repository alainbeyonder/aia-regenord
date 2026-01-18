import json
from typing import Any, Dict, List, Optional

from openai import OpenAI

from app.core.config import settings


class AIANarrationService:
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OpenAI API key not configured")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def explain(
        self,
        *,
        tone: str,
        result_json: Dict[str, Any],
        assumptions_json: Dict[str, Any],
    ) -> Dict[str, Any]:
        system_prompt = (
            "You are a senior financial analyst. Produce a concise, professional explanation "
            "based strictly on the provided JSON. Do not invent numbers. If a value is missing, "
            "say 'n/a'. Explain cash vs P&L differences clearly. Return ONLY valid JSON with keys: "
            "summary (3-4 lines), key_insights (5 items), levers (3 items), risks (2 items), "
            "banking_note (string, only if tone=bank, otherwise empty string)."
        )

        user_prompt = json.dumps(
            {
                "tone": tone,
                "result_json": result_json,
                "assumptions_json": assumptions_json,
            },
            ensure_ascii=False,
        )

        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content or ""
        parsed = self._safe_json_parse(content)
        return self._normalize_output(parsed, tone)

    @staticmethod
    def _safe_json_parse(content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(content[start : end + 1])
        raise ValueError("Invalid JSON response from OpenAI")

    @staticmethod
    def _normalize_output(data: Dict[str, Any], tone: str) -> Dict[str, Any]:
        def to_list(value: Optional[Any], size: int) -> List[str]:
            if not isinstance(value, list):
                value = []
            items = [str(item) for item in value[:size]]
            while len(items) < size:
                items.append("n/a")
            return items

        return {
            "summary": data.get("summary", ""),
            "key_insights": to_list(data.get("key_insights"), 5),
            "levers": to_list(data.get("levers"), 3),
            "risks": to_list(data.get("risks"), 2),
            "banking_note": data.get("banking_note", "") if tone == "bank" else "",
        }
