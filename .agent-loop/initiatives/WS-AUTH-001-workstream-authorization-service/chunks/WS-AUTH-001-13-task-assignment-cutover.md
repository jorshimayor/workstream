# Chunk Contract: WS-AUTH-001-13 - Task Management And Assignment Cutover

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Move task creation/screen/release, queue visibility, contributor claim, assignment,
and start operations to scoped manager or exact-project submitter permissions
while preserving task lifecycle guards.

## Why this chunk exists

Task and assignment authorization can be reviewed independently from submission
and checker visibility.

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
backend/app/modules/tasks/router.py
backend/app/modules/tasks/service.py
backend/app/modules/tasks/authorization.py
backend/app/modules/tasks/repository.py
backend/app/modules/tasks/schemas.py
backend/app/modules/tasks/models.py
backend/app/modules/tasks/lifecycle.py
backend/alembic/versions/0025_*.py
backend/app/modules/authorization/**
backend/app/modules/audit/**
backend/app/api/deps/auth.py
backend/app/workers/authority_reconciliation.py
backend/app/workers/celery_app.py
backend/tests/test_tasks.py
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
submission create/read/finalize
checker trigger/read or contributor checker results
new terminal task states or unrelated lifecycle redesign
review models or self-review implementation
token role or legacy active-worker-profile fallback
```

## Acceptance criteria

- Scoped Project Manager manages tasks only in covered projects.
- TaskRepository remains the canonical task/assignment persistence loader and
  returns domain records. The task application service or a feature-owned
  resource loader composes ResourceContext; persistence does not depend on
  authorization DTOs, and authorization does not duplicate task queries.
- Submitter/both grant for the exact project is required for queue/claim/start,
  plus existing task availability, assignment, ownership, and state guards.
- Every migrated task/assignment route or reconciliation command declares one
  primary registered action against the canonically loaded project, task, or
  assignment target. Feature-owned TaskRepository facts remain authoritative.
- Generated OpenAPI/command manifest-delta tests prove every protected
  task/assignment surface migrated here has exactly one active `ActionId`
  declaration.
- Administrative roles alone cannot claim contributor work.
- Existing Project Manager task management remains project-scoped. The
  reasoned start override is separately authorized as
  `operations.task.start_override` for Operator recovery; matched permission,
  scope, reason, and audit event distinguish the two paths.
- Before `operations.task.start_override` becomes active, migration `0025` and
  the typed audit schema add that already approved identifier to the 49-item
  AUTH-05A audit base. Upgrade/downgrade/re-upgrade and direct-SQL parity tests
  preserve all prior audit rows and reject unknown identifiers.
- Operator `operations.status.read` exposes a read-only cross-project task-queue
  operational projection with bounded fields; it does not grant task mutation.
  Audit Authority `audit.read` exposes only covered task evidence. Both paths
  filter before counts/cursors, conceal unauthorized resources, redact contributor
  details, and have explicit mutation-denial tests.
- ProjectRoleGrant revocation and ActorProfile suspension/deactivation/link
  revocation reconcile exclusive submitter assignments idempotently. For
  `claimed` or `in_progress`, the active assignment closes as
  `authority_revoked`, the task returns to `ready`, `assigned_to` clears, and
  immutable prior work/audit history remains. A `needs_revision` task instead
  remains `needs_revision` with a durable unassigned revision obligation. A
  covered manager may reassign it only to an active exact-project submitter;
  the replacement receives the bounded contributor-visible prior findings, prepared
  revision context, supersession linkage, and replay requirements. Reactivation
  does not restore the old assignment. Submitted/evaluation/review-pending
  history is not rewritten.
- Reconciliation uses the authority invalidation event plus a durable worker or
  same-transaction consuming service with retry/ownership defined in the
  runbook. Review-lease reconciliation remains explicitly deferred to
  WS-REV-001.
- When the durable worker path is selected, it is explicitly registered in the
  existing Celery include list; no second worker registry or scheduler is added.
- Revoked/suspended actors fail on the next request and transaction recheck.
- Cross-project/contributor visibility remains concealed.
- No migrated operation uses token roles or `require_any_role()`.
- Task queue/claim/start remove their enumerated
  `LegacyWorkflowEligibilityCompatibility` consumers; only the submission
  consumer remains for chunk 14.
- The API drill provisions an exact-project submitter/both grant through the
  supported service/API path before claim. The legacy workflow-profile route
  remains bounded only because chunk 14 still owns the final submission
  compatibility consumer; task queue/claim/start no longer depend on it.
- The assignment persistence column, model/schema/service fields, response
  contract, and new audit payload keys use `contributor_id`. Migration `0025`
  preserves every existing assignment owner, supports downgrade, and removes
  the legacy storage name without exposing a public compatibility alias.
- Full backend suite and API contract drill pass.
- Tests cover revoke/suspend/reactivate before claim, while claimed, while in
  progress, at needs-revision, after submit, duplicate reconciliation,
  reconciliation worker retry, a second contributor reclaiming released work, and needs-revision
  reassignment preserving prior findings, locked/rebased context, submission
  supersession, and high/medium finding replay requirements.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests scripts)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_authorization.py tests/test_auth.py tests/test_tasks.py \
  --cov=app.modules.authorization --cov-report=term-missing --cov-fail-under=90)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python scripts/api_contract_e2e.py)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic downgrade -1)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
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

Review exact-project contributor grants, manager scope, assignment guards, and
absence of lifecycle changes.

## Stop conditions

Stop if submission/checker behavior or task lifecycle semantics outside the
explicit authority-invalidation assignment release must change.
