# Chunk Contract: WS-AUTH-001-09 - Actor State, Identity Revocation, And Service Actors

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Implement actor suspension/reactivation/deactivation, identity-link
revoke/reactivate, controlled service-actor provisioning, and their audited,
idempotent authority invalidation behavior.

## Why this chunk exists

Local role grants are incomplete without immediate actor/link invalidation and
controlled service identity resolution.

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
backend/app/modules/audit/**
backend/tests/test_actors.py
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
service actors receiving Contributor domain, AdminRoleGrant, or ProjectRoleGrant
deactivation reversal
deleting actors, links, grants, or historical attribution
product adapter bindings or callback endpoints
```

## Acceptance criteria

- Suspension blocks later business mutations and is reversible.
- Deactivation is terminal and preserves history.
- Identity-link revocation blocks the same issuer subject immediately; link
  reactivation restores the same profile without duplication.
- Identity-link revocation for an effective Access Administrator takes the same
  `AuthorityControl FOR UPDATE` lock as grant/profile removal.
- Self-suspension/deactivation and final-admin loss are denied under the shared
  authority lock.
- Unknown services are denied without persistence.
- Access Administrator can pre-provision a service profile/link with reason.
- Agent and Space subjects remain unsupported and unpersisted.
- Every mutation is idempotent, reasoned, and audited without token material.
- Mixed concurrent link-revoke, grant-revoke, suspend, and deactivate attempts
  leave at least one authenticatable effective Access Administrator.
- `GET /api/v1/admin/actors`, actor detail, suspend/reactivate/deactivate,
  actor identity-link read, identity-link revoke/reactivate, and service actor
  create/list/detail routes from the adopted contract have
  allow/deny/privacy/rate-limit/replay tests.
- Suspension/link-revocation events explicitly require consuming lifecycle
  reconciliation; task assignment consumption belongs to chunk 13 and review
  lease consumption remains deferred to WS-REV-001.

## Verification commands

```bash
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

Review state-machine terminality, service separation, invalidation timing, and
preservation of historical records.

## Stop conditions

Stop if a consuming adapter authority must be invented or if a service must be
treated as a human/admin to make tests pass.
