# Chunk Contract: WS-AUTH-001-14 - Submission, Checker, And Audit Visibility Cutover

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Move submission precheck/create/read/finalize, checker trigger/read, checker
contributor projections, and task audit visibility to registered permissions and
canonical task/project/assignment guards.

## Why this chunk exists

Submission/checker authorization shares locked-task provenance and contributor
redaction rules but is separable from task claim and system-worker execution.

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
backend/app/modules/tasks/schemas.py
backend/app/modules/actors/**
backend/app/modules/checkers/router.py
backend/app/modules/checkers/service.py
backend/app/modules/authorization/**
backend/app/api/deps/auth.py
backend/tests/test_tasks.py
backend/tests/test_checkers.py
backend/tests/test_auth.py
backend/scripts/api_contract_e2e.py
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
checker execution/routing semantics or task lifecycle redesign
internal Celery worker authority cutover
review queue/lease/decision implementation
token role fallback
legacy active-worker-profile or workflow-eligibility compatibility fallback
```

## Acceptance criteria

- Exact-project submitter/both grant plus active assignment is required to
  create submissions; admin roles alone cannot submit.
- Manager repair/checker triggers require covered project permissions.
- Project Manager repair uses covered `project.task.manage`; Operator recovery
  uses distinct `operations.submission_gate.repair` and
  `operations.checker.retry` permissions. Each path requires a reason and
  records matched grant/permission without granting general project authority.
- Contributor reads preserve ownership, hidden-result redaction, and concealed
  not-found behavior.
- Audit reads expose only permission-appropriate bounded fields before counts.
- Operator `operations.status.read` receives only the bounded submission/checker
  operational projection required for recovery. Audit Authority `audit.read`
  receives covered task/submission/checker evidence-chain reads. Both are
  read-only, filter before counts/cursors, redact artifact bytes and unnecessary
  actor data, conceal unauthorized resources, and have mutation-denial tests.
- Revocation/suspension applies on next request and sensitive commit recheck.
- No migrated operation uses token roles or `require_any_role()`.
- Submission removes the final `LegacyWorkflowEligibilityCompatibility`
  consumer; eligibility is the exact-project submitter/both grant plus active
  assignment and lifecycle guards.
- With the final consumer removed, the legacy `/api/v1/workers/me/profile`
  route, typed-profile activation service/schema, and token-role workflow
  observation fields plus the now-unused compatibility adapter/allowlist are
  removed in the same chunk. Route-removal,
  stale-reference, fresh-database intake, and full API drill tests prove no
  intermediate release requires deleted metadata.
- For a replacement assignee on a durable `needs_revision` obligation,
  submission creation must consume that obligation atomically, link the
  superseded submission, and include replay for every prior high/medium finding
  under the prepared locked/rebased revision context. Missing linkage, context,
  or replay is denied without clearing or weakening the obligation. Tests cover
  successful replacement submission, each missing requirement, transaction
  failure/rollback, retry, and preservation of prior immutable attempts.
- Full backend suite and API contract drill pass.

## Verification commands

```bash
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

Review assignment ownership, manager repair scope, checker-result redaction,
audit disclosure, and unchanged checker routing.

## Stop conditions

Stop if authorization cutover requires changing checker outcomes, task states,
or review lifecycle behavior.
