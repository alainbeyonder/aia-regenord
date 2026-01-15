from pydantic_settings import BaseSettings
from typing import List, Optional
from dotenv import load_dotenv
import json
import os

load_dotenv()

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AIA Regenord"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: Optional[str] = "CHANGE_ME_TO_A_LONG_RANDOM_STRING"
    APP_BASE_URL: Optional[str] = "http://localhost:8000"
    FRONTEND_URL: Optional[str] = None

    # Database
    DATABASE_URL: Optional[str] = "postgresql://postgres:postgres@localhost:5432/aia_regenord"

    # QuickBooks Online
    QBO_CLIENT_ID: str
    QBO_CLIENT_SECRET: str
    QBO_REDIRECT_URI: str
    QBO_ENVIRONMENT: str = "production"  # Production par défaut - PAS de sandbox
    QBO_COMPANY_ID: Optional[str] = None

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_FILE: Optional[str] = None
    GOOGLE_SHEETS_FORECAST_ID: Optional[str] = None

    # DEXT
    DEXT_API_KEY: str = ""
    DEXT_API_URL: str = "https://api.dext.com/v1"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7

    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/aia-regenord.log"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS from environment if it's a JSON string
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            try:
                parsed = json.loads(cors_env)
                if isinstance(parsed, list):
                    self.CORS_ORIGINS = parsed
            except json.JSONDecodeError:
                pass  # Keep default value

settings = Settings()
