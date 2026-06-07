"""Pydantic schemas for task queue and assignment APIs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """Request schema for creating a draft task."""

    title: str
    description: str
    task_type: str | None = None
    difficulty: str | None = None
    skill_tags: list[str] = Field(default_factory=list)
    estimated_time_minutes: int | None = Field(default=None, ge=1)
    source_type: Literal["manual", "markdown_import", "csv_import"] = "manual"
    source_ref: str | None = None
    source_payload_hash: str | None = None
    import_batch_id: str | None = None
    external_task_id: str | None = None
    acceptance_criteria: str | None = None
    rejection_criteria: str | None = None
    required_files: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    deadline_at: datetime | None = None


class TaskTransitionRequest(BaseModel):
    """Optional request body for task lifecycle transitions."""

    reason: str | None = None


class EvidenceItemCreate(BaseModel):
    """Request schema for one evidence item in a submission packet."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[
        "log",
        "screenshot",
        "test_result",
        "package",
        "diff",
        "note",
        "external_reference",
    ]
    label: str = Field(min_length=1, max_length=200)
    uri: str | None = Field(default=None, max_length=1000)
    hash: str | None = Field(default=None, max_length=128)
    size_bytes: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactHashEntry(BaseModel):
    """Structured artifact hash entry supplied by a worker."""

    model_config = ConfigDict(extra="forbid")

    artifact: str = Field(min_length=1, max_length=1000)
    hash: str = Field(min_length=1, max_length=128)
    size_bytes: int | None = Field(default=None, ge=0)
    notes: str | None = None


class SubmissionCreate(BaseModel):
    """Request schema for creating a submission packet version."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    package_uri: str | None = Field(default=None, max_length=1000)
    package_hash: str = Field(min_length=1, max_length=128)
    artifact_hash_manifest: list[ArtifactHashEntry] = Field(min_length=1)
    worker_attestation: str = Field(min_length=1)
    evidence_items: list[EvidenceItemCreate] = Field(default_factory=list)


class TaskResponse(BaseModel):
    """Response schema for task records."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    locked_guide_version: str | None
    locked_checker_policy_version: str | None
    locked_review_policy_version: str | None
    locked_revision_policy_version: str | None
    locked_payment_policy_version: str | None
    source_type: str
    source_ref: str | None
    source_payload_hash: str | None
    import_batch_id: str | None
    external_task_id: str | None
    title: str
    description: str
    task_type: str | None
    difficulty: str | None
    skill_tags: list[str]
    estimated_time_minutes: int | None
    base_amount: Decimal | None
    currency: str | None
    payout_type: str | None
    status: str
    acceptance_criteria: str | None
    rejection_criteria: str | None
    required_files: list[str]
    required_evidence: list[str]
    deadline_at: datetime | None
    created_by: str
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime


class AssignmentResponse(BaseModel):
    """Response schema for task assignments."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    worker_id: str
    assigned_by: str
    assigned_at: datetime
    accepted_at: datetime | None
    released_at: datetime | None
    status: str


class TaskWithAssignmentResponse(BaseModel):
    """Response schema for a task operation that creates or uses an assignment."""

    task: TaskResponse
    assignment: AssignmentResponse


class EvidenceItemResponse(BaseModel):
    """Response schema for evidence items."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    submission_id: str
    type: str
    label: str
    uri: str | None
    hash: str | None
    size_bytes: int | None
    locked_at: datetime | None
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias="metadata_json",
        serialization_alias="metadata",
    )
    created_at: datetime


class SubmissionResponse(BaseModel):
    """Response schema for submission packet versions."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    worker_id: str
    version: int
    status: str
    summary: str
    package_uri: str | None
    package_hash: str
    artifact_hash_manifest: list[dict[str, Any]]
    worker_attestation: str
    locked_guide_version: str
    locked_checker_policy_version: str
    locked_review_policy_version: str
    locked_revision_policy_version: str
    locked_payment_policy_version: str
    submitted_at: datetime
    locked_at: datetime | None
    supersedes_submission_id: str | None
    evidence_items: list[EvidenceItemResponse] = Field(default_factory=list)


class AuditEventResponse(BaseModel):
    """Response schema for audit events."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_type: str
    entity_id: str
    event_type: str
    from_status: str | None
    to_status: str | None
    actor_id: str
    external_subject: str
    external_issuer: str
    actor_roles: list[str]
    claim_snapshot: dict[str, Any] = Field(default_factory=dict)
    auth_source: str
    is_dev_auth: bool
    reason: str | None
    event_payload: dict[str, Any]
    created_at: datetime
