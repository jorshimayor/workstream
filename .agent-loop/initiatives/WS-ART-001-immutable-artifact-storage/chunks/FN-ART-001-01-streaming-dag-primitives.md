# FN-ART-001-01: Streaming DAG Primitives

Parent: `WS-ART-001` | Repository: Flow Node | Risk: L1 | SLA: P1

## Goal

Refactor existing DAG ingest/retrieval to bounded async streams without exposing
new HTTP routes.

## Allowed Files

- `back-end/node/src/modules/storage/content/{service,dag,chunking,provider}.rs`
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

## Verification

```bash
cd /home/abiorh/flow/Flow-Node/back-end && cargo fmt --check
cd /home/abiorh/flow/Flow-Node/back-end && cargo clippy --all-targets --all-features -- -D warnings
cd /home/abiorh/flow/Flow-Node/back-end && cargo test modules::storage::content
cd /home/abiorh/flow/Flow-Node/back-end && cargo test
git -C /home/abiorh/flow/Flow-Node diff --check
```

Reviewers: senior engineering, QA/test, security/auth, architecture, CI
integrity, docs, reuse/dedup, test delta.

Human focus: bounded memory, cancellation safety, DAG integrity, and absence of
network exposure. Stop after this PR.

