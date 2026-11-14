from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Invoice AI API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "testing", "production"] = (
        "development"
    )
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/invoice_ai.db"
    AUTO_CREATE_TABLES: bool = True
    OPENAI_API_KEY: SecretStr | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # Development only. Set a strong, unique secret in production.
    SECRET_KEY: str = Field(
        default="dev-only-change-this-secret-before-production"
    )
    JWT_ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)

    API_V1_PREFIX: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
