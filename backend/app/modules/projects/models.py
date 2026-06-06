"""SQLAlchemy models for projects, guides, and guide-bound policies."""

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
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Project(Base):
    """Project container that owns guide versions and shared payout defaults."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    base_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    guides: Mapped[list[ProjectGuide]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectGuide(Base):
    """Versioned project guide that defines task and submission expectations."""

    __tablename__ = "project_guides"
    __table_args__ = (
        UniqueConstraint("project_id", "version", name="uq_project_guides_project_version"),
        Index(
            "uq_project_guides_one_active_per_project",
            "project_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    required_task_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    required_submission_fields: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    task_instructions: Mapped[str | None] = mapped_column(Text)
    output_requirements: Mapped[str | None] = mapped_column(Text)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text)
    rejection_criteria: Mapped[str | None] = mapped_column(Text)
    reviewer_rubric: Mapped[str | None] = mapped_column(Text)
    forbidden_actions: Mapped[str | None] = mapped_column(Text)
    required_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    difficulty_scale: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    estimated_time_policy: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    common_rejection_reasons: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    evidence_policy: Mapped[dict | None] = mapped_column(JSON)
    unacceptable_work_policy: Mapped[str | None] = mapped_column(Text)
    approved_by: Mapped[str | None] = mapped_column(String(100))
    effective_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    change_summary: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped[Project] = relationship(back_populates="guides")


class CheckerPolicy(Base):
    """Checker requirements attached to a project guide version."""

    __tablename__ = "checker_policies"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "guide_version"],
            ["project_guides.project_id", "project_guides.version"],
            name="fk_checker_policies_project_guide",
        ),
        UniqueConstraint("project_id", "guide_version", name="uq_checker_policies_project_version"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    guide_version: Mapped[str] = mapped_column(String(50), nullable=False)
    required_checkers: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    warning_checkers: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    blocking_severities: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReviewPolicy(Base):
    """Review rules attached to a project guide version."""

    __tablename__ = "review_policies"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "guide_version"],
            ["project_guides.project_id", "project_guides.version"],
            name="fk_review_policies_project_guide",
        ),
        UniqueConstraint("project_id", "guide_version", name="uq_review_policies_project_version"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    guide_version: Mapped[str] = mapped_column(String(50), nullable=False)
    requires_second_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allowed_decisions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    minimum_finding_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    sla_hours: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RevisionPolicy(Base):
    """Revision-loop rules attached to a project guide version."""

    __tablename__ = "revision_policies"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "guide_version"],
            ["project_guides.project_id", "project_guides.version"],
            name="fk_revision_policies_project_guide",
        ),
        UniqueConstraint(
            "project_id",
            "guide_version",
            name="uq_revision_policies_project_version",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    guide_version: Mapped[str] = mapped_column(String(50), nullable=False)
    max_revision_rounds: Mapped[int] = mapped_column(Integer, nullable=False)
    revision_deadline_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    auto_reject_after_limit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allowed_resubmission_states: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    reviewer_reassignment_rule: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PaymentPolicy(Base):
    """Payment rules attached to a project guide version."""

    __tablename__ = "payment_policies"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "guide_version"],
            ["project_guides.project_id", "project_guides.version"],
            name="fk_payment_policies_project_guide",
        ),
        UniqueConstraint("project_id", "guide_version", name="uq_payment_policies_project_version"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    guide_version: Mapped[str] = mapped_column(String(50), nullable=False)
    base_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(String(20))
    payout_type: Mapped[str | None] = mapped_column(String(50))
    revision_payment_rule: Mapped[str | None] = mapped_column(Text)
    rejection_payment_rule: Mapped[str | None] = mapped_column(Text)
    accepted_payment_rule: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
