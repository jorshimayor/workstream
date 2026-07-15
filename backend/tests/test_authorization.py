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
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.modules.audit.schemas import ActorReferenceKind, AuthorityAuditEventInput, AuthorityEventType
from app.modules.audit.service import AuditService
from app.modules.authorization.catalogue import (
    ACTION_BY_ID,
    ACTION_DEFINITIONS,
    ACTION_IDS,
    HISTORICAL_PERMISSION_IDS,
    NEW_PERMISSION_IDS,
    PERMISSION_IDS,
    ActionAvailability,
    ActionDefinition,
    ActionId,
    ActionOwner,
    PermissionId,
    _index_actions,
    resolve_executable_action,
)
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


def test_closed_permission_and_action_catalogue_is_exact_and_non_executable() -> None:
    expected = {
        "actor.profile.read_self": ("actor.profile.read_self", "WS-AUTH-001-07B"),
        "actor.profile.update_self": ("actor.profile.update_self", "WS-AUTH-001-07B"),
        "operations.task.start_override": ("operations.task.start_override", "WS-AUTH-001-13"),
        "operations.submission_gate.repair": ("operations.submission_gate.repair", "WS-AUTH-001-14"),
        "operations.checker.retry": ("operations.checker.retry", "WS-AUTH-001-14"),
        "artifact.binding.read": ("artifact.binding.read", "WS-ART-001-02D"),
        "artifact.replica.read": ("artifact.replica.read", "WS-ART-001-02D"),
        "artifact.receipt.read": ("artifact.receipt.read", "WS-ART-001-02D"),
        "artifact.verification_job.read": ("artifact.verification_job.read", "WS-ART-001-02D"),
        "artifact.verification_job.retry": ("artifact.verification_job.retry", "WS-ART-001-02D"),
        "artifact.recovery_attempt.read": ("artifact.recovery_attempt.read", "WS-ART-001-02D"),
        "artifact.audit.read": ("artifact.audit.read", "WS-ART-001-02D"),
        "operations.artifact_storage_admission.read": ("operations.status.read", "WS-ART-001-02D"),
        "artifact.guide_source.ingest": ("artifact.guide_source.ingest", "WS-ART-001-03"),
        "artifact.guide_source.read": ("artifact.guide_source.read", "WS-ART-001-03"),
        "artifact.upload_session.create": ("artifact.upload_session.create", "WS-ART-001-04A"),
        "artifact.upload_session.read": ("artifact.upload_session.read", "WS-ART-001-04A"),
        "artifact.upload_item.write": ("artifact.upload_item.write", "WS-ART-001-04A"),
        "artifact.upload_session.seal": ("artifact.upload_session.seal", "WS-ART-001-04A"),
        "artifact.upload_session.cancel": ("artifact.upload_session.cancel", "WS-ART-001-04A"),
        "artifact.upload_session.expire": ("artifact.upload_session.expire", "WS-ART-001-04A"),
        "artifact.guide_source.binding.create": ("artifact.binding.create", "WS-ART-001-03"),
        "artifact.submission.binding.create": ("artifact.binding.create", "WS-ART-001-05"),
        "artifact.checker_output.binding.create": ("artifact.binding.create", "WS-ART-001-06B"),
        "artifact.verification.execute": ("artifact.verification.execute", "WS-ART-001-02D"),
        "artifact.pending_work.scan": ("artifact.pending_work.scan", "WS-ART-001-02D"),
        "artifact.put_attempt.resolve": ("artifact.put_attempt.resolve", "WS-ART-001-02D"),
        "artifact.pre_submit.checker_input.materialize": (
            "artifact.checker_input.materialize",
            "WS-ART-001-04B",
        ),
        "artifact.post_submit.checker_input.materialize": (
            "artifact.checker_input.materialize",
            "WS-ART-001-06A",
        ),
        "artifact.checker_output.write": ("artifact.checker_output.write", "WS-ART-001-06B"),
    }
    assert len(PERMISSION_IDS) == 73
    assert len(HISTORICAL_PERMISSION_IDS) == 49
    assert len(NEW_PERMISSION_IDS) == 24
    assert len(ACTION_IDS) == len(ACTION_DEFINITIONS) == len(ACTION_BY_ID) == 30
    assert set(ACTION_BY_ID) == ACTION_IDS
    assert {definition.owner for definition in ACTION_DEFINITIONS} == set(ActionOwner)
    assert all(
        definition.availability is ActionAvailability.PLANNED
        for definition in ACTION_DEFINITIONS
    )
    assert {
        definition.action_id.value: (
            definition.permission_id.value,
            definition.owner.value,
        )
        for definition in ACTION_DEFINITIONS
    } == expected
    with pytest.raises(ValueError, match="not active"):
        resolve_executable_action(ActionId.ACTOR_PROFILE_READ_SELF)
    with pytest.raises(TypeError):
        ACTION_BY_ID[ActionId.ACTOR_PROFILE_READ_SELF] = ACTION_DEFINITIONS[0]


