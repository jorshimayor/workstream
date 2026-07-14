from __future__ import annotations

from collections import UserDict
from collections.abc import Mapping
import json
from pathlib import Path
from types import MappingProxyType
from uuid import UUID, uuid4

from alembic import command
from alembic.config import Config
from pydantic import ValidationError
import pytest
from sqlalchemy import delete, text
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


def _assert_value_not_retained(value: object, forbidden: str, seen: set[int] | None = None) -> None:
    """Traverse public exception state and prove rejected input is absent."""
    seen = seen or set()
    if id(value) in seen:
        return
    seen.add(id(value))
    if isinstance(value, str):
        assert forbidden not in value
    elif isinstance(value, BaseException):
        for item in (value.args, vars(value), value.__cause__, value.__context__):
            _assert_value_not_retained(item, forbidden, seen)
    elif isinstance(value, Mapping):
        for key, item in value.items():
            _assert_value_not_retained((key, item), forbidden, seen)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            _assert_value_not_retained(item, forbidden, seen)


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
    async with engine.connect() as connection:
        existing = set(
            (
                await connection.execute(
                    text("select id from audit_events where event_domain = 'authority'")
                )
            ).scalars()
        )
    try:
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        async with engine.begin() as connection:
            created = (
                set(
                    (
                        await connection.execute(
                            text("select id from audit_events where event_domain = 'authority'")
                        )
                    ).scalars()
                )
                - existing
            )
            if created:
                await connection.execute(text("lock table audit_events in access exclusive mode"))
                await connection.execute(
                    text(
                        "alter table audit_events disable trigger audit_events_reject_update_delete"
                    )
                )
                await connection.execute(delete(AuditEvent).where(AuditEvent.id.in_(created)))
                await connection.execute(
                    text(
                        "alter table audit_events enable trigger audit_events_reject_update_delete"
                    )
                )
        await engine.dispose()


def _authority_input(event_type: AuthorityEventType, **overrides) -> AuthorityAuditEventInput:
    event_id = overrides.pop("event_id", uuid4())
    defaults = {
        AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED: {
            "entity_type": "authorization_decision",
            "reason": "authorization_evaluation",
            "after_facts": {"allowed": True},
        },
        AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED: {
            "entity_type": "authorization_decision",
            "reason": "authorization_evaluation",
            "after_facts": {"allowed": False},
        },
        AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED: {
            "entity_type": "authority_invalidation",
            "reason": "authority_state_changed",
            "before_facts": {"effective": True},
            "after_facts": {"effective": False},
        },
    }[event_type]
    values = {
        "event_id": event_id,
        "event_type": event_type,
        "entity_id": str(event_id),
        "actor_ref_kind": ActorReferenceKind.SYSTEM_PRINCIPAL,
        "actor_ref": "workstream:system:bootstrap",
        "request_id": uuid4(),
        "correlation_id": uuid4(),
        "permission_id": "actor.profile.read_any",
        **defaults,
    }
    values.update(overrides)
    return AuthorityAuditEventInput(**values)


def test_authority_input_rejects_unbounded_or_inconsistent_evidence() -> None:
    secret = "secret-bearer-value"
    payload = _authority_input(AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED).model_dump(
        mode="json"
    ) | {"raw_token": secret}
    constructors = (
        lambda value: AuthorityAuditEventInput(**value),
        AuthorityAuditEventInput.model_validate,
    )
    mappings = (payload, UserDict(payload), MappingProxyType(payload))
    for constructor in constructors:
        for mapping in mappings:
            with pytest.raises(TypeError, match="invalid authority audit input") as caught:
                constructor(mapping)
            _assert_value_not_retained(caught.value, secret)
    with pytest.raises(TypeError, match="invalid authority audit input") as caught:
        AuthorityAuditEventInput.model_validate_json(json.dumps(payload))
    _assert_value_not_retained(caught.value, secret)

    safe = _authority_input(AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED).model_dump(
        mode="json"
    )
    assert AuthorityAuditEventInput.model_validate_json(json.dumps(safe)).model_dump(mode="json") == safe
    for raw in ("{secret-bearer-value", '"secret-bearer-value"', '["secret-bearer-value"]'):
        for document in (raw, raw.encode(), bytearray(raw.encode())):
            with pytest.raises(TypeError, match="invalid authority audit input") as caught:
                AuthorityAuditEventInput.model_validate_json(document)
            _assert_value_not_retained(caught.value, secret)

    for patch, forbidden in (
        (
            {"actor_ref_kind": ActorReferenceKind.LEGACY_ACTOR, "actor_ref": "provider@example.com"},
            "provider@example.com",
        ),
        ({"after_facts": {"allowed": "secret-bearer-value"}}, secret),
        ({"after_facts": {"allowed": {"secret": secret}}}, secret),
        (
            {"after_facts": {"decision_code": "https://issuer.example/private"}},
            "https://issuer.example/private",
        ),
        ({"reason": "secret-bearer-value"}, secret),
        ({"entity_type": "secret-bearer-value"}, secret),
        ({"permission_id": [secret]}, secret),
    ):
        candidate = safe | patch
        with pytest.raises(TypeError, match="invalid authority audit input") as caught:
            AuthorityAuditEventInput.model_validate(candidate)
        _assert_value_not_retained(caught.value, forbidden)
    with pytest.raises(ValidationError, match="resource ID requires"):
        _authority_input(
            AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED,
            resource_id=str(uuid4()),
        )
    with pytest.raises(ValidationError, match="invalid denied authorization"):
        _authority_input(
            AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED,
            denial_code="actor_suspended",
            idempotency_reference=uuid4(),
        )
    with pytest.raises(ValidationError, match="invalidation evidence"):
        _authority_input(AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED)
    event_id = uuid4()
    with pytest.raises(ValidationError, match="own event"):
        _authority_input(
            AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED,
            event_id=event_id,
            permission_id=None,
            invalidation_cause_event_id=event_id,
            invalidation_target_kind="actor_profile",
            invalidation_target_ref=str(uuid4()),
        )


