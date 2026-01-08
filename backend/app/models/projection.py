from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Projection(Base):
    __tablename__ = "projections"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    period_date = Column(Date, nullable=False)  # date du mois projeté
    period_type = Column(String(20), default="monthly")  # monthly, annual

    # Revenus
    revenue_licenses = Column(Numeric(15, 2), default=0)
    revenue_consulting = Column(Numeric(15, 2), default=0)
    revenue_products = Column(Numeric(15, 2), default=0)
    revenue_other = Column(Numeric(15, 2), default=0)
    total_revenue = Column(Numeric(15, 2), nullable=False)

    # Dépenses
    expense_salaries = Column(Numeric(15, 2), default=0)
    expense_consulting = Column(Numeric(15, 2), default=0)
    expense_marketing = Column(Numeric(15, 2), default=0)
    expense_operations = Column(Numeric(15, 2), default=0)
    expense_other = Column(Numeric(15, 2), default=0)
    total_expenses = Column(Numeric(15, 2), nullable=False)

    # EBITDA et résultat net
    ebitda = Column(Numeric(15, 2), nullable=False)
    net_income = Column(Numeric(15, 2), nullable=False)

    # Cash flow
    operating_cash_flow = Column(Numeric(15, 2), default=0)
    investing_cash_flow = Column(Numeric(15, 2), default=0)
    financing_cash_flow = Column(Numeric(15, 2), default=0)
    net_cash_flow = Column(Numeric(15, 2), nullable=False)

    # Bilan (simplifié)
    assets = Column(Numeric(15, 2), default=0)
    liabilities = Column(Numeric(15, 2), default=0)
    equity = Column(Numeric(15, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    scenario = relationship("Scenario", back_populates="projections")
