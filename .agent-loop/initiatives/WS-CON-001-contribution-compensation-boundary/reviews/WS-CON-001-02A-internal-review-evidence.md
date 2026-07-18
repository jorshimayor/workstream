# Internal Review Evidence: WS-CON-001-02A

## Chunk

`WS-CON-001-02A` - Shared Transactional Outbox Persistence

Risk: L1 infrastructure, schema, concurrency, audit, and data-integrity risk.

## Baseline And Scope

Trusted main SHA: `f18b620932bb257dc1dc355bc0504271813dc6b1`

The implementation is limited to one linear PostgreSQL migration after
ART-owned revision 0025, the generic outbox persistence/append module, shared
metadata registration, focused tests,
initiative evidence, and exactly one merge intent. It adds no dispatcher,
delivery executor, Celery registration, broker, route, feature handler, AUTH
identifier, contribution, compensation, review, task, project, audit, or ART
behavior.

The user-owned unstaged deletion of the older contribution reference PDF is
outside the chunk and is excluded from every commit and review.

## Implemented Contract

- One immutable event envelope contains caller-provided event, aggregate,
  project, correlation, causation, idempotency, and payload facts; PostgreSQL
  forces producer and occurrence time.
- Operational delivery state is a separate closed shape prepared for a later
  migration-free 02B implementation but exposes no transition service here.
- Insert/update/delete/truncate custody prevents forged initial state, immutable
  envelope mutation, illegal transitions, evidence regression, physical
  deletion, and archival reopening.
- Terminal retention is archival-in-place. A guarded downgrade takes an
  `ACCESS EXCLUSIVE` lock and refuses durable rows.
- Payload input is strict, bounded, lower-snake-case JSON with recursive secret
  key rejection and stable non-reflective errors.
- Append reuses `canonical_json_hash`, reserves with PostgreSQL conflict
  handling, locks both identities in deterministic order, flushes only the
  caller session, and never commits or publishes.
- Exact replay preserves database occurrence time; any immutable drift or split
  event/idempotency identity raises `outbox_idempotency_conflict`.

## Verification Results

```text
33 passed in 151.73s on the ART 0025 -> CON 0026 chain
outbox coverage: 95.43% (required: at least 90%)
8 passed, 51 deselected in 125.42s (exact contract selector)
1 passed, 25 deselected in 96.33s (migration/downgrade guard)
16 passed in 180.79s (isolated database runner self-tests in a quiet window)
real API contract end-to-end: passed
1347 passed in 17741.96s / 4:55:41 (exact isolated PostgreSQL full suite)
repository coverage: 85.35% (required: at least 78%)
isolated evidence database: workstream_test_d513fb2f03b1
isolated evidence tree: f72bb6e6dc71cb38dcb397b34caf9db6f916db4c
isolated evidence Alembic head: 0026_shared_transactional_outbox
87 passed (agent-loop gates)
Ruff: passed
Docstring coverage: passed at 91.5%
Markdown links: passed for 15 changed Markdown files
Workstream stale wording: passed
AUTH stale documentation: passed
ART stale contract: passed at phase artifact_store_cutover
REV stale contract: passed
git diff --check: passed
local roadmap workbook: absent, so the one-sheet export check is not applicable
```

The full suite used the unchanged test command, isolation rule, assertions, and
coverage thresholds. Its measured 4:55:41 runtime completed under the repaired
18,000-second fail-closed safety ceiling; the earlier 12,600-second ceiling had
terminated the same clean suite at approximately 90 percent. Exact-SHA reviewer
results remain pending until this deterministic evidence is committed as the
frozen review candidate.

## Test Delta

Tests add strict schema/privacy bounds, caller rollback, exact replay, immutable
drift, split identity, concurrent commit/rollback races, direct-SQL custody,
legal and illegal delivery transitions, terminal archival, delete/truncate
denial, exact migration surface, and concurrent downgrade writer behavior.
Existing assertions, skips, coverage settings, and test commands are unchanged.

## Required Internal Review

Reviewed code SHA: pending

Reviewed at: pending

Reviewer run IDs: pending

| Reviewer | Result | Blocking findings | Notes |
|---|---|---|---|
| Senior engineering | Pending | Pending | Pending exact-SHA review |
| QA/test | Pending | Pending | Pending exact-SHA review |
| Security/auth | Pending | Pending | Pending exact-SHA review |
| Product/ops | Pending | Pending | Pending exact-SHA review |
| Architecture | Pending | Pending | Pending exact-SHA review |
| Docs | Pending | Pending | Pending exact-SHA review |
| Reuse/dedup | Pending | Pending | Pending exact-SHA review |
| Test delta | Pending | Pending | Pending exact-SHA review |
| CI integrity | Pending | Pending | Pending exact-SHA review |

## Remaining Human Gates

- Human approval is required for the specific PR before merge.
- 02B remains a separately started chunk and owns dispatcher/recovery behavior.
- `outbox.dispatch`, its fixed service identity/static row, AUTH-09E admission,
  prepared authorization, and activation remain upstream gates for 02B.
- No passing check grants a feature handler authority through dispatcher
  authority.

## Stop Condition

Stop at the CON-02A full PR human checkpoint. Do not merge without explicit
approval for that PR and do not begin `WS-CON-001-02B` automatically.