def test_authority_input_enforces_grant_scope_matrix() -> None:
    """Grant evidence cannot contradict role, project, or replacement scope."""
    source = _authority_input(AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED).model_dump()
    event_id = uuid4()
    project_id = str(uuid4())
    source.update(
        event_id=event_id,
        event_type=AuthorityEventType.ADMIN_ROLE_GRANT_ISSUED,
        entity_type="admin_role_grant",
        entity_id=str(uuid4()),
        permission_id=None,
        reason="authority_assignment",
        project_id=project_id,
        after_facts={
            "status": "active",
            "role": "project_manager",
            "scope_type": "project",
            "scope_id": project_id,
            "effective": True,
        },
    )
    assert AuthorityAuditEventInput.model_validate(source).project_id == project_id

    for patch in (
        {"after_facts": source["after_facts"] | {"role": "access_administrator"}},
        {"after_facts": source["after_facts"] | {"scope_id": str(uuid4())}},
        {"project_id": None},
    ):
        with pytest.raises(ValidationError, match="facts|scope"):
            AuthorityAuditEventInput.model_validate(source | patch)

    replacement = source | {
        "event_type": AuthorityEventType.PROJECT_ROLE_GRANT_REPLACED,
        "entity_type": "project_role_grant",
        "reason": "authority_replacement",
        "before_facts": {
            "status": "active",
            "role": "submitter",
            "scope_type": "project",
            "scope_id": project_id,
            "effective": True,
        },
        "after_facts": {
            "status": "active",
            "role": "reviewer",
            "scope_type": "project",
            "scope_id": str(uuid4()),
            "effective": True,
        },
    }
    with pytest.raises(ValidationError, match="scope"):
        AuthorityAuditEventInput.model_validate(replacement)


