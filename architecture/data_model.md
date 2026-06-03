# Data Model

## Entity Overview

```text
User
  WorkerProfile
  ReviewerProfile

Project
  ProjectGuide
  CheckerPolicy
  ReviewPolicy
  PaymentPolicy
  ProjectLesson

Task
  Assignment
  Submission
    EvidenceItem
    CheckerRun
      CheckerResult
    ReadinessCertificate
    Review
      ReviewFinding
    RevisionReplay
  ContributionRecord
  PaymentRecord
  ReputationEvent
  AuditEvent
```

## User

Fields:

- `id`
- `name`
- `email`
- `role`
- `created_at`
- `status`

Roles:

- admin
- project_manager
- worker
- reviewer
- finance
- auditor

`Operator` is a product persona, not a separate v0.1 permission role. In the application model, operator actions are performed by project managers, workers, reviewers, admins, or finance users depending on the action.

## WorkerProfile

Fields:

- `user_id`
- `display_name`
- `skill_tags`
- `accepted_count`
- `needs_revision_count`
- `rejected_count`
- `paid_total`
- `pending_payout_total`
- `reputation_score`
- `status`

## ReviewerProfile

Fields:

- `user_id`
- `skill_tags`
- `reviews_completed`
- `accept_count`
- `needs_revision_count`
- `reject_count`
- `overturned_count`
- `average_turnaround_hours`
- `review_quality_score`
- `status`

## Project

Fields:

- `id`
- `name`
- `slug`
- `description`
- `status`
- `base_amount`
- `currency`
- `created_at`
- `updated_at`

Status:

- draft
- active
- paused
- archived

## ProjectGuide

Fields:

- `id`
- `project_id`
- `version`
- `content_markdown`
- `required_task_fields`
- `required_submission_fields`
- `task_instructions`
- `output_requirements`
- `acceptance_criteria`
- `rejection_criteria`
- `reviewer_rubric`
- `forbidden_actions`
- `required_skills`
- `difficulty_scale`
- `estimated_time_policy`
- `common_rejection_reasons`
- `evidence_policy`
- `unacceptable_work_policy`
- `approved_by`
- `effective_at`
- `change_summary`
- `created_by`
- `created_at`
- `superseded_at`

The guide is versioned. Every task records the guide version active at creation or screening time before the task enters `READY`. Later source adapters must also lock the guide version during normalization before workers see the task.

Material changes require a new guide version. Material changes include acceptance criteria, rejection criteria, reviewer rubric, output requirements, evidence policy, checker policy, review policy, revision policy, and payment policy.

## CheckerPolicy

Fields:

- `id`
- `project_id`
- `guide_version`
- `required_checkers`
- `warning_checkers`
- `blocking_severities`
- `created_at`

Example:

```json
{
  "required_checkers": [
    "check_task_schema",
    "check_submission_packet",
    "check_evidence_present"
  ],
  "blocking_severities": ["high"]
}
```

## ReviewPolicy

Fields:

- `id`
- `project_id`
- `guide_version`
- `requires_second_review`
- `allowed_decisions`
- `minimum_finding_fields`
- `sla_hours`
- `created_at`

## PaymentPolicy

Fields:

- `id`
- `project_id`
- `guide_version`
- `base_amount`
- `currency`
- `payout_type`
- `revision_payment_rule`
- `rejection_payment_rule`
- `accepted_payment_rule`
- `created_at`

## ProjectLesson

Fields:

- `id`
- `project_id`
- `guide_version`
- `source`
- `lesson_type`
- `summary`
- `recommended_change`
- `status`
- `created_by`
- `created_at`
- `closed_at`

Lesson types:

- guide_update
- checker_update
- reviewer_policy_update
- queue_policy_update
- payment_policy_update
- risk_note

Status:

- open
- accepted
- rejected
- implemented

## Task

Fields:

- `id`
- `project_id`
- `guide_version`
- `source_type`
- `source_ref`
- `source_payload_hash`
- `import_batch_id`
- `external_task_id`
- `title`
- `description`
- `task_type`
- `difficulty`
- `skill_tags`
- `estimated_time_minutes`
- `base_amount`
- `currency`
- `payout_type`
- `status`
- `acceptance_criteria`
- `rejection_criteria`
- `required_files`
- `required_evidence`
- `deadline_at`
- `created_by`
- `assigned_to`
- `created_at`
- `updated_at`

Status:

- draft
- screening
- ready
- claimed
- in_progress
- submitted
- auto_checking
- pre_review_gate
- review_pending
- needs_revision
- accepted
- rejected
- cancelled

Source type:

- manual
- markdown_import
- csv_import

External origin adapters are later work. When added, they normalize into this task shape instead of creating a separate task lifecycle.

## Assignment

Fields:

- `id`
- `task_id`
- `worker_id`
- `assigned_by`
- `assigned_at`
- `accepted_at`
- `released_at`
- `status`

## Submission

Fields:

- `id`
- `task_id`
- `worker_id`
- `version`
- `status`
- `summary`
- `package_uri`
- `package_hash`
- `artifact_hash_manifest`
- `worker_attestation`
- `guide_version`
- `checker_policy_version`
- `review_policy_version`
- `payment_policy_version`
- `submitted_at`
- `locked_at`
- `supersedes_submission_id`

Status:

- submitted
- checking
- check_failed
- review_pending
- needs_revision
- accepted
- rejected

## EvidenceItem

Fields:

- `id`
- `submission_id`
- `type`
- `label`
- `uri`
- `hash`
- `size_bytes`
- `locked_at`
- `metadata`
- `created_at`

Types:

- log
- screenshot
- test_result
- package
- diff
- note
- external_reference

## CheckerRun

Fields:

