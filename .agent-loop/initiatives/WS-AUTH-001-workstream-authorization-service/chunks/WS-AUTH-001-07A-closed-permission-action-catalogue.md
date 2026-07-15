# Chunk Contract: WS-AUTH-001-07A - Closed Permission And Action Catalogue

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Create one closed typed catalogue for all 73 approved PermissionIds and the
exact reserved recovery/artifact ActionIds, then add typed and PostgreSQL action
evidence parity without making any action executable.

## Why this chunk exists

The deny-by-default kernel cannot safely start until permission and action
identifiers have one validated source, planned actions fail closed, and audit
storage can preserve a stable action identifier.

## Risk routing

- Risk class: L1
- SLA: P1
- Work type: authorization architecture, audit schema, migration, tests, docs
- Human gate: explicit PR review and merge approval
- Required reviewers: senior engineering, QA/test, security/auth, product/ops,
  architecture, CI integrity, docs, reuse/dedup, test delta

## Allowed files

```text
backend/app/modules/authorization/**
backend/app/modules/audit/**
backend/app/modules/tasks/models.py
backend/alembic/versions/0021_authorization_action_evidence.py
backend/tests/test_authorization.py
backend/tests/test_audit.py
backend/tests/test_alembic.py
docs/spec_authorization_service.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-07A.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
authorization decision evaluation
active route or command declarations
grant tables, grant queries, or role expansion
actor, project, task, checker, review, contribution, or artifact API cutover
feature resource composers, guards, or repositories
dynamic permissions or policy language
public permission/admin-role/context APIs
```

## Exact reserved ActionIds

The catalogue registers the following as `planned`; none can authorize:

```text
operations.task.start_override
operations.submission_gate.repair
operations.checker.retry
artifact.binding.read
artifact.replica.read
artifact.receipt.read
artifact.verification_job.read
artifact.verification_job.retry
artifact.recovery_attempt.read
artifact.audit.read
operations.artifact_storage_admission.read
artifact.guide_source.ingest
artifact.guide_source.read
artifact.upload_session.create
artifact.upload_session.read
artifact.upload_item.write
artifact.upload_session.seal
artifact.upload_session.cancel
artifact.upload_session.expire
artifact.guide_source.binding.create
artifact.submission.binding.create
artifact.checker_output.binding.create
artifact.verification.execute
artifact.pending_work.scan
artifact.put_attempt.resolve
artifact.pre_submit.checker_input.materialize
artifact.post_submit.checker_input.materialize
artifact.checker_output.write
```

Each planned definition stores only `action_id`, its approved `permission_id`,
the owning specification/chunk, and `availability=planned`. Principal class,
resource facts, guards, composers, concealment, and revalidation are activation
blueprints owned by later chunks and are not registered here.

## Acceptance criteria

- `PermissionId` is the single closed typed source for exactly the 73 approved
  values in `docs/spec_authorization_service.md`.
- Existing audit validation consumes that source rather than maintaining a
  second permission literal set.
- A frozen action catalogue contains exactly the 28 planned ActionIds above,
  with exact approved PermissionId mapping, owner, and availability.
- Catalogue construction fails on duplicate or unknown actions, unknown
  permissions, invalid owners, invalid availability, missing approved entries,
  or extra entries.
- Planned actions cannot be resolved as executable and cannot be promoted by
  configuration or request input.
- Artifact storage admission remains mapped only to
  `operations.status.read`; it grants no `artifact.*` capability.
- Migration `0021` adds nullable `audit_events.action_id`, preserves all
  historical rows as null, and constrains every non-null value to the registered
  ActionId set.
- `AuthorityAuditEventInput` admits a bounded registered `action_id`; unknown
  values fail before rejected input can escape diagnostics.
- Existing non-action authority events remain valid with null `action_id`.
- Downgrade refuses to discard any non-null action evidence. A clean database
  with only null action IDs can downgrade and re-upgrade.
- Direct SQL proves unknown ActionIds fail and registered ActionIds persist.
- The canonical specification separates four-field planned registry metadata
  from later feature activation blueprints.
- Operations docs cover startup catalogue failure, evidence inspection, and the
  guarded rollback rule.
- No workflow, dependency, test skip, coverage exclusion, or global threshold
  changes.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests alembic/versions/0021_authorization_action_evidence.py)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=<isolated-test-db> \
  .venv/bin/python -m pytest -q tests/test_authorization.py tests/test_audit.py \
  tests/test_alembic.py --cov=app.modules.authorization \
  --cov=app.modules.audit --cov-branch --cov-report=term-missing \
  --cov-fail-under=90)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=<isolated-test-db> \
  .venv/bin/python scripts/run_isolated_tests.py tests/test_authorization.py \
  tests/test_audit.py tests/test_alembic.py)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
git diff --check
```

GitHub Backend remains authoritative for the full suite and repository-wide 78
percent floor.

## Human review focus

Review exact 73-permission parity, exact 28-action planned mapping, inability to
execute planned actions, audit privacy, PostgreSQL constraint parity, historical
null preservation, and guarded downgrade.

## Stop conditions

Stop if the catalogue requires feature resource facts, executable grant
candidates, a generic policy engine, or dynamic/user-authored identifiers.

Stop after merge and signed memory. Do not start AUTH-07B automatically.
