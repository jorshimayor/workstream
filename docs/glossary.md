# Glossary

## Workstream

Flow's task evaluation and contribution infrastructure: the system for project guides, task queues, submission packets, automated checks, reviewer routing, evaluation sprints, revision loops, contribution records, payment status, and reputation signals.

## Project

A configured work program with its own human-facing guide, submission artifact policy, checker policies, review policy, revision policy, payment policy, and queue.

## Project Owner

The external or internal organization that provides open-ended project material
and business terms. That material can be markdown, URL-backed documentation,
repository docs, examples, rubrics, task instructions, base payout or payment
policy inputs, or other project-specific source material. The project owner
does not author or approve Workstream's machine-readable internal policy schema.

## ActorContext

Legacy name for the trusted per-request identity context resolved from a
verified Flow token. During WS-AUTH-001 migration it is replaced by a minimal
`VerifiedIssuerToken` plus locally resolved `AuthorizationContext`. Token roles
are not Workstream product authority.

## ActorIdentity

Legacy registry record for a verified Flow actor. WS-AUTH-001 classifies each
row before migrating safe UUID actor identifiers into canonical
`ActorProfile.id` plus a new `ActorIdentityLink`. It is not a grant or
Workstream-owned authentication.

## ActorProfile

The single canonical Workstream actor root. It records actor kind and status;
it does not itself grant project or administrative authority. Verified
issuer/subject identities attach through `ActorIdentityLink`. Authority comes
from `AdminRoleGrant` or exact-project `ProjectRoleGrant` records plus resource
and lifecycle guards.

Legacy typed profile row IDs are workflow metadata IDs and never canonical
actor IDs or grants.

## ActorIdentityLink

The active-or-revoked link between one canonical issuer/opaque subject and one
ActorProfile. Raw tokens, provider credentials, and full claims are not stored.

## ArtifactUploadSession

The task- or guide-scoped operational staging record that authorizes bounded
artifact upload, sealing, expiry, and single-use consumption. It is not a
submission and grants no review authority.

## ArtifactContent

Workstream's provider-neutral immutable content identity: server-computed
SHA-256, byte count, and bounded media metadata. Opaque provider identifiers and
protocol observations are replica details, not this record's identity.

## ArtifactUploadItem

The per-item mutable upload-operation ledger inside an
`ArtifactUploadSession`. It owns byte reservation, logical role, scoped
idempotency, request digest, CAS state, provider operation reference, and the
resulting `ArtifactContent`. It is not an `ArtifactBinding`.

## ArtifactBinding

The immutable logical association between `ArtifactContent` and one exact
Workstream project/resource/logical role. Staging is not a binding. Replacement
creates a new row with `supersedes_binding_id`; prior rows remain history. It
records Workstream meaning and provenance, not storage-provider state.

## ArtifactReplica

One provider copy of `ArtifactContent`, identified by opaque provider artifact
and optional bounded protocol observations. Verification, availability, and
integrity states belong here and do not create task or review states. Logical
Workstream references are represented only by `ArtifactBinding`.

## ArtifactOperationReceipt

An append-only record of an idempotent storage-provider operation, canonical
request/response digests, provider reference, bounded outcome, and timestamps.

## ArtifactSetManifest

The server-generated canonical description of a sealed upload session's content
IDs, logical roles, trusted file facts, SHA-256 values, and byte counts. Every
entry has a server-derived identity over all semantic fields, exact duplicate
entries are rejected, and a total ordering makes the hash deterministic. Its
hash commits only to that exact set. A separate pre-submit admission record
binds the hash to actor, task, policy, checker, exact submission input, result,
and expiry.

## ReviewPacketManifest

The future WS-REV-owned, system-generated packet presented to an authorized
reviewer. It references general artifact bindings and is not implemented by the
WS-ART storage foundation.

## ReviewEvidenceArtifact

The future WS-REV-owned reviewer attachment record. It references a verified
general artifact binding and requires reviewer assignment/lease authority.

## AdminRoleGrant

An immutable administrative authority record for Access Administrator,
Operator, Project Manager, Finance Authority, or Audit Authority at compatible
system/project scope.

## ProjectRoleGrant

An immutable exact-project contributor authority record with role `submitter`,
`reviewer`, or `both`.

## Contributor

The umbrella human product term for a person participating in Workstream. A
contributor has an exact-project `submitter`, `reviewer`, or `both` grant.
Celery, checker, setup, and background workers are internal services, not human
product roles.

## Source

Where a task came from. In v0.1, sources are manual creation, controlled markdown import, or controlled CSV import.

## Origin

A future external task source that can submit tasks into Workstream through an adapter. External origin onboarding is not part of v0.1.

## Project Guide

The human-facing operating guide for a project. It contains the project instructions, quality bar, task examples, reviewer rubric, common rejection reasons, and links or summaries for the approved policies. A project guide may be markdown, an imported document, or a URL-backed guide, but runtime enforcement uses approved machine-readable policies attached to the guide version.

## Guide Sufficiency Report

The Workstream-owned sufficiency record for a project guide version and source
snapshot. It is normally produced by `ProjectGuideSufficiencyAgent`, but an
authorized covered Project Manager can create a manual report when needed.
It records
whether the guide passed, is blocked by gaps, or passed with warnings that an
authorized covered Project Manager must acknowledge before activation. Manual reports
clear only the manual policy path; agent derivation requires an agent-created
sufficiency report for the same snapshot.

## Project Setup Run

