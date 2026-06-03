from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Configuración centralizada de la aplicación."""
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://skema:skema@localhost:5432/skema_db"
    SQL_ECHO: bool = False
    
    # API
    API_PORT: int = 8000
    
    # Classifier
    CLASSIFIER_MODEL: str = "hybrid"
    CONFIDENCE_THRESHOLD: float = 0.60
    
    # Embeddings
    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
