# Chunk Contract: WS-AUTH-001-07A - Closed Permission And Action Catalogue

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Create one closed typed catalogue for all 73 approved PermissionIds and the
exact reserved self/recovery/artifact ActionIds, then add typed and PostgreSQL action
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

## Exact planned action catalogue

The owner is a full canonical chunk ID. The closed owner set is exactly the
distinct values in this table; abbreviations, free-form domains, and aliases
are invalid. Every row has `availability=planned` and cannot authorize.

| ActionId | PermissionId | Owner | Availability |
|---|---|---|---|
| `actor.profile.read_self` | `actor.profile.read_self` | `WS-AUTH-001-07B` | `planned` |
| `actor.profile.update_self` | `actor.profile.update_self` | `WS-AUTH-001-07B` | `planned` |
| `operations.task.start_override` | `operations.task.start_override` | `WS-AUTH-001-13` | `planned` |
| `operations.submission_gate.repair` | `operations.submission_gate.repair` | `WS-AUTH-001-14` | `planned` |
| `operations.checker.retry` | `operations.checker.retry` | `WS-AUTH-001-14` | `planned` |
| `artifact.binding.read` | `artifact.binding.read` | `WS-ART-001-02D` | `planned` |
| `artifact.replica.read` | `artifact.replica.read` | `WS-ART-001-02D` | `planned` |
| `artifact.receipt.read` | `artifact.receipt.read` | `WS-ART-001-02D` | `planned` |
| `artifact.verification_job.read` | `artifact.verification_job.read` | `WS-ART-001-02D` | `planned` |
| `artifact.verification_job.retry` | `artifact.verification_job.retry` | `WS-ART-001-02D` | `planned` |
| `artifact.recovery_attempt.read` | `artifact.recovery_attempt.read` | `WS-ART-001-02D` | `planned` |
| `artifact.audit.read` | `artifact.audit.read` | `WS-ART-001-02D` | `planned` |
| `operations.artifact_storage_admission.read` | `operations.status.read` | `WS-ART-001-02D` | `planned` |
| `artifact.guide_source.ingest` | `artifact.guide_source.ingest` | `WS-ART-001-03` | `planned` |
| `artifact.guide_source.read` | `artifact.guide_source.read` | `WS-ART-001-03` | `planned` |
| `artifact.upload_session.create` | `artifact.upload_session.create` | `WS-ART-001-04A` | `planned` |
| `artifact.upload_session.read` | `artifact.upload_session.read` | `WS-ART-001-04A` | `planned` |
| `artifact.upload_item.write` | `artifact.upload_item.write` | `WS-ART-001-04A` | `planned` |
| `artifact.upload_session.seal` | `artifact.upload_session.seal` | `WS-ART-001-04A` | `planned` |
| `artifact.upload_session.cancel` | `artifact.upload_session.cancel` | `WS-ART-001-04A` | `planned` |
| `artifact.upload_session.expire` | `artifact.upload_session.expire` | `WS-ART-001-04A` | `planned` |
| `artifact.guide_source.binding.create` | `artifact.binding.create` | `WS-ART-001-03` | `planned` |
| `artifact.submission.binding.create` | `artifact.binding.create` | `WS-ART-001-05` | `planned` |
| `artifact.checker_output.binding.create` | `artifact.binding.create` | `WS-ART-001-06B` | `planned` |
| `artifact.verification.execute` | `artifact.verification.execute` | `WS-ART-001-02D` | `planned` |
| `artifact.pending_work.scan` | `artifact.pending_work.scan` | `WS-ART-001-02D` | `planned` |
| `artifact.put_attempt.resolve` | `artifact.put_attempt.resolve` | `WS-ART-001-02D` | `planned` |
| `artifact.pre_submit.checker_input.materialize` | `artifact.checker_input.materialize` | `WS-ART-001-04B` | `planned` |
| `artifact.post_submit.checker_input.materialize` | `artifact.checker_input.materialize` | `WS-ART-001-06A` | `planned` |
| `artifact.checker_output.write` | `artifact.checker_output.write` | `WS-ART-001-06B` | `planned` |

Each definition stores only these four fields. Principal class, resource facts,
guards, composers, concealment, and revalidation are activation blueprints
owned by later chunks and are not registered here.

## Acceptance criteria

- `PermissionId` is the single closed typed source for exactly the 73 approved
  values in `docs/spec_authorization_service.md`.
