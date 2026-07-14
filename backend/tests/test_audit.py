from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from alembic import command
from alembic.config import Config
from pydantic import ValidationError
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import (
    ActorReferenceKind,
    AuthorityAuditEventInput,
    AuthorityEventType,
)
from app.modules.audit.service import AuditService
from app.modules.tasks.models import AuditEvent


@pytest.fixture
def audit_database_env(postgres_database_url: str, migration_lock) -> str:
    """Ensure audit tests do not inherit another migration test's schema state."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    with migration_lock():
        command.upgrade(config, "head")
    return postgres_database_url


@pytest.fixture
async def audit_factory(audit_database_env: str):
    """Provide independent sessions over the isolated migrated database."""
    engine = create_async_engine(audit_database_env)
    try:
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        async with engine.begin() as connection:
            await connection.execute(
                text("lock table audit_events in access exclusive mode")
            )
            await connection.execute(
                text(
                    "alter table audit_events disable trigger "
                    "audit_events_reject_update_delete"
                )
            )
            await connection.execute(
                text("delete from audit_events where event_domain = 'authority'")
            )
            await connection.execute(
                text(
                    "alter table audit_events enable trigger "
                    "audit_events_reject_update_delete"
                )
            )
        await engine.dispose()


def _authority_input(event_type: AuthorityEventType, **overrides) -> AuthorityAuditEventInput:
    values = {
        "event_type": event_type,
        "entity_type": "actor",
        "entity_id": str(uuid4()),
        "actor_ref_kind": ActorReferenceKind.SYSTEM_PRINCIPAL,
        "actor_ref": "workstream:system:test",
        "request_id": uuid4(),
        "correlation_id": uuid4(),
        "permission_id": "actor.manage",
    }
    values.update(overrides)
    return AuthorityAuditEventInput(**values)


def test_authority_input_rejects_unbounded_or_inconsistent_evidence() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        _authority_input(
            AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED,
            raw_token="must-never-enter-evidence",
        )
    with pytest.raises(ValidationError, match="reference fields must be paired"):
        _authority_input(
            AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED,
            resource_type="project",
        )
    with pytest.raises(ValidationError, match="state facts"):
        _authority_input(
            AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED,
            before_facts={"nested": {"unsafe": True}},
        )
    with pytest.raises(ValidationError, match="exceed size limit"):
        _authority_input(
            AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED,
            before_facts={"status": "x" * 4096},
        )
    with pytest.raises(ValidationError, match="not allowed for this event"):
        _authority_input(
            AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED,
            before_facts={"policy_body": "must-never-enter-evidence"},
        )
    with pytest.raises(ValidationError, match="denial cannot reference"):
        _authority_input(
            AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED,
            denial_code="actor_suspended",
            idempotency_reference=uuid4(),
        )
    with pytest.raises(ValidationError, match="invalidation evidence"):
        _authority_input(AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED)


async def test_authority_writer_persists_typed_privacy_neutral_events(audit_factory) -> None:
    future_idempotency = uuid4()
    allowed = _authority_input(
        AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED,
        project_id=str(uuid4()),
        resource_type="project",
        resource_id=str(uuid4()),
        before_facts={"status": "active"},
    )
    denied = _authority_input(
        AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED,
        denial_code="permission_denied",
        reason="Local permission was not effective.",
    )
    invalidation = _authority_input(
        AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED,
        permission_id=None,
        invalidation_cause_event_id=allowed.event_id,
        invalidation_target_kind="actor",
        invalidation_target_ref="legacy:target",
        idempotency_reference=future_idempotency,
        after_facts={"status": "revoked"},
    )

    async with audit_factory() as session:
        service = AuditService(session)
        stored = [
            await service.add_authority_event(value)
            for value in (allowed, denied, invalidation)
        ]
        await session.commit()

    assert [event.event_type for event in stored] == [
        "SensitiveAuthorizationAllowed",
        "SensitiveAuthorizationDenied",
        "AuthorityInvalidationRequested",
    ]
    assert all(event.occurred_at is not None for event in stored)
    for event in stored:
        assert event.event_domain == "authority"
        assert event.event_version == 1
        assert event.external_subject is None
        assert event.external_issuer is None
        assert event.actor_roles == []
        assert event.claim_snapshot == {}
        assert event.event_payload == {}
        assert event.auth_source == "local_authority"
        assert event.is_dev_auth is False
    assert stored[0].idempotency_reference is None
    assert UUID(stored[2].idempotency_reference) == future_idempotency


async def test_legacy_writer_and_reader_remain_compatible(audit_factory) -> None:
    event = AuditEvent(
        id=str(uuid4()),
        entity_type="task",
        entity_id=str(uuid4()),
        event_type="task_created",
        from_status=None,
        to_status="draft",
        actor_id="legacy-actor",
        external_subject="opaque-subject",
        external_issuer="https://issuer.example.test",
        actor_roles=["project_manager"],
        claim_snapshot={"bounded": True},
        auth_source="verified_token",
        is_dev_auth=False,
        event_payload={"source_type": "manual"},
    )
    async with audit_factory() as session:
        repository = AuditRepository(session)
        stored = await repository.add_audit_event(event)
        await session.commit()
        listed = await repository.list_audit_events("task", event.entity_id)

    assert listed == [stored]
    assert stored.event_domain == "legacy_lifecycle"
    assert stored.event_version is None
    assert stored.occurred_at is None
    assert stored.event_payload == {"source_type": "manual"}


async def test_authority_event_rollback_leaves_no_row(audit_factory) -> None:
    value = _authority_input(AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED)
    async with audit_factory() as session:
        await AuditService(session).add_authority_event(value)
        await session.rollback()
    async with audit_factory() as session:
        assert await session.get(AuditEvent, str(value.event_id)) is None


async def test_database_rejects_malformed_and_mutated_audit_rows(audit_factory) -> None:
    value = _authority_input(AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED)
    legacy_id = str(uuid4())
    async with audit_factory() as session:
        await AuditService(session).add_authority_event(value)
        await AuditRepository(session).add_audit_event(
            AuditEvent(
                id=legacy_id,
                entity_type="task",
                entity_id=str(uuid4()),
                event_type="task_created",
                actor_id="legacy-actor",
                external_subject="opaque-subject",
                external_issuer="https://issuer.example.test",
                actor_roles=[],
                claim_snapshot={},
                auth_source="verified_token",
                is_dev_auth=False,
                event_payload={},
            )
        )
        await session.commit()

    async with audit_factory() as session:
        for event_id in (str(value.event_id), legacy_id):
            with pytest.raises(DBAPIError, match="append-only"):
                await session.execute(
                    text("update audit_events set reason = 'changed' where id = :id"),
                    {"id": event_id},
                )
            await session.rollback()
            with pytest.raises(DBAPIError, match="append-only"):
                await session.execute(
                    text("delete from audit_events where id = :id"),
                    {"id": event_id},
                )
            await session.rollback()
        with pytest.raises(DBAPIError, match="append-only"):
            await session.execute(text("truncate table audit_events cascade"))
        await session.rollback()
        rows = (
            await session.execute(
                text(
                    "select id, reason, event_domain from audit_events "
                    "where id in (:authority_id, :legacy_id) order by id"
                ),
                {"authority_id": str(value.event_id), "legacy_id": legacy_id},
            )
        ).all()
        assert {(row.id, row.reason, row.event_domain) for row in rows} == {
            (str(value.event_id), None, "authority"),
            (legacy_id, None, "legacy_lifecycle"),
        }

        with pytest.raises(IntegrityError):
            await session.execute(
                text(
                    "insert into audit_events "
                    "(id, entity_type, entity_id, event_type, actor_id, actor_roles, "
                    "claim_snapshot, auth_source, is_dev_auth, event_payload, event_domain) "
                    "values (:id, 'actor', :entity_id, 'SensitiveAuthorizationAllowed', "
                    "'legacy', '[]', '{}', 'local_authority', false, '{}', 'authority')"
                ),
                {"id": str(uuid4()), "entity_id": str(uuid4())},
            )
        await session.rollback()
