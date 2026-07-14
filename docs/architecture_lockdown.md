# Architecture Lockdown

Last updated: 2026-07-14

## Purpose

This note locks the Workstream v0.1 architecture around source-agnostic intake, project guide discipline, task contracts, human accountability for agent-assisted work, contribution records, payment records, and reputation consequences.

The ADR files under `docs/decision_*.md` are the decision record for this lockdown. When a locked rule changes, update or add an ADR before changing implementation specs.

The canonical v0.1 scope remains narrower:

```text
Project guide
-> submission artifact policy
-> task screening
-> task queue
-> pre-submit checker policy
-> submission packet
-> automated checks
-> pre-review gate
-> human review
-> revision replay
-> review decision: accept / needs_revision / reject
-> contribution record
-> payment record
-> reputation event
```

## Locked For v0.1

### Source-Agnostic, Manual First

Workstream is source-agnostic, but v0.1 does not include external source adapters.

Allowed v0.1 intake:

- manual task creation
- controlled markdown import
- controlled CSV import

Every imported or manually created task still normalizes into the same Workstream task contract.

### Three Gates

Workstream uses three separate quality gates:

1. Project activation gate
2. Task screening gate
3. Submission quality gate

### Authorization Boundary

Workstream verifies external Flow tokens and owns product authorization through
local ActorProfile/ActorIdentityLink records, administrative grants,
exact-project submitter/reviewer grants, registered permissions, resource and
lifecycle guards, revocation, and append-only authority evidence.

Token roles and typed workflow profiles are not product authority. All public
routes remain under `/api/v1`. ADR 0012 and the canonical authorization service
specification control authorization wording in this lockdown.

External origin qualification and task ingestion map to project activation and task screening in v0.1. External origins remain deferred.

### Project Guide Structure

Every project guide is human-facing. It must explain:

- purpose
- task types
- task instructions
- acceptance criteria
- rejection criteria
- reviewer rubric
- required skills
- difficulty scale
- estimated time policy
- common rejection reasons

Every active guide version must also have approved machine-readable policies:

- immutable guide-source snapshot
- guide sufficiency report
- submission artifact policy
- effective project submission artifact policy hash
- project pre-submit checker bundle hash
- post-submit checker policy
- review policy
- revision policy
- payment policy

The guide may summarize or link to those policies, but the policies are the enforcement source.

Project owners provide open-ended project material and business terms.
Workstream evaluates guide sufficiency, derives
`SubmissionArtifactPolicy` from that material, and an authorized covered
Project Manager approves the internal policy bundle
before guide activation. Project owners do not approve Workstream's internal
submission policy schema.

`SubmissionArtifactPolicy` defines project-level intake rules. Workstream combines it with the non-bypassable Workstream default submission artifact policy to create `EffectiveProjectSubmissionArtifactPolicy`. Workstream then generates, persists, and locks project `PreSubmitCheckerPolicy` with a compiled bundle hash from that effective project submission artifact policy. Tasks lock the applicable guide snapshot, effective project submission artifact policy hash, and pre-submit checker bundle hash before entering the contributor pipeline.

Blocking pre-submit failures prevent submission creation. Preflight failures
return `PreSubmitCheckResponse(status="failed", eligible_to_submit=false,
results=[...])`. Blocked submission-create attempts return
`pre_submission_checker_failed` with structured pass/fail/warning details and
create no submission row, no submission version, no task transition to
`submitted`, and no submission-created audit event. Workstream still writes a
task audit event named `pre_submission_check_failed` with the structured checker
result for project operators; this is audit evidence, not a product review
decision.

Tasks lock to the active guide version at creation or screening time before entering `READY`. Material guide changes require a new guide version.

### Task Contract

Every task must carry enough information to make claiming, checking, reviewing, and payment auditable:

- project id
- locked guide version
- title
- description
- task type
- required output
- acceptance criteria
- required artifacts and evidence references derived from the locked project pre-submit checker policy
- difficulty
- skill tags
- estimated time when known
- locked payment policy amount
- locked payment policy currency
- locked payment policy payout type
- deadline or SLA when applicable
- source type and source reference when imported

### Human Accountability

Workstream allows agent-assisted work, but the contributor or owner is accountable for the submitted packet.

In v0.1, this is enforced through:

- assignment ownership
- contributor attestation
- immutable submission versions
- checker results bound to artifact hashes
- human review before acceptance
- reputation events tied to outcomes

An explicit owner-agent execution workspace is later work.

### Immutable Artifact Storage

Workstream stores guide material, submission artifacts, checker inputs, checker
logs, and checker outputs through the provider-neutral `ArtifactStore` port.

```text
LocalStorageAdapter          development and focused tests only
S3CompatibleArtifactStore    AWS S3 in v0.1 production
MinIO                        local and CI S3-compatible integration proof
```

AWS S3 is the only v0.1 production provider. Cloudflare R2 and Flow Node are
deferred adapter initiatives. No provider owns product identity, authorization,
lifecycle, bindings, audit, or integrity truth. PostgreSQL owns those facts;
object storage owns private immutable bytes.

Provider acknowledgement, ETag, and provider checksum metadata are not enough
to bind content. Workstream independently reads, hashes, and counts the complete
object before it becomes bindable. Production clients receive no provider
credentials, object references, signed URLs, or direct-upload authority.

v0.1 performs no physical deletion of completed artifacts. R2 and Flow Node are
separate deferred adapter initiatives and are not v0.1 runtime dependencies.

### Contribution Records

Accepted work must create a durable contribution record separate from payment status.

The contribution record is the evidence-backed certification that a contributor completed accepted work under a locked project guide. Payment records and reputation events attach to this contribution record, but do not replace it.

## Deferred

These ideas remain architecture-compatible, but they are not part of the first build:

- external origin onboarding
- webhook drop notifications to external origins
- automated source adapters
- automated task routing
- owner-agent account pairs as first-class runtime objects
- agent identity registry writes
- ERC-8183 settlement
- ERC-8004 reputation writes
- x402 micropayments
- marketplace discovery

## Canonical Names

Use these names consistently:

- `check_acceptance_criteria_present`
- `ContributionRecord`
- `SubmissionArtifactPolicy`
- `EffectiveProjectSubmissionArtifactPolicy`
- `PreSubmitCheckerPolicy`
- `PostSubmitCheckerPolicy`
- `pre_submission_checker_failed`
- `Project activation gate`
- `Task screening gate`
- `Submission quality gate`
- `contributor_claim_status`
- `reviewer_closure_status`

Revision replay contributor claim statuses:

- `fixed`
- `disputed`
- `not_applicable`

Revision replay reviewer closure statuses:

- `closed_fixed`
- `closed_rebutted`
- `partially_closed`
- `still_open`
- `obsolete`
