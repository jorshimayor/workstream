from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import fcntl
import hashlib
import os
from pathlib import Path

import pytest

from app.core.config import get_settings

DEFAULT_TEST_DATABASE_URL = "postgresql+asyncpg://workstream:workstream@localhost:5433/workstream"
DDL_LOCK_DIRECTORY = Path("/tmp")


@contextmanager
def postgres_ddl_lock(database_url: str) -> Iterator[None]:
    """Serialize Alembic resets only for processes sharing one database."""
    database_key = hashlib.sha256(database_url.encode("utf-8")).hexdigest()[:16]
    lock_path = DDL_LOCK_DIRECTORY / f"workstream-postgres-ddl-{database_key}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


@pytest.fixture
def migration_lock(postgres_database_url: str):
    """Return a database-scoped PostgreSQL DDL lock context manager."""

    @contextmanager
    def lock() -> Iterator[None]:
        """Acquire the lock for this fixture's exact test database."""
        with postgres_ddl_lock(postgres_database_url):
            yield

    return lock


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
