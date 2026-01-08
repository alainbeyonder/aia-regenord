from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["authentication"])
def auth_health():
    return {"status": "ok", "service": "auth"}
