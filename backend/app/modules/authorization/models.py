"""SQLAlchemy models for authority mutation idempotency."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, DateTime, SmallInteger, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class AuthorityIdempotencyRecord(Base):
    """Internal reservation and typed replay reference for one authority mutation."""

    __tablename__ = "authority_idempotency_records"
    __table_args__ = (
        UniqueConstraint(
            "actor_ref_kind", "actor_ref", "operation", "idempotency_key",
            name="replay_namespace",
        ),
        UniqueConstraint("id", "actor_ref_kind", "actor_ref", name="actor_reference"),
        CheckConstraint(
            "actor_ref_kind in ('legacy_actor', 'actor_profile', 'system_principal')",
            name="actor_kind",
        ),
        CheckConstraint(
            "((actor_ref_kind = 'system_principal' and actor_ref = "
            "'workstream:system:bootstrap') or (actor_ref_kind <> 'system_principal' and "
            "actor_ref ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'))",
            name="actor_reference",
        ),
        CheckConstraint(
            "operation in ('service_actor.create', 'admin_role_grant.issue', "
            "'admin_role_grant.revoke', 'project_role_grant.issue', "
            "'project_role_grant.revoke', 'actor_profile.suspend', "
            "'actor_profile.reactivate', 'actor_profile.deactivate', "
            "'actor_identity_link.revoke', 'actor_identity_link.reactivate')",
            name="operation",
        ),
        CheckConstraint("request_digest ~ '^sha256:[0-9a-f]{64}$'", name="request_digest"),
        CheckConstraint("status in ('pending', 'committed')", name="status"),
        CheckConstraint(
            "response_resource_version is null or response_resource_version > 0",
            name="response_version",
        ),
        CheckConstraint(
            "(status = 'pending' and response_resource_type is null and "
            "response_resource_id is null and response_resource_version is null and "
            "response_http_status is null and committed_at is null) or "
            "(status = 'committed' and response_resource_type is not null and "
            "response_resource_id is not null and response_http_status is not null and "
            "committed_at is not null)",
            name="state_shape",
        ),
        CheckConstraint(
            "response_http_status is null or ((operation in ('service_actor.create', "
            "'admin_role_grant.issue', 'project_role_grant.issue') and "
            "response_http_status = 201) or (operation not in ('service_actor.create', "
            "'admin_role_grant.issue', 'project_role_grant.issue') and "
            "response_http_status = 200))",
            name="response_status",
        ),
        CheckConstraint(
            "(operation = 'service_actor.create' and (response_resource_type is null or "
            "response_resource_type = 'actor_profile')) or "
            "(operation like 'admin_role_grant.%' and (response_resource_type is null or "
            "response_resource_type = 'admin_role_grant')) or "
            "(operation like 'project_role_grant.%' and (response_resource_type is null or "
            "response_resource_type = 'project_role_grant')) or "
            "(operation like 'actor_profile.%' and (response_resource_type is null or "
            "response_resource_type = 'actor_profile')) or "
            "(operation like 'actor_identity_link.%' and (response_resource_type is null or "
            "response_resource_type = 'actor_identity_link'))",
            name="response_type",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(), nullable=False)
    actor_ref_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_ref: Mapped[str] = mapped_column(String(100), nullable=False)
    operation: Mapped[str] = mapped_column(String(48), nullable=False)
    request_digest: Mapped[str] = mapped_column(String(71), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    response_resource_type: Mapped[str | None] = mapped_column(String(32))
    response_resource_id: Mapped[UUID | None] = mapped_column(Uuid())
    response_resource_version: Mapped[int | None] = mapped_column(BigInteger)
    response_http_status: Mapped[int | None] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    committed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
