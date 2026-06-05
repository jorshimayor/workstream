from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.core.config import get_settings


@pytest.fixture
def sqlite_database_url(tmp_path: Path) -> str:
    return f"sqlite+aiosqlite:///{tmp_path / 'workstream_test.db'}"


@pytest.fixture
def isolated_database_env(monkeypatch: pytest.MonkeyPatch, sqlite_database_url: str) -> str:
    monkeypatch.setenv("WORKSTREAM_DATABASE_URL", sqlite_database_url)
    get_settings.cache_clear()
    yield sqlite_database_url
    get_settings.cache_clear()
