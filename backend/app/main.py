from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Agent IA Financier pour projections 3 ans",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (all API routes are under /api)
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup():
    # Dev only: create tables automatically
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "AIA Regenord API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
