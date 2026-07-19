# Internal Review Evidence: WS-CON-001-02A

## Chunk

`WS-CON-001-02A` - Shared Transactional Outbox Persistence

Risk: L1 infrastructure, schema, concurrency, audit, and data-integrity risk.

## Baseline And Scope

Trusted main SHA: `93dd392484b397cfdfaaa833631dc2c27f591ed7`

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

AUTH-09D-B PR #152 changes no 02A code or migration. It activates exactly two
identity-link lifecycle actions and adds substantial AUTH route/test coverage.
A third full-suite attempt was stopped after one hour when that PR advanced
trusted main; its metadata was removed and it is not evidence.

A fourth local full-suite attempt on the frozen `93dd3924` baseline was stopped
after approximately 4 hours 15 minutes by human direction to keep
repository-wide suites in GitHub CI. Its metadata was removed and it is not
evidence. The active verification rule now uses bounded focused proof locally
and requires the existing GitHub Backend full-suite job on the pushed PR.

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
  key rejection, ordinary validation mapped to a detached domain error, one
  defensive deep snapshot, and stable input/persistence errors with no
  payload-bearing cause or context.
- Append reuses `canonical_json_hash`, reserves with PostgreSQL conflict
  handling, locks both identities in deterministic order, flushes only the
  caller session, and never commits or publishes.
- Exact replay preserves database occurrence time; any immutable drift or split
  event/idempotency identity raises `outbox_idempotency_conflict`.

## Current Reconciliation Verification Results

```text
40 passed, 30 deselected in 146.65s (exact bounded isolated outbox row after final review repair)
outbox coverage after final review repair: 95.15% (required: at least 90%)
78 passed in 378.36s on current main's outbox/migration, real-MinIO ART, and AUTH-09D-B suite
pre-repair outbox coverage: 95.43%
8 passed, 56 deselected in 50.92s (exact contract selector)
2 passed in 88.51s (affected AUTH lifecycle downgrade tests)
16 passed in 102.10s (isolated database runner self-tests with admin URL)
real API contract end-to-end on 0027: passed
88 passed (agent-loop gates after AUTH-09D-B)
Ruff: passed
Docstring coverage: passed at 90.9%
Markdown links: passed for 15 changed Markdown files
Workstream/AUTH/ART/REV stale-contract scans: passed after PR #152 reconciliation
merge intent and git diff --check: passed
Alembic heads: one head, 0027_shared_transactional_outbox after PR #152
repository-wide isolated PostgreSQL plus real-MinIO suite: required in GitHub CI after push
```

## Pre-Reconciliation Verification Results

These results were produced on the former `f18b620` / outbox-0026 chain. They
prove the implementation before AUTH-09D-A but are not publication evidence for
the reconciled `93dd3924` / outbox-0027 chain. Current bounded focused evidence
is recorded above; GitHub CI owns exact-head repository-wide proof after the
full PR is pushed.

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

The historical full suite used the unchanged test command, isolation rule,
assertions, and coverage thresholds. Its measured 4:55:41 runtime explains why
repository-wide proof is now CI-owned. Exact-SHA reviewer results were
superseded when AUTH-09D-A changed the backend and migration head.

## Test Delta

Tests add strict schema/privacy bounds; detached errors across constructor and
all exported Pydantic validation entry points, including hostile container
subclasses; defensive nested-payload snapshotting across the first await;
stable database error redaction; caller rollback including injected
post-reservation failure; exact replay; immutable drift; split identity;
concurrent commit/rollback races; direct-SQL custody; legal and illegal delivery
transitions; terminal archival; delete/truncate denial; exact migration surface;
and concurrent downgrade writer behavior.
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
