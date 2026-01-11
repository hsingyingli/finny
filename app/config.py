from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+psycopg://ai:ai@localhost:5532/ai"

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_refresh_secret_key: str = "your-refresh-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15  # 15 minutes
    jwt_refresh_token_expire_days: int = 30  # 30 days

    # App
    app_name: str = "Finny API"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
