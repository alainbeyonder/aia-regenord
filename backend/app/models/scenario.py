from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True, nullable=False)
    name = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    assumptions = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relations
    company = relationship("Company", back_populates="scenarios")
    projections = relationship(
        "Projection",
        back_populates="scenario",
        cascade="all, delete-orphan",
    )