async def test_authority_writer_persists_typed_privacy_neutral_events(audit_factory) -> None:
    future_idempotency = uuid4()
    project_id = str(uuid4())
    allowed = _authority_input(
        AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED,
        project_id=project_id,
        resource_type="project",
        resource_id=project_id,
    )
    denied = _authority_input(
        AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED,
        denial_code="permission_not_granted",
    )
    invalidation = _authority_input(
        AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED,
        permission_id=None,
        invalidation_cause_event_id=allowed.event_id,
        invalidation_target_kind="actor_profile",
        invalidation_target_ref=str(uuid4()),
        idempotency_reference=future_idempotency,
    )

    async with audit_factory() as session:
        service = AuditService(session)
        stored = [
            await service.add_authority_event(value) for value in (allowed, denied, invalidation)
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


async def test_authority_invalidation_requires_an_existing_authority_cause(audit_factory) -> None:
    legacy_id = str(uuid4())
    invalidation = _authority_input(
        AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED,
        permission_id=None,
        invalidation_cause_event_id=uuid4(),
        invalidation_target_kind="actor_profile",
        invalidation_target_ref=str(uuid4()),
    )
    async with audit_factory() as session:
        with pytest.raises(ValueError, match="existing authority event"):
            await AuditService(session).add_authority_event(invalidation)
        await AuditRepository(session).add_audit_event(
            AuditEvent(
                id=legacy_id,
                entity_type="task",
                entity_id=str(uuid4()),
                event_type="task_created",
                actor_id="legacy",
                external_subject="opaque",
                external_issuer="https://issuer.test",
                actor_roles=[],
                claim_snapshot={},
                auth_source="verified_token",
                is_dev_auth=False,
                event_payload={},
            )
        )
        invalidation.invalidation_cause_event_id = UUID(legacy_id)
        with pytest.raises(ValueError, match="existing authority event"):
            await AuditService(session).add_authority_event(invalidation)
        assert await session.get(AuditEvent, str(invalidation.event_id)) is None


async def test_legacy_repository_rejects_unvalidated_authority_rows(audit_factory) -> None:
    raw = AuditEvent(
        id=str(uuid4()),
        entity_type="actor",
        entity_id=str(uuid4()),
        event_type="SensitiveAuthorizationAllowed",
        actor_id="provider@example.com",
        actor_roles=[],
        claim_snapshot={},
        auth_source="local_authority",
        is_dev_auth=False,
        event_payload={},
        event_domain="authority",
    )
    async with audit_factory() as session:
        with pytest.raises(ValueError, match="typed audit service"):
            await AuditRepository(session).add_audit_event(raw)
        assert raw not in session


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
            (str(value.event_id), "authorization_evaluation", "authority"),
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
        insert = text(
            "insert into audit_events "
            "(id, entity_type, entity_id, event_type, actor_id, actor_roles, claim_snapshot, "
            "auth_source, is_dev_auth, event_payload, event_domain, event_version, actor_ref_kind, "
            "request_id, correlation_id, permission_id, reason, after_facts) values "
            "(:id, :entity_type, :id, 'SensitiveAuthorizationAllowed', :actor_id, '[]', '{}', "
            "'local_authority', false, '{}', 'authority', 1, :actor_kind, :request_id, "
            ":correlation_id, 'actor.profile.read_any', :reason, cast(:facts as json))"
        )
        for patch in (
            {"actor_kind": "legacy_actor", "actor_id": "provider@example.com"},
            {"facts": '{"decision_code":"https://issuer.test"}'},
            {"facts": '{"allowed":"secret-bearer-value"}'},
            {"entity_type": "provider@example.com"},
            {"reason": "secret-bearer-value"},
        ):
            with pytest.raises(IntegrityError):
                values = {
                    "id": str(uuid4()),
                    "actor_id": "workstream:system:bootstrap",
                    "actor_kind": "system_principal",
                    "request_id": str(uuid4()),
                    "correlation_id": str(uuid4()),
                    "entity_type": "authorization_decision",
                    "reason": "authorization_evaluation",
                    "facts": '{"allowed":true}',
                }
                values.update(patch)
                await session.execute(
                    insert,
                    values,
                )
            await session.rollback()
        grant_insert = text(
            "insert into audit_events "
            "(id, entity_type, entity_id, event_type, actor_id, actor_roles, claim_snapshot, "
            "auth_source, is_dev_auth, event_payload, event_domain, event_version, actor_ref_kind, "
            "request_id, correlation_id, project_id, reason, after_facts) values "
            "(:id, 'admin_role_grant', :entity_id, 'AdminRoleGrantIssued', "
            "'workstream:system:bootstrap', '[]', '{}', 'local_authority', false, '{}', "
            "'authority', 1, 'system_principal', :request_id, :correlation_id, :project_id, "
            "'authority_assignment', cast(:facts as json))"
        )
        project_id = str(uuid4())

        def grant_values(facts: str, *, scope_project_id: str | None = project_id) -> dict:
            return {
                "id": str(uuid4()),
                "entity_id": str(uuid4()),
                "request_id": str(uuid4()),
                "correlation_id": str(uuid4()),
                "project_id": scope_project_id,
                "facts": facts,
            }

        valid_facts = json.dumps(
            {
                "status": "active",
                "role": "project_manager",
                "scope_type": "project",
                "scope_id": project_id,
                "effective": True,
            }
        )
        await session.execute(grant_insert, grant_values(valid_facts))
        await session.commit()
        for values in (
            grant_values(valid_facts.replace(project_id, str(uuid4()))),
            grant_values(valid_facts.replace("project_manager", "access_administrator")),
            grant_values(
                json.dumps(
                    {
                        "status": "active",
                        "role": "project_manager",
                        "scope_type": "system",
                        "effective": True,
                    }
                )
            ),
        ):
            with pytest.raises(IntegrityError):
                await session.execute(grant_insert, values)
            await session.rollback()
        invalidation_insert = text(
            "insert into audit_events (id, entity_type, entity_id, event_type, actor_id, "
            "actor_roles, claim_snapshot, auth_source, is_dev_auth, event_payload, event_domain, "
            "event_version, actor_ref_kind, request_id, correlation_id, invalidation_cause_event_id, "
            "invalidation_target_kind, invalidation_target_ref, reason, before_facts, after_facts) "
            "values (:id, 'authority_invalidation', :id, "
            "'AuthorityInvalidationRequested', 'workstream:system:bootstrap', '[]', '{}', "
            "'local_authority', false, '{}', 'authority', 1, 'system_principal', :request_id, "
            ":correlation_id, :cause_id, 'actor_profile', :target_ref, "
            "'authority_state_changed', '{\"effective\": true}', '{\"effective\": false}')"
        )
        for cause_id in (str(uuid4()), legacy_id):
            with pytest.raises(IntegrityError):
                await session.execute(
                    invalidation_insert,
                    {
                        "id": str(uuid4()),
                        "request_id": str(uuid4()),
                        "correlation_id": str(uuid4()),
                        "cause_id": cause_id,
                        "target_ref": str(uuid4()),
                    },
                )
            await session.rollback()
