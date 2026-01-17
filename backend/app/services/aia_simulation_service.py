from typing import Dict, List


class AIASimulationService:
    @staticmethod
    def _series(base: float, months: int) -> List[float]:
        return [round(base + (idx * 10.0), 2) for idx in range(months)]

    @staticmethod
    def build_placeholder_result(
        company_id: int,
        assumption_set_id: int,
        horizon_months: int,
        horizon_years: int,
    ) -> Dict:
        seed = (company_id or 0) * 100 + (assumption_set_id or 0)
        pnl_monthly = AIASimulationService._series(1000 + seed, horizon_months)
        cashflow_monthly = AIASimulationService._series(500 + seed, horizon_months)
        balance_sheet_monthly = AIASimulationService._series(2000 + seed, horizon_months)

        return {
            "pnl_monthly": pnl_monthly,
            "cashflow_monthly": cashflow_monthly,
            "balance_sheet_monthly": balance_sheet_monthly,
            "pnl_year2": {"total": round(120000 + seed, 2)},
            "pnl_year3": {"total": round(130000 + seed, 2)},
            "cashflow_year2": {"total": round(60000 + seed, 2)},
            "cashflow_year3": {"total": round(65000 + seed, 2)},
            "balance_sheet_year2": {"total": round(300000 + seed, 2)},
            "balance_sheet_year3": {"total": round(320000 + seed, 2)},
            "reconciliation": {
                "status": "placeholder",
                "company_id": company_id,
                "assumption_set_id": assumption_set_id,
                "horizon_months": horizon_months,
                "horizon_years": horizon_years,
            },
        }
