# WS-AUTH-001-09A Internal Review Evidence

Reviewed code SHA: `beab5d9149a04c5ab0f8f4ce226b1b61ce24190a`
Reviewed implementation SHA: `beab5d9149a04c5ab0f8f4ce226b1b61ce24190a`
Reviewed at: `2026-07-16T14:27:18Z`
Reviewer run IDs: auth09_contract_senior, auth09_contract_qa,
auth09_contract_security
Reviewer tracks: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, and test delta

## Deterministic Evidence

- The repaired actor, auth, authorization, audit, API-control, and complete
  Alembic suite passed 379 tests against fresh isolated PostgreSQL at migration
  head `0023_service_actor_identity`.
- Forty-seven focused confidential mapping, canonical-input, and linked-
  worktree custody tests passed after the full suite.
- Branch-aware package coverage passes at 90.55 percent for actors and 91.50
  percent for authorization. The new mapping module is 95.91 percent.
- Direct PostgreSQL behavior proves exact legacy mapping, actor identity
  constraints, immutable migration evidence, all eight downgrade action guards,
  clean downgrade, and re-upgrade.
- The static matrix rejects identity-row swaps and any PermissionId, owner, or
  availability drift. All eleven artifact actions and all eight AUTH-09 route
  actions remain planned and inert.
- Strict canonical JSON, owner-only regular files, database/checksum binding,
  shared CLI/Alembic path custody, redacted failures, and no-Git deployment
  behavior pass adversarial tests.
- External-review repair tests prove revision `0023` imports only its packaged
  frozen contract, current v1 envelopes remain compatible, installed-wheel
  location cannot weaken custody, and async engine cleanup stays on one loop
  without masking an earlier bounded failure. Fifty-two focused tests, one
  mapped isolated migration test, and an actual wheel-import custody drill pass.
- Ruff, merge-intent validation, stale Workstream/authorization/artifact scans,
  Markdown links, 71 agent-gate tests, 92.1 percent docstring coverage, and diff
  integrity pass.
- No workflow, dependency, skip, exclusion, or coverage threshold was changed.
  Package discovery adds only the frozen `migration_contracts` package; the
  built wheel contains its two expected files. GitHub Backend remains
  authoritative for the repository-wide 78 percent floor.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---|---|---|
| senior engineering | PASS AFTER FIXES | none | Strict custody, exact matrix validation, and immutable migration evidence are coherent and reviewable. |
| QA/test | PASS AFTER FIXES | none | Behavior tests cover row swaps, metadata drift, canonical bytes, path custody, and SQL tampering. |
| security/auth | PASS AFTER FIXES | none | Local service identity remains separate from the external credential link; no authority path activates. |
| product/ops | PASS | none | Internal services never become Contributors or receive human grants. |
| architecture | PASS | none | ActorProfile owns stable identity and AUTH owns one static matrix without assignment rows. |
| CI integrity | PASS | none | CI, dependencies, thresholds, skips, and exclusions are unchanged. |
| docs | PASS | none | Specification, runbook, migration custody, and stop paths match runtime behavior. |
| reuse/dedup | PASS | none | One shared path guard serves CLI and Alembic; one static matrix remains authoritative. |
| test delta | PASS AFTER FIXES | none | Additive adversarial tests assert failure and unchanged-state behavior rather than coverage-only execution. |

## Findings Resolved

The repair now validates each exact service-to-action row plus PermissionId,
ActionOwner, and planned availability. Mapping drafts and envelopes reject
coerced schema versions and any bytes outside compact key-sorted canonical JSON
with one newline. One shared absolute-path guard excludes the main checkout,
every linked worktree, and Git metadata in both the CLI and migration while
supporting deployments without Git metadata. Retained migration evidence has
exact count/digest/database-binding constraints and rejects update, delete, or
truncate.

CodeRabbit's valid findings are also repaired. Historical revision `0023` no
longer imports mutable actor helpers; it receives explicit repository custody
while using a packaged frozen contract. The operator CLI executes and disposes
its async engine on one event loop, preserves an existing bounded error across
cleanup cancellation, and reports cleanup failure only after successful work.

Valid findings addressed: yes

Open sub-agent sessions: none

## Remaining Risk And Gate

Direct `O_EXCL` envelope publication is fail-closed but does not fsync the
parent directory. A host crash may require regenerating the private envelope;
partial, missing, or unverifiable evidence cannot pass migration or activate
authority. This is a nonblocking operational recovery risk.

Refreshed GitHub Backend, Agent Gates, CodeRabbit, and explicit human merge
approval remain. Do not start `WS-AUTH-001-09B` automatically.
