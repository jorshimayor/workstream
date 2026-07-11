# FN-ART-001-02: Authenticated Artifact HTTP Contract

Parent: `WS-ART-001` | Repository: Flow Node | Risk: L1 | SLA: P0

## Goal

Expose authenticated idempotent private ingest/retrieve/status routes using the
versioned Workstream provider contract.

## Allowed Files

- focused REST routes/DTOs/app state/bootstrap/auth/config
- artifact catalog/idempotency migrations and tests
- copied `contracts/artifact-store/version_1/**` with source digest
- focused API/security docs

## Not Allowed

No unauthenticated byte route, human token acceptance, recursive retain/verify,
semantic search, public announcement, or Workstream lifecycle state.

## Acceptance Criteria

- First byte route enforces pinned issuer/algorithm, audience `flow-node`,
  service subject, time/jti, endpoint scopes, TLS production gate, and redaction.
- Local test issuer works only in explicit development mode.
- Ingest is streaming, atomic, private, and idempotent; key scope includes
  service subject, operation, provider-neutral request reference, and byte
  commitment. Same request replays; mismatch returns 409.
- Artifact routes remove the temporary non-streaming compatibility wrapper
  introduced by FN-ART-001-01; no exposed route buffers a complete artifact.
- The `core_ingest_retrieve_status` subset of the copied Workstream contract
  vectors covers responses, limits, errors, malformed receipts, auth matrix,
  disconnect/cancellation, exact-byte retrieval, altered receipt/object
  recovery, exact replay, idempotency mismatch, and truncated recovery streams.
- REST uses the shared real block store; metadata-only `ContentService` is not
  used by artifact routes.
- The additive catalog/idempotency migration preserves existing blocks, does
  not promote legacy published/discovered metadata to verified artifacts,
  refuses a non-empty production downgrade, and passes empty-fixture
  downgrade/re-upgrade tests.
- A dedicated `artifact_http_contract` integration-test target is non-empty;
  the test runner fails if target discovery reports zero tests.

## Verification

```bash
cd /home/abiorh/flow/Flow-Node/back-end && cargo fmt --check
cd /home/abiorh/flow/Flow-Node/back-end && cargo clippy --all-targets --all-features -- -D warnings
cd /home/abiorh/flow/Flow-Node/back-end && ./scripts/run_nonempty_cargo_test_target.sh artifact_http_contract
cd /home/abiorh/flow/Flow-Node/back-end && cargo test
git -C /home/abiorh/flow/Flow-Node diff --check
```

Reviewers: senior engineering, QA/test, security/auth, architecture, CI
integrity, docs, reuse/dedup, test delta.

Human focus: service identity, route privacy, idempotency scope, and byte
round-trip proof. Stop after this PR.
