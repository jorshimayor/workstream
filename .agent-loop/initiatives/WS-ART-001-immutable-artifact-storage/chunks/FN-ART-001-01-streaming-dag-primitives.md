# FN-ART-001-01: Streaming DAG Primitives

Parent: `WS-ART-001` | Repository: Flow Node | Risk: L1 | SLA: P1

## Goal

Refactor existing DAG ingest/retrieval to bounded async streams without exposing
new HTTP routes.

## Allowed Files

- `back-end/node/src/modules/storage/content/{service,dag,chunking,provider}.rs`
- `back-end/scripts/run_nonempty_cargo_test_target.sh`
- focused storage tests/fixtures and internal docs

## Not Allowed

No REST exposure, auth, catalog, UI/route pruning, public announcement change,
or Workstream repository edits.

## Acceptance Criteria

- Ingest does not require complete `&[u8]`; retrieval does not return full
  `Vec<u8>` internally.
- Configurable chunk buffer remains at or below 1 MiB per transfer.
- Exact bytes pass small, chunk-boundary, multi-chunk, and tree-DAG round trips.
- Empty input, max size, cancellation, partial read/write, disk exhaustion,
  missing block, corrupt block, total-size mismatch, traversal limits, and temp
  cleanup are tested.
- Existing non-streaming callers use a bounded compatibility wrapper only inside
  Flow Node and are scheduled for removal by FN-ART-001-02.
- A dedicated `artifact_streaming_contract` integration-test target is
  non-empty; the test runner fails if target discovery reports zero tests.

## Verification

```bash
(cd back-end && cargo fmt --check)
(cd back-end && cargo clippy --all-targets --all-features -- -D warnings)
(cd back-end && ./scripts/run_nonempty_cargo_test_target.sh artifact_streaming_contract)
(cd back-end && cargo test)
git diff --check
```

Reviewers: senior engineering, QA/test, security/auth, architecture, CI
integrity, docs, reuse/dedup, test delta.

Human focus: bounded memory, cancellation safety, DAG integrity, and absence of
network exposure. Stop after this PR.
