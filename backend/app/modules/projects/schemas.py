"""Pydantic schemas for project guide API requests and responses."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class CheckerPolicyInput(BaseModel):
    """Input schema for checker requirements on a guide version."""

    required_checkers: list[str] = Field(default_factory=list)
    warning_checkers: list[str] = Field(default_factory=list)
    blocking_severities: list[str] = Field(default_factory=list)


class ReviewPolicyInput(BaseModel):
    """Input schema for review rules on a guide version."""

    requires_second_review: bool = False
    allowed_decisions: list[Literal["accept", "needs_revision", "reject"]] = Field(
        default_factory=lambda: ["accept", "needs_revision", "reject"]
    )
    minimum_finding_fields: list[str] = Field(default_factory=list)
    sla_hours: int | None = None


class RevisionPolicyInput(BaseModel):
    """Input schema for revision-loop rules on a guide version."""

    max_revision_rounds: int = Field(ge=1)
    revision_deadline_hours: int = Field(ge=1)
    auto_reject_after_limit: bool = True
    allowed_resubmission_states: list[str] = Field(default_factory=lambda: ["needs_revision"])
    reviewer_reassignment_rule: str | None = None


class PaymentPolicyInput(BaseModel):
    """Input schema for payout rules on a guide version."""

    base_amount: Decimal | None = None
    currency: str | None = None
    payout_type: str | None = None
    revision_payment_rule: str | None = None
    rejection_payment_rule: str | None = None
    accepted_payment_rule: str | None = None


class ProjectCreate(BaseModel):
    """Request schema for creating a project shell."""

    name: str
    slug: str
    description: str | None = None
    base_amount: Decimal | None = None
    currency: str | None = None


class ProjectResponse(BaseModel):
    """Response schema for project records."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: str | None
    status: str
    base_amount: Decimal | None
    currency: str | None
    created_at: datetime
    updated_at: datetime


class ProjectGuideCreate(BaseModel):
    """Request schema for creating a draft project guide."""

    version: str
    content_markdown: str
    required_task_fields: list[str] = Field(default_factory=list)
    required_submission_fields: list[str] = Field(default_factory=list)
    task_instructions: str | None = None
    output_requirements: str | None = None
    acceptance_criteria: str | None = None
    rejection_criteria: str | None = None
    reviewer_rubric: str | None = None
    forbidden_actions: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    difficulty_scale: dict[str, Any] = Field(default_factory=dict)
    estimated_time_policy: dict[str, Any] = Field(default_factory=dict)
    common_rejection_reasons: list[str] = Field(default_factory=list)
    evidence_policy: dict[str, Any] | None = None
    unacceptable_work_policy: str | None = None
    change_summary: str | None = None
    checker_policy: CheckerPolicyInput | None = None
    review_policy: ReviewPolicyInput | None = None
    revision_policy: RevisionPolicyInput | None = None
    payment_policy: PaymentPolicyInput | None = None


class ProjectGuideUpdate(BaseModel):
    """Request schema for editing mutable fields on a draft guide."""

    content_markdown: str | None = None
    required_task_fields: list[str] | None = None
    required_submission_fields: list[str] | None = None
    task_instructions: str | None = None
    output_requirements: str | None = None
    acceptance_criteria: str | None = None
    rejection_criteria: str | None = None
    reviewer_rubric: str | None = None
    forbidden_actions: str | None = None
    required_skills: list[str] | None = None
    difficulty_scale: dict[str, Any] | None = None
    estimated_time_policy: dict[str, Any] | None = None
    common_rejection_reasons: list[str] | None = None
    evidence_policy: dict[str, Any] | None = None
    unacceptable_work_policy: str | None = None
    change_summary: str | None = None
    checker_policy: CheckerPolicyInput | None = None
    review_policy: ReviewPolicyInput | None = None
    revision_policy: RevisionPolicyInput | None = None
    payment_policy: PaymentPolicyInput | None = None


class ProjectGuideResponse(BaseModel):
    """Response schema for project guide records."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    version: str
    status: str
    content_markdown: str
    required_task_fields: list[str]
    required_submission_fields: list[str]
    task_instructions: str | None
    output_requirements: str | None
    acceptance_criteria: str | None
    rejection_criteria: str | None
    reviewer_rubric: str | None
    forbidden_actions: str | None
    required_skills: list[str]
    difficulty_scale: dict[str, Any]
    estimated_time_policy: dict[str, Any]
    common_rejection_reasons: list[str]
    evidence_policy: dict[str, Any] | None
    unacceptable_work_policy: str | None
    approved_by: str | None
    effective_at: datetime | None
    change_summary: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime
    superseded_at: datetime | None


class CheckerPolicyResponse(BaseModel):
    """Response schema for checker policy records."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    guide_version: str
    required_checkers: list[str]
    warning_checkers: list[str]
    blocking_severities: list[str]
    created_at: datetime


class ReviewPolicyResponse(BaseModel):
    """Response schema for review policy records."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    guide_version: str
    requires_second_review: bool
    allowed_decisions: list[str]
    minimum_finding_fields: list[str]
    sla_hours: int | None
    created_at: datetime


class RevisionPolicyResponse(BaseModel):
    """Response schema for revision policy records."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    guide_version: str
    max_revision_rounds: int
    revision_deadline_hours: int
    auto_reject_after_limit: bool
    allowed_resubmission_states: list[str]
    reviewer_reassignment_rule: str | None
    created_at: datetime


class PaymentPolicyResponse(BaseModel):
    """Response schema for payment policy records."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    guide_version: str
    base_amount: Decimal | None
    currency: str | None
    payout_type: str | None
    revision_payment_rule: str | None
    rejection_payment_rule: str | None
    accepted_payment_rule: str | None
    created_at: datetime


class ActiveGuideResponse(BaseModel):
    """Response schema for an active guide and its policy context."""

    guide: ProjectGuideResponse
    checker_policy: CheckerPolicyResponse
    review_policy: ReviewPolicyResponse
    revision_policy: RevisionPolicyResponse
    payment_policy: PaymentPolicyResponse
