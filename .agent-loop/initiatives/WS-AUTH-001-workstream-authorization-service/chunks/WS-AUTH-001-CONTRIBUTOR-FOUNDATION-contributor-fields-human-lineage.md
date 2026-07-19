# Chunk Contract: WS-AUTH-001-CONTRIBUTOR-FOUNDATION - Contributor Fields And Canonical-Human Lineage

## Status

Active contract review. PR #152 merged AUTH-09D-B as `93dd392`; signed
schema-v2 memory at `912a6254` stopped and named this same-initiative
successor. The user explicitly started this chunk on 2026-07-19. Its branch
starts from trusted `main` at `93dd392`, whose single Alembic head is
`0026_actor_profile_lifecycle`.

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Clean-cut the two current human attribution fields to `contributor_id`, bind
them to canonical human `ActorProfile` records at the database boundary, and
expose one transaction-local canonical-active-human revalidation capability for
later task and revision mutations.

## Why this chunk exists

The previous plan deferred the assignment rename to AUTH-13 and the submission
rename to AUTH-14. That ordering blocks REV from safely adding canonical task,
guide, and submission lineage until most product authorization cutovers finish.
This bounded schema foundation removes that cycle without activating an action,
changing a grant, or implementing review behavior.

## Risk class

L1

## SLA

P1

## Preconditions

- AUTH-09D-B is merged and signed automated memory names this chunk as its
  same-initiative successor.
- The branch is created from current trusted `main`, records the exact single
  Alembic head, and allocates only the then-current next migration.
- Preimplementation review approves the exact database primitive used to
  enforce human ActorProfile lineage and its downgrade behavior.

## Allowed files

```text
backend/app/modules/actors/{models,repository}.py
backend/app/modules/authorization/{repository,service,runtime}.py
backend/app/modules/tasks/{models,schemas,repository,service}.py
backend/app/modules/checkers/** only for exact renamed contributor-ID reads
backend/app/db/models.py
backend/alembic/versions/<then-current-next>_contributor_foundation.py
backend/tests/test_actors.py
backend/tests/test_authorization.py
backend/tests/test_auth.py
backend/tests/test_tasks.py
backend/tests/test_checkers.py
backend/tests/test_alembic.py
backend/scripts/api_contract_e2e.py
.github/workflows/backend.yml only if a persistent focused coverage command is missing
docs/architecture_data_model.md
docs/operations_authorization_service.md
docs/spec_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-CONTRIBUTOR-FOUNDATION.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
permission, ActionId, owner, evaluator, or availability changes
project/admin role grant changes
AUTH-09E service admission or fixed-service authority
task, assignment, submission, checker, review, or revision lifecycle state or
transition changes beyond the exact active-human write guard below
Submission task-assignment lineage, predecessor chains, or guide stamps owned by REV
renaming the separately enumerated AUTH-14 attestation and contributor-facing fields
token-role removal, legacy workflow eligibility removal, or AUTH-13/14 route cutover
compatibility aliases, dual fields, fallback reads/writes, or data duplication
```

## Acceptance criteria

- The retired `TaskAssignment` human-owner field is clean-cut to
  `contributor_id` across the
  PostgreSQL column and index, SQLAlchemy model, Pydantic response, service and
  repository references, audit payloads, scripts, and tests. The old name is
  absent; no property, response alias, shadow column, or dual write remains.
- The retired `Submission` human-owner field receives the same clean cut.
  Existing task,
  submission, checker, and revision behavior and attribution remain unchanged
  apart from the intentional response-field rename and fail-closed
  transaction-local active-human write revalidation.
- Both `contributor_id` columns are non-null foreign keys to the canonical
  `actor_profiles.id` root. A single reviewed, reusable PostgreSQL lineage
  primitive rejects a service ActorProfile for either field and is suitable for
  later canonical-human actor fields without creating another actor registry.
- The migration preflight reports every missing ActorProfile, non-human
  ActorProfile, malformed identifier, and inconsistent assignment/submission
  attribution with bounded row identifiers, then aborts atomically. It never
  guesses an actor, maps by email, selects the latest profile, or fabricates
  remediation data.