@pytest.mark.parametrize(
    "definitions, message",
    [
        (ACTION_DEFINITIONS[:-1], "incomplete"),
        (ACTION_DEFINITIONS[:-1] + (ACTION_DEFINITIONS[0],), "incomplete"),
        (
            ACTION_DEFINITIONS[:-1]
            + (
                ActionDefinition(
                    ActionId.ARTIFACT_CHECKER_OUTPUT_WRITE,
                    PermissionId.ARTIFACT_CHECKER_OUTPUT_WRITE,
                    ActionOwner.ART_02D,
                    ActionAvailability.PLANNED,
                ),
            ),
            "metadata mismatch",
        ),
        (
            ACTION_DEFINITIONS[:-1]
            + (
                ActionDefinition(
                    ActionId.ARTIFACT_CHECKER_OUTPUT_WRITE,
                    PermissionId.ARTIFACT_CHECKER_OUTPUT_WRITE,
                    ActionOwner.ART_06B,
                    ActionAvailability.ACTIVE,
                ),
            ),
            "must remain planned",
        ),
        (
            ACTION_DEFINITIONS[:-1]
            + (
                ActionDefinition(
                    ActionId.ARTIFACT_CHECKER_OUTPUT_WRITE,
                    "unknown.permission",  # type: ignore[arg-type]
                    ActionOwner.ART_06B,
                    ActionAvailability.PLANNED,
                ),
            ),
            "invalid row",
        ),
    ],
)
def test_action_catalogue_construction_fails_closed(
    definitions: tuple[ActionDefinition, ...],
    message: str,
) -> None:
    with pytest.raises(RuntimeError, match=message):
        _index_actions(definitions)


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


