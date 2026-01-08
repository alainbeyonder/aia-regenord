from typing import List, Dict, Any
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import isoparse
from sqlalchemy.orm import Session
import logging

from app.models.scenario import Scenario
from app.models.projection import Projection

logger = logging.getLogger(__name__)


class ProjectionEngine:
    """
    12 months (monthly) + Year 2 & 3 (annual) => 14 projections

    Seasonal mode:
      If assumptions.parameters.monthly_plan is provided (12 items),
      we use it for months 1-12 (revenue + expenses can vary month-to-month).

    Year 2 and Year 3:
      - Controlled by assumptions.parameters.group_rules.year2 / year3
      - Defaults if missing:
          year2: revenue +30%, variable +30%, fixed 0%
          year3: revenue +30% (compounded), variable +30% (compounded), fixed 0%
    """

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Public
    # -------------------------
    def calculate_projections(self, scenario_id: int) -> List[Projection]:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        assumptions = scenario.assumptions or {}
        base_date = self._parse_base_date(assumptions)

        parameters = assumptions.get("parameters") or {}
        monthly_plan = parameters.get("monthly_plan")

        projections: List[Projection] = []

        # --- Year 1: 12 monthly projections
        year1_monthly: List[Projection] = []
        for m in range(12):
            period_dt = base_date + relativedelta(months=m)
            if monthly_plan:
                proj = self._monthly_from_plan(
                    scenario=scenario,
                    assumptions=assumptions,
                    period_dt=period_dt,
                    month_index=m,
                    monthly_plan=monthly_plan,
                )
            else:
                proj = self._monthly_from_growth_model(
                    scenario=scenario,
                    assumptions=assumptions,
                    period_dt=period_dt,
                    month_index=m,
                )

            projections.append(proj)
            year1_monthly.append(proj)

        # --- Year 2 & 3 annual projections based on Year1 totals + group_rules
        y2_rev, y2_var, y2_fix, y3_rev, y3_var, y3_fix = self._year_multipliers(assumptions)

        year2 = self._annual_from_year1(
            year1_monthly=year1_monthly,
            scenario_id=scenario.id,
            period_dt=base_date + relativedelta(years=1),
            year_label="annual",
            revenue_multiplier=y2_rev,
            variable_multiplier=y2_var,
            fixed_multiplier=y2_fix,
        )

        year3 = self._annual_from_year1(
            year1_monthly=year1_monthly,
            scenario_id=scenario.id,
            period_dt=base_date + relativedelta(years=2),
            year_label="annual",
            revenue_multiplier=y3_rev,
            variable_multiplier=y3_var,
            fixed_multiplier=y3_fix,
        )

        projections.append(year2)
        projections.append(year3)

        # Save
        for p in projections:
            self.db.add(p)
        self.db.commit()

        return projections

    # -------------------------
    # Parsing / helpers
    # -------------------------
    def _parse_base_date(self, assumptions: Dict[str, Any]) -> datetime:
        raw = assumptions.get("base_date")
        if not raw:
            raise ValueError("Missing assumptions.base_date (ISO string)")
        return isoparse(raw)

    def _to_float(self, v: Any, default: float = 0.0) -> float:
        try:
            if v is None:
                return default
            return float(v)
        except Exception:
            return default

    def _get_group_rules(self, assumptions: Dict[str, Any]) -> Dict[str, Any]:
        params = assumptions.get("parameters") or {}
        return params.get("group_rules") or {}

    def _year_multipliers(self, assumptions: Dict[str, Any]):
        """
        Returns:
          y2_rev, y2_var, y2_fix, y3_rev, y3_var, y3_fix

        group_rules format:
          {
            "year2": {"revenue_growth_pct": 0.30, "variable_cost_growth_pct": 0.30, "fixed_cost_growth_pct": 0.02},
            "year3": {"revenue_growth_pct": 0.30, "variable_cost_growth_pct": 0.30, "fixed_cost_growth_pct": 0.02}
          }

        If missing:
          year2 defaults: revenue 0.30, variable 0.30, fixed 0.00
          year3 defaults: same growth as year2 (compounded)
        """
        rules = self._get_group_rules(assumptions)

        y2 = rules.get("year2") or {}
        y3 = rules.get("year3") or {}

        y2_rev_growth = self._to_float(y2.get("revenue_growth_pct"), 0.30)
        y2_var_growth = self._to_float(
            y2.get("variable_cost_growth_pct"),
            y2_rev_growth,  # default variable follows revenue
        )
        y2_fix_growth = self._to_float(y2.get("fixed_cost_growth_pct"), 0.0)

        # Multipliers for year2
        y2_rev = 1.0 + y2_rev_growth
        y2_var = 1.0 + y2_var_growth
        y2_fix = 1.0 + y2_fix_growth

        # Year3: if not specified, reuse year2 growth rates
        y3_rev_growth = self._to_float(y3.get("revenue_growth_pct"), y2_rev_growth)
        y3_var_growth = self._to_float(
            y3.get("variable_cost_growth_pct"),
            self._to_float(y3.get("revenue_growth_pct"), y2_var_growth),  # default var follows revenue
        )
        y3_fix_growth = self._to_float(y3.get("fixed_cost_growth_pct"), self._to_float(y2.get("fixed_cost_growth_pct"), 0.0))

        # Multipliers for year3 are compounded over year2
        y3_rev = y2_rev * (1.0 + y3_rev_growth)
        y3_var = y2_var * (1.0 + y3_var_growth)
        y3_fix = y2_fix * (1.0 + y3_fix_growth)

        return y2_rev, y2_var, y2_fix, y3_rev, y3_var, y3_fix

    # -------------------------
    # Monthly: Seasonal plan
    # -------------------------
    def _monthly_from_plan(
        self,
        scenario: Scenario,
        assumptions: Dict[str, Any],
        period_dt: datetime,
        month_index: int,
        monthly_plan: List[Dict[str, Any]],
    ) -> Projection:
        """
        monthly_plan: list of 12 items. Each item supports:
          {
            "month": "YYYY-MM" (optional),
            "revenue": {"licenses":..., "consulting":..., "products":..., "other":...},
            "expenses": {"salaries":..., "marketing":..., "operations":..., "other":..., "consulting":...}
          }
        If fewer than 12 items, missing months default to 0.
        """
        item = monthly_plan[month_index] if month_index < len(monthly_plan) else {}

        revenue = item.get("revenue") or {}
        expenses = item.get("expenses") or {}

        revenue_licenses = self._to_float(revenue.get("licenses"))
        revenue_consulting = self._to_float(revenue.get("consulting"))
        revenue_products = self._to_float(revenue.get("products"))
        revenue_other = self._to_float(revenue.get("other"))

        total_revenue = revenue_licenses + revenue_consulting + revenue_products + revenue_other

        expense_salaries = self._to_float(expenses.get("salaries"))
        expense_marketing = self._to_float(expenses.get("marketing"))
        expense_operations = self._to_float(expenses.get("operations"))
        expense_consulting = self._to_float(expenses.get("consulting"))
        expense_other = self._to_float(expenses.get("other"))

        # Optional: variable percent if "other" not specified
        if expense_other == 0.0:
            expense_assumptions = assumptions.get("expense_assumptions") or {}
            other_pct = self._to_float(expense_assumptions.get("other_percentage"), 0.0)
            expense_other = total_revenue * other_pct

        total_expenses = expense_salaries + expense_consulting + expense_marketing + expense_operations + expense_other

        ebitda = total_revenue - total_expenses
        net_income = ebitda

        operating_cash_flow = net_income

        investing_cash_flow = 0.0
        financing_cash_flow = 0.0

        # CAPEX items ("YYYY-MM")
        capex = (assumptions.get("capex_assumptions") or {}).get("items") or []
        key = period_dt.strftime("%Y-%m")
        for capex_item in capex:
            if capex_item.get("date") == key:
                investing_cash_flow -= self._to_float(capex_item.get("amount"))

        net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow

        return Projection(
            scenario_id=scenario.id,
            period_date=period_dt.date(),
            period_type="monthly",

            revenue_licenses=revenue_licenses,
            revenue_consulting=revenue_consulting,
            revenue_products=revenue_products,
            revenue_other=revenue_other,
            total_revenue=total_revenue,

            expense_salaries=expense_salaries,
            expense_consulting=expense_consulting,
            expense_marketing=expense_marketing,
            expense_operations=expense_operations,
            expense_other=expense_other,
            total_expenses=total_expenses,

            ebitda=ebitda,
            net_income=net_income,

            operating_cash_flow=operating_cash_flow,
            investing_cash_flow=investing_cash_flow,
            financing_cash_flow=financing_cash_flow,
            net_cash_flow=net_cash_flow,

            assets=0,
            liabilities=0,
            equity=0,
        )

    # -------------------------
    # Monthly: fallback smooth model (optional)
    # -------------------------
    def _monthly_from_growth_model(
        self,
        scenario: Scenario,
        assumptions: Dict[str, Any],
        period_dt: datetime,
        month_index: int,
    ) -> Projection:
        sales = assumptions.get("sales_assumptions") or {}
        expenses = assumptions.get("expense_assumptions") or {}

        licenses_config = sales.get("licenses", {})
        base_licenses = self._to_float(licenses_config.get("base_count"))
        monthly_price = self._to_float(licenses_config.get("monthly_price"), 1000)
        growth_rate = self._to_float(licenses_config.get("monthly_growth_rate"), 0.0)
        licenses_count = base_licenses * ((1 + growth_rate) ** month_index)
        revenue_licenses = licenses_count * monthly_price

        consulting_config = sales.get("consulting", {})
        base_consulting = self._to_float(consulting_config.get("base_monthly"), 0.0)
        consulting_growth = self._to_float(consulting_config.get("growth_rate"), 0.0)
        revenue_consulting = base_consulting * ((1 + consulting_growth) ** month_index)

        products_config = sales.get("products", {})
        products_base = self._to_float(products_config.get("monthly_revenue"), 0.0)
        products_growth = self._to_float(products_config.get("growth_rate"), 0.0)
        revenue_products = products_base * ((1 + products_growth) ** month_index)

        revenue_other = 0.0
        total_revenue = revenue_licenses + revenue_consulting + revenue_products + revenue_other

        salaries_config = expenses.get("salaries", {})
        base_salaries = self._to_float(salaries_config.get("base_monthly"), 0.0)
        annual_increase = self._to_float(salaries_config.get("annual_increase"), 0.0)
        salaries_growth = annual_increase / 12.0
        expense_salaries = base_salaries * ((1 + salaries_growth) ** month_index)

        marketing_config = expenses.get("marketing", {})
        expense_marketing = self._to_float(marketing_config.get("base_monthly"), 0.0)

        operations_config = expenses.get("operations", {})
        expense_operations = self._to_float(operations_config.get("base_monthly"), 0.0)

        other_pct = self._to_float(expenses.get("other_percentage"), 0.0)
        expense_other = total_revenue * other_pct

        expense_consulting = 0.0
        total_expenses = expense_salaries + expense_consulting + expense_marketing + expense_operations + expense_other

        ebitda = total_revenue - total_expenses
        net_income = ebitda

        operating_cash_flow = net_income
        investing_cash_flow = 0.0
        financing_cash_flow = 0.0
        net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow

        return Projection(
            scenario_id=scenario.id,
            period_date=period_dt.date(),
            period_type="monthly",

            revenue_licenses=revenue_licenses,
            revenue_consulting=revenue_consulting,
            revenue_products=revenue_products,
            revenue_other=revenue_other,
            total_revenue=total_revenue,

            expense_salaries=expense_salaries,
            expense_consulting=expense_consulting,
            expense_marketing=expense_marketing,
            expense_operations=expense_operations,
            expense_other=expense_other,
            total_expenses=total_expenses,

            ebitda=ebitda,
            net_income=net_income,

            operating_cash_flow=operating_cash_flow,
            investing_cash_flow=investing_cash_flow,
            financing_cash_flow=financing_cash_flow,
            net_cash_flow=net_cash_flow,

            assets=0,
            liabilities=0,
            equity=0,
        )

    # -------------------------
    # Annual: apply your rule based on Year1 totals
    # -------------------------
    def _annual_from_year1(
        self,
        year1_monthly: List[Projection],
        scenario_id: int,
        period_dt: datetime,
        year_label: str,
        revenue_multiplier: float,
        variable_multiplier: float,
        fixed_multiplier: float,
    ) -> Projection:
        def s(attr: str) -> float:
            return float(sum(getattr(p, attr) or 0 for p in year1_monthly))

        # Revenues (by category)
        y1_rev_licenses = s("revenue_licenses")
        y1_rev_consulting = s("revenue_consulting")
        y1_rev_products = s("revenue_products")
        y1_rev_other = s("revenue_other")
        y1_total_revenue = s("total_revenue")

        # Expenses split
        y1_exp_salaries = s("expense_salaries")
        y1_exp_consulting = s("expense_consulting")
        y1_exp_marketing = s("expense_marketing")
        y1_exp_operations = s("expense_operations")
        y1_exp_other = s("expense_other")

        fixed_costs_y1 = y1_exp_salaries + y1_exp_consulting + y1_exp_marketing + y1_exp_operations
        variable_costs_y1 = y1_exp_other

        # Apply multipliers
        total_revenue = y1_total_revenue * revenue_multiplier

        # Allocate revenue categories proportionally (keep the mix)
        def alloc(y1_part: float) -> float:
            if y1_total_revenue <= 0:
                return 0.0
            return total_revenue * (y1_part / y1_total_revenue)

        revenue_licenses = alloc(y1_rev_licenses)
        revenue_consulting = alloc(y1_rev_consulting)
        revenue_products = alloc(y1_rev_products)
        revenue_other = alloc(y1_rev_other)

        fixed_costs = fixed_costs_y1 * fixed_multiplier
        variable_costs = variable_costs_y1 * variable_multiplier

        # Re-split fixed costs by their original proportions
        def split_fixed(y1_component: float) -> float:
            if fixed_costs_y1 <= 0:
                return 0.0
            return fixed_costs * (y1_component / fixed_costs_y1)

        expense_salaries = split_fixed(y1_exp_salaries)
        expense_consulting = split_fixed(y1_exp_consulting)
        expense_marketing = split_fixed(y1_exp_marketing)
        expense_operations = split_fixed(y1_exp_operations)
        expense_other = variable_costs

        total_expenses = expense_salaries + expense_consulting + expense_marketing + expense_operations + expense_other

        ebitda = total_revenue - total_expenses
        net_income = ebitda

        operating_cash_flow = net_income
        investing_cash_flow = 0.0
        financing_cash_flow = 0.0
        net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow

        return Projection(
            scenario_id=scenario_id,
            period_date=period_dt.date(),
            period_type=year_label,

            revenue_licenses=revenue_licenses,
            revenue_consulting=revenue_consulting,
            revenue_products=revenue_products,
            revenue_other=revenue_other,
            total_revenue=total_revenue,

            expense_salaries=expense_salaries,
            expense_consulting=expense_consulting,
            expense_marketing=expense_marketing,
            expense_operations=expense_operations,
            expense_other=expense_other,
            total_expenses=total_expenses,

            ebitda=ebitda,
            net_income=net_income,

            operating_cash_flow=operating_cash_flow,
            investing_cash_flow=investing_cash_flow,
            financing_cash_flow=financing_cash_flow,
            net_cash_flow=net_cash_flow,

            assets=0,
            liabilities=0,
            equity=0,
        )
