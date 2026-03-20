"""
Configuration management using environment variables
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "EduTech Terminal Platform"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "development-secret-key")
    jwt_secret: str = os.getenv("JWT_SECRET", "jwt-secret-key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./edutech.db")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Kubernetes
    kubernetes_namespace: str = "edutech-terminal"
    use_kubernetes: bool = os.getenv("USE_KUBERNETES", "false").lower() == "true"
    
    # Session
    session_timeout: int = 3600
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001"
    ]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()