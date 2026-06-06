from __future__ import annotations

import os

import pytest

from app.core.config import get_settings

DEFAULT_TEST_DATABASE_URL = "postgresql+asyncpg://workstream:workstream@localhost:5433/workstream"


@pytest.fixture
def postgres_database_url() -> str:
    return os.environ.get(
        "WORKSTREAM_TEST_DATABASE_URL",
        os.environ.get("WORKSTREAM_DATABASE_URL", DEFAULT_TEST_DATABASE_URL),
    )


@pytest.fixture
def isolated_database_env(monkeypatch: pytest.MonkeyPatch, postgres_database_url: str) -> str:
    monkeypatch.setenv("WORKSTREAM_DATABASE_URL", postgres_database_url)
    get_settings.cache_clear()
    yield postgres_database_url
    get_settings.cache_clear()
