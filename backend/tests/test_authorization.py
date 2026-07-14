from __future__ import annotations

import asyncio
from collections import UserDict
from collections.abc import Mapping
from pathlib import Path
from uuid import UUID, uuid4

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.modules.audit.schemas import ActorReferenceKind, AuthorityAuditEventInput, AuthorityEventType
from app.modules.authorization.schemas import (
    ActorIdentityLinkReactivateRequest,
    ActorIdentityLinkRevokeRequest,
    ActorProfileDeactivateRequest,
    ActorProfileReactivateRequest,
    ActorProfileSuspendRequest,
    AdminRole,
    AdminRoleGrantIssueRequest,
    AdminRoleGrantRevokeRequest,
    AdminScope,
    AuthorityClaimHandle,
    AuthorityInvalidationContext,
    AuthorityMismatchContext,
    AuthorityOperation,
    AuthorityResourceType,
    AuthorityResponseReference,
    ClaimedReservation,
    InvalidAuthorityClaimError,
    MismatchedReservation,
    PendingAuthorityReservationError,
    ProjectRole,
    ProjectRoleGrantIssueRequest,
    ProjectRoleGrantRevokeRequest,
    ReplayedReservation,
    ServiceActorCreateRequest,
    derive_reason_digest,
    derive_service_identity_digest,
    derive_service_profile_digest,
    parse_authority_request,
)
from app.modules.authorization.service import AuthorityMutationService

DIGEST = "sha256:" + "a" * 64


