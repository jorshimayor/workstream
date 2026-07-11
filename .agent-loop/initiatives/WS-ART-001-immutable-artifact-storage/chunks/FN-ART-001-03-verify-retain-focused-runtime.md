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

## Verification

```bash
cd /home/abiorh/flow/Flow-Node/back-end && cargo fmt --check
cd /home/abiorh/flow/Flow-Node/back-end && cargo clippy --all-targets --all-features -- -D warnings
cd /home/abiorh/flow/Flow-Node/back-end && cargo test artifact
cd /home/abiorh/flow/Flow-Node/back-end && cargo test artifact_contract::verify_retain_release
cd /home/abiorh/flow/Flow-Node/back-end && cargo test artifact_contract::version_1
cd /home/abiorh/flow/Flow-Node/back-end && cargo test
cd /home/abiorh/flow/Flow-Node && docker compose -f docker-compose.workstream.yml up -d --build
cd /home/abiorh/flow/Flow-Node && docker compose -f docker-compose.workstream.yml down -v
git -C /home/abiorh/flow/Flow-Node diff --check
```

Reviewers: senior engineering, QA/test, security/auth, architecture, CI
integrity, docs, reuse/dedup, test delta.

Human focus: full-DAG proof, GC race safety, focused build contents, and private
defaults. Stop after this PR.
