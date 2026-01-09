from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router

# Import all models to ensure they are registered with Base.metadata
# This ensures Alembic can detect all tables
from app.models import (
    Company, QBOConnection, QBOAccount, QBOTransaction,
    QBOTransactionLine, QBOReportSnapshot, Scenario, Projection
)

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
    # Create tables automatically if they don't exist
    # This works for both development and production
    # In production, tables are created on first startup
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Creating database tables if they don't exist...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        # Log error but don't crash the app
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating database tables: {e}")
        # In production, this might fail if tables already exist - that's OK


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
