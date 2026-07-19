# Internal Review Evidence: WS-CON-001-02A

## Chunk

`WS-CON-001-02A` - Shared Transactional Outbox Persistence

Risk: L1 infrastructure, schema, concurrency, audit, and data-integrity risk.

## Baseline And Scope

Trusted main SHA: `1b5422fcaa361152af7c2b1f82a763d99c0e6db5`

The implementation is limited to one linear PostgreSQL migration after
AUTH-owned revision 0026, the generic outbox persistence/append module, shared
metadata registration, focused tests,
initiative evidence, and exactly one merge intent. It adds no dispatcher,
delivery executor, Celery registration, broker, route, feature handler, AUTH
identifier, contribution, compensation, review, task, project, audit, or ART
behavior.

The user-owned unstaged deletion of the older contribution reference PDF is
outside the chunk and is excluded from every commit and review.

REV PLAN2 PR #150 is planning/specification-only. It preserves the exact 02A
runtime and migration while refreshing future CON/REV gate names. The first
post-AUTH full-suite attempt was stopped after two hours when that PR advanced
trusted main; its metadata was removed and it is not evidence.

ART-02B1 PR #151 changes no 02A code or migration, but it adds locked S3 SDK
dependencies, a real MinIO CI service, and substantial backend tests. A second
full-suite attempt was stopped after 3 hours 7 minutes when that PR advanced
trusted main; its metadata was removed and it is not evidence.

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

## Current Reconciliation Verification Results

```text
76 passed in 243.28s on current main's outbox/migration plus real-MinIO ART suite
outbox coverage: 95.43% (required: at least 90%)
8 passed, 56 deselected in 50.92s (exact contract selector)
2 passed in 88.51s (affected AUTH lifecycle downgrade tests)
16 passed in 102.10s (isolated database runner self-tests with admin URL)
real API contract end-to-end on 0027: passed
88 passed (agent-loop gates after ART-02B1)
Ruff: passed
Docstring coverage: passed at 90.9%
Markdown links: passed for 15 changed Markdown files
Workstream/AUTH/ART/REV stale-contract scans: passed after PR #151 reconciliation
merge intent and git diff --check: passed
Alembic heads: one head, 0027_shared_transactional_outbox after PR #151
full-suite fail-closed ceiling: 25,200s; tests/isolation/coverage unchanged
repository-wide isolated PostgreSQL plus real-MinIO suite: pending on frozen `1b5422fc` SHA
```

## Pre-Reconciliation Verification Results

These results were produced on the former `f18b620` / outbox-0026 chain. They
prove the implementation before AUTH-09D-A but are not publication evidence for
the reconciled `1b5422fc` / outbox-0027 chain. Current focused evidence is
recorded above; the exact full suite must rerun before reviewer fanout.

```text
33 passed in 151.73s on the former ART 0025 -> CON 0026 chain
outbox coverage: 95.43% (required: at least 90%)
8 passed, 51 deselected in 125.42s (exact contract selector)
1 passed, 25 deselected in 96.33s (migration/downgrade guard)
16 passed in 180.79s (isolated database runner self-tests in a quiet window)
real API contract end-to-end: passed
1347 passed in 17741.96s / 4:55:41 (exact isolated PostgreSQL full suite)
repository coverage: 85.35% (required: at least 78%)
isolated evidence database: workstream_test_d513fb2f03b1
isolated evidence tree: f72bb6e6dc71cb38dcb397b34caf9db6f916db4c
isolated evidence Alembic head: 0026_shared_transactional_outbox (superseded)
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
results were superseded when AUTH-09D-A changed the backend and migration head.

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
