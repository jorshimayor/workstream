# Internal Review Evidence: WS-CI-001-01

Open sub-agent sessions: none

Valid findings addressed: yes

Reviewed code SHA: `ab75b96ba5eba3fad0f127dc1b892c3a804b2c7b`

Reviewed at: 2026-07-20T17:11:39Z

Reviewer run IDs: senior-engineering/architecture/reuse-dedup=`ci_repair_arch`; QA/test/CI-integrity/test-delta=`ci_repair_qa`; security/auth/product/ops/docs=`ci_repair_sec_ops`

## Binding

- Base: `c12ba1c8d4bbde86d0e2c19826f5791afc130489`
- Final reviewed implementation: `ab75b96ba5eba3fad0f127dc1b892c3a804b2c7b`
- Contract: `WS-CI-001-01 — Parallel Full-Suite Coverage`
- Scope: CI workflow, one shared shard tool, additive tests, operator runbook,
  initiative evidence, and exactly one merge intent; no product runtime change

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---|---|---|
| senior engineering | PASS | None | Cohesive inventory-to-fan-in trust boundary. |
| QA/test | PASS AFTER FIXES | None | Exact runtime-finished node proof replaces pre-run collection claims. |
| security/auth | PASS AFTER FIXES | None | Fixed artifacts, byte hashes, read-only permissions, safe hook path. |
| product/ops | PENDING CONFIRMATION | Stale trust bundle | This evidence-only correction discloses the hosted failure and repaired SHA. |
| architecture | PASS | None | Shared Python policy boundary; YAML only orchestrates. |
| CI integrity | PASS AFTER FIXES | None | Stable required check and unchanged 78/90 thresholds. |
| docs | PENDING CONFIRMATION | Stale trust bundle | Runbook is accurate; repaired PR evidence now requires confirmation. |
| reuse/dedup | PASS | None | Existing isolated database runner remains sole DB owner. |
| test delta | PASS AFTER FIXES | None | Additive tests; no skip, assertion, or threshold weakening. |

## Findings repaired

- Hosted run `29759523305` proved raw parameter display IDs can change across
  pytest processes. Replaced cross-process raw-node execution with validated
  whole-module execution, exact same-process collection/completion equality,
  and stable preflight test-base cardinality binding.
- Added regressions for changed UUID-like/nested parameter displays and for a
  collected node that does not complete.
- Disclosed the failed/cancelled hosted run and rebound the PR trust bundle to
  the repaired implementation SHA; hosted rerun remains pending.

- Added authenticated fan-in summary containing tree, manifest, per-shard
  duration/node/module balance, total runner seconds, and timing imbalance;
  the final check prints and uploads it through a pinned action.
- Removed one unused JSON helper and one unused workflow output.
- Replaced ambiguous CI “worker” wording with test-process terminology.

## Deterministic Evidence

```text
Ruff: passed
Python compilation: passed
shard + coverage-contract tests at repaired head: 204 passed
agent-gate tests at repaired head: 91 passed
clean-environment collection/fan-in dry run: 31 modules, 1775 nodes
shard weights: 445 / 444 / 443 / 443
real local shard diagnostic: 445 collected, 246 completed before deliberate interrupt
diagnostic database and role cleanup: verified absent
merge-intent validation: passed
loop-memory state validation: passed
Markdown links: passed for 13 changed Markdown files
stale Workstream/authorization/artifact/review scans: passed
git diff --check: passed
```

The static sensor reports `REVIEW_REQUIRED` for a large L1 CI diff and the moved
global-threshold enforcement point. This is expected review routing, not a bypass:
the final authenticated fan-in enforces the same 78 percent global floor and all
twelve 90 percent subsystem floors. Seven reviewer tracks passed; product/ops
and docs require confirmation of this evidence-only correction.

## Remaining Gate

The new GitHub matrix and actual latency/cost can only be proven on the pushed PR
head. Hosted `Backend / test`, Agent Gates, external review, and human merge
approval remain mandatory. `WS-CI-001-02` and `WS-ENG-001-04B` are inactive.
