from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class QBOTransactionLine(Base):
    __tablename__ = "qbo_transaction_lines"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True, nullable=False)
    transaction_id = Column(Integer, ForeignKey("qbo_transactions.id"), index=True, nullable=False)

    qbo_txn_id = Column(String, index=True, nullable=False)
    qbo_txn_type = Column(String, nullable=True)
    txn_date = Column(Date, index=True, nullable=False)

    account_qbo_id = Column(String, index=True, nullable=True)
    amount = Column(Numeric(14, 2), nullable=False)

    counterparty = Column(String, nullable=True)
    memo = Column(Text, nullable=True)

    updated_at_qbo = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="qbo_transaction_lines")
    transaction = relationship("QBOTransaction", back_populates="transaction_lines")