- `id`
- `submission_id`
- `status`
- `started_at`
- `finished_at`
- `runner_version`
- `guide_version`
- `checker_policy_version`
- `submission_version`
- `artifact_hash_manifest`
- `summary`

Status:

- running
- passed
- warning
- failed

## CheckerResult

Fields:

- `id`
- `checker_run_id`
- `checker_name`
- `status`
- `severity`
- `message`
- `suggested_fix`
- `evidence_refs`
- `created_at`

Status:

- pass
- warn
- fail

Severity:

- low
- medium
- high

## CheckerDefinition

Fields:

- `id`
- `checker_id`
- `name`
- `phase`
- `default_severity`
- `default_blocks_review`
- `version`
- `worker_visible`
- `description`
- `created_at`
- `retired_at`

Phase:

- project_activation
- task_screening
- submission_quality
- pre_review_gate
- lifecycle_transition
- payment_reconciliation

The checker registry prevents project guide templates, checker policies, and implementation code from drifting into different checker names for the same rule.

## ReadinessCertificate

Fields:

- `id`
- `submission_id`
- `checker_run_id`
- `artifact_hash_manifest`
- `blocking_failures_count`
- `warnings_count`
- `ready_for_review`
- `issued_by`
- `issued_at`
- `invalidated_at`

Purpose:

The readiness certificate records the exact checker run and artifact hashes that allowed a submission to enter human review.

If any submitted artifact changes, the certificate is invalidated and a new submission/checker run is required.

## Review

Fields:

- `id`
- `submission_id`
- `reviewer_id`
- `decision`
- `summary`
- `confidence`
- `acceptance_evidence_refs`
- `guide_version`
- `review_policy_version`
- `created_at`
- `completed_at`

Decision:

- accept
- needs_revision
- reject

## ReviewFinding

Fields:

- `id`
- `review_id`
- `severity`
- `area`
- `issue`
- `required_fix`
- `evidence_ref`
- `created_at`

Severity:

- low
- medium
- high

## RevisionReplay

Fields:

- `id`
- `task_id`
- `prior_submission_id`
- `new_submission_id`
- `created_by`
- `created_at`

Each replay has items:

- `prior_finding_id`
- `fix_summary`
- `evidence_ref`
- `worker_claim_status`
- `reviewer_closure_status`

Worker claim status:

- fixed
- disputed
- not_applicable

Reviewer closure status:

- closed_fixed
- closed_rebutted
- partially_closed
- still_open
- obsolete

## ContributionRecord

Fields:

- `id`
- `project_id`
- `task_id`
- `accepted_submission_id`
- `accepting_review_id`
- `worker_id`
- `guide_version`
- `checker_run_id`
- `readiness_certificate_id`
- `artifact_hash_manifest`
- `acceptance_evidence_refs`
- `skill_tags`
- `difficulty`
- `accepted_amount`
- `currency`
- `payout_type`
- `created_from_audit_event_id`
- `status`
- `accepted_at`
- `created_at`
- `exported_at`
- `voided_at`
- `void_reason`

Status:

- recorded
- exported
- voided

Purpose:

The contribution record is created when work is accepted. It certifies that a specific worker completed accepted work under a locked project guide with cited evidence. Payment records and reputation events attach to this record, but do not replace it.

## PaymentRecord

Fields:

- `id`
- `contribution_record_id`
- `task_id`
- `worker_id`
- `base_amount`
- `accepted_amount`
- `pending_amount`
- `paid_amount`
- `currency`
- `payout_type`
- `status`
- `payment_reference`
- `payment_policy_version`
- `dispute_reason`
- `disputed_at`
- `accepted_at`
- `paid_at`

Status:

- none
- pending
- payout_submitted
- paid
- disputed

## PaymentAdjustment

Fields:

- `id`
- `payment_record_id`
- `actor_id`
- `old_amount`
- `new_amount`
- `currency`
- `reason`
- `evidence_ref`
- `created_at`

Payment adjustments are append-only. Accepted amount changes must use this record instead of editing payment values silently.

## ReputationEvent

Fields:

- `id`
- `user_id`
- `task_id`
- `submission_id`
- `contribution_record_id`
- `event_type`
- `skill_tags`
- `weight`
- `score_delta`
- `reason`
- `created_at`

Event types:

- accepted
- needs_revision
- rejected
- revision_closed
- contribution_recorded
- paid
- review_overturned
- review_confirmed

## AuditEvent

Fields:

- `id`
- `entity_type`
- `entity_id`
- `actor_id`
- `event_type`
- `before`
- `after`
- `reason`
- `guide_version`
- `submission_id`
- `checker_run_id`
- `review_id`
- `contribution_record_id`
- `override_id`
- `created_at`

Audit events are append-only.

## Required Invariants

- a task must belong to a project
- a task records the project guide version used at creation
- a task cannot enter ready without passing screening or documented admin override
- a submission must belong to a task
- a review must belong to a submission
- an accepted task must have at least one accepted submission
- an accepted task must create a contribution record
- no payment exposure exists without a contribution record
- a paid task must have an accepted payment record
- reputation events for accepted work must reference the accepted contribution record
- reviewer-quality reputation events must reference a review or audit source
- payment amount changes require a payment adjustment record
- disputed payments cannot become `paid` without a dispute resolution audit event
- high-severity checker failures block review unless an admin override is recorded
- a checker run must reference the exact submission version and artifact hashes it evaluated
- a readiness certificate must reference the exact checker run that cleared the submission for review
- a review cannot accept a submission if the checker run belongs to a different submission version
- every status transition creates an audit event
- every needs-revision decision has at least one review finding
- every accept decision cites evidence
- repeated review/checker failures become ProjectLesson records
- submission artifacts are immutable after `locked_at`
- a changed artifact requires a new submission version
- task lifecycle status and payment status remain separate