- Existing valid values are preserved exactly by column rename. Upgrade and
  downgrade preserve values and indexes; downgrade refuses if a downstream
  constraint depends on the reusable lineage primitive.
- Direct SQL tests reject missing and service ActorProfiles for both tables,
  accept canonical human ActorProfiles, and prove later suspension or
  deactivation does not rewrite immutable historical attribution.
- AUTH exposes one narrow transaction-local operation that locks and
  revalidates an exact ActorProfile as active and human under the canonical
  profile-before-resource order. It returns no grants or identity claims and
  introduces no second authorization path.
- Task claim and submission creation consume that operation at their sensitive
  write boundary without changing their existing role, task-state, assignment,
  checker, or commit semantics. Profile suspension/deactivation racing either
  write is proved in both lock orders; the losing write leaves no assignment,
  submission, checker result, audit mutation, or partial evidence.
- Behavior tests preserve claim, start, initial submit, checker-caused revision
  resubmission, audit history, idempotency, concealment, and rollback behavior
  while asserting the canonical `contributor_id` response and evidence shape.
- Migration tests cover valid upgrade/downgrade/upgrade, each unsafe preflight
  refusal, direct-SQL kind enforcement, dependency-aware downgrade refusal, and
  one Alembic head.
- Changed actor, authorization, and task modules remain at or above 90 percent
  focused coverage; repository-wide coverage does not fall below 78 percent.

## Proposed implementation

1. Allocate migration `0027_contributor_foundation` from the confirmed single
   head. Under an access-exclusive lock on `actor_profiles`,
   `task_assignments`, and `submissions`, preflight bounded identifiers and
   attribution consistency, rename both columns and their generated indexes,
   and add non-null foreign keys to `actor_profiles.id` without rewriting
   values.
2. Install one reusable PostgreSQL trigger function whose column name is an
   explicit trigger argument. Its table-specific triggers reject any new or
   changed contributor reference whose referenced profile is not human. The
   foreign keys own existence; the trigger owns kind. Actor status is not part
   of historical lineage, so later suspension or deactivation remains valid.
3. Add one authorization repository/service operation that locks the exact
   `ActorProfile` row with `FOR UPDATE`, refreshes it in the current
   transaction, and returns only success/failure for `human` plus `active`.
   It does not inspect identity links, grants, roles, actions, token claims, or
   permissions.
4. Invoke that guard after the existing coarse role check but before loading
   task or assignment resources in claim and submission creation. Map failure
   to one stable task-layer 403 and keep caller-owned commit/rollback behavior.
5. Clean-cut ORM, response, audit, checker-context, script, test, and current
   documentation reads to `contributor_id`. Keep `worker_attestation` and
   legacy role/eligibility cutover fields unchanged because AUTH-13/14 own
   those separate compatibility removals.
6. Prove migration refusal and preservation, direct-SQL lineage enforcement,
   claim/submission behavior and rollback, and both lock orders against profile
   suspension/deactivation before the focused and repository-wide evidence
   gates.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests scripts)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_actors.py tests/test_auth.py tests/test_alembic.py \
  --cov=app.modules.actors --cov-report=term-missing --cov-fail-under=90)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_authorization.py tests/test_auth.py tests/test_alembic.py \
  --cov=app.modules.authorization --cov-report=term-missing --cov-fail-under=90)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_tasks.py tests/test_checkers.py tests/test_alembic.py \
  --cov=app.modules.tasks --cov-report=term-missing --cov-fail-under=90)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python scripts/api_contract_e2e.py)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic downgrade -1)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
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

Review the clean absence of retired human-owner identifiers, exact preservation of attribution,
database rejection of service identities, migration remediation/refusal, race
closure, and the absence of AUTH-13/14 or REV behavior.

## Stop conditions

Stop if migration requires guessed identity mapping, a second actor registry,
an API compatibility alias, changed lifecycle behavior, or an authorization
availability change. Stop after merge and signed memory; do not start AUTH-09E,
REV-02A, or another chunk automatically.
