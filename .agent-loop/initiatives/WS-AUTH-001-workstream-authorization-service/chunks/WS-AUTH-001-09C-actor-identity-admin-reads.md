# Chunk Contract: WS-AUTH-001-09C - Actor And Identity-Link Administration Reads

## Goal

Activate privacy-bounded administrative reads for one canonical actor and that
actor's single v0.1 identity link.

## Allowed files

```text
backend/app/modules/actors/**
backend/app/modules/authorization/**
backend/app/api/router.py
backend/app/api/deps/authorization.py
backend/tests/test_actors.py
backend/tests/test_auth.py
backend/tests/test_authorization.py
backend/tests/test_api_controls.py
backend/scripts/api_contract_e2e.py
docs/spec_authorization_service.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-09C.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
actor or identity-link mutation
collection/list endpoints, totals, or cursor pagination
issuer, subject, email, raw reason, token, grant, or assignment disclosure
service-token admission
schema migration or new persistence table
artifact, task, review, project, or grant behavior
```

## Exact surfaces

| Route | ActionId | PermissionId | Target | Candidate |
|---|---|---|---|---|
| `GET /api/v1/actors/{actor_profile_id}` | `actor.profile.read` | `actor.profile.read_any` | exact actor profile | effective Access Administrator or Audit Authority grant |
| `GET /api/v1/actors/{actor_profile_id}/identity-links` | `actor.identity_link.read` | `actor.identity_link.read` | exact actor profile and linked identity metadata | effective Access Administrator or Audit Authority grant |

Actor response fields are ID, kind, status, provisioning method, display name,
created/updated/last-seen timestamps, and bounded lifecycle timestamps. Link
response fields are link ID, actor ID, subject kind, status, linked/last-verified
and bounded revoke/reactivate timestamps. Neither response exposes issuer,
subject, contact email, raw reason, token material, claim data, grants, or
service assignments.

## Boundary and acceptance

- Exactly two actions activate: totals are 65 actions, 12 active and 53
  planned. Every route has one manifest declaration and one typed target.
- Missing targets are concealed only after caller authorization; unauthorized
  callers receive no existence, count, timing, or field-shape oracle.
- Reads are not charged to the admin mutation limiter.
- Only successful caller verification timestamps advance. Target timestamps
  never change because they were read; denial and failure do not advance them.
- Allow/deny, role separation, suspended/deactivated caller, revoked caller
  link, privacy, 503 rollback, and OpenAPI behavior tests pass with at least 90
  percent focused actor/authorization coverage and the global 78 percent floor.

## Risk and reviewers

L1 / P1. Required: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, and test delta.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests scripts/api_contract_e2e.py)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_actors.py tests/test_auth.py tests/test_authorization.py \
  tests/test_api_controls.py)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python scripts/api_contract_e2e.py)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
git diff --check
```

## Human review focus

Review role separation, exact target loading, concealment order, caller-only
verification timestamps, and the absence of private identity or grant data.

## Stop condition

Stop after merge and signed memory. Do not start AUTH-09D automatically.