def _operation_success(
    claim: AuthorityClaimHandle,
    request,
    response: AuthorityResponseReference,
) -> AuthorityAuditEventInput:
    """Build the exact concrete success evidence for one canonical operation case."""
    event, permission, reason = {
        AuthorityOperation.SERVICE_ACTOR_CREATE: (
            AuthorityEventType.SERVICE_ACTOR_PROVISIONED,
            "actor.service.provision",
            "manual_service_provisioning",
        ),
        AuthorityOperation.ADMIN_ROLE_GRANT_ISSUE: (
            AuthorityEventType.ADMIN_ROLE_GRANT_ISSUED,
            "admin_role.grant",
            "authority_assignment",
        ),
        AuthorityOperation.ADMIN_ROLE_GRANT_REVOKE: (
            AuthorityEventType.ADMIN_ROLE_GRANT_REVOKED,
            "admin_role.revoke",
            "authority_revocation",
        ),
        AuthorityOperation.PROJECT_ROLE_GRANT_ISSUE: (
            AuthorityEventType.PROJECT_ROLE_GRANT_REPLACED
            if getattr(request, "replaced_grant_id", None)
            else AuthorityEventType.PROJECT_ROLE_GRANT_ISSUED,
            "project.role_grant.manage",
            "authority_replacement"
            if getattr(request, "replaced_grant_id", None)
            else "authority_assignment",
        ),
        AuthorityOperation.PROJECT_ROLE_GRANT_REVOKE: (
            AuthorityEventType.PROJECT_ROLE_GRANT_REVOKED,
            "project.role_grant.manage",
            "authority_revocation",
        ),
        AuthorityOperation.ACTOR_PROFILE_SUSPEND: (
            AuthorityEventType.ACTOR_PROFILE_SUSPENDED,
            "actor.profile.suspend",
            "security_response",
        ),
        AuthorityOperation.ACTOR_PROFILE_REACTIVATE: (
            AuthorityEventType.ACTOR_PROFILE_REACTIVATED,
            "actor.profile.reactivate",
            "administrative_correction",
        ),
        AuthorityOperation.ACTOR_PROFILE_DEACTIVATE: (
            AuthorityEventType.ACTOR_PROFILE_DEACTIVATED,
            "actor.profile.deactivate",
            "security_response",
        ),
        AuthorityOperation.ACTOR_IDENTITY_LINK_REVOKE: (
            AuthorityEventType.ACTOR_IDENTITY_LINK_REVOKED,
            "actor.identity_link.revoke",
            "identity_lifecycle_change",
        ),
        AuthorityOperation.ACTOR_IDENTITY_LINK_REACTIVATE: (
            AuthorityEventType.ACTOR_IDENTITY_LINK_REACTIVATED,
            "actor.identity_link.reactivate",
            "identity_lifecycle_change",
        ),
    }[request.operation]
    before_facts = None
    after_facts = None
    project_id = None
    target_actor = None
    matched_grant = None
    if isinstance(request, ServiceActorCreateRequest):
        after_facts = {
            "status": "active",
            "subject_kind": "service",
            "provisioning_method": "manual_service_provisioning",
        }
    elif isinstance(request, AdminRoleGrantIssueRequest):
        target_actor = request.target_actor_id
        project_id = request.scope_project_id
        after_facts = {
            "status": "active",
            "role": request.role.value,
            "scope_type": request.scope_type.value,
            "effective": True,
        }
        if project_id:
            after_facts["scope_id"] = str(project_id)
    elif isinstance(request, AdminRoleGrantRevokeRequest):
        before_facts = {
            "status": "active",
            "role": "access_administrator",
            "scope_type": "system",
            "effective": True,
        }
        after_facts = before_facts | {"status": "revoked", "effective": False}
    elif isinstance(request, ProjectRoleGrantIssueRequest):
        project_id = request.project_id
        target_actor = request.target_actor_id
        matched_grant = request.replaced_grant_id
        after_facts = {
            "status": "active",
            "role": request.role.value,
            "scope_type": "project",
            "scope_id": str(project_id),
            "effective": True,
        }
        if matched_grant:
            before_facts = after_facts | {"role": "reviewer"}
    elif isinstance(request, ProjectRoleGrantRevokeRequest):
        project_id = request.project_id
        before_facts = {
            "status": "active",
            "role": "submitter",
            "scope_type": "project",
            "scope_id": str(project_id),
            "effective": True,
        }
        after_facts = before_facts | {"status": "revoked", "effective": False}
    elif isinstance(request, ActorProfileSuspendRequest):
        before_facts, after_facts = {"status": "active"}, {"status": "suspended"}
    elif isinstance(request, ActorProfileReactivateRequest):
        before_facts, after_facts = {"status": "suspended"}, {"status": "active"}
    elif isinstance(request, ActorProfileDeactivateRequest):
        before_facts, after_facts = {"status": "active"}, {"status": "deactivated"}
    elif isinstance(request, ActorIdentityLinkRevokeRequest):
        before_facts, after_facts = {"status": "active"}, {"status": "revoked"}
    elif isinstance(request, ActorIdentityLinkReactivateRequest):
        before_facts, after_facts = {"status": "revoked"}, {"status": "active"}

    event_id = uuid4()
    return AuthorityAuditEventInput(
        event_id=event_id,
        event_type=event,
        entity_type=response.resource_type.value,
        entity_id=str(response.resource_id),
        actor_ref_kind=claim.actor_ref_kind,
        actor_ref=claim.actor_ref,
        request_id=uuid4(),
        correlation_id=uuid4(),
        target_actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE if target_actor else None,
        target_actor_ref=str(target_actor) if target_actor else None,
        matched_grant_id=str(matched_grant) if matched_grant else None,
        permission_id=permission,
        project_id=str(project_id) if project_id else None,
        resource_type=response.resource_type.value,
        resource_id=str(response.resource_id),
        target_ref_kind=response.resource_type.value,
        target_ref_id=str(response.resource_id),
        reason=reason,
        idempotency_reference=claim.record_id,
        before_facts=before_facts,
        after_facts=after_facts,
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
async def test_committed_record_rejects_additional_success_and_invalidation(
    authorization_factory,
) -> None:
    actor, key, request = uuid4(), uuid4(), _request()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, key, request)
        completed = await _complete(service, claim, request)
        await session.commit()

    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        extra_success = _success(claim, request)
        with pytest.raises(IntegrityError, match="committed authority idempotency is closed"):
            await service.complete(
                claim=claim,
                request=request.model_dump(),
                response=completed.response,
                success=extra_success,
                invalidation=AuthorityInvalidationContext(
                    event_id=uuid4(),
                    request_id=extra_success.request_id,
                    correlation_id=extra_success.correlation_id,
                ),
            )
        await session.rollback()

    async with authorization_factory() as session:
        cause_id = await session.scalar(
            text(
                "select id from audit_events where idempotency_reference=:id "
                "and event_type='ActorProfileSuspended'"
            ),
            {"id": claim.record_id},
        )
        context_id, request_id, correlation_id = uuid4(), uuid4(), uuid4()
        invalidation = AuthorityAuditEventInput(
            event_id=context_id,
            event_type=AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED,
            entity_type="authority_invalidation",
            entity_id=str(context_id),
            actor_ref_kind=claim.actor_ref_kind,
            actor_ref=claim.actor_ref,
            request_id=request_id,
            correlation_id=correlation_id,
            permission_id="actor.profile.suspend",
            resource_type="actor_profile",
            resource_id=str(request.actor_profile_id),
            reason="authority_state_changed",
            idempotency_reference=claim.record_id,
            invalidation_cause_event_id=UUID(cause_id),
            invalidation_target_kind="actor_profile",
            invalidation_target_ref=str(request.actor_profile_id),
            before_facts={"effective": True},
            after_facts={"effective": False},
        )
        with pytest.raises(IntegrityError, match="committed authority idempotency is closed"):
            await AuditService(session).add_authority_event(invalidation)
        await session.rollback()

    async with authorization_factory() as session:
        assert await session.scalar(
            text("select count(*) from audit_events where idempotency_reference=:id"),
            {"id": claim.record_id},
        ) == 2


