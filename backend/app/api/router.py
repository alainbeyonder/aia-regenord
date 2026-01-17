from fastapi import APIRouter

# Import sub-routers here
from app.api.qbo import router as qbo_router
from app.api.aia import router as aia_router
from app.api.auth import router as auth_router
from app.api.files import router as files_router
from app.api.health import router as health_router

api_router = APIRouter()

# Register routes
api_router.include_router(qbo_router)
api_router.include_router(aia_router)
api_router.include_router(auth_router)
api_router.include_router(files_router)
api_router.include_router(health_router)

# If you have other routers later, add them here:
# from app.api.scenarios import router as scenarios_router
# api_router.include_router(scenarios_router)
