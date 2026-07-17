# Internal Review Evidence: WS-ART-001-02A3

## Chunk

`WS-ART-001-02A3`: ArtifactStore v2 Local Clean Cut

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: `f110a21dd694c9744d0036d380898f602d0d96ff`

Reviewed at: 2026-07-17T18:38:59Z

Reviewer run IDs: senior-engineering=019f7161-b4a3-7170-9e99-0be3f8464603; architecture=019f7161-bdad-7030-8104-902a61b4d6fb; QA/test=019f7161-d775-7e00-b493-1201899227fe; security/auth=019f7161-c843-7e02-9c6c-6b9f90e77f76; product/ops=019f7161-e69f-7593-96e2-e784499237ec; reuse/dedup=019f7161-f8ba-7d80-bf97-b2d28b6ac41e; CI-integrity=019f7167-7753-7481-9d4f-8a2e5f300333; test-delta=019f7167-7b6d-7850-b400-f7d0c39d6f4f; docs=019f7167-8271-7a13-8bea-c1fcf2a41151

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
| senior engineering | PASS | None | The test covers a real worker failure contract rather than padding lines; operational evidence remains truthful. |
| QA/test | PASS | None | Real PostgreSQL state, sanitized response, bounded log metadata, and secret non-disclosure are asserted. |
| security/auth | PASS | None | The repair strengthens redaction proof and changes no auth or privilege boundary. |
| product/ops | PASS | None | `setup_blocked` remains the established project-setup outcome; no product lifecycle was activated. |
| architecture | PASS | None | Test-only repair changes no ART, AUTH, REV, CON, adapter, or capability boundary. |
| ci integrity | PASS | None | The unchanged cumulative worker gate is expected to rise above 90 percent from the newly covered statements. |
| docs | PASS | None | The failed external run and bounded test repair are described without overstating the rerun result. |
| reuse/dedup | PASS | None | The bounded test follows the existing real-DB worker-test pattern without adding production duplication. |
| test delta | PASS | None | Assertions prove the exact missed domain-failure branch and do not weaken existing tests or gates. |

## Valid Findings Addressed

- GitHub Backend CI passed the full repository coverage and first three focused
  gates, then reported 88.20 percent cumulative `app/workers/*` coverage. Added
  real-PostgreSQL coverage for the known `ProjectServiceError` worker path,
  including sanitized result, persisted `setup_blocked` state, and bounded log
  metadata. The new test executes the previously missed lines 174-193 without
  narrowing or weakening the 90 percent worker gate.

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
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q tests/test_projects.py::test_project_setup_worker_persists_sanitized_domain_failure
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
The added real-PostgreSQL worker test passed and executes the ten statements in
the previously missed known-domain-failure branch. GitHub must confirm the
cumulative worker percentage on the republished head.

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
