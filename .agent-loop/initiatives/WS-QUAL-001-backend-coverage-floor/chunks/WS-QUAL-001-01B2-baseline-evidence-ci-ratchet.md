# Chunk Contract: WS-QUAL-001-01B2 Baseline Evidence And CI Ratchet

Status: proposed after 01B1; inactive until 01B1 merge, memory, separate explicit
start, internal contract review, and human approval of the split.

## Goal, Risk, And Budget

Extend the reviewed policy core with Git provenance and publish the configured
initial full-app floor, canonical evidence, read-only CI ratchet, and runbook.

- Risk: L1 CI/evidence integrity; SLA P1
- Implementation cap: 500 lines outside `.agent-loop`
- Allowed: `backend/scripts/coverage_policy.py`,
  `backend/tests/test_coverage_contract.py`, `backend/pyproject.toml`,
  `.github/workflows/backend.yml`, `docs/operations_backend_testing.md`, the
  canonical WS-QUAL baseline evidence, and WS-QUAL/global memory/reviews
- Forbidden: `backend/app/**`, runner/API-drill implementation, migrations,
  schemas, product/auth behavior, unrelated tests, exclusions, pragmas,
  skips/xfail, weakened assertions, or coverage-raising tests

## Acceptance Criteria

- Add local-only one-write initialization and default read-only validation;
  CI cannot create or rewrite evidence.
- Bind runner metadata to checkout HEAD and new evidence to one clean executable
  tree. Accept only enumerated evidence descendants and correctly handle PR
  synthetic merge commits, base advancement/rebase drift, bootstrap merge push,
  and push comparison with exact nonzero prior revision.
- Real temporary-Git tests prove bootstrap, unchanged/updated evidence, evidence-
  only descendants, executable drift, invalid/non-ancestor bases, and push floor,
  covered-count, milestone, and denominator regressions.
- Configure the candidate six-place full-app floor, preserve the independent
  artifact 90 gate and exact 16+remaining test partition, and run policy read-
  only in CI with no bypass or threshold override.
- Generate canonical credential-free baseline evidence from a second complete
  isolated run on the committed implementation SHA. Admin DSN stays env-only;
  shell traps remove temporary coverage/metadata.
- Update the runbook with bootstrap, validation, ratchet, credential handling,
  temp cleanup, and recovery.

## Verification And Review

Use the exact compute/initialize/validate state machine and three-stage commands
from the reviewed parent 01B contract, plus full Ruff, policy tests, pip check,
stale wording/auth/link checks, diff hygiene, and the internal evidence gate.

Required reviewers: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, and test delta. Human focus:
Git/tree provenance, prior-revision push ratchet, exact floor/evidence, CI
non-bypass, credentials, and no coverage-chasing tests.

Stop above 500 lines or on missed floor/provenance/CI proof. Do not start chunk 02.
