from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_secret_key: str = Field(default="dev-only-change-me", repr=False)
    database_url: str = "postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"
    storage_dir: str = "/app/storage"

    ai_provider: str = "none"
    anthropic_api_key: str = Field(default="", repr=False)
    ai_model: str = ""

    salary_threshold_inr: int = 1_500_000  # strictly greater-than rule applied in filters

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
