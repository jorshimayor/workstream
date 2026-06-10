from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path

import pytest

from app.core.config import get_settings

DEFAULT_TEST_DATABASE_URL = "postgresql+asyncpg://workstream:workstream@localhost:5433/workstream"
DDL_LOCK_PATH = Path("/tmp/workstream-postgres-ddl.lock")


@contextmanager
def postgres_ddl_lock() -> Iterator[None]:
    """Serialize schema-wide Alembic resets across local pytest processes."""
    DDL_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DDL_LOCK_PATH.open("w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


@pytest.fixture
def migration_lock():
    """Return the process-wide Postgres DDL lock context manager."""
    return postgres_ddl_lock


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
