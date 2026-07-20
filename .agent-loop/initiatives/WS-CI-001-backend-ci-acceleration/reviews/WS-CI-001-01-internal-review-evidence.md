# Internal Review Evidence: WS-CI-001-01

Open sub-agent sessions: none

Valid findings addressed: yes

Reviewed code SHA: `a6141d5b7155c178d533e718404cb04576c900d7`

Reviewed at: 2026-07-20T16:23:40Z

Reviewer run IDs: senior-engineering/architecture/reuse-dedup=`ci_impl_arch`; QA/test/CI-integrity/test-delta=`ci_impl_qa`; security/auth/product/ops/docs=`ci_impl_sec_ops`

## Binding

- Base: `c12ba1c8d4bbde86d0e2c19826f5791afc130489`
- Final reviewed implementation: `14c50b464efca95da4f57b30272e0ce7e0435c11`
- Contract: `WS-CI-001-01 — Parallel Full-Suite Coverage`
- Scope: CI workflow, one shared shard tool, additive tests, operator runbook,
  initiative evidence, and exactly one merge intent; no product runtime change

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---|---|---|
| senior engineering | PASS | None | Cohesive inventory-to-fan-in trust boundary. |
| QA/test | PASS AFTER FIXES | None | Exact runtime-finished node proof replaces pre-run collection claims. |
| security/auth | PASS AFTER FIXES | None | Fixed artifacts, byte hashes, read-only permissions, safe hook path. |
| product/ops | PASS AFTER FIXES | None | Authenticated timing/cost evidence now reaches operators. |
| architecture | PASS | None | Shared Python policy boundary; YAML only orchestrates. |
| CI integrity | PASS AFTER FIXES | None | Stable required check and unchanged 78/90 thresholds. |
| docs | PASS AFTER FIXES | None | Runbook matches timing report and completed-node semantics. |
| reuse/dedup | PASS | None | Existing isolated database runner remains sole DB owner. |
| test delta | PASS AFTER FIXES | None | Additive tests; no skip, assertion, or threshold weakening. |

## Findings repaired

- Replaced shard metadata derived from a second collection with exact manifest
  node argv and a repository-owned pytest hook recording each node after its
  actual runtime lifecycle finishes. A successful shard requires the completed
  set to equal the canonical manifest exactly once.
- Added a regression proving a collected-but-not-executed node fails.
- Added authenticated fan-in summary containing tree, manifest, per-shard
  duration/node/module balance, total runner seconds, and timing imbalance;
  the final check prints and uploads it through a pinned action.
- Removed one unused JSON helper and one unused workflow output.
- Replaced ambiguous CI “worker” wording with test-process terminology.

## Deterministic Evidence

```text
Ruff: passed
Python compilation: passed
planner + agent-gate + coverage-contract tests: 294 passed
isolated-runner + coverage-contract tests: 188 passed
clean-environment real collection/fan-in dry run: 31 modules, 1774 nodes
shard weights: 443 / 444 / 443 / 444
merge-intent validation: passed
loop-memory state validation: passed
Markdown links: passed for 11 changed Markdown files
stale Workstream/authorization/artifact/review scans: passed
git diff --check: passed
```

The static sensor reports `REVIEW_REQUIRED` for a large L1 CI diff and the moved
global-threshold enforcement point. This is expected review routing, not a bypass:
the final authenticated fan-in enforces the same 78 percent global floor and all
twelve 90 percent subsystem floors, and all nine reviewer tracks passed.

## Remaining Gate

The new GitHub matrix and actual latency/cost can only be proven on the pushed PR
head. Hosted `Backend / test`, Agent Gates, external review, and human merge
approval remain mandatory. `WS-CI-001-02` and `WS-ENG-001-04B` are inactive.
