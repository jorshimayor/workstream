# WS-ART-001-01: Artifact Domain And Local Adapter

Parent: `WS-ART-001` | Repository: Workstream | Risk: L1 | SLA: P1

## Goal

Implement versioned provider contract fixtures, provider-neutral artifact
records/port, configuration, and `LocalStorageAdapter` conformance.

## Allowed Files

- `contracts/artifact-store/version_1/**`
- `backend/app/interfaces/artifacts.py`
- `backend/app/modules/artifacts/**`
- `backend/app/adapters/artifacts/local.py`
- `backend/app/core/hashing.py`, `backend/app/modules/audit/repository.py`
- `backend/app/core/config.py`, `backend/app/db/models.py`
- one new `backend/alembic/versions/*.py`
- `backend/tests/test_artifacts.py`, `test_config.py`, `test_alembic.py`
- `scripts/check_stale_artifact_contracts.py`
- `scripts/test_agent_gates.py`
- owning artifact docs only

## Not Allowed

No public upload API, Flow Node adapter, product cutover, provider call in a
lifecycle transaction, legacy-field removal, or WS-AUTH implementation.

## Acceptance Criteria

- Separate upload session/item, content, immutable binding, replica, and receipt
  records; staging creates no binding.
- Generic port exposes no CID/DAG/pin types.
- Manifest/request/response digests reuse or centrally extend
  `canonical_json_hash`; no artifact-local canonical JSON helper is added.
- Binding/release/quarantine/reconciliation audit evidence uses the shared
  `AuditEvent`/`AuditRepository`; operation receipts do not form a parallel
  audit framework.
- Additive migration succeeds with current legacy rows and promotes none.
- Local adapter performs bounded atomic writes, independent SHA-256/size checks,
  opaque IDs, private permissions, idempotent replay/mismatch, retrieval, verify,
  retain/release/status, cancellation cleanup, and no path leakage.
- Empty/boundary/oversize/disk-failure tests use overridden limits and assert
  cleanup plus bounded buffering.
- Crash recovery with a persisted expected digest reopens and independently
  hashes/counts provider bytes; without one it requires exact client replay
  under the same idempotency key. Receipt-only, altered
  commitment/receipt/object/replay, and truncated-stream fixtures create zero
  content/binding rows and quarantine where integrity is implicated.
- Production configuration rejects local adapter and missing retention policy.
- A phased stale-contract scanner exists in this foundation chunk. It rejects
  obsolete artifact terms only after their owning cutover is active and is
  covered by focused gate tests, so later chunks cannot claim a scanner that
  does not yet exist.

## Verification

```bash
(cd backend && .venv/bin/ruff check app tests scripts)
(cd backend && .venv/bin/docstr-coverage --config .docstr.yaml)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q tests/test_artifacts.py tests/test_config.py tests/test_alembic.py)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q)
(cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/api_contract_e2e.py)
python3 scripts/test_agent_gates.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/check_loop_memory_state.py
python3 scripts/check_internal_review_evidence.py
git diff --check
```

Reviewers: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, test delta.

Human focus: record separation, port neutrality, migration additivity, storage
privacy, and production guards. Stop after this PR.
