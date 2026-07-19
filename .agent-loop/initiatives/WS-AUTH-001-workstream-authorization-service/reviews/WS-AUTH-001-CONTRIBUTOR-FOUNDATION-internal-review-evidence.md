# WS-AUTH-001-CONTRIBUTOR-FOUNDATION Internal Review Evidence

Reviewed code SHA: `b48aa3dd8ba5ddc74b89524169a7df0a52a3fb27`

Reviewed implementation SHA: `4d1fc507c343d483677a332c2a91885e32571693`

Reviewed against trusted main:
`93dd392484b397cfdfaaa833631dc2c27f591ed7`

Reviewed at: `2026-07-19T07:14:31Z`

Reviewer run IDs: `auth_xint_roles`, `auth_xint_art_service`

Reviewer tracks: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, and test delta

## Deterministic Evidence

- The repaired contributor migration matrix passed two real PostgreSQL tests in
  102.35 seconds. It proves upgrade/downgrade/upgrade preservation, atomic
  refusal, secret-safe bounded diagnostics, exact trigger arguments and
  SQLSTATEs, nullable delegation, both-table INSERT/UPDATE parity, historical
  human lineage, one Alembic head, and dependency-safe downgrade refusal.
- All 12 named PostgreSQL lifecycle/task interleavings passed in 636.24 seconds
  with observed `pg_stat_activity` lock waits. Lifecycle-first denial preserves
  every task-owned surface and calls neither checker nor enqueue; task-write-first
  commits canonical contributor attribution and calls each exactly once before
  the later lifecycle mutation.
- Actor/task unit and focused database behavior tests passed. The repaired
  canonical API-error test passed in 63.79 seconds, and the real HTTP API
  contract drill passed with canonical `contributor_id` claim/submission output.
- The eight Alembic tests implicated by the first Backend run passed in their CI
  order on one isolated PostgreSQL database in 959.71 seconds. The three root
  lifecycle tests also passed independently in 339.89 seconds. Lifecycle tests
  now target their owned `0026` revision; general-head and dedicated `0027`
  contributor-foundation coverage remain unchanged.
- Ruff, 90.3 percent repository docstring coverage, both stale-wording scans,
  Markdown links, diff integrity, one Alembic head, and all 88 agent gates pass.
- No skip, xfail, assertion weakening, test deletion, coverage exclusion,
  threshold reduction, action/permission/grant change, or compatibility field
  was introduced.
- GitHub Backend is the mandatory pre-merge proof for the unchanged 78 percent
  repository-wide floor and the persistent 90 percent actor, authorization,
  and task subsystem reports. Internal evidence does not claim those aggregate
  reports before CI produces them.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---|---|---|
| senior engineering | PASS AFTER FIXES | none | Clean field cutover, transaction ownership, lock order, and chunk boundary are maintainable. |
| QA/test | PASS AFTER FIXES | none | Migration, API, rollback, preservation, and all 12 observed races cover the declared behavior. |
| security/auth | PASS AFTER FIXES | none | Malformed diagnostics are redacted; lineage and active-identity checks fail closed without a second authorization path. |
| product/ops | PASS AFTER FIXES | none | Human attribution is Contributor-safe; later legacy role/attestation cleanup remains separately owned. |
| architecture | PASS | none | Actor-owned revalidation and database lineage add no action, grant, evaluator, or availability path. |
| CI integrity | PASS AFTER FIXES | none | The 90 percent task report is additive; all existing thresholds remain mandatory. |
| docs | PASS AFTER FIXES | none | Current docs name the exact reusable function, triggers, foreign keys, indexes, remediation, and later boundaries. |
| reuse/dedup | PASS | none | Existing ActorRepository and TaskRepository transaction participants are reused. |
| test delta | PASS AFTER FIXES | none | Assertions were strengthened for privacy, exact SQL branches, invocation counts, and races. |

## Findings Resolved

Valid findings addressed: yes

Open sub-agent sessions: none

Initial candidate `e41c33c0` failed because malformed legacy values could be
serialized into deployment diagnostics, the direct-SQL matrix omitted closed
trigger branches, lifecycle-first races did not count transient checker/enqueue
calls, current docs omitted exact reusable object names and contained two stale
human terms, and aggregate coverage language was overstated. Candidate
`4d1fc507` redacts before serialization, bounds and tests realistic canaries,
closes the SQL and invocation matrices, corrects the docs, and records Backend
coverage as a mandatory external pre-merge gate. Fresh exact-SHA implementation
review passed all nine tracks with no remaining findings. A final exact-head
confirmation passed the same tracks on `4db178147`, whose only additional
committed delta synchronizes lifecycle state and strict agent-gate assertions.
The first GitHub Backend run then exposed five stale uses of `head` in tests
whose assertions explicitly owned revision `0026`; PostgreSQL correctly rolled
back the full `0027` to `0025` downgrade transaction when the `0026` evidence
guard refused, so the asserted revision remained `0027`. Test-only repair
`b48aa3dd` scopes those tests to `0026`. Fresh exact-SHA senior, QA/test,
security/auth, product/ops, architecture, CI-integrity, docs, reuse/dedup, and
test-delta review passed with no findings and confirmed that `0027` behavior is
still covered by full-head and contributor-foundation tests.

## Remaining Risk And Gate

External GitHub Backend, Agent Gates, CodeRabbit, and explicit human review
remain. Backend must pass the unchanged global 78 percent floor and every
persistent 90 percent subsystem report before merge. This chunk activates no
authorization action or service caller. `WS-AUTH-001-09E` remains inactive
until this PR merges, signed memory passes, and the user explicitly starts it.
