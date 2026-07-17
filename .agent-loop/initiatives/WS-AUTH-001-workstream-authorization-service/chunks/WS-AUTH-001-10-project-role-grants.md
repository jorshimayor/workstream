# Chunk Contract: WS-AUTH-001-10 - Project Qualification And Contributor Role Grants

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Implement immutable qualification snapshots and exact-project independent
`ProjectRoleGrant(submitter|reviewer|adjudicator)` create, list, and revoke
behavior under scoped Project Manager authority.

## Why this chunk exists

Project contributor authority must be durable, explicit, revocable, and
separate from both token claims and administrative roles.

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
backend/app/modules/projects/models.py
backend/app/modules/projects/repository.py
backend/app/api/router.py
backend/app/db/models.py
backend/app/modules/audit/**
backend/alembic/versions/0024_*.py
backend/tests/test_actors.py
backend/tests/test_projects.py
backend/tests/test_auth.py
backend/tests/test_alembic.py
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
automated grants from skills or reputation
self-grant or self-revoke of the issuer's own contributor grant through the
administrative project-grant operation
admin roles satisfying submitter/reviewer/adjudicator permissions
task/review lifecycle implementation
project/task/checker authorization cutover
```

## Acceptance criteria

- Snapshot is immutable, actor/project/requested-role-bound, privacy-bounded,
  and records unavailable evidence explicitly.
- Qualification snapshots and ProjectRoleGrants are owned by the authorization
  module; ActorProfile/IdentityLink remain actor-owned, and ProjectRepository
  remains the canonical project loader. No duplicate grant/project repository
  is introduced.
- Only a Project Manager whose active grant covers the project can issue or
  revoke a contributor grant.
- The same covered `project.role_grant.manage` permission provides a scoped,
  paginated contributor-candidate lookup for the grant workflow. It returns
  only minimal actor fields, filters unauthorized rows before totals/cursors,
  cannot enumerate unrelated project activity, and never exposes issuer
  subject, identity-link metadata, contact data, skills, or reputation as
  authority.
- Target must be an active human and cannot be the issuing manager.
- A manager who separately holds a contributor grant cannot revoke that grant
  through their own administrative request; denial is stable and audited.
- A partial unique index on `(actor_profile_id, project_id, role) WHERE status =
  'active'` permits at most one active grant for the same exact role while a
  contributor may hold active submitter, reviewer, and adjudicator rows
  concurrently.
- Issue never revokes another role. Regrant after revocation creates a new
  immutable row.
- Create and revoke require canonical request hashing: same key and
  same request returns the committed graph; same key with different request is
  rejected.
- State, idempotency result, audit event, and invalidation event commit in one
  transaction.
- Only manual creation is enabled; automated schema value cannot be emitted.
- Revocation is visible on the next authorization context build.
- Revocation evidence and invalidation identify the exact revoked role;
  downstream consumers reconcile only the matching task, review, or future
  adjudication responsibility.
- Project manager/admin role alone never creates contributor capability.
- PostgreSQL concurrency tests cover identical-role creates, concurrent
  different-role creates, regrant versus revoke, and revocation versus
  authorization.
- `POST/GET /api/v1/projects/{project_id}/role-grants`, grant detail, and grant
  revoke routes have multi-role, self-revoke, scope, privacy, rate-limit,
  replay, and negative tests.
- Every protected grant/candidate route declares one active `ActionId` mapped to
  `project.role_grant.read` or `project.role_grant.manage` against the
  canonically loaded project/grant target. Generated manifest-delta tests prove
  every surface introduced here has exactly one declaration.
- Contributor-candidate lookup has covered-manager allow, uncovered/cross-
  project deny, pagination/count concealment, minimal-field, rate-limit, and
  inactive/non-human exclusion tests; no UUID must be recovered from logs or
  direct database access.
- Migration enforces snapshot/grant ownership FKs, checks, partial unique and
  supporting indexes, database-time fields, immutability, prior-head upgrade,
  downgrade, and preserved history.

## Verification commands

```bash
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic downgrade -1)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_authorization.py tests/test_auth.py tests/test_actors.py \
  tests/test_projects.py --cov=app.modules.authorization \
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

Review exact-project scope, self-grant protection, role-specific snapshot
privacy, independent issue/revoke semantics, and absence of implicit grants.

## Stop conditions

Stop if contributor authority depends on a token role, inferred qualification,
or project ID supplied without canonical database resolution.
