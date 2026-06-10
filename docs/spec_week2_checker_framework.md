# Week 2 Checker Framework Specification

## Purpose

Week 2 adds the automated checker boundary between locked submissions and human review.

The checker framework protects reviewer time by proving that the latest locked submission is structurally valid, evidence-backed, policy-complete, and tied to the exact artifact hashes that were checked.

## Scope

- `CheckerRun` records
- `CheckerResult` records
- checker status and severity model
- pre-submit static checker path
- post-submit internal auto-check path
- checker registry and runner service
- project-required checker policy enforcement
- blocking versus warning calculation
- user-facing `needs_revision` routing from checker failures
- backend API access to checker runs and results
- dry-run/demo output for checker visibility
- pre-review gate enforcement for `REVIEW_PENDING`

## Non-Scope

- product frontend implementation
- reviewer queue UI
- review decision form
- human review decision records/forms for `accept`, `needs_revision`, or `reject`
- revision replay enforcement
- contribution records
- payment records
- reputation updates
- external source adapters
- blockchain, x402, escrow, or settlement rails

## Core Invariant

```text
Draft packet -> Pre-submit checks -> Submit -> Lock -> Internal CheckerRun -> CheckerResults -> REVIEW_PENDING or NEEDS_REVISION
```

A task cannot reach `REVIEW_PENDING` unless the latest locked submission has a completed checker run for the exact submission version and artifact context.

The checker binding includes:

- `task_id`
- `submission_id`
- `submission_version`
- `package_hash`
- `artifact_hash_manifest`
- locked project guide version
- locked checker policy version
- locked review policy version
- locked revision policy version
- locked payment policy version

## Two-Stage Checker Model

Workstream has two checker moments.

Pre-submit static checks run before the packet is finalized. They give immediate feedback on packet shape and obvious policy issues:

- required field presence
- package hash presence
- artifact hash manifest shape
- evidence references
- worker attestation
- storage reference safety
- task assignment and state compatibility

Pre-submit failures do not create review decisions and do not need to create durable post-submit checker runs.

Post-submit internal checks run after a submission is created and locked. These checks are the source of truth for review gating. They run from Workstream-owned services, use locked task guide and policy context, and persist durable checker runs/results.

## User-Facing Outcome Boundary

Users see the same simple outcome language everywhere:

- `accepted`
- `rejected`
- `needs_revision`

Automated checker failures may route a submitted packet to `needs_revision` when the failure is worker-fixable. This is user-facing revision, not a human review decision.

Week 2 may set a checker-caused task/submission outcome of `needs_revision`, but it does not create a human review decision record.

Internally Workstream records the source:

- `outcome = needs_revision`
- `outcome_source = auto_checker`
- `checker_run_id = <run id>`
- `review_decision_id = null`

Human reviewer revision remains:

- `outcome = needs_revision`
- `outcome_source = human_review`
- `review_decision_id = <review decision id>`

Checkers can route to `needs_revision`, but they must not create fake human review decisions.

Checkers decide:

- passing required checks can allow `REVIEW_PENDING`
- warning checks can still allow `REVIEW_PENDING` with visible context
- worker-fixable blocking failures route to `needs_revision`
- platform/infrastructure failures stay in checker/admin retry handling

Human review decisions remain only:

- `accept`
- `needs_revision`
- `reject`

Stored human review decision tokens are `accept`, `needs_revision`, and `reject`. User-facing task outcomes are displayed as Accepted, Rejected, and Needs revision. Internal lifecycle constants may use uppercase enum names, but persisted workflow values and API payloads should use canonical lowercase tokens.

## Week 2 Visibility Boundary

Checker results are exposed through backend contracts and operational output:

- checker run API responses
- checker result API responses
- task/submission API expansion where needed
- dry-run scripts
- Week 1 API demo/debug output when useful

Week 2 does not build the product frontend page for checker results. The planned React + Vite operations dashboard consumes these backend contracts later.

## Chunk Breakdown

### Chunk 6: Checker Contract And Records

Creates the durable checker run/result model, pre-submit response contract, API schemas, service boundaries, and migration.

Conditions of satisfaction:

- checker runs are tied to one submission version
- checker results are immutable after persistence
- status and severity values are canonical
- pre-submit feedback has a response contract but is not authoritative review-gate proof
- post-submit checker runs can record `allow_review`, `needs_revision`, or `operator_retry` as routing recommendations
- checker-caused `needs_revision` stores `outcome_source = auto_checker`
- checker output can be read through backend APIs

### Chunk 7: Checker Runner And Registry

Creates the checker interface, registry, pre-submit static checker path, runner service, and first structural checkers.

Detailed spec: [Chunk 7 Checker Runner And Registry](spec_chunk_7_checker_runner_registry.md).

Conditions of satisfaction:

- registered checker names cannot drift from policy names
- pre-submit checks return immediate feedback before final submission
- `check_submission_packet` runs against real submission data
- failed structural checks produce stored checker results
- broken submissions are blocked before human review

### Chunk 8: Evidence And Policy Checkers

Adds evidence, integrity, acceptance criteria, policy context, forbidden file, confidentiality, and generated-artifact checks.

Conditions of satisfaction:

- missing evidence blocks `REVIEW_PENDING`
- artifact hash mismatch blocks `REVIEW_PENDING`
- missing locked policy context blocks `REVIEW_PENDING`
- worker-visible messages do not leak sensitive internals

### Chunk 9: Pre-Review Gate

Automatically triggers internal post-submit checks after submission locking and calculates whether a checked submission moves to `REVIEW_PENDING` or user-facing `NEEDS_REVISION`.

Conditions of satisfaction:

- the gate uses the latest locked submission only
- required checker list comes from locked project checker policy
- blocking severities come from locked project checker policy
- checker-caused revision does not create a human review decision
- override requires actor, reason, and audit event

### Chunk 10: Checker Trial

Runs real sample submissions through the checker framework.

Conditions of satisfaction:

- at least one clean submission reaches `REVIEW_PENDING`
- at least one intentionally broken submission is blocked
- checker failures are documented in a failure catalog
- false-positive and missing-checker notes are recorded

## Verifier Agents

- senior engineering
- QA/test
- security/auth
- product/ops
