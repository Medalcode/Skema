from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://skema:skema@localhost:5432/skema_db"
    SQL_ECHO: bool = False
    API_PORT: int = 8000
    CLASSIFIER_MODEL: str = "hybrid"
    CONFIDENCE_THRESHOLD: float = 0.60
    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"
    CORS_ORIGINS: list[str] = ["*"]
    API_KEY: str = ""
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )


settings = Settings()
