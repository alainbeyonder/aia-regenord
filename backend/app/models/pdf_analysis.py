from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class PdfAnalysis(Base):
    __tablename__ = "pdf_analyses"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    pl_upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    bs_upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    loans_upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)
    client_view_json = Column(JSON, nullable=False)
    aia_view_json = Column(JSON, nullable=False)
    reconciliation_json = Column(JSON, nullable=False)
    warnings_json = Column(JSON, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="pdf_analyses")
    created_by_user = relationship("User", back_populates="pdf_analyses")
