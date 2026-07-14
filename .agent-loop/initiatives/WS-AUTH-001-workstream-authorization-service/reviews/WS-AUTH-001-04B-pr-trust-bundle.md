# PR Trust Bundle: WS-AUTH-001-04B

## Chunk

`WS-AUTH-001-04B` - PostgreSQL Rate Controls

## Goal

Provide privacy-keyed, cross-replica PostgreSQL rate controls for future first
access and authority mutations without attaching them to production routes.

## What Changed

- Added atomic database-time fixed-window counters with durable denial,
  saturation safety, and bounded lock-safe pruning.
- Added HMAC-keyed server dependencies for `first_access` and
  `admin_mutation`; both remain unattached.
- Added migration `0017_api_controls` with guarded downgrade custody.
- Added non-retaining secret configuration across constructor, environment,
  layered dotenv, and Pydantic's public model-validation methods.
- Clarified that artifact production I/O requires central AUTH permissions,
  service principals, and exact resource authorization before adapter work.

## Design

Each consume owns a short independent committed session. One PostgreSQL upsert
uses one `statement_timestamp()` CTE to insert, reset, increment, saturate, and
return authoritative window state. HMAC framing stores only scope and a 32-byte
digest. The server key is private `SecretStr` state assigned only after
successful Pydantic validation; Pydantic receives no recoverable key object.

## Scope Control

The production delta is 480 non-comment lines, below the 500-line hard stop.
No route consumer, actor/grant behavior, product authority, artifact runtime,
AUTH-05 implementation, Redis counter, or in-memory cross-replica state was
added.

## Behavior Proof

Tests cover exact limits, repeated denial, expiry, database-clock retry values,
concurrency, cross-session durability, downstream rollback, saturation,
pruning, unavailable database phases, cancellation, privacy-safe persistence,
schema constraints, migration races, and representative artifact preservation.
Secret tests traverse structured error objects and complete exception graphs
and instrument the BaseSettings boundary directly.

## Tests And Checks

- 77 focused isolated PostgreSQL tests passed at 97 percent changed-subsystem
  statement coverage.
- 59 final configuration/object-graph tests passed.
- Exact AUTH-04B migration and real API E2E passed.
- Ruff, docstring threshold, stale scans, links, loop memory, 36 Agent Gates,
  additive test delta, and diff hygiene passed.
- GitHub Backend must provide the unchanged repository-wide 78 percent floor;
  the interrupted local global run is not evidence.

## Reviewer Results

Senior engineering, QA/test, security/auth, privacy/data, product/ops,
architecture, CI integrity, docs, reuse/dedup, and test-delta tracks pass final
SHA `922778b`. Reviewed production SHA is `67484b5`; the final delta is additive
tests and review memory only.

## External Review

GitHub Backend, Agent Gates, CodeRabbit, and explicit human review begin after
ready PR publication. None replaces the completed internal review.

## Remaining Risks

- The dependencies are intentionally unattached; later owning chunks must add
  route-specific permissions and consumer tests.
- Secret rotation resets effective counters and requires the documented
  cross-replica quiescence procedure.
- The global suite and 78 percent repository floor remain GitHub-owned because
  the local run was interrupted by host shutdown.

## Human Review Focus

Inspect transaction custody, HMAC framing/privacy, database-time math, pruning
lock order, migration downgrade refusal, secret object-graph non-retention, and
the fact that no production route consumes either dependency.

## Human Merge Ownership

Only the user may approve and merge this PR. Publication is not merge approval,
and AUTH-05 does not start automatically.
