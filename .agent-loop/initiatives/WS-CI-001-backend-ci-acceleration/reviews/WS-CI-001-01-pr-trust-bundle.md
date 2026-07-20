# WS-CI-001-01 PR Trust Bundle

## Goal

Reduce Backend CI wall-clock time by running the complete test inventory in four
isolated jobs, then authenticate and combine all evidence before the unchanged
required coverage gates pass.

## Design

- Preflight discovers every canonical test module and stable test-base cardinality.
- Deterministic file-level bin packing keeps modules intact across four shards.
- Every shard validates the checked-out tree, uses its own PostgreSQL database
  and MinIO instance, executes whole assigned modules, and proves exact
  same-process runtime collection/completion equality against the preflight
  cardinality signature.
- Fixed bundles bind tree SHA, manifest digest, exact collected/completed nodes, coverage
  bytes, shard identity, and non-secret duration metadata.
- Final `Backend / test` runs with `if: always()`, rejects every upstream or
  artifact inconsistency, combines coverage, and enforces 78 percent global plus
  twelve 90 percent subsystem floors.
- API contract E2E runs concurrently in its own isolated database.

## Scope Control

No backend application code, schema, migration, dependency, existing test
behavior, assertion, skip, coverage floor, authentication, authorization,
artifact product behavior, payment, review, approval, or merge authority changed.
No path-based workflow suppression was added.

## Evidence

- At repaired implementation SHA `ab75b96ba5eba3fad0f127dc1b892c3a804b2c7b`,
  204 shard/coverage-contract tests and 91 agent-gate tests pass; Ruff,
  compilation, loop-state, stale scans, Markdown links, and diff integrity pass.
- The repaired clean-environment dry run discovers 31 modules and 1,775 nodes
  and validates complete four-shard fan-in at weights 445/444/443/443.
- A real local shard proved 445 same-process nodes were collected and whole
  module paths—not preflight parameter IDs—reached pytest. It was intentionally
  interrupted after 246 completions because runtime was no longer a
  proportionate local check; its exact owned database and role were removed and
  verified absent. This is diagnostic evidence, not a passing full-shard claim.
- Earlier unchanged isolated-runner/coverage-contract proof passed 188 tests
  against local PostgreSQL before the hosted repair.
- Ruff, compilation, merge-intent, loop-state, stale scans, Markdown links, and
  diff integrity pass.
- Actions are SHA-pinned; PostgreSQL and MinIO are digest-pinned.
- Workflow permissions are read-only and checkout credentials are not persisted.

## Internal Review

Repaired implementation SHA `ab75b96ba5eba3fad0f127dc1b892c3a804b2c7b`
passes senior engineering, QA/test, security/auth, architecture, CI integrity,
reuse/dedup, and test-delta review. Product/ops and docs identified this stale
trust bundle as blocking; this evidence-only correction records their finding
and requires exact-head confirmation before push.

## Hosted Failure and Repair

GitHub Actions run `29759523305` reached green preflight and API E2E, then shard
jobs failed because import-time UUID parameter display values changed between
the preflight and shard pytest processes. The invalid run was cancelled after
root cause confirmation to avoid wasting runner minutes. It is not success
evidence.

The repair no longer executes raw cross-process node IDs. It executes validated
whole modules, proves exact final collection equals exact completion inside the
same pytest process, and binds stable test-base cardinalities to preflight. A
new hosted run has not started yet; exact-head hosted success and timing remain
mandatory before human merge approval.

## Remaining Risk

Collected-node counts may not predict runtime for migration-heavy modules; the
partial local shard reinforced that risk without proving hosted wall time.
Hosted execution must show actual per-shard durations, wall-clock improvement,
and aggregate runner cost. The workflow fails closed rather than silently falling
back if sharding is unstable.

## Human Review Focus

Exact runtime-node evidence, action/plugin provenance, database/MinIO isolation,
fixed artifact set and byte hashes, cancellation propagation, coverage combine,
unchanged thresholds, stable `Backend / test`, and latency-versus-runner-cost.

## Human Merge Ownership

Only the human may approve and merge the PR after hosted exact-head evidence.
`WS-CI-001-02` and `WS-ENG-001-04B` remain inactive.
