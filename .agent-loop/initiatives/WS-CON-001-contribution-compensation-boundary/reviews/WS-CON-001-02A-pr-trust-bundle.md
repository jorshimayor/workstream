# PR Trust Bundle: WS-CON-001-02A

## Goal

Land feature-neutral shared PostgreSQL outbox truth and a caller-transaction
append participant, with enough persistence shape for 02B to add dispatcher
mechanics without another migration.

Risk: L1 infrastructure/data boundary; SLA P1.

## Human-Approved Intent

The human explicitly started 02A after CON-01 merged. This chunk must remain
generic and authorization-neutral: AUTH owns every action, permission,
evaluator, service admission, and activation decision, while 02B and later
feature chunks own execution behavior.

## What Changed

- Added one linear `0027_shared_transactional_outbox` migration after the
  AUTH-owned `0026_actor_profile_lifecycle` revision.
- Added the generic outbox model, strict append schemas, reservation repository,
  and flush-only service.
- Registered the model in shared SQLAlchemy metadata.
- Added PostgreSQL migration, concurrency, replay, privacy, custody, rollback,
  and state-shape tests.
- Updated the WS-CON chunk ledger and added exactly one schema-v2 merge intent
  naming 02B with a separate explicit start.

## Design And Boundary

- Immutable event truth and mutable operational delivery state are separate.
- PostgreSQL, not the caller, owns producer, occurrence time, initial state,
  counters, and initial eligibility time.
- Event ID and global idempotency key are independent identities; exact replay
  requires every immutable fact to match.
- The repository inserts with conflict suppression, locks matching identities
  deterministically, and uses only the supplied `AsyncSession`.
- The service reuses the existing repository-wide `app.core.hashing` canonical
  JSON helper and emits only stable error codes.
- Retention is one-way terminal archival; event truth cannot be deleted or
  truncated.
- No route, dispatcher, delivery executor, broker, Celery task, handler,
  authorization identifier, or product-domain mutation is present.

## Alternatives Rejected

- A new canonicalizer or generic idempotency framework.
- An outbox-owned session, commit, enqueue, publish, or post-commit repair.
- Event identity inferred only from the idempotency key.
- Mutable payload/envelope facts or physical retention deletion.
- A schema too small for 02B that would force a second delivery-state migration.
- Dispatcher authority inherited by protected feature handlers.

## Proof

- Reconciled exact contract selector: 8 passed, 56 deselected.
- Current-main outbox plus migration/lifecycle-guard suite: 36 passed in
  156.17 seconds; the reconciled outbox implementation retains 95.43% focused
  coverage.
- After ART-02B1 merged, the combined outbox/migration plus real-MinIO S3
  focused suite passed 76 tests in 243.28 seconds on the current tree.
- Affected AUTH lifecycle downgrade tests: 2 passed, including atomic rollback
  to the full `0027` head when AUTH refuses `0026 -> 0025`.
- Alembic reports exactly one head: `0027_shared_transactional_outbox`.
- Isolated database runner self-tests: 16 passed in 102.10 seconds with the
  required admin URL.
- Real API contract end-to-end on the `0027` chain: passed.
- Pre-reconciliation exact isolated PostgreSQL full suite: 1347 passed in 17741.96 seconds
  (4:55:41), with 85.35% repository coverage against the 78% floor.
- The pre-reconciliation isolated evidence records tree `f72bb6e`, database
  `workstream_test_d513fb2f03b1`, and the superseded Alembic head
  `0026_shared_transactional_outbox`; exact `0027` evidence must replace it
  before publication.
- Agent-loop gates: 88 passed after ART-02B1.
- Ruff, 90.9% docstring coverage, Markdown links, stale Workstream/AUTH/ART/REV
  scans, and diff hygiene pass.
- AUTH-09D-A reconciliation moved the migration to `0027`; the focused evidence
  above is current, while full-suite evidence and exact-SHA internal reviewer
  results must rerun before publication.
- REV PLAN2 PR #150 then advanced trusted main to `983b9e53`. It changes only
  planning/specification files, preserves the 02A runtime boundary, and updates
  future CON/REV child gates. A two-hour suite on the prior head was stopped,
  discarded, and is not counted; exact-head full-suite evidence remains
  pending.
- ART-02B1 PR #151 then advanced trusted main to `1b5422fc`. It adds the real
  S3-compatible adapter, MinIO service, SDK pins, CI gates, and a substantial
  backend test delta without changing 02A code or migration. The 3-hour
  7-minute run on the prior tree was stopped and discarded; exact-head
  PostgreSQL plus real-MinIO evidence remains pending.

## Test And CI Integrity

No existing test was deleted, skipped, weakened, or rewritten to accept broken
behavior. No workflow, dependency, package script, test runner, lint/typecheck
command, coverage threshold, or CI configuration changed.

The measured full-suite runtime completed under an 18,000-second fail-closed
safety ceiling. The prior 12,600-second ceiling stopped the same clean command
at approximately 90 percent; extending only the ceiling preserved every test,
assertion, isolation control, and coverage requirement.

For the reconciled AUTH-09D-A baseline, the ceiling is 25,200 seconds because
that prior run consumed 17,741.96 of 18,000 seconds and main added substantial
backend/migration coverage. Tests, assertions, isolation, and the 78/90
coverage thresholds remain unchanged.

## Human Review Focus

1. Is the immutable/operational schema complete for migration-free 02B without
   implementing dispatcher behavior early?
2. Do global idempotency and event-ID collisions fail closed under concurrent
   commit and rollback orders?
3. Are payload bounds and secret-key rejection sufficient for a generic event
   envelope?
4. Do database custody, archival, and guarded downgrade preserve durable event
   truth?
5. Does append remain entirely inside the caller-owned transaction with no AUTH
   or product-domain boundary expansion?

## Follow-Up And Ownership

The same-initiative successor is `WS-CON-001-02B`, Shared Outbox Dispatcher And
Recovery. It requires a separate explicit start after this PR merges and after
its AUTH/service prerequisites refresh from trusted main.

Only the human owner may approve and merge the specific 02A PR. Passing
reviewers, CI, or CodeRabbit do not authorize merge or the next chunk.
