# WS-AUTH-001-09D-A Internal Review Evidence

Reviewed code SHA: `cc7e6cc4c12d2f378c71a9ddd65ebe8f3bed9643`

Reviewed implementation SHA: `e64b03f0baca2defd668a3cb806d04f06387bd9c`

Reviewed against trusted main:
`f18b620932bb257dc1dc355bc0504271813dc6b1`

Reviewed at: `2026-07-18T15:39:32Z`

Reviewer run IDs: `auth_xint_roles`, `auth_xint_rev_con`,
`auth_xint_art_service`

Reviewer tracks: senior engineering, QA/test, security/auth, product/ops,
architecture, migration/data integrity, CI integrity, docs, reuse/dedup, and
test delta

## Deterministic Evidence

- Migration `0026_actor_profile_lifecycle` is the sole head after trusted ART
  migration `0025`. Five exact upgrade, guard, dirty-row, downgrade, and
  re-upgrade nodes pass in 181.50 seconds on isolated PostgreSQL.
- The real signed-token lifecycle matrix covers human and fixed-service profile
  suspend, reactivate, and terminal deactivate behavior. It also covers all nine
  injected transaction failure stages with stable 503 responses and no partial
  state, audit, timestamp, or idempotency residue. It passes in 100.36 seconds.
- Ordered races identify each second PostgreSQL connection and observe
  `wait_event_type='Lock'` before releasing the first request. The exact race
  node passes in 140.69 seconds without timing sleeps establishing order.
- Actor branch coverage passes at 90.70 percent. Authorization branch coverage
  passes 110 tests at 91.78 percent, and the lifecycle service is 100 percent
  branch-covered. The later production delta changes only closed action-owner
  metadata, which is exercised by exact catalogue and migration tests.
- The exact catalogue test passes with 65 ActionIds: 15 active and 50 planned.
  Three historical migration nodes affected by the owner split pass in 199.52
  seconds, and all 30 Alembic tests collect without a stale enum error.
- The real HTTP API contract, repository-wide Ruff, stale Workstream and
  authorization scans, Markdown links, all 87 Agent Gates, merge-intent
  validation, and diff integrity pass. No workflow, dependency, threshold,
  exclusion, or skip changed.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---|---|---|
| senior engineering | PASS AFTER FIXES | none | Lifecycle state, transaction ownership, idempotency, rollback, and lock order are coherent. |
| QA/test | PASS AFTER FIXES | none | Behavior proof covers privacy, fixed-service targets, nine failure stages, database refusal branches, and observed lock waits. |
| security/auth | PASS AFTER FIXES | none | Denials conceal matched-grant internals, target disclosure follows authorization, and fresh reactivation attribution is enforced. |
| product/ops | PASS | none | Authorized administrators can manage exact profiles without admitting service callers or activating link mutations. |
| architecture | PASS AFTER FIXES | none | Central AUTH ownership, route-owned commit, and exact 09D-A/09D-B activation custody remain intact. |
| migration/data integrity | PASS AFTER FIXES | none | Upgrade and downgrade refusal matrices preserve revision, schema, rows, and evidence. |
| CI integrity | PASS AFTER FIXES | none | Historical owner selectors use both child owners and all affected database tests pass. |
| docs | PASS AFTER FIXES | none | Specification, architecture, operations, chunk state, and catalogue ownership agree. |
| reuse/dedup | PASS | none | Existing AUTH kernel, repositories, evidence, idempotency, and transaction helpers are reused. |
| test delta | PASS AFTER FIXES | none | Tests are additive and behavior-based; no assertion, threshold, or selection was weakened. |

## Findings Resolved

The first QA review found four blockers: denial evidence retained matched-grant
IDs, database guards accepted missing or stale reactivation provenance, the
fixed-service/failure matrix was incomplete, and races did not observe a real
database waiter. All four were repaired and independently re-reviewed.

Architecture/migration review then found two blockers: code-owned activation
custody still named the rejected 09D parent, and migration refusal branches were
not all exercised. Exact child owners and the complete refusal matrix were
added. Final review found four historical Alembic selectors using the removed
parent enum; they now preserve their original include/exclude semantics with
both child owners. All required tracks pass the final exact reviewed head.

Valid findings addressed: yes

Open sub-agent sessions: none

## Remaining Gate

GitHub Backend, Agent Gates, CodeRabbit, and explicit human merge approval are
external gates. `WS-AUTH-001-09D-B` remains inactive until this chunk merges,
trusted-main memory passes, and the user explicitly starts it.
