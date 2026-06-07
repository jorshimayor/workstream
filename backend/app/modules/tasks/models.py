"""SQLAlchemy models for task queue, assignment, profiles, and audit events."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class WorkerProfile(Base):
    """Worker profile derived from a trusted external Flow actor."""

    __tablename__ = "worker_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    external_subject: Mapped[str] = mapped_column(String(200), nullable=False)
    external_issuer: Mapped[str] = mapped_column(String(200), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320))
    skill_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class ReviewerProfile(Base):
    """Reviewer profile derived from a trusted external Flow actor."""

    __tablename__ = "reviewer_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    external_subject: Mapped[str] = mapped_column(String(200), nullable=False)
    external_issuer: Mapped[str] = mapped_column(String(200), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320))
    skill_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class WorkstreamTask(Base):
    """Task queue record with server-stamped guide and policy context."""

    __tablename__ = "workstream_tasks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "locked_guide_version"],
            ["project_guides.project_id", "project_guides.version"],
            name="fk_workstream_tasks_locked_guide",
        ),
        ForeignKeyConstraint(
            ["project_id", "locked_checker_policy_version"],
            ["checker_policies.project_id", "checker_policies.guide_version"],
            name="fk_workstream_tasks_locked_checker_policy",
        ),
        ForeignKeyConstraint(
            ["project_id", "locked_review_policy_version"],
            ["review_policies.project_id", "review_policies.guide_version"],
            name="fk_workstream_tasks_locked_review_policy",
        ),
        ForeignKeyConstraint(
            ["project_id", "locked_revision_policy_version"],
            ["revision_policies.project_id", "revision_policies.guide_version"],
            name="fk_workstream_tasks_locked_revision_policy",
        ),
        ForeignKeyConstraint(
            ["project_id", "locked_payment_policy_version"],
            ["payment_policies.project_id", "payment_policies.guide_version"],
            name="fk_workstream_tasks_locked_payment_policy",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    locked_guide_version: Mapped[str | None] = mapped_column(String(50))
    locked_checker_policy_version: Mapped[str | None] = mapped_column(String(50))
    locked_review_policy_version: Mapped[str | None] = mapped_column(String(50))
    locked_revision_policy_version: Mapped[str | None] = mapped_column(String(50))
    locked_payment_policy_version: Mapped[str | None] = mapped_column(String(50))
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    source_ref: Mapped[str | None] = mapped_column(String(500))
    source_payload_hash: Mapped[str | None] = mapped_column(String(128))
    import_batch_id: Mapped[str | None] = mapped_column(String(100))
    external_task_id: Mapped[str | None] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[str | None] = mapped_column(String(100))
    difficulty: Mapped[str | None] = mapped_column(String(50))
    skill_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    estimated_time_minutes: Mapped[int | None] = mapped_column(Integer)
    base_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(String(20))
    payout_type: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text)
    rejection_criteria: Mapped[str | None] = mapped_column(Text)
    required_files: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    required_evidence: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    assignments: Mapped[list[TaskAssignment]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )


class TaskAssignment(Base):
    """Worker assignment record for a task claim."""

    __tablename__ = "task_assignments"
    __table_args__ = (
        Index(
            "uq_task_assignments_one_active_per_task",
            "task_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(
        ForeignKey("workstream_tasks.id"),
        nullable=False,
        index=True,
    )
    worker_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    assigned_by: Mapped[str] = mapped_column(String(100), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)

    task: Mapped[WorkstreamTask] = relationship(back_populates="assignments")


class AuditEvent(Base):
    """Audit event for actor-attributed task lifecycle changes."""

    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    from_status: Mapped[str | None] = mapped_column(String(30))
    to_status: Mapped[str | None] = mapped_column(String(30))
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    external_subject: Mapped[str] = mapped_column(String(200), nullable=False)
    external_issuer: Mapped[str] = mapped_column(String(200), nullable=False)
    actor_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    claim_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    auth_source: Mapped[str] = mapped_column(String(30), nullable=False)
    is_dev_auth: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reason: Mapped[str | None] = mapped_column(Text)
    event_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
