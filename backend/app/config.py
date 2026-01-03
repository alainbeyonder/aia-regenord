from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache

class Settings(BaseSettings):
    """Configuration de l'application AIA Regenord"""
    
    # Informations de l'application
    APP_NAME: str = "AIA Regenord"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # QuickBooks Online API
    QBO_CLIENT_ID: str
    QBO_CLIENT_SECRET: str
    QBO_REDIRECT_URI: str = "http://localhost:8000/callback"
    QBO_COMPANY_ID: str
    QBO_REFRESH_TOKEN: str = ""
    QBO_ACCESS_TOKEN: str = ""
    
    # OpenAI API
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Base de données
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/aia_regenord"
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 heure
    
    # Sécurité
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Projections financières
    PROJECTION_YEARS: int = 3
    DEFAULT_GROWTH_RATE: float = 0.05  # 5%
    DEFAULT_INFLATION_RATE: float = 0.03  # 3%
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Retourne une instance singleton des paramètres"""
    return Settings()

settings = get_settings()
