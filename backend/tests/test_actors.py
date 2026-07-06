from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.adapters.auth.dev import actor_id_from_external_identity
from app.core.config import get_settings
from app.db import session as db_session
from app.main import create_app
from app.modules.actors.models import ActorIdentity, ActorProfile
from app.modules.actors.schemas import ActorProfileActivationRequest
from app.modules.actors.service import ActorService
from app.modules.tasks.models import AuditEvent
from app.schemas.auth import ActorContext


@pytest.fixture
def actor_database_env(
    monkeypatch: pytest.MonkeyPatch,
    postgres_database_url: str,
    migration_lock,
) -> Iterator[str]:
    """Run actor registry tests against a migrated Postgres schema."""
    monkeypatch.setenv("WORKSTREAM_DATABASE_URL", postgres_database_url)
    set_dev_actor(monkeypatch, roles="worker", subject="actor-registry-worker")
    get_settings.cache_clear()
    asyncio.run(db_session.dispose_engine())

    config = alembic_config()
    with migration_lock():
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        yield postgres_database_url
        command.downgrade(config, "base")
    asyncio.run(db_session.dispose_engine())
    get_settings.cache_clear()


@pytest.fixture
async def actor_client(actor_database_env: str) -> AsyncIterator[AsyncClient]:
    """Yield an in-process client backed by the migrated actor database."""
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


