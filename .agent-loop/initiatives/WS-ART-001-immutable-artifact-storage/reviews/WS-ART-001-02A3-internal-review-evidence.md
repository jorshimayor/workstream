# Internal Review Evidence: WS-ART-001-02A3

## Chunk

`WS-ART-001-02A3`: ArtifactStore v2 Local Clean Cut

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: `441d39230a341f2c43dd548776a2437ae6b2395d`

Reviewed at: 2026-07-17T08:20:30Z

Reviewer run IDs: senior-engineering=019f6ef7-e1b5-7952-a261-aa73faad5816; architecture=019f6ef7-e901-7a30-9240-2027703ff4ae; QA/test=019f6ef7-f1ff-72a1-9e88-9b47557fad89; security/auth=019f6ef7-fec4-7b53-99ff-a349d3d113f9; product/ops=019f6ef8-0d4a-7610-befb-9431d4483880; reuse/dedup=019f6ef8-190a-7b60-932d-71f6d3b422c1; CI-integrity=019f6f0b-3052-7123-bf19-36c7ec9e1bc6; test-delta=019f6f0b-36d1-7833-b1ed-08b19011a984; docs=019f6f0b-3fc2-7f12-9ea1-3b8a43ccc0eb

Only review artifacts, this initiative's status, and `LOOP_STATE.md` changed
after the reviewed SHA. No implementation, migration, test, workflow, policy,
or chunk-contract content changed after review.

## Reviewed Change

- Replaced ArtifactStore v1 with the four-operation byte-only v2 port and one
  typed factory path.
- Rebuilt LocalStorage around immutable content-derived paths, exact replay,
  bounded range reads, no-follow descriptors, exclusive publication, and
  sanitized failures.
- Added the immutable storage-namespace fence and recorded provider
  acknowledgement as `stored_pending_verification` with replica state
  `pending/unknown/unknown`.
- Made same-object replica finalization atomic across concurrent PostgreSQL
  transactions while retaining one append-only receipt per upload item.
- Guaranteed best-effort resource cleanup always attempts digest-lock release
  without masking the original sanitized error or caller cancellation.
- Removed v1 provider-retention/receipt semantics, dormant Flow Node
  configuration, and invented authorization ownership.
- Activated only bounded startup and Celery Beat scratch cleanup. Product
  ingest, S3, verification, recovery, review, and AUTH actions remain inactive.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Atomic finalization and independent cleanup ownership passed after repair. |
| QA/test | PASS | None | Concurrency, cancellation, migration, namespace, and state-transition proof passed. |
| security/auth | PASS | None | Filesystem, integrity, namespace, sanitization, and AUTH custody remained fail closed. |
| product/ops | PASS | None | No product review, contribution, payment, reputation, or recovery lifecycle was activated. |
| architecture | PASS | None | Byte-only adapter, typed factory, capability boundaries, and chunk scope passed. |
| ci integrity | PASS | None | Scoped 90 percent gates and the repository 78 percent floor remain fail closed. |
| docs | PASS | None | Artifact contract and operations documentation match the implemented boundary. |
| reuse/dedup | PASS | None | Shared adapter, scratch, cancellation, locking, and hashing abstractions are reused. |
| test delta | PASS | None | V1 tests were replaced by stronger v2 contract, race, migration, and cleanup proof. |

## Valid Findings Addressed

- Replaced the replica read-then-insert race with PostgreSQL
  `ON CONFLICT DO NOTHING` plus a current-row load and strict content,
  namespace, adapter, and provider-profile validation.
- Added a real two-session concurrency test proving two exact replay
  finalizations produce one replica and two receipts.
- Made LocalStorage cleanup attempt digest-lock release in an independent
  `finally` even when temporary unlink or fsync fails.
- Added regression coverage proving cleanup errors cannot leak the owned lock
  or replace the caller's sanitized failure/cancellation semantics.
- Added a namespace-only populated-v2 downgrade refusal test so the deployment
  fence cannot be discarded by a clean-cut rollback.
- Reconciled merged-main loop state and marked the pre-main review record as
  superseded rather than reusing stale review provenance.

## Commands Run

```bash
cd backend && .venv/bin/ruff check app/modules/artifacts/repository.py app/modules/artifacts/service.py app/adapters/artifacts/local.py tests/test_artifacts.py tests/test_local_artifact_store.py
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q tests/test_artifacts.py::test_concurrent_same_object_finalization_reuses_one_replica
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test COVERAGE_FILE=.coverage.art02a3 .venv/bin/coverage run -m pytest -q tests/test_artifacts.py tests/test_artifact_preparation.py tests/test_config.py tests/test_app.py tests/test_api_controls.py tests/test_artifact_architecture.py tests/test_artifact_cleanup_wiring.py tests/test_artifact_store_conformance.py tests/test_local_artifact_store.py
cd backend && .venv/bin/pytest -q tests/test_artifact_store_conformance.py tests/test_local_artifact_store.py --cov=app.adapters.artifacts.local --cov=app.interfaces.artifacts --cov-report=term-missing --cov-fail-under=90
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/pytest -q tests/test_alembic.py::test_artifact_store_v2_empty_clean_cut_and_reversible_shape tests/test_alembic.py::test_artifact_store_v2_refuses_populated_v1_before_ddl tests/test_alembic.py::test_artifact_store_v2_refuses_populated_v2_downgrade_before_ddl tests/test_alembic.py::test_artifact_store_v2_waits_for_concurrent_v1_writer_and_refuses
cd backend && .venv/bin/docstr-coverage --config .docstr.yaml
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/test_agent_gates.py
git diff --check
```

Results: 254 ART-focused tests passed; the dedicated PostgreSQL replica-race
test passed; 47 LocalStorage/conformance tests passed at 91.64 percent; all four
clean-cut migration cases passed; ART scope coverage was 93.32 percent,
configuration coverage 96.92 percent, and `app/main.py` coverage 90.35 percent.
Ruff, 93.0 percent docstring coverage, stale contract/authorization/wording,
Markdown links, 80 agent-gate tests, and diff checks passed.

The isolated full repository suite, 78 percent whole-app floor, cumulative
worker/main gates, and real API drill remain authoritative in GitHub Backend CI.
The intentionally aborted broad local project/task run is not completion
evidence; it was stopped because full regression is assigned to GitHub Actions.

## Remaining Risks

- The migration intentionally refuses any populated pre-production v1 artifact
  table rather than fabricating v2 provenance.
- LocalStorage remains development/test only. Hosted bytes remain disabled
  until the separately approved S3-compatible adapter and AWS activation proof.
- `stored_pending_verification` remains non-bindable. Admission, verification,
  publication, and recovery belong to later chunks.

## Stop Condition

Publish the evidence-bound head for GitHub CI, CodeRabbit, and human review.
Do not merge without explicit user approval and do not start
`WS-ART-001-02B1`.
