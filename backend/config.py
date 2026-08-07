from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://shortlister:shortlister@localhost:5432/resume_shortlister"
    api_secret_key: str = "dev-secret-key-change-in-production"
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "./uploads"
    vector_store_path: str = "./vector_store"
    max_upload_size_mb: int = 25
    redis_url: str = "redis://localhost:6379/0"
    environment: str = "development"
    log_level: str = "INFO"

    groq_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    ollama_base_url: str = "http://localhost:11434"
    llm_provider_order: str = "gemini,groq,ollama"
    default_llm_model: str = "llama-3.3-70b-versatile"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Auth
    google_client_id: str = ""
    google_client_secret: str = ""

    # Security
    file_encryption_key: str = ""
    signed_url_ttl_seconds: int = 3600
    rate_limit_per_minute: int = 100
    rate_limit_rank_per_hour: int = 10

    # Monitoring
    sentry_dsn: str = ""
    enable_structured_logging: bool = True

    # Celery
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
