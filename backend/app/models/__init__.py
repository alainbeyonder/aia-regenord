# Base model import (important for Alembic)
from app.core.database import Base

# Import all models to ensure they are registered with Base.metadata
from .company import Company
from .qbo_connection import QBOConnection
from .qbo_account import QBOAccount
from .qbo_transaction import QBOTransaction
from .qbo_transaction_line import QBOTransactionLine
from .qbo_report_snapshot import QBOReportSnapshot
from .scenario import Scenario
from .projection import Projection

__all__ = [
    "Base",
    "Company",
    "QBOConnection",
    "QBOAccount",
    "QBOTransaction",
    "QBOTransactionLine",
    "QBOReportSnapshot",
    "Scenario",
    "Projection",
]