- Existing audit validation consumes that source rather than maintaining a
  second permission literal set.
- A frozen action catalogue contains exactly the 30 planned ActionIds above,
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
- Typed validation and PostgreSQL enforce every non-null ActionId's exact
  PermissionId mapping from the 30-row catalogue; an action cannot be persisted
  with another registered permission.
- Every PermissionId outside migration `0018`'s historical 49-value set requires
  a non-null ActionId whose catalogue row maps to that PermissionId. The three
  planned actions mapped to an existing PermissionId may still carry their
  registered action while the historical permission remains valid without one
  for pre-`0021` event shapes.
- A non-null `action_id` is valid only for `SensitiveAuthorizationAllowed` or
  `SensitiveAuthorizationDenied`; unrelated authority/lifecycle events must
  remain null.
- Migration `0021` replaces the 49-value permission constraint with exact
  73-value typed/PostgreSQL parity without changing historical values.
- `AuthorityAuditEventInput` admits a bounded registered `action_id`; unknown
  values and action/permission mismatches fail before rejected input can escape
  diagnostics.
- Because all 30 actions remain `planned`, `AuthorityAuditEventInput` rejects
  `SensitiveAuthorizationAllowed` when any of them is present. A planned action
  may be persisted only as bounded `SensitiveAuthorizationDenied` evidence;
  activation chunks own later allowed evidence.
- PostgreSQL is deliberately availability-neutral: it enforces registration,
  decision-event-only use, and the exact action-to-permission mapping, but does
  not freeze `planned` versus `active`. Later owner chunks activate catalogue
  rows in typed code without altering migration `0021`.
- Existing non-action authority events remain valid with null `action_id`.
- Downgrade refuses when either any non-null action evidence or any PermissionId
  outside the historical 49-value set exists in `permission_id`, a permission-
  registry target reference, or a permission-registry invalidation reference. A
  clean database satisfying all predicates can downgrade, restores the exact
  prior 49-value permission constraint, drops the action column/constraint, and
  re-upgrades.
- Downgrade takes `LOCK audit_events IN ACCESS EXCLUSIVE MODE` before checking
  both refusal predicates or changing constraints. Deterministic independent-
  session proof shows a concurrent insert cannot pass between the checks and
  destructive DDL.
- Direct SQL proves unknown ActionIds and mismatched action/permission pairs
  fail and every new permission without its mapped action fails. Direct-SQL
  positive fixtures use denied evidence for every planned ActionId; denial-only
  availability is tested at `AuthorityAuditEventInput`, not as a PostgreSQL
  constraint.
- The canonical specification separates four-field planned registry metadata
  from later feature activation blueprints.
- Operations docs cover startup catalogue failure, evidence inspection, and the
  guarded rollback rule.
- No workflow, dependency, test skip, coverage exclusion, or global threshold
  changes.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests alembic/versions/0021_authorization_action_evidence.py)
(cd backend && tmp_dir=$(mktemp -d) && trap 'rm -rf "$tmp_dir"' EXIT && \
  .venv/bin/coverage erase && \
  WORKSTREAM_TEST_ADMIN_DATABASE_URL=<local-admin-dsn> \
  .venv/bin/python scripts/run_isolated_tests.py \
  --metadata-json "$tmp_dir/07a.json" --timeout-seconds 1800 -- \
  .venv/bin/python -m pytest -q tests/test_authorization.py tests/test_audit.py \
  tests/test_alembic.py --cov=app.modules.authorization \
  --cov=app.modules.audit --cov-branch --cov-report= --cov-fail-under=0 && \
  .venv/bin/coverage report --include='app/modules/authorization/*' \
  --fail-under=90 && \
  .venv/bin/coverage report --include='app/modules/audit/*' --fail-under=90)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
git diff --check
```

GitHub Backend remains authoritative for the full suite and repository-wide 78
percent floor.

## Human review focus

Review exact 73-permission parity, exact 30-action planned mapping, typed/SQL
mapping enforcement, inability to record planned actions as allowed, audit
privacy, PostgreSQL constraint parity, historical null preservation, and guarded
downgrade.

## Stop conditions

Stop if the catalogue requires feature resource facts, executable grant
candidates, a generic policy engine, or dynamic/user-authored identifiers.

Stop after merge and signed memory. Do not start AUTH-07B automatically.
