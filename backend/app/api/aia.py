"""
Endpoints API pour les vues financières AIA.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
import csv
import io
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.assumption_set import AssumptionSet
from app.models.simulation_run import SimulationRun
from app.models.pdf_analysis import PdfAnalysis
from app.models.upload import Upload
from app.models.user import User
from app.services.aia_simulation_service import AIASimulationService
from app.services.aia_narration_service import AIANarrationService
from app.services.pdf_analyze_service import PdfAnalyzeService
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


class AssumptionSetCreate(BaseModel):
    company_id: int
    name: str = Field(..., min_length=2, max_length=255)
    scenario_key: str = Field(..., min_length=2, max_length=100)
    payload_json: Dict[str, Any]


class AssumptionSetResponse(BaseModel):
    id: int
    company_id: int
    name: str
    scenario_key: str
    status: str
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime


class SimulationCreate(BaseModel):
    company_id: int
    assumption_set_id: int
    period_start: date
    horizon_months: int = Field(12, ge=1, le=36)
    horizon_years: int = Field(2, ge=0, le=5)
    baseline_refs: Optional[Dict[str, Any]] = None


class SimulationRunResponse(BaseModel):
    id: int
    company_id: int
    assumption_set_id: int
    period_start: date
    period_end: date
    horizon_months: int
    horizon_years: int
    result_json: Dict[str, Any]
    created_by_user_id: int
    created_at: datetime


class ExplainRequest(BaseModel):
    company_id: int
    run_id: int
    tone: Optional[str] = "executive"


class PdfAnalyzeRequest(BaseModel):
    company_id: int
    pl_upload_id: int
    bs_upload_id: int
    loans_upload_id: Optional[int] = None


def _resolve_company_id(company_id: Optional[int], current_user: User) -> int:
    if current_user.role != "admin":
        if not current_user.company_id:
            raise HTTPException(status_code=400, detail="User has no company")
        if company_id is not None and company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user.company_id
    if company_id is None:
        raise HTTPException(status_code=400, detail="company_id required")
    return company_id


def _ensure_company_access(company_id: int, current_user: User) -> None:
    if current_user.role != "admin" and company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Forbidden")


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


@router.post("/assumptions", response_model=AssumptionSetResponse)
def create_assumption_set(
    payload: AssumptionSetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _resolve_company_id(payload.company_id, current_user)
    assumption_set = AssumptionSet(
        company_id=company_id,
        name=payload.name,
        scenario_key=payload.scenario_key,
        payload_json=payload.payload_json,
        status="draft",
        created_by_user_id=current_user.id,
    )
    db.add(assumption_set)
    db.commit()
    db.refresh(assumption_set)
    return assumption_set


@router.get("/assumptions", response_model=List[AssumptionSetResponse])
def list_assumption_sets(
    company_id: Optional[int] = Query(None, description="ID de l'entreprise"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _resolve_company_id(company_id, current_user)
    return (
        db.query(AssumptionSet)
        .filter(AssumptionSet.company_id == company_id)
        .order_by(AssumptionSet.created_at.desc())
        .all()
    )


@router.get("/assumptions/{assumption_id}", response_model=AssumptionSetResponse)
def get_assumption_set(
    assumption_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assumption_set = db.query(AssumptionSet).filter(AssumptionSet.id == assumption_id).one_or_none()
    if not assumption_set:
        raise HTTPException(status_code=404, detail="Assumption set not found")
    _ensure_company_access(assumption_set.company_id, current_user)
    return assumption_set


@router.post("/assumptions/{assumption_id}/validate", response_model=AssumptionSetResponse)
def validate_assumption_set(
    assumption_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assumption_set = db.query(AssumptionSet).filter(AssumptionSet.id == assumption_id).one_or_none()
    if not assumption_set:
        raise HTTPException(status_code=404, detail="Assumption set not found")
    _ensure_company_access(assumption_set.company_id, current_user)
    assumption_set.status = "validated"
    assumption_set.updated_at = datetime.utcnow()
    db.add(assumption_set)
    db.commit()
    db.refresh(assumption_set)
    return assumption_set


@router.post("/simulate")
def simulate(
    payload: SimulationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _resolve_company_id(payload.company_id, current_user)
    assumption_set = (
        db.query(AssumptionSet)
        .filter(AssumptionSet.id == payload.assumption_set_id)
        .one_or_none()
    )
    if not assumption_set:
        raise HTTPException(status_code=404, detail="Assumption set not found")
    if assumption_set.company_id != company_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    period_end = payload.period_start + relativedelta(
        months=payload.horizon_months + (payload.horizon_years * 12)
    )
    result_json = AIASimulationService.build_placeholder_result(
        company_id=company_id,
        assumption_set_id=payload.assumption_set_id,
        horizon_months=payload.horizon_months,
        horizon_years=payload.horizon_years,
    )

    run = SimulationRun(
        company_id=company_id,
        assumption_set_id=payload.assumption_set_id,
        period_start=payload.period_start,
        period_end=period_end,
        horizon_months=payload.horizon_months,
        horizon_years=payload.horizon_years,
        result_json=result_json,
        created_by_user_id=current_user.id,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return {"run_id": run.id}


@router.get("/runs", response_model=List[SimulationRunResponse])
def list_simulation_runs(
    company_id: Optional[int] = Query(None, description="ID de l'entreprise"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _resolve_company_id(company_id, current_user)
    return (
        db.query(SimulationRun)
        .filter(SimulationRun.company_id == company_id)
        .order_by(SimulationRun.created_at.desc())
        .all()
    )


@router.get("/runs/{run_id}", response_model=SimulationRunResponse)
def get_simulation_run(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    _ensure_company_access(run.company_id, current_user)
    return run


@router.post("/explain")
def explain_run(
    payload: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_tones = {"bank", "executive", "internal"}
    tone = payload.tone or "executive"
    if tone not in allowed_tones:
        raise HTTPException(status_code=400, detail="Invalid tone")

    company_id = _resolve_company_id(payload.company_id, current_user)
    run = db.query(SimulationRun).filter(SimulationRun.id == payload.run_id).one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    if run.company_id != company_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    assumption_set = (
        db.query(AssumptionSet)
        .filter(AssumptionSet.id == run.assumption_set_id)
        .one_or_none()
    )
    if not assumption_set or assumption_set.company_id != company_id:
        raise HTTPException(status_code=404, detail="Assumption set not found")

    try:
        service = AIANarrationService()
        return service.explain(
            tone=tone,
            result_json=run.result_json,
            assumptions_json=assumption_set.payload_json,
        )
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=502, detail=str(error))


@router.post("/pdf/analyze")
def analyze_pdf(
    payload: PdfAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _resolve_company_id(payload.company_id, current_user)

    uploads = (
        db.query(Upload)
        .filter(Upload.id.in_([payload.pl_upload_id, payload.bs_upload_id]))
        .all()
    )
    if len(uploads) != 2:
        raise HTTPException(status_code=404, detail="Upload not found")
    upload_map = {upload.id: upload for upload in uploads}
    pl_upload = upload_map.get(payload.pl_upload_id)
    bs_upload = upload_map.get(payload.bs_upload_id)

    if pl_upload.company_id != company_id or bs_upload.company_id != company_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    loans_upload = None
    if payload.loans_upload_id:
        loans_upload = db.query(Upload).filter(Upload.id == payload.loans_upload_id).one_or_none()
        if not loans_upload:
            raise HTTPException(status_code=404, detail="Loans upload not found")
        if loans_upload.company_id != company_id:
            raise HTTPException(status_code=403, detail="Forbidden")

    service = PdfAnalyzeService()
    client_view, aia_view, reconciliation, warnings = service.analyze(
        pl_path=pl_upload.storage_url,
        bs_path=bs_upload.storage_url,
    )

    analysis = PdfAnalysis(
        company_id=company_id,
        pl_upload_id=pl_upload.id,
        bs_upload_id=bs_upload.id,
        loans_upload_id=loans_upload.id if loans_upload else None,
        client_view_json=client_view,
        aia_view_json=aia_view,
        reconciliation_json=reconciliation,
        warnings_json=warnings,
        created_by_user_id=current_user.id,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        "client_view": client_view,
        "aia_view": aia_view,
        "reconciliation": reconciliation,
        "warnings": warnings,
    }


@router.get("/pdf/analysis/latest")
def latest_pdf_analysis(
    company_id: Optional[int] = Query(None, description="ID de l'entreprise"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _resolve_company_id(company_id, current_user)
    analysis = (
        db.query(PdfAnalysis)
        .filter(PdfAnalysis.company_id == company_id)
        .order_by(PdfAnalysis.created_at.desc())
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysis_id": analysis.id,
        "client_view": analysis.client_view_json,
        "aia_view": analysis.aia_view_json,
        "reconciliation": analysis.reconciliation_json,
        "warnings": analysis.warnings_json,
        "created_at": analysis.created_at.isoformat(),
    }
