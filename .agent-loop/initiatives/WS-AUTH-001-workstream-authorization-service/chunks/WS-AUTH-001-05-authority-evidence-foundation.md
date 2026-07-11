# Chunk Contract: WS-AUTH-001-05 - Authority Evidence And Idempotency Foundation

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Evolve the existing `audit_events`/`AuditRepository` path with canonical
mutation idempotency and authority invalidation evidence before actor or grant
mutations use it.

## Why this chunk exists

Authority-changing APIs cannot ship with temporary provenance that a later
chunk would need to reconstruct.

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
backend/app/modules/audit/**
backend/app/modules/authorization/**
backend/app/db/models.py
backend/app/modules/tasks/models.py
backend/app/modules/tasks/repository.py
backend/app/modules/tasks/service.py
backend/alembic/versions/0017_*.py
backend/tests/test_auth.py
backend/tests/test_alembic.py
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
actor/profile migration or first-access behavior
permission/grant evaluation
admin/project grants
project/task/checker authorization cutover
backfilling fabricated authority events
```

## Acceptance criteria

- Idempotency rows store canonical request hash, operation, actor reference,
  status, and bounded committed response reference with unique replay guards.
- Authority events have final versioned fields for acting/target references,
  matched grant, project, reason, idempotency key, bounded before/after state,
  and database time.
- Existing `AuditEvent` is extended; no parallel AuthorityEvent table/model is
  created. `TaskRepository.add_audit_event` delegates to or is consolidated
  with `AuditRepository` so one shared writer owns persistence.
- Audit persistence exposes insert/read operations only through supported
  application paths. Migration-level enforcement rejects authority-event
  update/delete by the application database role; focused tests prove attempts
  fail without changing prior rows. The runbook defines retention and the
  separately controlled privileged database-maintenance path.
- Authorization-owned idempotency models, repository queries, and service
  orchestration remain separate feature modules. Middleware, generic core
  helpers, and ORM models do not own replay queries or transaction policy.
- The injected AsyncSession remains the UnitOfWork boundary. Caller services
  own commit/rollback; no generic parallel UoW wrapper is introduced.
- Session-bound repository APIs let callers atomically persist business state,
  idempotency result, authority event, and invalidation event.
- Migration owns idempotency/audit constraints, indexes, UTC/database-time
  defaults, prior-head upgrade, downgrade, and re-upgrade.
- Each later authority-mutation chunk must test its specified successful and
  denied audit events atomically when that behavior is introduced; chunk 16
  cannot backfill an omitted event.

## Verification commands

```bash
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic downgrade -1)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
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

Review reuse of AuditEvent/AuditRepository, idempotency uniqueness/replay,
AsyncSession transaction ownership, and unchanged product authorization.

## Stop conditions

Stop if final evidence requires a canonical ActorProfile FK before migration;
use stable actor-reference fields rather than introducing a parallel actor.