@pytest.mark.asyncio
async def test_completion_rejects_resource_and_project_not_bound_to_request(
    authorization_factory,
) -> None:
    actor, key, request = uuid4(), uuid4(), _request()
    wrong_request = _request()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, key, request)
        wrong_success = _success(claim, wrong_request)
        with pytest.raises(TypeError, match="invalid authority completion input"):
            await service.complete(
                claim=claim,
                request=request.model_dump(),
                response=AuthorityResponseReference(
                    resource_type=AuthorityResourceType.ACTOR_PROFILE,
                    resource_id=wrong_request.actor_profile_id,
                    http_status=200,
                ),
                success=wrong_success,
                invalidation=AuthorityInvalidationContext(
                    event_id=uuid4(),
                    request_id=wrong_success.request_id,
                    correlation_id=wrong_success.correlation_id,
                ),
            )
        await session.rollback()

    project_request = ProjectRoleGrantIssueRequest(
        operation=AuthorityOperation.PROJECT_ROLE_GRANT_ISSUE,
        project_id=uuid4(),
        target_actor_id=uuid4(),
        role=ProjectRole.SUBMITTER,
        reason_digest=DIGEST,
    )
    wrong_project = project_request.model_copy(update={"project_id": uuid4()})
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, uuid4(), project_request)
        response = AuthorityResponseReference(
            resource_type=AuthorityResourceType.PROJECT_ROLE_GRANT,
            resource_id=uuid4(),
            http_status=201,
        )
        success = _operation_success(claim, wrong_project, response)
        with pytest.raises(TypeError, match="invalid authority completion input"):
            await service.complete(
                claim=claim,
                request=project_request.model_dump(),
                response=response,
                success=success,
                invalidation=AuthorityInvalidationContext(
                    event_id=uuid4(),
                    request_id=success.request_id,
                    correlation_id=success.correlation_id,
                ),
            )
        await session.rollback()


