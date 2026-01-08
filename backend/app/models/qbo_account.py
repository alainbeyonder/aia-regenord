from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class QBOAccount(Base):
    __tablename__ = "qbo_accounts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True, nullable=False)

    qbo_account_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    account_type = Column(String, nullable=True)
    account_subtype = Column(String, nullable=True)
    classification = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    updated_at_qbo = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

