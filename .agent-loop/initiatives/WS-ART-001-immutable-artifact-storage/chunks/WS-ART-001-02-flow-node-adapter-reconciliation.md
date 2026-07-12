# WS-ART-001-02: Flow Node Adapter And Reconciliation

Parent: `WS-ART-001` | Repository: Workstream | Risk: L1 | SLA: P1

## Goal

Implement `FlowNodeAdapter`, metadata-only operation outbox/reconciliation,
pinned provider delivery, and local integration.

## Allowed Files

- `backend/app/adapters/artifacts/flow_node.py`
- artifact services/repositories/workers/config
- development-only artifact fault-control wiring and tests
- Celery and `docker-compose.yml`, focused backend Docker build files
- one additive migration if required
- `backend/tests/test_artifacts.py`, `backend/tests/test_alembic.py`
- artifact adapter/integration tests and operations docs

## Not Allowed

No byte payload in DB/Redis/outbox, product cutover, provider fallback, human
token forwarding, or provider-triggered lifecycle transition.

## Acceptance Criteria

- Synchronous ingest follows D4 and independently compares SHA-256/size.
- Crash after provider success/before receipt commit never trusts the receipt
  alone. With persisted expected SHA-256 and size, reconciliation independently
  reopens/hashes/counts the object; with either commitment absent, the item becomes
  `replay_required` until exact client replay under the same idempotency key.
- A development-only one-shot failpoint can interrupt after provider commit and
  before Workstream transaction B for deterministic proof. It requires the
  local test-control credential and cannot be configured or routed in
  production.
- Outbox is limited to verify/retain/status/reconcile/release and is at least
  once with stable keys, bounded jitter/backoff, attempt history, and dead-letter
  visibility.
- Reconciliation, quarantine, retain, and release product audit events use the
  shared `AuditRepository`; provider receipts remain operation evidence only.
- Concurrent dispatch/reconcile has one monotonic provider effect and one
  canonical receipt outcome; row counts are asserted.
- Same v1 vectors pass LocalStorageAdapter and a Flow Node image pinned by full
  immutable registry digest. CI verifies the registry identity, manifest digest,
  expected source revision/contract digest, and available build provenance; a
  mutable tag or version-only reference is rejected.
- If an additive migration is required, fresh/prior-head upgrade,
  populated-state preservation, empty downgrade, and re-upgrade are owned and
  proved in `test_alembic.py`; otherwise the chunk records that no migration was
  created.
- Compose health proves adapter-level authenticated ingest/retrieve/status from
  Workstream's service principal directly through `FlowNodeAdapter`; it does not
  claim a public Workstream artifact API before the product cutover.

## Verification

```bash
(cd backend && .venv/bin/ruff check app tests scripts)
(cd backend && .venv/bin/docstr-coverage --config .docstr.yaml)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q tests/test_artifacts.py tests/test_alembic.py)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q)
(cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/api_contract_e2e.py)
docker compose up -d --build --wait --wait-timeout 120 postgres redis flow-node
(cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/artifact_store_contract_e2e.py)
docker compose down -v
python3 scripts/test_agent_gates.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/check_loop_memory_state.py
python3 scripts/check_internal_review_evidence.py
git diff --check
```

Reviewers: all required tracks.

Human focus: data-plane choreography, receipt monotonicity, secrets, retries,
and pinned provider revision. Stop after this PR.
