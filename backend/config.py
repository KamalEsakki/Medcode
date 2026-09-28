import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "MedCode AI Backend"
    VERSION: str = "1.1.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://medcode_user:medcode_secure_pass_2026@localhost:5432/medcode_db")
    SQLITE_FALLBACK_URL: str = "sqlite:///./medcode_local.db"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "medcode_prototype_super_secret_jwt_key_2026_change_in_production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "*"
    ]
    
    # AI Engine
    AI_MODE: str = os.getenv("AI_MODE", "demo") # "demo" or "live"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Zoom Integration Settings (Placeholders - Application works seamlessly in demo mode if empty)
    ZOOM_ACCOUNT_ID: Optional[str] = os.getenv("ZOOM_ACCOUNT_ID", "")
    ZOOM_CLIENT_ID: Optional[str] = os.getenv("ZOOM_CLIENT_ID", "")
    ZOOM_CLIENT_SECRET: Optional[str] = os.getenv("ZOOM_CLIENT_SECRET", "")
    ZOOM_WEBHOOK_SECRET: Optional[str] = os.getenv("ZOOM_WEBHOOK_SECRET", "")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
