# FN-ART-001-03: Verification, Retention, And Focused Runtime

Parent: `WS-ART-001` | Repository: Flow Node | Risk: L1 | SLA: P1

## Goal

Add bounded recursive verify/retain, replica status/receipts, and a deployable
focused Workstream artifact runtime target.

## Allowed Files

- storage DAG traversal/GC coordination
- artifact routes/catalog/receipts
- runtime feature/build target, Dockerfile/Compose health configuration
- focused tests/docs

## Not Allowed

No semantic search, peer retrieval, public announcement, UI/WebAuthn/spaces/AI
routes in the focused binary, source deletion from Flow Node main, or Workstream
domain IDs in provider contracts.

## Acceptance Criteria

- Verify/retain traverse all reachable nodes with limits on blocks, depth,
  cycles, bytes, and time.
- Retain is atomic with GC or followed by complete re-verification; partial
  failure is quarantined and never reported retained.
- Status separates verification, retention, availability, and integrity.
- Release requires `artifact:release`, the exact owning retention reference,
  legal-hold and retention-policy checks, append-only audit evidence, and CAS;
  read/verify/retain/status scopes and foreign references cannot release
  content.
- Focused target contains only health and authenticated artifact operations,
  disables network announcement/retrieval, and has no unrelated runtime deps.
- Docker health plus corruption, missing-block, and simulated retain-refusal
  controls are test-only, require the development test-control credential, and
  are absent from production builds/configuration.
- The focused runtime exposes a machine-checkable compiled route inventory so
  CI can prove production builds contain no test-control routes or handlers.
- The `verify_retain_release` contract-vector subset and then the complete
  `version_1` provider suite pass against the focused runtime.
- The additive retention/reference/status migration verifies existing artifact
  rows before retain eligibility, refuses downgrade while active retention
  references exist, and passes empty-fixture downgrade/re-upgrade tests.
- A dedicated `artifact_retention_contract` integration-test target is
  non-empty; the test runner fails if target discovery reports zero tests.

## Verification

```bash
(cd back-end && cargo fmt --check)
(cd back-end && cargo clippy --all-targets --all-features -- -D warnings)
(cd back-end && ./scripts/run_nonempty_cargo_test_target.sh artifact_retention_contract)
(cd back-end && cargo test)
docker compose -f docker-compose.workstream.yml up -d --build --wait --wait-timeout 120
./scripts/run_artifact_contract_vectors.sh --compose docker-compose.workstream.yml --suite version_1
docker compose -f docker-compose.workstream.yml run --rm flow-node-production-route-audit
docker compose -f docker-compose.workstream.yml down -v
git diff --check
```

Reviewers: senior engineering, QA/test, security/auth, architecture, CI
integrity, docs, reuse/dedup, test delta.

Human focus: full-DAG proof, GC race safety, focused build contents, and private
defaults. Stop after this PR.