A non-authoritative orchestration ledger for automatic project setup. It records
queue status, current setup step, Celery task id, bounded errors, and output
record ids for guide sufficiency, submission artifact policy derivation, and
post-submit checker setup continuation. The actual policy truth remains in the
source snapshot, sufficiency report, submission artifact policy, effective
project policy, pre-submit checker policy, and post-submit checker policy rows.

## Submission Artifact Policy

The Workstream-derived, covered-Project-Manager-approved machine-readable
contract for what a contributor must submit. It is derived from open-ended project
guide material after guide sufficiency passes or passes with warnings, reviewed
by an authorized covered Project Manager after any
warnings are acknowledged, and attached to a project guide version. It defines
required artifacts, evidence requirements, forbidden artifacts, attestation
requirements, size limits, and project-specific packaging rules. It can add or
tighten requirements, but it cannot weaken Workstream's default submission
artifact rules. Server-generated manifests, SHA-256, and the configured storage
provider are unconditional platform invariants rather than project policy
choices.

The project-specific policy row is still `SubmissionArtifactPolicy`; Workstream
does not define a separate `ProjectSubmissionArtifactPolicy` type.

## Effective Project Submission Artifact Policy

The deterministic merge of Workstream's default submission artifact policy and the project-approved submission artifact policy. Workstream computes this effective project policy before generating the project pre-submit checker policy.

## Pre-Submit Checker Policy

The server-generated project checker matrix produced from the effective project submission artifact policy, persisted with a compiled bundle hash, and locked by tasks before they enter the contributor pipeline. It runs before Workstream creates a submission row or submission version. The preflight endpoint returns `PreSubmitCheckResponse`; a blocked submission-create attempt returns `pre_submission_checker_failed` with structured pass/fail/warning details. Neither path returns review decision values: `accept`, `needs_revision`, or `reject`.

## pre_submission_checker_failed

The contributor-facing domain error code returned when a submission-create attempt is blocked by pre-submit checks. It includes structured pass/fail/warning details in the error details and is not a review decision. It must not be stored as `accept`, `needs_revision`, or `reject`. The preflight endpoint returns `PreSubmitCheckResponse` instead of this error code.

## Task

A unit of work inside a project.

## Task Work Context

The contributor-safe API projection of a task's locked guide, project summary,
review policy, revision policy, payment policy, and lifecycle state. It is read
from the task's stamped locked context and does not expose source snapshot
hashes, private source/import refs, compiled checker bundles, checker configs,
Celery ids, or setup errors.

## Task Submission Requirements

The contributor-safe API projection of the task's locked effective project
submission artifact policy. It tells the contributor the exact required artifacts,
evidence keys, forbidden artifact rules, storage reference rules, packaging
rules, hash algorithm, size limits, and attestation terms before submission.

## Task Locked Context

The permission-scoped Project Manager, Operator, or Audit projection of a task's
locked guide and policy provenance, including guide source snapshot id/hash, effective policy
id/hash, pre-submit checker policy id/hash, post-submit checker policy
id/hash/body summary, and review, revision, and payment policy versions.

## Task Contract

The normalized task fields required for Workstream to screen, assign, check, review, pay, and audit work.

## Submission Packet

The contributor's submitted output plus summary, artifacts, evidence references, hashes, and metadata. Workstream assigns the submission version server-side after blocking pre-submit checks pass.

## Checker

An automated rule that validates a task or submission before human review.

## Checker Policy

The set of required and warning checks for a project phase. Pre-submit checker policy is generated from the effective project submission artifact policy. Post-submit checker policy governs durable internal checker runs after a submission is finalized into the pre-review gate.

## Human Review

The judgment layer where a reviewer accepts, rejects, or requests revision.

## Finding

A structured reviewer issue with severity, area, required fix, and evidence.

## Revision Replay

A resubmission record showing how each prior review finding was addressed.

## Evidence

Proof supporting task completion or review decision. Examples: logs, hashes, tests, screenshots, diffs, notes.

## Artifact Store

The provider-neutral typed capability through which Workstream stores and reads
private immutable bytes. `LocalStorageAdapter` implements it for development
and focused tests. `S3CompatibleArtifactStore` implements it for MinIO
integration and AWS S3 v0.1 production deployments. Providers do
not own Workstream authorization, binding, lifecycle, audit, or integrity
decisions.

## Artifact Verification Job

A durable Celery request to read and hash a complete stored object before its
replica becomes bindable. PostgreSQL coordinates execution with an executor
UUID, lease expiry, and generation fencing. This infrastructure lease is not a
contributor task claim or reviewer lease.

## Artifact Recovery Attempt

A reason- and idempotency-bound Operator authorization/audit envelope with
distinct source and retry verification job IDs. It is not executable work and
owns no Celery executor, execution lease, or generation; the retry verification
job owns those infrastructure coordination fields.

## S3-Compatible Artifact Store

The object-storage adapter that implements `ArtifactStore` using the S3
protocol. AWS S3 is the v0.1 production provider; MinIO is used for local and CI
integration proof. Cloudflare R2 is deferred to a separate approved initiative.

## Payment Ledger

The fulfillment-status record for payable compensation awards, including
pending, submitted, paid, disputed, and external-reference facts. Explicitly
unpaid contribution rules create no award or payment-ledger entry.

## Reputation Ledger

The outcome-based record of contributor and reviewer performance.

## Contribution Record

The immutable, evidence-backed record of one completed contribution under locked
project context. `completed_review` is created for every valid recorded human
Review; `accepted_submission` is created for the submitter only on `accept`.
Compensation and reputation records may attach to either contribution type, but
do not replace the contribution record.

## Human Owner

The person accountable for a submitted packet, even when agents or external tools helped produce the work.
