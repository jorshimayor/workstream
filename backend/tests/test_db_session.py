from __future__ import annotations

import importlib

import pytest
from sqlalchemy import text

from app.core.config import get_settings


async def test_async_database_session_executes_simple_query(
    isolated_database_env: str,
) -> None:
    get_settings.cache_clear()
    db_session = importlib.reload(importlib.import_module("app.db.session"))
    session_iterator = db_session.get_db_session()

    try:
        session = await anext(session_iterator)
        result = await session.execute(text("SELECT 1"))

        assert result.scalar_one() == 1
    finally:
        await session_iterator.aclose()
        await db_session.dispose_engine()
        get_settings.cache_clear()


async def test_get_database_url_requires_workstream_database_url(monkeypatch) -> None:
    monkeypatch.delenv("WORKSTREAM_DATABASE_URL", raising=False)
    get_settings.cache_clear()
    db_session = importlib.reload(importlib.import_module("app.db.session"))

    try:
        with pytest.raises(RuntimeError, match="WORKSTREAM_DATABASE_URL must be set"):
            db_session.get_database_url()
    finally:
        await db_session.dispose_engine()
        get_settings.cache_clear()


async def test_get_engine_requires_workstream_database_url(monkeypatch) -> None:
    monkeypatch.delenv("WORKSTREAM_DATABASE_URL", raising=False)
    get_settings.cache_clear()
    db_session = importlib.reload(importlib.import_module("app.db.session"))

    try:
        with pytest.raises(RuntimeError, match="WORKSTREAM_DATABASE_URL must be set"):
            db_session.get_engine()
    finally:
        await db_session.dispose_engine()
        get_settings.cache_clear()
