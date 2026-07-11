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
- artifact adapter/integration tests and operations docs

## Not Allowed

No byte payload in DB/Redis/outbox, product cutover, provider fallback, human
token forwarding, or provider-triggered lifecycle transition.

## Acceptance Criteria

- Synchronous ingest follows D4 and independently compares SHA-256/size.
- Crash after provider success/before receipt commit never trusts the receipt
  alone. With a persisted expected digest, reconciliation independently
  reopens/hashes/counts the object; without one, the item becomes
  `replay_required` until exact client replay under the same idempotency key.
- A development-only one-shot failpoint can interrupt after provider commit and
  before Workstream transaction B for deterministic proof. It requires the
  local test-control credential and cannot be configured or routed in
  production.
- Outbox is limited to verify/retain/status/reconcile/release and is at least
  once with stable keys, bounded jitter/backoff, attempt history, and dead-letter
  visibility.
- Concurrent dispatch/reconcile has one monotonic provider effect and one
  canonical receipt outcome; row counts are asserted.
- Same v1 vectors pass LocalStorageAdapter and pinned Flow Node image.
- Compose health proves authenticated ingest/retrieve/status without product
  module changes.

## Verification

```bash
cd backend && .venv/bin/ruff check app tests scripts
cd backend && .venv/bin/docstr-coverage --config .docstr.yaml
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q tests/test_artifacts.py
docker compose up -d --build postgres redis flow-node
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/artifact_store_contract_e2e.py
docker compose down -v
python3 scripts/check_markdown_links.py
git diff --check
```

Reviewers: all required tracks.

Human focus: data-plane choreography, receipt monotonicity, secrets, retries,
and pinned provider revision. Stop after this PR.
