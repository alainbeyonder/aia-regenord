from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    assumption_set_id = Column(Integer, ForeignKey("assumption_sets.id"), nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    horizon_months = Column(Integer, default=12, nullable=False)
    horizon_years = Column(Integer, default=2, nullable=False)
    result_json = Column(JSON, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="simulation_runs")
    assumption_set = relationship("AssumptionSet", back_populates="simulation_runs")
    created_by_user = relationship("User", back_populates="simulation_runs")
