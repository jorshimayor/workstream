# Chunk Contract: WS-AUTH-001-04B - PostgreSQL Rate Controls

## Status

Inactive. This contract requires AUTH-04A merge/memory, a separate explicit
user start, and required preimplementation review before any runtime edit.

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Provide privacy-keyed, cross-replica PostgreSQL fixed-window rate controls for
future first-access and authority-management mutations without attaching them
to routes owned by later chunks.

## Risk class and SLA

L1 / P1

## Size circuit breaker

- Stop at 350 changed non-comment production lines for a scope checkpoint.
- Stop and replan above 500 changed non-comment production lines.

## Allowed files

```text
backend/app/core/config.py
backend/app/api/deps/api_controls.py
backend/app/modules/api_controls/__init__.py
backend/app/modules/api_controls/models.py
backend/app/modules/api_controls/repository.py
backend/app/modules/api_controls/service.py
backend/app/db/models.py
backend/alembic/versions/0017_api_controls.py
backend/tests/test_api_rate_controls.py
backend/tests/test_config.py
backend/tests/test_alembic.py
backend/scripts/api_contract_e2e.py
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
request/error-context implementation owned by AUTH-04A
new routes or attachment to unrelated existing routes
first-access, grant, actor-state, or product authorization behavior
Redis/in-memory counters or persisted raw identity/network/token material
AUTH-05 or later chunk implementation
```

## Persistence and transaction contract

- Persist one row per `(control_scope, key_digest)` with bounded scope, fixed
  HMAC-SHA256 digest length, `window_started_at`, `window_expires_at`,
  `request_count`, and `updated_at` using timezone-aware database timestamps.
- Enforce nonempty bounded scope, exact digest length, positive bounded count,
  ordered window timestamps, uniqueness, and the lookup/expiry indexes required
  by the executed query.
- One PostgreSQL upsert uses one `statement_timestamp()` value to reset an
  expired window or atomically increment an active window and returns database
  now, window start/end, and count. Saturate at the database integer maximum.
- Counts `1..limit` allow. Count `limit+1` and later deny and remain durably
  consumed. `Retry-After` is the ceiling of remaining database-time seconds,
  clamped to `1..window_seconds`.
- Invoke the upsert in a dedicated short-lived session/transaction and commit
  before returning either allow or 429. A downstream request rollback cannot
  undo rate consumption.

## Privacy and configuration contract

- Derive `key_digest` with HMAC-SHA256 using domain
  `workstream-api-rate/v1`, the bounded control scope, and exact issuer plus
  opaque subject bytes framed by four-byte big-endian lengths and UTF-8 values.
- Persist only scope and digest. Never persist or log raw issuer, subject,
  actor ID, email, role, token, claims, or network address.
- Add `api_rate_limit_key_secret` with no default and minimum 32-byte secret
  material. Never render or log it. Present malformed values fail settings
  construction.
- Defaults are first-access `10/60s` and admin-mutation `30/60s`, with limit
  bounds `1..10000` and window bounds `1..3600`.
- Missing secret remains startup-compatible while no route is attached, but
  invoking a protected dependency without it returns a safe retryable 503.
  Database unavailability also fails closed as safe retryable 503.
- Secret rotation intentionally resets effective counters. The runbook requires
  quiescing protected writes for at most the largest configured window before
  replacing the secret.

## Route boundary and behavior proof

- Export named first-access and admin-mutation dependencies for later owning
  chunks, but attach neither dependency here.
- Inventory path/method and dependency consumers to prove no route or consumer
  changed.
- Prove allow, exact limit, repeated exceed, expiry reset, distinct key/scope,
  concurrent increments, cross-session visibility, downstream rollback
  independence, missing/malformed secret, database unavailable, bounded
  `Retry-After`, and privacy-safe persistence.

## Migration proof

- `0017_api_controls` revises `0016_artifact_domain`.
- Prove `0016 -> 0017 -> 0016 -> 0017`, seeded-row preservation across the
  supported direction, unique/check/index enforcement, invalid insert
  rejection, and the explicit nonempty-table downgrade policy.

## Verification commands

```bash
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/python -m pytest -q tests/test_api_rate_controls.py tests/test_config.py tests/test_alembic.py)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/python -m pytest -q --cov=app.modules.api_controls --cov=app.api.deps.api_controls --cov-report=term-missing --cov-fail-under=90 tests/test_api_rate_controls.py tests/test_config.py tests/test_alembic.py)
(cd backend && .venv/bin/python scripts/run_isolated_tests.py --metadata-json <temp-metadata-json> --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78)
(cd backend && .venv/bin/python scripts/run_isolated_tests.py --metadata-json <temp-metadata-json> --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/python scripts/api_contract_e2e.py)
(cd backend && .venv/bin/python -m ruff check app tests scripts)
python3 scripts/check_loop_memory_state.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_markdown_links.py
python3 scripts/check_internal_review_evidence.py
python3 scripts/test_agent_gates.py
git diff --check
```

## Required reviewers

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

## Stop conditions

- Stop if a rate count can be rolled back with downstream work.
- Stop if atomic database-time semantics cannot be proven under concurrency.
- Stop if a raw identity or token-derived value would be persisted or logged.
- Stop if production changes exceed the size circuit breaker.
- Stop after 04B; do not start AUTH-05 automatically.