@pytest.fixture
def authorization_database_env(postgres_database_url: str, migration_lock) -> str:
    """Ensure authorization tests run at the current isolated schema head."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    with migration_lock():
        command.upgrade(config, "head")
    return postgres_database_url


@pytest.fixture
async def authorization_factory(authorization_database_env: str):
    """Provide sessions and remove only rows created by this test module."""
    engine = create_async_engine(authorization_database_env)
    try:
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        async with engine.begin() as connection:
            await connection.execute(text("lock table authority_idempotency_records in access exclusive mode"))
            await connection.execute(text("lock table audit_events in access exclusive mode"))
            await connection.execute(text("alter table audit_events disable trigger audit_events_reject_update_delete"))
            await connection.execute(text("alter table authority_idempotency_records disable trigger authority_idempotency_guard"))
            await connection.execute(text("delete from audit_events where idempotency_reference is not null or denial_code='idempotency_mismatch'"))
            await connection.execute(text("delete from authority_idempotency_records"))
            await connection.execute(text("alter table authority_idempotency_records enable trigger authority_idempotency_guard"))
            await connection.execute(text("alter table audit_events enable trigger audit_events_reject_update_delete"))
        await engine.dispose()


def _request(target: UUID | None = None) -> ActorProfileSuspendRequest:
    return ActorProfileSuspendRequest(
        operation=AuthorityOperation.ACTOR_PROFILE_SUSPEND,
        actor_profile_id=target or uuid4(),
        reason_digest=DIGEST,
    )


def _success(
    claim: AuthorityClaimHandle,
    request: ActorProfileSuspendRequest,
    *,
    request_id: UUID | None = None,
    correlation_id: UUID | None = None,
) -> AuthorityAuditEventInput:
    event_id = uuid4()
    return AuthorityAuditEventInput(
        event_id=event_id,
        event_type=AuthorityEventType.ACTOR_PROFILE_SUSPENDED,
        entity_type="actor_profile",
        entity_id=str(request.actor_profile_id),
        actor_ref_kind=claim.actor_ref_kind,
        actor_ref=claim.actor_ref,
        request_id=request_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        permission_id="actor.profile.suspend",
        resource_type="actor_profile",
        resource_id=str(request.actor_profile_id),
        target_ref_kind="actor_profile",
        target_ref_id=str(request.actor_profile_id),
        reason="security_response",
        idempotency_reference=claim.record_id,
        before_facts={"status": "active"},
        after_facts={"status": "suspended"},
    )


async def _claim(service: AuthorityMutationService, actor: UUID, key: UUID, request):
    result = await service.reserve(
        idempotency_key=key,
        actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
        actor_ref=str(actor),
        request=request.model_dump(),
    )
    assert isinstance(result, ClaimedReservation)
    return result.claim


async def _complete(service, claim, request):
    success = _success(claim, request)
    response = AuthorityResponseReference(
        resource_type=AuthorityResourceType.ACTOR_PROFILE,
        resource_id=request.actor_profile_id,
        version=1,
        http_status=200,
    )
    result = await service.complete(
        claim=claim,
        request=request.model_dump(),
        response=response,
        success=success,
        invalidation=AuthorityInvalidationContext(
            event_id=uuid4(),
            request_id=success.request_id,
            correlation_id=success.correlation_id,
        ),
    )
    return result


@pytest.mark.asyncio
async def test_claim_completion_and_exact_replay_have_one_evidence_pair(
    authorization_factory,
) -> None:
    actor, key, request = uuid4(), uuid4(), _request()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, key, request)
        completed = await _complete(service, claim, request)
        await session.commit()

    async with authorization_factory() as session:
        replay = await AuthorityMutationService(session).reserve(
            idempotency_key=key,
            actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
            actor_ref=str(actor),
            request=request.model_dump(),
        )
        assert isinstance(replay, ReplayedReservation)
        assert replay.response == completed.response
        await session.commit()
        counts = (
            await session.execute(
                text(
                    "select event_type, count(*) from audit_events "
                    "where idempotency_reference=:record group by event_type order by event_type"
                ),
                {"record": claim.record_id},
            )
        ).all()
    assert counts == [("ActorProfileSuspended", 1), ("AuthorityInvalidationRequested", 1)]


@pytest.mark.asyncio
async def test_pending_commit_fails_and_rollback_allows_retry(authorization_factory) -> None:
    actor, key, request = uuid4(), uuid4(), _request()
    async with authorization_factory() as session:
        await _claim(AuthorityMutationService(session), actor, key, request)
        with pytest.raises(DBAPIError, match="pending authority idempotency"):
            await session.commit()
        await session.rollback()
    async with authorization_factory() as session:
        result = await _claim(AuthorityMutationService(session), actor, key, request)
        assert result.request_digest.startswith("sha256:")
        await session.rollback()


@pytest.mark.asyncio
async def test_same_session_pending_and_forged_claim_fail_closed(authorization_factory) -> None:
    actor, key, request = uuid4(), uuid4(), _request()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, key, request)
        with pytest.raises(PendingAuthorityReservationError):
            await service.reserve(
                idempotency_key=key,
                actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
                actor_ref=str(actor),
                request=request.model_dump(),
            )
        forged = claim.model_copy(update={"request_digest": "sha256:" + "b" * 64})
        with pytest.raises(InvalidAuthorityClaimError):
            await service._repository.complete(
                forged,
                AuthorityResponseReference(
                    resource_type=AuthorityResourceType.ACTOR_PROFILE,
                    resource_id=request.actor_profile_id,
                    http_status=200,
                ),
            )
        await session.rollback()


@pytest.mark.asyncio
async def test_mismatch_is_private_and_denial_uses_clean_transaction(authorization_factory) -> None:
    actor, key, request = uuid4(), uuid4(), _request()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        await _complete(service, await _claim(service, actor, key, request), request)
        await session.commit()
    different = _request()
    async with authorization_factory() as session:
        result = await AuthorityMutationService(session).reserve(
            idempotency_key=key,
            actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
            actor_ref=str(actor),
            request=different.model_dump(),
        )
        assert isinstance(result, MismatchedReservation)
        assert result.model_dump() == {"outcome": "mismatch"}
        await session.rollback()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        denial_id = await service.record_mismatch_denial(
            actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
            actor_ref=str(actor),
            request=different.model_dump(),
            context=AuthorityMismatchContext(
                event_id=uuid4(), request_id=uuid4(), correlation_id=uuid4()
            ),
        )
        await session.commit()
        denial = await session.scalar(
            text("select denial_code from audit_events where id=:id"), {"id": str(denial_id)}
        )
    assert denial == "idempotency_mismatch"


def test_request_admission_is_frozen_bounded_and_nonretaining() -> None:
    secret = "SECRET_AUTHORITY_INPUT_9f4b"
    source = UserDict(_request().model_dump())
    admitted = parse_authority_request(source)
    source["reason_digest"] = "sha256:" + "b" * 64
    assert admitted.reason_digest == DIGEST

    rejected = [
        {**_request().model_dump(), "reason_digest": secret},
        {**_request().model_dump(), "actor_profile_id": str(uuid4()).upper()},
        {**_request().model_dump(), "extra": secret},
    ]
    for value in rejected:
        with pytest.raises(TypeError, match="invalid authority mutation request") as caught:
            parse_authority_request(value)
        assert secret not in str(caught.value)
        assert secret not in repr(caught.value.args)
        assert caught.value.__cause__ is None
        assert caught.value.__context__ is None


class _ChangingMapping(Mapping):
    def __init__(self, first: dict, second: dict) -> None:
        self.first, self.second, self.calls = first, second, 0

    def __iter__(self):
        return iter(self.first)

    def __len__(self):
        return len(self.first)

    def __getitem__(self, key):
        self.calls += 1
        return (self.first if self.calls == 1 else self.second)[key]


def test_state_changing_mapping_cannot_change_validated_snapshot() -> None:
    first = _request().model_dump()
    hostile = _ChangingMapping(first, {**first, "reason_digest": "not-a-digest"})
    with pytest.raises(TypeError, match="invalid authority mutation request"):
        parse_authority_request(hostile)


def test_every_operation_has_one_strict_canonical_request_variant() -> None:
    project, actor, resource = uuid4(), uuid4(), uuid4()
    requests = [
        ServiceActorCreateRequest(
            operation=AuthorityOperation.SERVICE_ACTOR_CREATE,
            identity_reference_digest=derive_service_identity_digest(
                "https://identity.flowresearch.tech", "opaque-service-subject"
            ),
            profile_payload_digest=derive_service_profile_digest("Adapter", "Approved"),
        ),
        AdminRoleGrantIssueRequest(
            operation=AuthorityOperation.ADMIN_ROLE_GRANT_ISSUE,
            target_actor_id=actor,
            role=AdminRole.PROJECT_MANAGER,
            scope_type=AdminScope.PROJECT,
            scope_project_id=project,
            reason_digest=derive_reason_digest("Assigned"),
        ),
        AdminRoleGrantRevokeRequest(
            operation=AuthorityOperation.ADMIN_ROLE_GRANT_REVOKE,
            grant_id=resource,
            reason_digest=DIGEST,
        ),
        ProjectRoleGrantIssueRequest(
            operation=AuthorityOperation.PROJECT_ROLE_GRANT_ISSUE,
            project_id=project,
            target_actor_id=actor,
            role=ProjectRole.BOTH,
            replaced_grant_id=resource,
            reason_digest=DIGEST,
        ),
        ProjectRoleGrantRevokeRequest(
            operation=AuthorityOperation.PROJECT_ROLE_GRANT_REVOKE,
            project_id=project,
            grant_id=resource,
            reason_digest=DIGEST,
        ),
        ActorProfileSuspendRequest(
            operation=AuthorityOperation.ACTOR_PROFILE_SUSPEND,
            actor_profile_id=resource,
            reason_digest=DIGEST,
        ),
        ActorProfileReactivateRequest(
            operation=AuthorityOperation.ACTOR_PROFILE_REACTIVATE,
            actor_profile_id=resource,
            reason_digest=DIGEST,
        ),
        ActorProfileDeactivateRequest(
            operation=AuthorityOperation.ACTOR_PROFILE_DEACTIVATE,
            actor_profile_id=resource,
            reason_digest=DIGEST,
        ),
        ActorIdentityLinkRevokeRequest(
            operation=AuthorityOperation.ACTOR_IDENTITY_LINK_REVOKE,
            identity_link_id=resource,
            reason_digest=DIGEST,
        ),
        ActorIdentityLinkReactivateRequest(
            operation=AuthorityOperation.ACTOR_IDENTITY_LINK_REACTIVATE,
            identity_link_id=resource,
            reason_digest=DIGEST,
        ),
    ]
    assert {parse_authority_request(item.model_dump()).operation for item in requests} == set(
        AuthorityOperation
    )


@pytest.mark.asyncio
async def test_failure_after_evidence_flush_rolls_back_claim_and_events(
    authorization_factory, monkeypatch
) -> None:
    actor, key, request = uuid4(), uuid4(), _request()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, key, request)

        async def fail_completion(*_args, **_kwargs):
            raise RuntimeError("injected completion failure")

        monkeypatch.setattr(service._repository, "complete", fail_completion)
        with pytest.raises(RuntimeError, match="injected completion failure"):
            await _complete(service, claim, request)
        await session.rollback()
    async with authorization_factory() as session:
        assert await session.scalar(
            text("select count(*) from authority_idempotency_records where id=:id"),
            {"id": claim.record_id},
        ) == 0
        assert await session.scalar(
            text("select count(*) from audit_events where idempotency_reference=:id"),
            {"id": claim.record_id},
        ) == 0


async def _wait_for_database_lock(database_url: str, application_name: str) -> None:
    """Observe the loser waiting on PostgreSQL rather than using a timing sleep."""
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            for _ in range(5000):
                waiting = await connection.scalar(
                    text(
                        "select exists(select 1 from pg_stat_activity where "
                        "application_name=:name and wait_event_type='Lock')"
                    ),
                    {"name": application_name},
                )
                if waiting:
                    return
                await asyncio.sleep(0)
    finally:
        await engine.dispose()
    raise AssertionError("concurrent reservation never reached the database lock")


@pytest.mark.asyncio
async def test_concurrent_exact_and_mismatched_retries_serialize_at_unique_namespace(
    authorization_database_env: str,
    authorization_factory,
) -> None:
    del authorization_factory  # fixture owns immutable-row cleanup
    actor, key, request = uuid4(), uuid4(), _request()
    winner_engine = create_async_engine(
        authorization_database_env,
        connect_args={"server_settings": {"application_name": "auth05b-winner"}},
    )
    loser_engine = create_async_engine(
        authorization_database_env,
        connect_args={"server_settings": {"application_name": "auth05b-loser"}},
    )
    winner_factory = async_sessionmaker(winner_engine, expire_on_commit=False)
    loser_factory = async_sessionmaker(loser_engine, expire_on_commit=False)

    async def lose(candidate):
        async with loser_factory() as session:
            return await AuthorityMutationService(session).reserve(
                idempotency_key=key,
                actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
                actor_ref=str(actor),
                request=candidate.model_dump(),
            )

    try:
        async with winner_factory() as winner:
            service = AuthorityMutationService(winner)
            claim = await _claim(service, actor, key, request)
            loser = asyncio.create_task(lose(request))
            await asyncio.wait_for(
                _wait_for_database_lock(authorization_database_env, "auth05b-loser"),
                timeout=5,
            )
            await _complete(service, claim, request)
            await winner.commit()
        assert isinstance(await asyncio.wait_for(loser, timeout=5), ReplayedReservation)

        key = uuid4()
        async with winner_factory() as winner:
            service = AuthorityMutationService(winner)
            claim = await _claim(service, actor, key, request)
            loser = asyncio.create_task(lose(_request()))
            await asyncio.wait_for(
                _wait_for_database_lock(authorization_database_env, "auth05b-loser"),
                timeout=5,
            )
            await _complete(service, claim, request)
            await winner.commit()
        assert isinstance(await asyncio.wait_for(loser, timeout=5), MismatchedReservation)
    finally:
        await winner_engine.dispose()
        await loser_engine.dispose()


@pytest.mark.asyncio
async def test_same_key_is_isolated_by_actor_reference_kind(authorization_factory) -> None:
    key, request = uuid4(), _request()
    async with authorization_factory() as first, authorization_factory() as second:
        one = await AuthorityMutationService(first).reserve(
            idempotency_key=key,
            actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
            actor_ref=str(uuid4()),
            request=request.model_dump(),
        )
        two = await AuthorityMutationService(second).reserve(
            idempotency_key=key,
            actor_ref_kind=ActorReferenceKind.LEGACY_ACTOR,
            actor_ref=str(uuid4()),
            request=request.model_dump(),
        )
        assert isinstance(one, ClaimedReservation)
        assert isinstance(two, ClaimedReservation)
        await first.rollback()
        await second.rollback()