@pytest.mark.asyncio
async def test_database_rejects_cross_actor_entity_and_cause_context_bypasses(
    authorization_factory,
) -> None:
    actor, request = uuid4(), _request()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, uuid4(), request)
        cross_actor = _success(claim, request).model_copy(update={"actor_ref": str(uuid4())})
        with pytest.raises(IntegrityError, match="idempotency reference"):
            await AuditService(session).add_authority_event(cross_actor)
        await session.rollback()

    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, uuid4(), request)
        wrong_entity = _success(claim, request).model_copy(
            update={"entity_type": "admin_role_grant"}
        )
        with pytest.raises(IntegrityError, match="success event does not match operation"):
            await AuditService(session).add_authority_event(wrong_entity)
        await session.rollback()

    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, uuid4(), request)
        success = _success(claim, request)
        await AuditService(session).add_authority_event(success)
        event_id = uuid4()
        wrong_context = AuthorityAuditEventInput(
            event_id=event_id,
            event_type=AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED,
            entity_type="authority_invalidation",
            entity_id=str(event_id),
            actor_ref_kind=claim.actor_ref_kind,
            actor_ref=claim.actor_ref,
            request_id=uuid4(),
            correlation_id=success.correlation_id,
            permission_id="actor.profile.suspend",
            resource_type="actor_profile",
            resource_id=str(request.actor_profile_id),
            reason="authority_state_changed",
            idempotency_reference=claim.record_id,
            invalidation_cause_event_id=success.event_id,
            invalidation_target_kind="actor_profile",
            invalidation_target_ref=str(request.actor_profile_id),
            before_facts={"effective": True},
            after_facts={"effective": False},
        )
        with pytest.raises(IntegrityError, match="invalid linked authority cause"):
            await AuditService(session).add_authority_event(wrong_context)
        await session.rollback()

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
        claim = await _claim(service, actor, key, request)
        await _complete(service, claim, request)
        await session.commit()
    different = _request()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        result = await service.reserve(
            idempotency_key=key,
            actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
            actor_ref=str(actor),
            request=different.model_dump(),
        )
        assert isinstance(result, MismatchedReservation)
        assert result.model_dump() == {"outcome": "mismatch"}
        await session.rollback()
        denial_id = await service.record_mismatch_denial(
            actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
            actor_ref=str(actor),
            request=different.model_dump(),
            context=AuthorityMismatchContext(
                event_id=uuid4(), request_id=uuid4(), correlation_id=uuid4()
            ),
        )
        await session.commit()
        denial = (
            await session.execute(
                text(
                    "select denial_code, idempotency_reference, resource_type, resource_id, "
                    "count(*) over () from audit_events where id=:id"
                ),
                {"id": str(denial_id)},
            )
        ).one()
        linked = await session.scalar(
            text(
                "select count(*) from audit_events where idempotency_reference=:id "
                "and event_type in ('ActorProfileSuspended','AuthorityInvalidationRequested')"
            ),
            {"id": claim.record_id},
        )
    assert denial == ("idempotency_mismatch", None, "actor_profile", str(different.actor_profile_id), 1)
    assert linked == 2


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

    for construct in (
        lambda: ActorProfileSuspendRequest(
            operation=AuthorityOperation.ACTOR_PROFILE_SUSPEND,
            actor_profile_id=uuid4(),
            reason_digest=secret,
        ),
        lambda: ActorProfileSuspendRequest.model_validate(
            {
                "operation": AuthorityOperation.ACTOR_PROFILE_SUSPEND,
                "actor_profile_id": uuid4(),
                "reason_digest": secret,
            }
        ),
        lambda: ActorProfileSuspendRequest.model_validate_json(
            '{"operation":"actor_profile.suspend","actor_profile_id":"'
            + str(uuid4())
            + '","reason_digest":"'
            + secret
            + '"}'
        ),
        lambda: derive_reason_digest("\ud800" + secret),
        lambda: derive_service_identity_digest("https://identity.example", "\ud800" + secret),
        lambda: derive_service_profile_digest("\ud800" + secret, "approved"),
    ):
        with pytest.raises(TypeError) as caught:
            construct()
        assert secret not in str(caught.value)
        assert secret not in repr(caught.value.args)
        assert secret not in repr(caught.value.__dict__)
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
async def test_all_operation_and_replacement_mappings_commit_one_linked_pair(
    authorization_factory,
) -> None:
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
            reason_digest=DIGEST,
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
            role=ProjectRole.SUBMITTER,
            reason_digest=DIGEST,
        ),
        ProjectRoleGrantIssueRequest(
            operation=AuthorityOperation.PROJECT_ROLE_GRANT_ISSUE,
            project_id=project,
            target_actor_id=actor,
            role=ProjectRole.SUBMITTER,
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
    resource_types = {
        AuthorityOperation.SERVICE_ACTOR_CREATE: AuthorityResourceType.ACTOR_PROFILE,
        AuthorityOperation.ADMIN_ROLE_GRANT_ISSUE: AuthorityResourceType.ADMIN_ROLE_GRANT,
        AuthorityOperation.ADMIN_ROLE_GRANT_REVOKE: AuthorityResourceType.ADMIN_ROLE_GRANT,
        AuthorityOperation.PROJECT_ROLE_GRANT_ISSUE: AuthorityResourceType.PROJECT_ROLE_GRANT,
        AuthorityOperation.PROJECT_ROLE_GRANT_REVOKE: AuthorityResourceType.PROJECT_ROLE_GRANT,
        AuthorityOperation.ACTOR_PROFILE_SUSPEND: AuthorityResourceType.ACTOR_PROFILE,
        AuthorityOperation.ACTOR_PROFILE_REACTIVATE: AuthorityResourceType.ACTOR_PROFILE,
        AuthorityOperation.ACTOR_PROFILE_DEACTIVATE: AuthorityResourceType.ACTOR_PROFILE,
        AuthorityOperation.ACTOR_IDENTITY_LINK_REVOKE: AuthorityResourceType.ACTOR_IDENTITY_LINK,
        AuthorityOperation.ACTOR_IDENTITY_LINK_REACTIVATE: AuthorityResourceType.ACTOR_IDENTITY_LINK,
    }
    create_operations = {
        AuthorityOperation.SERVICE_ACTOR_CREATE,
        AuthorityOperation.ADMIN_ROLE_GRANT_ISSUE,
        AuthorityOperation.PROJECT_ROLE_GRANT_ISSUE,
    }
    record_ids = []
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        for request in requests:
            claim = await _claim(service, uuid4(), uuid4(), request)
            response_id = (
                uuid4()
                if request.operation in create_operations
                else getattr(
                    request,
                    "grant_id",
                    getattr(request, "actor_profile_id", getattr(request, "identity_link_id", None)),
                )
            )
            response = AuthorityResponseReference(
                resource_type=resource_types[request.operation],
                resource_id=response_id,
                version=1,
                http_status=201 if request.operation in create_operations else 200,
            )
            success = _operation_success(claim, request, response)
            completed = await service.complete(
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
            assert completed.response == response
            record_ids.append(claim.record_id)
            await session.commit()
        counts = (
            await session.execute(
                text(
                    "select idempotency_reference, count(*) from audit_events "
                    "where idempotency_reference = any(:records) "
                    "group by idempotency_reference"
                ),
                {"records": record_ids},
            )
        ).all()
    assert len(counts) == len(requests)
    assert {count for _, count in counts} == {2}


@pytest.mark.asyncio
async def test_issue_mismatch_derives_project_and_omits_nonexistent_grant_resource(
    authorization_factory,
) -> None:
    project = uuid4()
    request = ProjectRoleGrantIssueRequest(
        operation=AuthorityOperation.PROJECT_ROLE_GRANT_ISSUE,
        project_id=project,
        target_actor_id=uuid4(),
        role=ProjectRole.REVIEWER,
        reason_digest=DIGEST,
    )
    context = AuthorityMismatchContext(
        event_id=uuid4(), request_id=uuid4(), correlation_id=uuid4()
    )
    async with authorization_factory() as session:
        event_id = await AuthorityMutationService(session).record_mismatch_denial(
            actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
            actor_ref=str(uuid4()),
            request=request.model_dump(),
            context=context,
        )
        await session.commit()
        row = (
            await session.execute(
                text(
                    "select project_id, resource_type, resource_id from audit_events where id=:id"
                ),
                {"id": str(event_id)},
            )
        ).one()
    assert row == (str(project), None, None)


@pytest.mark.asyncio
async def test_failure_after_evidence_flush_rolls_back_claim_and_events(
    authorization_factory, monkeypatch
) -> None:
    actor, key, request = uuid4(), uuid4(), _request()
    async with authorization_factory() as session:
        service = AuthorityMutationService(session)
        claim = await _claim(service, actor, key, request)
        synthetic_id = uuid4()
        await service.record_mismatch_denial(
            actor_ref_kind=claim.actor_ref_kind,
            actor_ref=claim.actor_ref,
            request=request.model_dump(),
            context=AuthorityMismatchContext(
                event_id=synthetic_id,
                request_id=uuid4(),
                correlation_id=uuid4(),
            ),
        )

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
        assert await session.scalar(
            text("select count(*) from audit_events where id=:id"),
            {"id": str(synthetic_id)},
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
async def test_same_key_is_isolated_independently_by_actor_and_reference_kind(
    authorization_factory,
) -> None:
    key, request = uuid4(), _request()
    actor = str(uuid4())
    async with (
        authorization_factory() as first,
        authorization_factory() as second,
        authorization_factory() as third,
    ):
        one = await AuthorityMutationService(first).reserve(
            idempotency_key=key,
            actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
            actor_ref=actor,
            request=request.model_dump(),
        )
        two = await AuthorityMutationService(second).reserve(
            idempotency_key=key,
            actor_ref_kind=ActorReferenceKind.LEGACY_ACTOR,
            actor_ref=actor,
            request=request.model_dump(),
        )
        three = await AuthorityMutationService(third).reserve(
            idempotency_key=key,
            actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
            actor_ref=str(uuid4()),
            request=request.model_dump(),
        )
        assert isinstance(one, ClaimedReservation)
        assert isinstance(two, ClaimedReservation)
        assert isinstance(three, ClaimedReservation)
        await first.rollback()
        await second.rollback()
        await third.rollback()
