# Week 2 Checker Framework Specification

## Purpose

Week 2 adds the automated checker boundary between locked submissions and human review.

The checker framework protects reviewer time by proving that the latest locked submission is structurally valid, evidence-backed, policy-complete, and tied to the exact artifact hashes that were checked.

## Scope

- `CheckerRun` records
- `CheckerResult` records
- checker status and severity model
- checker registry and runner service
- project-required checker policy enforcement
- blocking versus warning calculation
- backend API access to checker runs and results
- dry-run/demo output for checker visibility
- pre-review gate enforcement for `REVIEW_PENDING`

## Non-Scope

- product frontend implementation
- reviewer queue UI
- review decision form
- accept, needs_revision, or reject decisions
- revision replay enforcement
- contribution records
- payment records
- reputation updates
- external source adapters
- blockchain, x402, escrow, or settlement rails

## Core Invariant

```text
Submission -> Lock -> CheckerRun -> CheckerResults -> Gate -> REVIEW_PENDING or checker-blocked
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

## Checker Decision Boundary

Checkers do not accept, reject, or request revision.

Checkers only decide whether a submission is allowed to enter human review:

- passing required checks can allow `REVIEW_PENDING`
- warning checks remain visible but do not block by default
- blocking failures prevent `REVIEW_PENDING`

Human review decisions remain only:

- `accept`
- `needs_revision`
- `reject`

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

Creates the durable checker run/result model, API schemas, service boundaries, and migration.

Conditions of satisfaction:

- checker runs are tied to one submission version
- checker results are immutable after persistence
- status and severity values are canonical
- checker output can be read through backend APIs

### Chunk 7: Checker Runner And Registry

Creates the checker interface, registry, runner service, and first structural checkers.

Conditions of satisfaction:

- registered checker names cannot drift from policy names
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

Calculates whether a checked submission can move to `REVIEW_PENDING`.

Conditions of satisfaction:

- the gate uses the latest locked submission only
- required checker list comes from locked project checker policy
- blocking severities come from locked project checker policy
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