def alembic_config() -> Config:
    """Return Alembic configuration for backend migrations."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    return config


def set_dev_actor(
    monkeypatch: pytest.MonkeyPatch,
    *,
    roles: str,
    subject: str,
    token: str = "actor-token",
    issuer: str = "flow-test",
    email: str | None = None,
    display_name: str | None = None,
) -> None:
    """Configure the development verifier for one actor."""
    monkeypatch.setenv("WORKSTREAM_AUTH_PROVIDER", "dev")
    monkeypatch.setenv("WORKSTREAM_ENVIRONMENT", "test")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_TOKEN", token)
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_SUBJECT", subject)
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_ISSUER", issuer)
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_EMAIL", email or f"{subject}@example.test")
    monkeypatch.setenv(
        "WORKSTREAM_DEV_AUTH_DISPLAY_NAME",
        display_name or subject.replace("-", " ").title(),
    )
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_ROLES", roles)
    get_settings.cache_clear()


def auth_headers(token: str = "actor-token") -> dict[str, str]:
    """Return bearer auth headers for actor registry tests."""
    return {"Authorization": f"Bearer {token}"}


def actor_id(subject: str, issuer: str = "flow-test") -> str:
    """Return the stable actor id for a test issuer and subject."""
    return actor_id_from_external_identity(issuer, subject)


def actor_context(
    *,
    subject: str,
    roles: tuple[str, ...],
    claim_snapshot: dict | None = None,
) -> ActorContext:
    """Build a trusted actor context for service-level actor tests."""
    return ActorContext(
        actor_id=actor_id(subject),
        external_subject=subject,
        external_issuer="flow-test",
        email=f"{subject}@example.test",
        display_name=subject.replace("-", " ").title(),
        roles=roles,
        claim_snapshot=claim_snapshot or {"roles": roles},
        auth_source="dev_mock",
        is_dev_auth=True,
    )


async def test_auth_me_registers_identity_and_observed_profiles_without_duplicates(
    actor_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_dev_actor(monkeypatch, roles="worker,reviewer", subject="observed-actor")

    first = await actor_client.get("/api/v1/auth/me", headers=auth_headers())
    second = await actor_client.get("/api/v1/auth/me", headers=auth_headers())

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    async with db_session.get_session_factory()() as session:
        identity_rows = (
            await session.execute(
                select(ActorIdentity).where(ActorIdentity.actor_id == actor_id("observed-actor"))
            )
        ).scalars().all()
        profile_rows = (
            await session.execute(
                select(ActorProfile)
                .where(ActorProfile.actor_id == actor_id("observed-actor"))
                .order_by(ActorProfile.profile_type.asc())
            )
        ).scalars().all()

    assert len(identity_rows) == 1
    assert identity_rows[0].last_seen_roles == ["worker", "reviewer"]
    assert [(profile.profile_type, profile.status) for profile in profile_rows] == [
        ("reviewer", "observed"),
        ("worker", "observed"),
    ]


async def test_repeated_auth_me_does_not_rewrite_unchanged_observed_profile(
    actor_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_dev_actor(monkeypatch, roles="worker", subject="freshness-worker")
    first = await actor_client.get("/api/v1/auth/me", headers=auth_headers())
    assert first.status_code == 200, first.text
    stale_time = datetime.now(UTC) - timedelta(days=1)
    async with db_session.get_session_factory()() as session:
        profile = await session.scalar(
            select(ActorProfile).where(
                ActorProfile.actor_id == actor_id("freshness-worker"),
                ActorProfile.profile_type == "worker",
            )
        )
        assert profile is not None
        profile.updated_at = stale_time
        await session.commit()

    second = await actor_client.get("/api/v1/auth/me", headers=auth_headers())
    assert second.status_code == 200, second.text
    async with db_session.get_session_factory()() as session:
        profile_rows = (
            await session.execute(
                select(ActorProfile).where(
                    ActorProfile.actor_id == actor_id("freshness-worker"),
                    ActorProfile.profile_type == "worker",
                )
            )
        ).scalars().all()

    assert len(profile_rows) == 1
    assert profile_rows[0].status == "observed"
    assert profile_rows[0].updated_at == stale_time


async def test_auth_me_refreshes_identity_after_configured_interval(
    actor_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_dev_actor(monkeypatch, roles="worker", subject="stale-identity-worker")
    created = await actor_client.get("/api/v1/auth/me", headers=auth_headers())
    assert created.status_code == 200, created.text
    stale_time = datetime.now(UTC) - timedelta(minutes=10)
    async with db_session.get_session_factory()() as session:
        identity = await session.scalar(
            select(ActorIdentity).where(
                ActorIdentity.actor_id == actor_id("stale-identity-worker")
            )
        )
        assert identity is not None
        identity.last_seen_at = stale_time
        await session.commit()

    refreshed = await actor_client.get("/api/v1/auth/me", headers=auth_headers())
    assert refreshed.status_code == 200, refreshed.text
    async with db_session.get_session_factory()() as session:
        identity = await session.scalar(
            select(ActorIdentity).where(
                ActorIdentity.actor_id == actor_id("stale-identity-worker")
            )
        )

    assert identity is not None
    assert identity.last_seen_at > stale_time


async def test_zero_registry_refresh_interval_writes_identity_every_time(
    actor_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WORKSTREAM_ACTOR_REGISTRY_REFRESH_INTERVAL_SECONDS", "0")
    get_settings.cache_clear()
    set_dev_actor(monkeypatch, roles="worker", subject="always-refresh-worker")
    first = await actor_client.get("/api/v1/auth/me", headers=auth_headers())
    assert first.status_code == 200, first.text
    stale_time = datetime.now(UTC) - timedelta(minutes=10)
    async with db_session.get_session_factory()() as session:
        identity = await session.scalar(
            select(ActorIdentity).where(
                ActorIdentity.actor_id == actor_id("always-refresh-worker")
            )
        )
        assert identity is not None
        identity.last_seen_at = stale_time
        await session.commit()

    second = await actor_client.get("/api/v1/auth/me", headers=auth_headers())
    assert second.status_code == 200, second.text
    async with db_session.get_session_factory()() as session:
        identity = await session.scalar(
            select(ActorIdentity).where(
                ActorIdentity.actor_id == actor_id("always-refresh-worker")
            )
        )

    assert identity is not None
    assert identity.last_seen_at > stale_time


@pytest.mark.parametrize("role", ["worker", "reviewer", "admin", "project_manager"])
async def test_token_roles_create_observed_non_eligibility_profiles(
    actor_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    role: str,
) -> None:
    subject = f"{role}-observed"
    set_dev_actor(monkeypatch, roles=role, subject=subject)

    response = await actor_client.get("/api/v1/auth/me", headers=auth_headers())

    assert response.status_code == 200, response.text
    async with db_session.get_session_factory()() as session:
        profile = await session.scalar(
            select(ActorProfile).where(
                ActorProfile.actor_id == actor_id(subject),
                ActorProfile.profile_type == role,
            )
        )

    assert profile is not None
    assert profile.status == "observed"
    assert profile.scope_type == "global"
    assert profile.scope_id == "global"


async def test_worker_profile_activation_is_explicit_and_audited(
    actor_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_dev_actor(monkeypatch, roles="worker", subject="explicit-worker")

    response = await actor_client.post(
        "/api/v1/workers/me/profile",
        headers=auth_headers(),
        json={
            "skill_tags": [" STEM ", "stem", "finance"],
            "email": "spoof@example.test",
        },
    )
    assert response.status_code == 422

    profile_response = await actor_client.post(
        "/api/v1/workers/me/profile",
        headers=auth_headers(),
        json={"skill_tags": [" STEM ", "stem", "finance"]},
    )

    assert profile_response.status_code == 200, profile_response.text
    body = profile_response.json()
    assert body["profile_type"] == "worker"
    assert body["status"] == "active"
    assert body["skill_tags"] == ["stem", "finance"]
    assert body["email"] == "explicit-worker@example.test"
    async with db_session.get_session_factory()() as session:
        events = (
            await session.execute(
                select(AuditEvent).where(
                    AuditEvent.entity_type == "actor_profile",
                    AuditEvent.entity_id == body["id"],
                )
            )
        ).scalars().all()

    assert any(event.event_type == "actor_profile_activated" for event in events)


async def test_observation_preserves_active_and_disabled_statuses(
    actor_database_env: str,
) -> None:
    active_actor = actor_context(subject="active-preserved", roles=("worker",))
    disabled_actor = actor_context(subject="disabled-preserved", roles=("worker",))
    async with db_session.get_session_factory()() as session:
        service = ActorService(session)
        await service.activate_worker_profile(
            active_actor,
            ActorProfileActivationRequest(skill_tags=["stem"]),
        )
        await service.activate_worker_profile(
            disabled_actor,
            ActorProfileActivationRequest(skill_tags=["stem"]),
        )
        disabled_profile = await service.get_active_profile(disabled_actor.actor_id, "worker")
        assert disabled_profile is not None
        disabled_profile.status = "disabled"
        await session.commit()

        await service.register_actor(active_actor)
        await service.register_actor(disabled_actor)

    async with db_session.get_session_factory()() as session:
        active_profile = await session.scalar(
            select(ActorProfile).where(ActorProfile.actor_id == active_actor.actor_id)
        )
        disabled_profile = await session.scalar(
            select(ActorProfile).where(ActorProfile.actor_id == disabled_actor.actor_id)
        )

    assert active_profile is not None
    assert active_profile.status == "active"
    assert active_profile.profile_metadata == {"source": "worker_profile_api"}
    assert disabled_profile is not None
    assert disabled_profile.status == "disabled"
    assert disabled_profile.profile_metadata == {"source": "worker_profile_api"}


async def test_observation_can_explicitly_clear_metadata(actor_database_env: str) -> None:
    actor = actor_context(subject="metadata-clear-worker", roles=("worker",))
    async with db_session.get_session_factory()() as session:
        service = ActorService(session)
        await service.ensure_observed_profile(
            actor,
            profile_type="worker",
            scope_type="global",
            scope_id="global",
            profile_metadata={"source": "initial"},
        )
        await service.ensure_observed_profile(
            actor,
            profile_type="worker",
            scope_type="global",
            scope_id="global",
            profile_metadata={},
        )
        await session.commit()

    async with db_session.get_session_factory()() as session:
        profile = await session.scalar(
            select(ActorProfile).where(
                ActorProfile.actor_id == actor.actor_id,
                ActorProfile.profile_type == "worker",
            )
        )

    assert profile is not None
    assert profile.profile_metadata == {}


async def test_scoped_project_owner_profile_comes_from_trusted_relationship_claim(
    actor_database_env: str,
) -> None:
    actor = actor_context(
        subject="source-contact",
        roles=("project_manager",),
        claim_snapshot={
            "workstream_relationship_profiles": [
                {
                    "profile_type": "project_owner",
                    "scope_type": "project",
                    "scope_id": "project-123",
                    "profile_metadata": {
                        "organization": "Example Labs",
                        "api_key": "must-not-persist",
                    },
                }
            ]
        },
    )
    async with db_session.get_session_factory()() as session:
        service = ActorService(session)
        await service.register_actor(actor)
        await service.register_actor(actor)

    async with db_session.get_session_factory()() as session:
        identity = await session.scalar(
            select(ActorIdentity).where(ActorIdentity.actor_id == actor.actor_id)
        )
        profiles = (
            await session.execute(
                select(ActorProfile).where(
                    ActorProfile.actor_id == actor.actor_id,
                    ActorProfile.profile_type == "project_owner",
                )
            )
        ).scalars().all()
        audit_events = (
            await session.execute(
                select(AuditEvent).where(
                    AuditEvent.entity_type == "actor_profile",
                    AuditEvent.actor_id == actor.actor_id,
                )
            )
        ).scalars().all()

    assert identity is not None
    identity_snapshot = identity.last_claim_snapshot
    assert identity_snapshot["workstream_relationship_profiles"] == [
        {
            "profile_type": "project_owner",
            "scope_type": "project",
            "scope_id": "project-123",
        }
    ]
    assert "must-not-persist" not in str(identity_snapshot)
    assert "api_key" not in str(identity_snapshot)
    assert "secret" not in str(identity_snapshot).lower()
    assert "token" not in str(identity_snapshot).lower()
    assert len(profiles) == 1
    assert profiles[0].status == "observed"
    assert profiles[0].scope_type == "project"
    assert profiles[0].scope_id == "project-123"
    assert profiles[0].profile_metadata == {"source": "trusted_relationship_claim"}
    assert audit_events
    for audit_event in audit_events:
        claim_snapshot = audit_event.claim_snapshot
        assert "must-not-persist" not in str(claim_snapshot)
        assert "api_key" not in str(claim_snapshot)
        assert "secret" not in str(claim_snapshot).lower()
        assert "token" not in str(claim_snapshot).lower()


async def test_active_profile_without_matching_token_role_cannot_use_worker_profile_api(
    actor_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_dev_actor(monkeypatch, roles="worker", subject="role-lost-worker")
    created = await actor_client.post(
        "/api/v1/workers/me/profile",
        headers=auth_headers(),
        json={"skill_tags": ["stem"]},
    )
    assert created.status_code == 200, created.text

    set_dev_actor(monkeypatch, roles="project_manager", subject="role-lost-worker")
    denied = await actor_client.post(
        "/api/v1/workers/me/profile",
        headers=auth_headers(),
        json={"skill_tags": ["stem"]},
    )

    assert denied.status_code == 403
