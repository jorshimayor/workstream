# Chunk Contract: WS-AUTH-001-04A - Request And Error Context

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Add canonical request/correlation context and a stable privacy-bounded error
contract while preserving existing response fields, headers, routes, and
product authorization behavior.

## Risk class and SLA

L1 / P1

## Size circuit breaker

- Stop at 350 changed non-comment production lines for a scope checkpoint.
- Stop and replan above 500 changed non-comment production lines.
- Test, documentation, generated schema, and durable loop evidence lines do not
  count toward the production cap.

## Allowed files

```text
backend/app/main.py
backend/app/core/api_controls.py
backend/app/api/deps/auth.py
backend/app/modules/tasks/router.py
backend/tests/test_api_controls.py
backend/tests/test_app.py
backend/tests/test_auth.py
backend/tests/test_tasks.py
backend/scripts/api_contract_e2e.py
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
database models, migrations, rate counters, or rate-control settings
new routes or rate-control dependency attachments
product permission, role, actor-state, or identity behavior
AUTH-04B, AUTH-05, or later chunk implementation
weakened tests, coverage thresholds, or OpenAPI constraints
BaseHTTPMiddleware, response-body buffering, or response JSON rewriting
```

## Request-context contract

- Inspect raw ASGI header pairs so duplicate `X-Request-ID` or
  `X-Correlation-ID` fields cannot be collapsed by framework parsing.
- Accept zero or one value for each ID. Reject repeated fields, including
  identical duplicates, and reject comma-joined values.
- An accepted ID is exactly 36 ASCII characters and the canonical lowercase,
  hyphenated, non-nil RFC 4122 rendering of a UUID with version 1 through 8.
- Generate UUIDv4 for a missing request ID. A missing correlation ID reuses the
  effective request ID.
- Invalid ID input produces a bounded `invalid_request` response with a fresh
  safe request/correlation pair; supplied bytes are never reflected.
- Store effective IDs only on the request's ASGI scope state. Concurrent
  requests must not share context.
- Every response, including malformed-ID, 404, 405, validation, authentication,
  unhandled 500, streaming, and background-task responses, returns canonical
  `X-Request-ID` and `X-Correlation-ID` headers. Application-supplied ID response
  headers are overwritten with the effective pair.
- Use pure ASGI middleware that edits only `http.response.start` headers. It
  must preserve status, unrelated duplicate headers, `WWW-Authenticate`,
  `Retry-After`, content length, body chunks, streaming, and background work.

## Error contract

- The canonical nested object has required fields
  `error.code/message/details/correlation_id/retryable`.
- Add the object for explicit API errors, `HTTPException`, request validation,
  coded task-domain JSON errors, auth missing/invalid/unavailable conditions,
  404, 405, 409, 422, future 429/503 errors, and unhandled 500 responses.
- Default mappings are: 400/422 `invalid_request`, 401 `invalid_token`, 403
  `permission_not_granted`, 404 `resource_not_found`, 405
  `method_not_allowed`, 409 `conflict`, 429 `rate_limit_exceeded`, 503
  `service_unavailable`, and 500 `internal_error`. Existing auth branches may
  emit a more specific already-adopted stable code.
- Existing top-level `detail`, `code`, and `details` fields remain present with
  their current types and values. Coded task responses mirror their top-level
  `code/details` into the nested object.
- Preserve status codes and compatibility headers, including exact
  `WWW-Authenticate` and future `Retry-After` values.
- Validation uses a constant safe message and only the framework's already
  redacted, bounded validation-location/type information. It never exposes
  submitted input values.
- Unhandled errors use a constant message, empty details, and
  `retryable=false` in both debug and non-debug modes. No exception, SQL,
  token, claim, provider response, secret, or PII enters a response or log.
- Shared explicit response builders and exception handlers own JSON shapes.
  The request-context middleware must not parse or rewrite response bodies.

## OpenAPI and compatibility contract

- Document the required canonical error object and only the optional legacy
  compatibility fields that routes can actually return.
- Document request/correlation request headers, response ID headers,
  `WWW-Authenticate`, and future `Retry-After` behavior where applicable.
- Existing task coded-error schemas retain `additionalProperties: false`, their
  required top-level fields, and add required canonical `error` through an
  explicit compatible schema or `oneOf` composition.
- No route path, method, response status, or dependency consumer is added,
  removed, or attached by this chunk. Tests inventory the route set and relevant
  dependency consumers before and after the change.

## Behavior proof

- Missing, valid, malformed, non-ASCII, nil, uppercase, non-hyphenated,
  unsupported-version, repeated-identical, repeated-different, and comma-joined
  ID inputs.
- Request-only, correlation-only, both-ID, and concurrent-request isolation.
- Success, validation, 400, 401, 403, 404, 405, 409, 422, representative coded
  task errors, 500, streaming, background task, and duplicate unrelated header
  preservation.
- Exact legacy field/status/header preservation and bounded redaction.
- OpenAPI response-schema validation plus unchanged path/method and dependency
  consumer inventories.

## Verification commands

```bash
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/python -m pytest -q tests/test_api_controls.py tests/test_app.py tests/test_auth.py tests/test_tasks.py)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/python -m pytest -q --cov=app.core.api_controls --cov=app.main --cov-report=term-missing --cov-fail-under=90 tests/test_api_controls.py tests/test_app.py tests/test_auth.py tests/test_tasks.py)
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

## Human review focus

Review duplicate-ID rejection, ASGI response preservation, error privacy,
legacy compatibility, OpenAPI truth, and unchanged product authority.

## Stop conditions

- Stop if a response body must be parsed or buffered in middleware.
- Stop if an existing response field/header/assertion would need weakening.
- Stop if production changes exceed the size circuit breaker.
- Stop after the reviewed 04A PR; do not start 04B or AUTH-05 automatically.

## Activation

The user explicitly started parent AUTH-04 on 2026-07-13. Required plan review
split it before implementation. Only this repaired 04A contract is active;
runtime edits remain gated on its required preimplementation re-review.
