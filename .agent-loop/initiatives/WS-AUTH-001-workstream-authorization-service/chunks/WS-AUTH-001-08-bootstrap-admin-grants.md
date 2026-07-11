# Chunk Contract: WS-AUTH-001-08 - Bootstrap And Administrative Role Grants

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Implement the one-time local bootstrap operation, `AuthorityControl`, immutable
AdminRoleGrants, scope compatibility, grant/revoke APIs, idempotency, and
concurrency-safe final-access-administrator protection.

## Why this chunk exists

Workstream needs durable administrative authority before project permissions
or product surfaces can stop using token roles.

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
backend/app/modules/actors/**
backend/app/modules/authorization/**
backend/app/api/router.py
backend/app/db/models.py
backend/scripts/bootstrap_access_administrator.py
backend/app/modules/audit/**
backend/alembic/versions/0019_*.py
backend/tests/test_actors.py
backend/tests/test_auth.py
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
public bootstrap endpoint or shared bootstrap bearer secret
project contributor grants
product surface cutover
self-grant or self-revoke
service actors receiving admin grants
deleting revoked grants
```

## Acceptance criteria

- Bootstrap is a local management operation for an existing active human.
- Bootstrap locks `AuthorityControl(id = 1) FOR UPDATE` before checking for an
  effective administrator, then creates the initial grant, one-time state, and
  audited success atomically in that transaction.
- Bootstrap succeeds exactly once and records the fixed system bootstrap actor.
- Every later bootstrap attempt fails with the stable conflict and is audited;
  bootstrap is never treated as an idempotent replay.
- Five admin roles and their system/project scope compatibility are enforced.
- Only an effective Access Administrator issues/revokes admin grants.
- Admin-grant create/revoke identical replay is idempotent; mismatched replay
  is rejected.
- State, idempotency result, authority event, and invalidation event commit
  atomically for every grant/revoke operation.
- Self-grant and self-revoke are denied.
- The shared `AuthorityControl` row serializes bootstrap and every operation
  that can remove the final effective Access Administrator.
- Migration enforces `AuthorityControl(id = 1)`, role/scope compatibility,
  active-grant partial uniqueness, ownership FKs, supporting indexes, and
  database-time timestamps.
- A PostgreSQL concurrency test runs simultaneous bootstrap attempts for
  different target profiles and proves exactly one grant, one audited success,
  and one audited stable conflict. Additional concurrent tests prove at least
  one effective Access Administrator remains.
- Bootstrap, self-grant/self-revoke, and final-administrator denials emit their
  specified authority events in the owning transaction.
- `POST/GET /api/v1/admin-role-grants`,
  `GET /api/v1/actors/{actor_profile_id}/admin-role-grants`, and
  `POST /api/v1/admin-role-grants/{grant_id}/revoke` have
  allow/deny/scope/privacy/rate-limit/replay tests.
- Migration tests cover immutable revoked history, prior-head upgrade,
  downgrade, and preserved attribution.
- Runbook assigns bootstrap custody, environment access, dry-run/evidence,
  retry/failure handling, and rollback responsibility.

## Verification commands

```bash
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic downgrade -1)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && .venv/bin/python -m ruff check app tests scripts)
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

Review bootstrap exposure, idempotency, role/scope matrix, and the exact lock
used for final-admin safety.

## Stop conditions

Stop if bootstrap requires SQL edits, a public secret, or final-admin safety is
implemented by an unlocked count.
