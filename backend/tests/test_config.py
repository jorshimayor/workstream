from __future__ import annotations

from app.core.config import Settings


def test_default_settings_target_postgres() -> None:
    settings = Settings()

    assert settings.app_name == "Workstream API"
    assert settings.database_url.startswith("postgresql+asyncpg://")

