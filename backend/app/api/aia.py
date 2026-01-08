"""
Endpoints API pour les vues financières AIA.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import csv
import io
from datetime import datetime

from app.core.database import get_db
from app.services.aia_mapping_service import AIAFinancialMappingService

router = APIRouter(prefix="/aia", tags=["aia"])


class FinancialViewResponse(BaseModel):
    """Réponse pour la vue financière."""
    period_start: str
    period_end: str
    months: int
    totals_by_category: dict
    accounts_mapping: dict
    reconciliation: dict
    data_source: str


@router.get("/view", response_model=FinancialViewResponse)
def get_financial_view(
    company_id: int = Query(..., description="ID de l'entreprise"),
    months: int = Query(12, ge=1, le=36, description="Nombre de mois à analyser (1-36)"),
    db: Session = Depends(get_db)
):
    """
    Génère la vue financière agrégée par catégories AIA.
    
    Args:
        company_id: ID de l'entreprise
        months: Nombre de mois à analyser (défaut: 12, max: 36)
        db: Session de base de données
        
    Returns:
        Vue financière structurée avec mapping des comptes et réconciliation
        
    Raises:
        HTTPException: Si le service ne peut pas générer la vue
    """
    try:
        service = AIAFinancialMappingService()
        result = service.generate_financial_view(
            company_id=company_id,
            months=months,
            db=db
        )
        
        return FinancialViewResponse(**result)
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fichier de configuration non trouvé: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de la vue financière: {str(e)}"
        )


@router.get("/export/google-sheets")
def export_to_google_sheets(
    company_id: int = Query(..., description="ID de l'entreprise"),
    months: int = Query(12, ge=1, le=36, description="Nombre de mois à analyser (1-36)"),
    format: str = Query("csv", regex="^(csv|json)$", description="Format d'export: csv ou json"),
    db: Session = Depends(get_db)
):
    """
    Exporte la vue financière dans un format compatible Google Sheets.
    
    Formats disponibles:
    - csv: Fichier CSV avec feuilles séparées (format compatible Google Sheets)
    - json: JSON structuré en format tabulaire pour Google Sheets API
    
    Args:
        company_id: ID de l'entreprise
        months: Nombre de mois à analyser
        format: Format d'export (csv ou json)
        db: Session de base de données
        
    Returns:
        Fichier CSV ou JSON compatible Google Sheets
        
    Raises:
        HTTPException: Si le service ne peut pas générer l'export
    """
    try:
        service = AIAFinancialMappingService()
        result = service.generate_financial_view(
            company_id=company_id,
            months=months,
            db=db
        )
        
        if format == "csv":
            csv_content = service.format_for_google_sheets_csv(result)
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=aia_financial_view_{company_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                }
            )
        else:  # json
            json_data = service.format_for_google_sheets_json(result, company_id=company_id)
            return Response(
                content=json_data,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=aia_financial_view_{company_id}_{datetime.now().strftime('%Y%m%d')}.json"
                }
            )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fichier de configuration non trouvé: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de l'export: {str(e)}"
        )
