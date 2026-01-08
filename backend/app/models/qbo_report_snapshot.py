from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class QBOReportSnapshot(Base):
    __tablename__ = "qbo_report_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True, nullable=False)

    report_type = Column(String, index=True, nullable=False)  # "ProfitAndLoss" / "BalanceSheet"
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)

    raw_json = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
