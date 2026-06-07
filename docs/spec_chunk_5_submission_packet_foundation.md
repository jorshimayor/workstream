# Chunk 5: Submission Packet Foundation

## Purpose

This chunk adds the backend record for worker submission packets. A worker submits against a task id, Workstream stamps the locked guide and policy context from the task, and every submitted packet version becomes immutable once locked for checker execution.

This completes the Week 1 backend lifecycle through `SUBMITTED`.

## Scope

- submission packet model
- evidence item model
- package URI and package hash metadata
- artifact hash manifest
- worker attestation
- submission versioning
- task transition from `IN_PROGRESS` to `SUBMITTED`
- submission audit events
- API paths for creating, reading, listing, and locking submission packets

## Non-Scope

- checker execution
- checker run records
- human review decisions
- revision replay enforcement
- contribution, payment, or reputation records
- direct file upload or object storage implementation

Chunk 5 stores package and evidence references. Actual file storage still belongs behind the later object-storage abstraction.

## Data Model

`submissions`

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
- `locked_guide_version`
- `locked_checker_policy_version`
- `locked_review_policy_version`
- `locked_revision_policy_version`
- `locked_payment_policy_version`
- `submitted_at`
- `locked_at`
- `supersedes_submission_id`

Submissions intentionally reference the task's locked guide and policy version fields. This prevents task-owned locked context from changing silently after a submission has been recorded.

`evidence_items`

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

## API Contract

POST `/api/v1/tasks/{task_id}/submissions`

Creates a new submission version for the assigned worker.

Request body:

- `summary`
- `package_uri`
- `package_hash`
- `artifact_hash_manifest`
- `worker_attestation`
- `evidence_items`

The request body must not accept guide or policy version fields. Those fields come from the task.

GET `/api/v1/tasks/{task_id}/submissions`

Lists submission versions for a task visible to the current actor.

GET `/api/v1/submissions/{submission_id}`

Returns one visible submission packet.

POST `/api/v1/submissions/{submission_id}/lock`

Locks a submission packet before checker execution. Locking makes the packet immutable in place.

## Versioning Rules

- the first packet for a task is version `1`
- each later packet for that task creates version `2`, `3`, and so on
- a later packet sets `supersedes_submission_id` to the previous latest submission id
- `supersedes_submission_id` must point to the previous latest submission for the same task
- existing submission rows are never edited to replace artifacts
- artifact changes require a new submission version
- evidence rows belong to exactly one submission version
- locked submission packets cannot be mutated in place
- concurrent version conflicts return a controlled conflict response instead of a server error

## Lifecycle Rules

- a worker can submit only when assigned to the task
- first submission requires task status `IN_PROGRESS`
- first submission moves the task to `SUBMITTED`
- later replacement submissions are allowed while the task is still `SUBMITTED`
- submission packet content must satisfy the locked guide's `required_submission_fields`
- every submission creation writes a task audit event
- the audit event includes submission id, submission version, worker id, package hash, and artifact hash manifest
- locking a submission writes a task audit event
- only the latest submission version for a task can be locked
- Chunk 5 submission status is `submitted`; locking sets `locked_at` and does not change status

## Security And Auth

- Workstream still verifies external Flow auth only
- no Workstream-owned login or primary auth session is added
- only the assigned worker can create a submission for the task
- project managers and admins can read and lock submissions for operational flow
- workers can read their own task submissions
- response payloads return server-stamped locked guide and policy versions
- package and evidence URIs are stored as object references, not signed URLs or credentials

## Evidence Identity

Workstream generates evidence item ids at persistence time. Worker-provided manifest rows may include artifact paths or URIs, but the persisted evidence item id is the stable Workstream evidence id for later checker and review records.

## Audit Scope

Chunk 5 writes task audit events with submission identifiers in `event_payload`. Direct submission audit streams are deferred until a dedicated submission-review surface needs them.

## Conditions Of Satisfaction

- worker submits v1 packet against `task_id`
- worker does not provide guide or policy versions
- worker-provided guide or policy version fields are rejected by the API schema
- Workstream stamps locked guide and policy versions from task context
- task moves to `SUBMITTED`
- submitted packet can be locked before checker execution
- replacing an artifact creates a new submission version instead of mutating v1
- submission audit events include task, worker, version, package, and artifact context
- submission and immutability tests pass

## Verifier Agents

- senior engineering
- QA/test
- security/auth
