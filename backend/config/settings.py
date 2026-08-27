import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "AI Krishi Mitra"
    APP_VERSION: str = "1.0.0"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "ai_krishi_mitra")
    
    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production-ai-krishi-mitra-2025")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # CORS
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
