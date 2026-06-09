# Chunk 6: Checker Contract And Records

## Purpose

Chunk 6 creates the durable checker run and checker result contract for Week 2.

This chunk does not run the full checker framework yet. It defines the records, schemas, service boundaries, and read APIs that later chunks use for pre-submit static checks, post-submit internal auto checks, and review gating.

## Scope

- checker run model
- checker result model
- checker run status values
- checker result status and severity values
- run type and trigger source fields
- gate outcome fields
- source tracking for checker-caused `needs_revision`
- backend read APIs for checker runs and results
- internal service method for creating checker runs/results
- migration and ORM metadata
- tests for persistence, visibility, and immutability expectations

## Non-Scope

- real checker registry
- real checker execution
- automatic background trigger after submission locking
- task lifecycle movement to `AUTO_CHECKING`, `REVIEW_PENDING`, or `NEEDS_REVISION`
- product frontend
- reviewer queue UI
- human review decisions
- revision replay enforcement
- contribution, payment, or reputation records

## Required Model

`checker_runs`

- `id`
- `task_id`
- `submission_id`
- `submission_version`
- `run_type`
- `trigger_source`
- `status`
- `gate_outcome`
- `outcome_source`
- `triggered_by`
- `locked_guide_version`
- `locked_checker_policy_version`
- `locked_review_policy_version`
- `locked_revision_policy_version`
- `locked_payment_policy_version`
- `package_hash`
- `artifact_hash_manifest`
- `artifact_manifest_hash`
- `blocking_failure_count`
- `warning_count`
- `started_at`
- `completed_at`
- `failure_message`
- `created_at`
- `updated_at`

`checker_results`

- `id`
- `checker_run_id`
- `checker_id`
- `checker_name`
- `checker_version`
- `phase`
- `status`
- `severity`
- `blocks_review`
- `message`
- `suggested_fix`
- `evidence_refs`
- `metadata`
- `worker_visible`
- `created_at`

## Canonical Values

`checker_runs.run_type`

- `pre_submit`
- `post_submit`

`checker_runs.trigger_source`

- `api_preflight`
- `submission_locked`
- `manual_operator`
- `retry`

`checker_runs.status`

- `queued`
- `running`
- `completed`
- `failed`

`checker_runs.gate_outcome`

- `not_evaluated`
- `allow_review`
- `needs_revision`
- `operator_retry`

`checker_runs.outcome_source`

- `none`
- `auto_checker`

`checker_results.status`

- `pass`
- `warn`
- `fail`

`checker_results.severity`

- `low`
- `medium`
- `high`

## Record Binding

Post-submit checker runs must bind to one locked submission version.

The run snapshots:

- `task_id`
- `submission_id`
- `submission_version`
- `package_hash`
- `artifact_hash_manifest`
- deterministic `artifact_manifest_hash`
- locked project guide version
- locked checker policy version
- locked review policy version
- locked revision policy version
- locked payment policy version

The client does not provide locked guide or policy versions for checker runs. Workstream copies them from the persisted submission.

## User-Facing Revision Rule

User-facing outcomes remain simple:

- `accepted`
- `rejected`
- `needs_revision`

Checker-caused revision uses the same user-facing `needs_revision` state, but records the source internally:

- `gate_outcome = needs_revision`
- `outcome_source = auto_checker`
- `review_decision_id = null` when that field exists in later review work

Human reviewer revision remains separate later:

- `outcome = needs_revision`
- `outcome_source = human_review`
- `review_decision_id` present

Chunk 6 stores the checker-side source fields but does not implement human review decisions.

## API Contract

Read APIs:

- GET `/api/v1/submissions/{submission_id}/checker-runs`
- GET `/api/v1/checker-runs/{checker_run_id}`

The API must not allow clients to create arbitrary successful checker results.

Write behavior is internal service/repository only in Chunk 6. Chunk 7 and Chunk 9 can expose controlled trigger paths.

## Visibility Rules

Workers can read checker runs/results for their assigned task submissions.

Project managers and admins can read checker runs/results for project operations.

Worker-visible responses must include:

- checker name
- status
- severity
- message
- suggested fix when safe
- evidence references when safe

Worker-visible responses must not expose internal metadata when `worker_visible` is false.

Project managers and admins can see operational metadata.

## Conditions Of Satisfaction

- migration creates checker run and checker result tables
- ORM models match migration metadata
- checker runs reference existing task and submission records
- post-submit checker run creation snapshots locked submission context server-side
- artifact manifest hash is deterministic for equivalent manifests
- checker results are tied to one checker run
- canonical status/severity values are enforced by schemas/service constants
- read APIs return checker run and checker result records
- workers cannot read unrelated checker runs
- workers do not receive non-worker-visible metadata
- project managers and admins can read operational checker output
- clients cannot submit fake passed checker results through public APIs
- tests cover persistence, visibility, and locked-context snapshotting
- docstring coverage remains above threshold

## Verifier Agents

- senior engineering
- QA/test
- security/auth
- product/ops
