from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_db
from app.models.scenario import Scenario
from app.models.projection import Projection
from app.services.projection_engine import ProjectionEngine

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


# ----- Pydantic Schemas -----

class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    base_date: datetime
    projection_months: int = 36
    sales_assumptions: dict = Field(default_factory=dict)
    expense_assumptions: dict = Field(default_factory=dict)
    capex_assumptions: dict = Field(default_factory=dict)
    parameters: dict = Field(default_factory=dict)


class ScenarioResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    # On expose encore ces champs dans Swagger, mais ils viennent de assumptions
    base_date: Optional[datetime] = None
    projection_months: Optional[int] = None

    is_active: bool
    assumptions: Optional[dict] = None
    created_at: datetime


class ProjectionResponse(BaseModel):
    id: int
    scenario_id: int
    period_date: str
    period_type: str
    total_revenue: float
    total_expenses: float
    ebitda: float
    net_income: float
    net_cash_flow: float


# ----- Helpers -----

def scenario_to_response(s: Scenario) -> dict:
    """
    Convertit un modèle SQLAlchemy Scenario vers le format API attendu.
    base_date et projection_months sont lus depuis assumptions.
    """
    assumptions = s.assumptions or {}

    base_date_raw = assumptions.get("base_date")
    base_date = None
    if isinstance(base_date_raw, str):
        try:
            base_date = datetime.fromisoformat(base_date_raw.replace("Z", "+00:00"))
        except Exception:
            base_date = None

    return {
        "id": s.id,
        "name": s.name,
        "description": s.description,
        "base_date": base_date,
        "projection_months": assumptions.get("projection_months"),
        "is_active": s.is_active,
        "assumptions": assumptions,
        "created_at": s.created_at,
    }


# ----- Endpoints -----

@router.post("/", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(scenario: ScenarioCreate, db: Session = Depends(get_db)):
    db_scenario = Scenario(
        name=scenario.name,
        description=scenario.description,
        assumptions={
            "base_date": scenario.base_date.isoformat(),
            "projection_months": scenario.projection_months,
            "sales_assumptions": scenario.sales_assumptions,
            "expense_assumptions": scenario.expense_assumptions,
            "capex_assumptions": scenario.capex_assumptions,
            "parameters": scenario.parameters,
        },
        is_active=True,
    )
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return scenario_to_response(db_scenario)


@router.get("/", response_model=List[ScenarioResponse])
def list_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).filter(Scenario.is_active == True).all()
    return [scenario_to_response(s) for s in scenarios]


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario_to_response(scenario)


@router.post("/{scenario_id}/calculate")
def calculate_projections(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    db.query(Projection).filter(Projection.scenario_id == scenario_id).delete()
    db.commit()

    engine = ProjectionEngine(db)
    projections = engine.calculate_projections(scenario_id)

    return {"message": "Projections calculated", "count": len(projections)}


@router.get("/{scenario_id}/projections", response_model=List[ProjectionResponse])
def get_projections(scenario_id: int, db: Session = Depends(get_db)):
    projections = (
        db.query(Projection)
        .filter(Projection.scenario_id == scenario_id)
        .order_by(Projection.period_date)
        .all()
    )
    return projections


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario.is_active = False
    db.commit()
    return None
