# WS-CI-001-01 PR Trust Bundle

## Goal

Reduce Backend CI wall-clock time by running the complete test inventory in four
isolated jobs, then authenticate and combine all evidence before the unchanged
required coverage gates pass.

## Design

- Preflight discovers every canonical test module and collected pytest node.
- Deterministic file-level bin packing keeps modules intact across four shards.
- Every shard validates the checked-out tree, uses its own PostgreSQL database
  and MinIO instance, executes exact manifest node IDs, and records nodes only
  after their runtime lifecycle finishes.
- Fixed bundles bind tree SHA, manifest digest, exact completed nodes, coverage
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

- 294 focused planner/agent-gate/coverage-contract tests pass.
- 188 isolated-runner/coverage-contract tests pass against local PostgreSQL.
- Clean installed environment discovers 31 modules and 1,774 nodes and validates
  complete four-shard fan-in at weights 443/444/443/444.
- Ruff, compilation, merge-intent, loop-state, stale scans, Markdown links, and
  diff integrity pass.
- Actions are SHA-pinned; PostgreSQL and MinIO are digest-pinned.
- Workflow permissions are read-only and checkout credentials are not persisted.

## Internal Review

Implementation SHA `14c50b464efca95da4f57b30272e0ce7e0435c11` and final evidence head
`a6141d5b7155c178d533e718404cb04576c900d7` pass senior engineering, QA/test,
security/auth, product/ops, architecture, CI integrity, docs, reuse/dedup, and
test-delta review after all valid findings were repaired.

## Remaining Risk

Collected-node counts may not predict runtime for migration-heavy modules.
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
