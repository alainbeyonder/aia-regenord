from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional
import logging

from app.financial_projections import FinancialProjections
from app.qbo_client import QBOClient

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/projections")
async def get_projections(assumptions: Optional[Dict] = None):
    """Évaluations financières 3 ans"""
    try:
        fp = FinancialProjections()
        projections = fp.generate_projections(assumptions)
        return {
            "status": "success",
            "data": projections
        }
    except Exception as e:
        logger.error(f"Erreur projections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/qbo/profit-loss")
async def get_profit_loss(start_date: str, end_date: str):
    """Récupère P&L de QuickBooks"""
    try:
        qbo = QBOClient()
        data = qbo.get_profit_loss(start_date, end_date)
        if data:
            return {"status": "success", "data": data}
        raise HTTPException(status_code=404, detail="Données non trouvées")
    except Exception as e:
        logger.error(f"Erreur P&L: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/qbo/balance-sheet")
async def get_balance_sheet(as_of_date: str):
    """Récupère bilan de QuickBooks"""
    try:
        qbo = QBOClient()
        data = qbo.get_balance_sheet(as_of_date)
        if data:
            return {"status": "success", "data": data}
        raise HTTPException(status_code=404, detail="Données non trouvées")
    except Exception as e:
        logger.error(f"Erreur bilan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/qbo/cash-flow")
async def get_cash_flow(start_date: str, end_date: str):
    """Récupère cash flow de QuickBooks"""
    try:
        qbo = QBOClient()
        data = qbo.get_cash_flow(start_date, end_date)
        if data:
            return {"status": "success", "data": data}
        raise HTTPException(status_code=404, detail="Données non trouvées")
    except Exception as e:
        logger.error(f"Erreur cash flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
