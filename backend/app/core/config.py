from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Workstream API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "local"
    database_url: str = Field(
        default="postgresql+asyncpg://workstream:workstream@localhost:5432/workstream"
    )

    model_config = SettingsConfigDict(
        env_prefix="WORKSTREAM_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

