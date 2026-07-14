"""Application service for typed authority audit evidence."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuthorityAuditEventInput
from app.modules.tasks.models import AuditEvent


class AuditService:
    """Build and persist privacy-safe authority events in the caller unit of work."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the shared audit repository to the caller's session."""
        self._repository = AuditRepository(session)

    async def add_authority_event(self, value: AuthorityAuditEventInput) -> AuditEvent:
        """Persist one validated authority event without committing its transaction."""
        event = AuditEvent(
            id=str(value.event_id),
            entity_type=value.entity_type,
            entity_id=value.entity_id,
            event_type=value.event_type.value,
            from_status=None,
            to_status=None,
            actor_id=value.actor_ref,
            external_subject=None,
            external_issuer=None,
            actor_roles=[],
            claim_snapshot={},
            auth_source="local_authority",
            is_dev_auth=False,
            reason=value.reason,
            event_payload={},
            event_domain="authority",
            event_version=1,
            actor_ref_kind=value.actor_ref_kind.value,
            request_id=str(value.request_id),
            correlation_id=str(value.correlation_id),
            target_actor_ref_kind=(
                value.target_actor_ref_kind.value if value.target_actor_ref_kind else None
            ),
            target_actor_ref=value.target_actor_ref,
            matched_grant_id=value.matched_grant_id,
            permission_id=value.permission_id,
            project_id=value.project_id,
            resource_type=value.resource_type,
            resource_id=value.resource_id,
            target_ref_kind=value.target_ref_kind,
            target_ref_id=value.target_ref_id,
            denial_code=value.denial_code,
            idempotency_reference=(
                str(value.idempotency_reference) if value.idempotency_reference else None
            ),
            invalidation_cause_event_id=(
                str(value.invalidation_cause_event_id)
                if value.invalidation_cause_event_id
                else None
            ),
            invalidation_target_kind=value.invalidation_target_kind,
            invalidation_target_ref=value.invalidation_target_ref,
            before_facts=value.before_facts,
            after_facts=value.after_facts,
        )
        return await self._repository.add_audit_event(event)
