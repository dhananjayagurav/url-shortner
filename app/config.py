""" Application configuration loaded from environment configuration / .env file"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    base_url: str = "http://localhost:8000"

    database_url: str = (
        "postgresql+psycopg://urlshortener:urlshortener@localhost:5432/urlshortener"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()




