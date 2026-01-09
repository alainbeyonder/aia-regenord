from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class QBOTransaction(Base):
    """
    Modèle pour les transactions QuickBooks Online.
    Une transaction peut avoir plusieurs lignes (QBOTransactionLine).
    """
    __tablename__ = "qbo_transactions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    qbo_txn_id = Column(String(100), unique=True, nullable=False, index=True)
    qbo_txn_type = Column(String(50), nullable=False)  # Invoice, Payment, Expense, etc.
    txn_date = Column(DateTime, nullable=False, index=True)
    
    # Informations générales
    doc_number = Column(String(50), nullable=True)
    total_amount = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="CAD")
    
    # Métadonnées
    sync_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec les lignes de transaction
    transaction_lines = relationship("QBOTransactionLine", back_populates="transaction", cascade="all, delete-orphan")
