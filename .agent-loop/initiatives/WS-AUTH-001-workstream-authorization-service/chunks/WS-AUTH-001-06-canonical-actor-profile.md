# Chunk Contract: WS-AUTH-001-06 - Canonical Actor Profile And Identity Link

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Replace the current identity-plus-typed-profile registry with one canonical
ActorProfile, one ActorIdentityLink, atomic first-human provisioning, and
request-time actor resolution using the established evidence foundation.

## Why this chunk exists

All later grants and revocation depend on an unambiguous local actor and active
identity link.

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
backend/app/modules/tasks/service.py
backend/app/modules/tasks/router.py
backend/app/modules/tasks/schemas.py
backend/app/api/deps/auth.py
backend/app/api/routes/auth.py
backend/app/schemas/auth.py
backend/app/db/models.py
backend/app/modules/audit/**
backend/alembic/versions/0018_*.py
backend/tests/test_actors.py
backend/tests/test_auth.py
backend/tests/test_alembic.py
backend/tests/test_projects.py
backend/tests/test_tasks.py
backend/tests/test_checkers.py
backend/scripts/api_contract_e2e.py
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
admin or project grant creation
product-surface authorization cutover
implicit grants from legacy roles/profiles
guessing human/service kind from email, subject shape, or role claims
review or compensation models
```

## Acceptance criteria

- Exactly one canonical ActorProfile maps to one issuer/subject identity link.
- First valid human access creates profile, link, and audit evidence atomically.
- Concurrent first access creates no duplicate or orphan.
- Unknown service creates nothing and is denied; agent/Space creates nothing.
- Suspended/deactivated schema states exist but administration remains later.
- Existing actor IDs are preserved only through explicit safe classification.
- Classified legacy `ActorIdentity.actor_id` must parse as UUID and becomes the
  canonical `ActorProfile.id`; legacy typed profile row IDs never do.
- Non-empty ambiguous legacy data fails with a precise remediation path.
- Typed legacy profiles do not become grants.
- Existing task claim/start/submission eligibility remains operable only through
  `LegacyWorkflowEligibilityCompatibility`, which reads classified legacy
  workflow metadata and grants no product permission. Its exact task-service
  consumers are enumerated in a shrinking allowlist: chunk 13 removes
  queue/claim/start, chunk 14 removes submission and deletes the now-unused
  adapter/allowlist, and chunk 15 proves no obsolete path remains.
- Until exact-project grants exist, `/api/v1/workers/me/profile` remains an
  enumerated compatibility activation path for fresh-database intake. It writes
  only classified non-authoritative workflow metadata, cannot populate the
  canonical actor or grant models from token roles, and authorizes old workflow
  call sites only through `LegacyWorkflowEligibilityCompatibility`. The API
  drill proves first-human provisioning plus this supported compatibility path;
  chunk 13 removes its queue/claim/start consumers after grant provisioning;
  chunk 14 removes the route, activation service/schema, token-role observation
  fields, final submission consumer, and compatibility adapter together.
- Provisioning uses the established idempotency/audit/invalidation foundation
  and commits the profile, link, and events atomically.
- `/api/v1/actors/me` returns Contributor domain with no implied project/admin
  authority.
- `GET /api/v1/actors/me` and `PATCH /api/v1/actors/me` have request, privacy,
  unknown-field, negative-state, first-access allow/429, and
  rate-control-unavailable tests.
- Migration enforces every ActorProfile/ActorIdentityLink check, unique and
  supporting index, one-link ownership constraint, UTC/database-time field,
  and immutable-history rule from the adopted contract.
- Tests cover prior-head upgrade, failed ambiguous upgrade, successful
  classified upgrade, and preserved attribution. Downgrade/rollback must
  succeed after the external classification envelope is deleted post-upgrade,
  using only its durably recorded version/checksum and migration state.

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

Review legacy-data handling, UUID identity preservation, atomic provisioning,
final audit/idempotency ownership, and proof that no old profile row grants
authority.

## Stop conditions

Stop if legacy subject kind cannot be established safely, migration would
orphan historical actor references, an intermediate release cannot execute the
existing intake lifecycle, or a parallel canonical profile is needed.
