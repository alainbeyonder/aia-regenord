from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)

    role = Column(String(50), default="client", nullable=False)
    status = Column(String(50), default="active", nullable=False)
    must_change_password = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="users")
    handled_requests = relationship("AccessRequest", back_populates="handled_by_user")
    uploads = relationship("Upload", back_populates="user")
    assumption_sets = relationship("AssumptionSet", back_populates="created_by_user")
    simulation_runs = relationship("SimulationRun", back_populates="created_by_user")
    pdf_analyses = relationship("PdfAnalysis", back_populates="created_by_user")
