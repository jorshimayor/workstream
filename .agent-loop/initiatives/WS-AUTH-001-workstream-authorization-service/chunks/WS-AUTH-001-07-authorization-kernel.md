# Chunk Contract: WS-AUTH-001-07 - Authorization Kernel And Permission Registry

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Implement the deny-by-default AuthorizationService kernel, registered
permissions, canonical ResourceContext, stable AuthorizationDecision, actor
state/global guards, and reusable FastAPI/application dependencies before any
grant-management API.

## Why this chunk exists

Every later protected grant and product command must call one service rather
than introducing temporary direct grant queries.

## Approved plan reference

- INTENT: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/INTENT.md`
- PLAN: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/PLAN.md`
- CHUNK_MAP: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/CHUNK_MAP.md`

## Risk class

L1

## SLA

P1

## Allowed files

```text
backend/app/modules/authorization/**
backend/app/modules/actors/repository.py
backend/app/modules/actors/service.py
backend/app/api/deps/auth.py
backend/app/api/router.py
backend/app/main.py
backend/app/schemas/auth.py
backend/tests/test_auth.py
backend/tests/test_actors.py
backend/tests/test_app.py
backend/scripts/api_contract_e2e.py
docs/operations_authorization_service.md
docs/spec_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
dynamic/user-authored permissions or policy language
authorization decision cache across requests
direct role queries in routers
project/task/checker surface cutover
review/compensation permissions beyond registered future definitions
```

## Acceptance criteria

- Permission identifiers are a closed registered enum/value set.
- Request context contains verified identity plus current local actor/grant state
  and correlation/request IDs.
- Authorization resolves actor/link state, grant candidates, canonical project,
  ownership, global guards, and resource state in a defined order.
- Unknown permissions deny.
- System scope is not superuser authority.
- Suspended/deactivated/revoked actors deny before permission expansion.
- Stable structured error envelope and concealment rules are defined.
- Table-driven tests cover every current permission/role/scope candidate.
- Sensitive mutations can revalidate inside the caller transaction/UoW.
- The bootstrap system operation and default-human self permissions are the
  only usable candidates before grant tables ship.
- Direct role/grant authorization outside this service is explicitly banned.
- `GET /api/v1/authorization/permissions` and
  `GET /api/v1/authorization/admin-role-definitions` return registered,
  non-dynamic definitions with authorization/privacy tests.
- `GET /api/v1/actors/me/authorization-context` is introduced here, after the
  closed registry exists, with project-scoped capability allowlist, privacy,
  unknown-project, and inactive-actor tests.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python scripts/api_contract_e2e.py)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
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

Review deny-by-default ordering, permission matrix completeness, canonical
resource scope, concealment behavior, and transaction-local revalidation.

## Stop conditions

Stop if the service needs free-form client permissions, cached cross-request
decisions, or a generic policy engine.
