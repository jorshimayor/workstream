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

- Added one linear `0026_shared_transactional_outbox` migration after the
  ART-owned `0025_artifact_store_v2` revision.
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

- Exact contract selector: 8 passed, 47 deselected.
- Complete outbox suite: 33 passed with 95.43% focused coverage.
- Migration/downgrade guard: 1 passed, 21 deselected.
- Isolated database runner self-tests: 16 passed with the required admin URL.
- Real API contract end-to-end: passed.
- Agent-loop gates: 80 passed.
- Ruff, 91.5% docstring coverage, Markdown links, stale Workstream/AUTH/ART
  scans, and diff hygiene pass.
- Repository-wide isolated PostgreSQL result and exact-SHA internal reviewer
  results will be frozen before publication.

## Test And CI Integrity

No existing test was deleted, skipped, weakened, or rewritten to accept broken
behavior. No workflow, dependency, package script, test runner, lint/typecheck
command, coverage threshold, or CI configuration changed.

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
