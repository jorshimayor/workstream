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
backend/app/modules/audit/**
backend/app/modules/actors/repository.py
backend/app/modules/actors/service.py
backend/app/api/deps/auth.py
backend/app/api/router.py
backend/app/main.py
backend/app/schemas/auth.py
backend/alembic/versions/0021_authorization_action_evidence.py
backend/tests/test_auth.py
backend/tests/test_audit.py
backend/tests/test_alembic.py
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
- The closed registry includes every exact artifact permission in
  `docs/spec_authorization_service.md`: Operator reads/retry/recovery/audit,
  guide-source ingest, contributor upload-session create/read/item/seal/cancel
  actions, binding,
  verification, pending-work scan, guide-source read, checker-input
  materialization, and checker-output write. Broad `operations.*` permissions
  are not aliases for artifact authority.
- A closed typed action registry gives each active `ActionId` one approved
  `PermissionId`, canonical target resource type, target-resolution rule,
  allowed principal class, authority-candidate sources, mandatory registered
  guards, and transaction-revalidation requirement. Multiple closed actions may
  map to one retained broad permission with distinct targets/guards. Unknown
  action, permission, resource, or guard identifiers deny during
  registration/startup validation.
- Create and collection actions authorize against an existing parent or
  `system` target; request-supplied project, owner, parent, and state values are
  never canonical resource facts.
- Resource loading remains feature-owned. AUTH defines the bounded
  `ResourceContext` protocol as closed typed per-resource variants and defines
  the composition-root registration contract without importing feature
  repositories or duplicating feature queries. Guards declare required facts;
  missing, extra, or mistyped facts fail closed.
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
- Reusable FastAPI and application-command dependencies accept one primary
  registered action declaration. Domain invariants remain separate, and service
  commands use fixed Workstream principals rather than serialized human tokens.
- Catalogue completeness is staged: this chunk validates current usable
  definitions but does not require loaders or route declarations owned by
  inactive feature-cutover or later domain initiatives.
- Reserved planned action metadata contains only stable `ActionId`, approved
  `PermissionId`, owner, and availability; it never authorizes or predefines
  another domain's target, facts, guards, or composer. Active definitions
  require the owning domain contract, canonical composer, surface declaration,
  and behavior tests.
- `AuthorizationDecision`, bounded logs/metrics, and every action-based allowed
  or denied authority event carry the stable `ActionId`. Migration `0021`
  preserves historical nulls, establishes exact typed/PostgreSQL action-registry
  parity, and requires a registered identifier for AUTH-07-or-later
  action-based decision evidence. Upgrade/downgrade/re-upgrade, direct-SQL,
  unknown-ID, and preserved-history tests pass.
- The three authorization APIs introduced here have exact declarations:
  permission and admin-role definition reads use `admin_role.read` against
  `system` and expose only the authorized administrative metadata projection;
  self authorization-context read uses `actor.profile.read_self` against the
  current actor and returns active, currently authorized capabilities only.
  Planned metadata never appears as an actor capability.
- Generated OpenAPI/command manifest-delta tests prove every protected surface
  introduced by this chunk has exactly one active `ActionId` declaration.
- External denial precedence and concealment are an exact tested matrix. A
  sensitive action declares its transaction linearization contract, including
  ordered actor/link/grant/resource reload/locks or an explicitly approved
  serializable retry strategy; each later mutation chunk proves its own
  revoke-versus-command race.
- `GET /api/v1/authorization/permissions` and
  `GET /api/v1/authorization/admin-role-definitions` return registered,
  non-dynamic definitions with authorization/privacy tests.
- `GET /api/v1/actors/me/authorization-context` is introduced here, after the
  closed registry exists, with project-scoped capability allowlist, privacy,
  unknown-project, and inactive-actor tests.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic downgrade -1)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_authorization.py tests/test_audit.py tests/test_alembic.py \
  --cov=app.modules.authorization \
  --cov-report=term-missing --cov-fail-under=90)
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
resource scope, artifact permission separation, concealment behavior, and
transaction-local revalidation.

## Stop conditions

Stop if the service needs free-form client permissions, cached cross-request
decisions, or a generic policy engine.
