from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class QBOConnection(Base):
    __tablename__ = "qbo_connections"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True, nullable=False)  # client interne AIA
    realm_id = Column(String, index=True, nullable=False)

    access_token_encrypted = Column(Text, nullable=False)
    refresh_token_encrypted = Column(Text, nullable=False)
    token_expires_at = Column(DateTime, nullable=True)

    scopes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    last_sync_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
