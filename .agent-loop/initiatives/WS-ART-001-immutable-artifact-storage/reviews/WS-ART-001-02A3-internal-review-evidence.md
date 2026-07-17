# Internal Review Evidence: WS-ART-001-02A3

## Chunk

`WS-ART-001-02A3`: ArtifactStore v2 Local Clean Cut

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: `956dbcf9fd4b23b1d8daed8c0c666fd49f08303f`

Reviewed at: 2026-07-17T17:06:39Z

Reviewer run IDs: senior-engineering=019f712e-1587-7c33-acec-a11887ea70a3; architecture=019f7101-7405-7e42-9910-023cef1badf1; QA/test=019f7101-821c-72c1-96f0-3bd76d131e2d; security/auth=019f7101-9945-78e0-9b97-7e0bf0049cdf; product/ops=019f7112-43ce-7d10-bba3-7078d431f646; reuse/dedup=019f710c-af16-7823-9ef1-0a380b878f04; CI-integrity=019f70f4-68fe-73a0-999e-194487788070; test-delta=019f710c-bd3f-7142-b2a6-77ed19e3ea62; docs=019f70f4-75fe-77c3-b9da-661e0d3d9d4a

Only review artifacts may change after this reviewed SHA while follow-up review
and evidence closure complete. No implementation, migration, test, workflow,
policy, or chunk-contract change is permitted without invalidating this record.

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
| senior engineering | PASS AFTER FIXES | None | Exact-SHA binding, closed evidence state, and current proof values were repaired after follow-up. |
| QA/test | PASS | None | Concurrency, cancellation, migration, namespace, and state-transition proof passed. |
| security/auth | PASS | None | Filesystem, integrity, namespace, sanitization, and AUTH custody remained fail closed. |
| product/ops | PASS | None | No product review, contribution, compensation, reputation, or recovery lifecycle was activated. |
| architecture | PASS | None | Byte-only adapter, typed factory, capability boundaries, and chunk scope passed. |
| ci integrity | PASS AFTER FIXES | None | Exact-SHA evidence binding and current deterministic proof values now satisfy the fail-closed gate. |
| docs | PASS AFTER FIXES | None | Stale SHA, phase, and proof-value contradictions were removed from the evidence and trust bundle. |
| reuse/dedup | PASS | None | Shared adapter, scratch, cancellation, locking, hashing, and namespace abstractions are reused. |
| test delta | PASS AFTER FIXES | None | Current proof values match the strengthened v2 contract, race, migration, and cleanup test delta. |

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

Results: 268 ART-focused tests passed; 56 LocalStorage/conformance tests passed
at 91.08 percent; all four clean-cut migration cases passed; ART scope coverage
was 93.18 percent. Ruff, 92.0 percent docstring coverage, stale
contract/authorization/wording,
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
