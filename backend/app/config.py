from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings and configuration."""

    # Application
    app_name: str = "Mood API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://mood_user:mood_pass@db:5432/mood_db"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    # OpenAI
    openai_api_key: Optional[str] = None

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Storage
    storage_type: str = "local"  # local or s3
    storage_path: str = "/app/data"
    s3_bucket: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
