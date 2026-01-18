import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pdfplumber

from app.services.aia_mapping_service import AIAFinancialMappingService, normalize_text

logger = logging.getLogger(__name__)


class PdfAnalyzeService:
    TOTAL_KEYWORDS = [
        "total",
        "gross profit",
        "total income",
        "total expenses",
    ]

    def __init__(self) -> None:
        self.mapping_service = AIAFinancialMappingService()

    def analyze(
        self,
        *,
        pl_path: Optional[str],
        bs_path: Optional[str],
    ) -> Tuple[Dict, Dict, Dict, List[str]]:
        warnings: List[str] = []

        pnl_rows, pnl_totals = self._parse_pdf(pl_path, warnings, "P&L")
        bs_rows, bs_totals = self._parse_pdf(bs_path, warnings, "Balance Sheet")

        client_view = {
            "pnl": {"rows": pnl_rows, "totals": pnl_totals},
            "bs": {"rows": bs_rows, "totals": bs_totals},
        }

        aia_view = {
            "pnl": self._map_rows_to_aia(pnl_rows),
            "bs": self._map_rows_to_aia(bs_rows),
        }

        reconciliation = {
            "pnl_delta": self._reconcile(pnl_rows, aia_view["pnl"]),
            "bs_delta": self._reconcile(bs_rows, aia_view["bs"]),
        }

        return client_view, aia_view, reconciliation, warnings

    def _parse_pdf(self, path: Optional[str], warnings: List[str], label: str):
        if not path:
            warnings.append(f"{label} file missing")
            return [], {}

        file_path = Path(path)
        if not file_path.exists():
            warnings.append(f"{label} file not found at {path}")
            return [], {}

        text = self._extract_text(file_path, warnings, label)
        rows, totals = self._extract_rows(text)
        return rows, totals

    @staticmethod
    def _extract_text(path: Path, warnings: List[str], label: str) -> str:
        try:
            content = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    content.append(page_text)
            return "\n".join(content)
        except Exception as error:
            warnings.append(f"{label} parsing failed: {error}")
            logger.exception("PDF parsing failed")
            return ""

    def _extract_rows(self, text: str) -> Tuple[List[Dict], Dict]:
        rows: List[Dict] = []
        totals: Dict[str, float] = {}

        for line in text.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            label, amount = self._split_line_amount(cleaned)
            if not label:
                continue
            rows.append({"label": label, "amount": amount})
            if amount is not None and self._is_total_line(label):
                totals[label] = amount

        return rows, totals

    @staticmethod
    def _split_line_amount(line: str) -> Tuple[str, Optional[float]]:
        match = re.search(r"([\\(\\-]?\\d[\\d\\s,\\.]*\\d\\)?)(\\s*)$", line)
        if not match:
            return line, None
        amount_raw = match.group(1)
        label = line[: match.start(1)].strip()
        amount = PdfAnalyzeService._parse_amount(amount_raw)
        if label and amount is not None:
            return label, amount
        return line, None

    @staticmethod
    def _parse_amount(value: str) -> Optional[float]:
        if not value:
            return None
        raw = value.strip()
        negative = raw.startswith("(") and raw.endswith(")")
        raw = raw.strip("()")
        raw = raw.replace(" ", "")
        if "," in raw and "." in raw:
            raw = raw.replace(",", "")
        elif "," in raw and "." not in raw:
            parts = raw.split(",")
            if len(parts[-1]) in (2, 3):
                raw = ".".join(parts)
            else:
                raw = raw.replace(",", "")
        try:
            number = float(raw)
            return -number if negative else number
        except ValueError:
            return None

    @staticmethod
    def _is_total_line(label: str) -> bool:
        normalized = normalize_text(label)
        return any(keyword in normalized for keyword in PdfAnalyzeService.TOTAL_KEYWORDS)

    def _map_rows_to_aia(self, rows: List[Dict]) -> Dict:
        totals_by_category: Dict[str, float] = {}

        for row in rows:
            amount = row.get("amount")
            if amount is None:
                continue
            label = row.get("label", "")
            category, _ = self.mapping_service._map_account_to_category(label)
            totals_by_category[category] = totals_by_category.get(category, 0.0) + amount

        return {"totals_by_category": totals_by_category}

    @staticmethod
    def _reconcile(rows: List[Dict], aia_view: Dict) -> Dict:
        client_total = sum(row.get("amount") or 0 for row in rows)
        aia_total = sum(aia_view.get("totals_by_category", {}).values())
        delta = client_total - aia_total
        return {
            "client_total": round(client_total, 2),
            "aia_total": round(aia_total, 2),
            "delta": round(delta, 2),
        }
