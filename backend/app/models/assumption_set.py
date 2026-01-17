from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class AssumptionSet(Base):
    __tablename__ = "assumption_sets"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    scenario_key = Column(String(100), nullable=False)
    payload_json = Column(JSON, nullable=False)
    status = Column(String(50), default="draft", nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="assumption_sets")
    created_by_user = relationship("User", back_populates="assumption_sets")
    simulation_runs = relationship(
        "SimulationRun",
        back_populates="assumption_set",
        cascade="all, delete-orphan",
    )
