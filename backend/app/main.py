from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.endpoints import scenarios, qbo
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Créer les tables de la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AIA Regenord - Agent IA Financier",
    description="API pour projections financières 3 ans avec intégration QBO, DEXT, et Google Sheets",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(scenarios.router, prefix="/api")
app.include_router(qbo.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "AIA Regenord - Agent IA Financier API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
