# Chunk Contract: WS-AUTH-001-09B - Controlled Service Actor Provisioning

## Goal

Activate only `actor.service.provision` and let an effective Access
Administrator bind one opaque Identity Issuer subject to one unprovisioned
fixed service ActorProfile whose authority is derived from the closed matrix.

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
backend/tests/test_api_rate_controls.py
backend/scripts/api_contract_e2e.py
docs/spec_authorization_service.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-09B.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
client-supplied issuer, ActionIds, PermissionIds, roles, grants, or assignments
generic or unknown service identities
service actor list/detail routes
broadening the human admin dependency to admit service callers
artifact action activation, resource composition, or adapter attachment
```

## Exact surface

| Route | ActionId | PermissionId | Canonical target | Candidate |
|---|---|---|---|---|
| `POST /api/v1/service-actors` | `actor.service.provision` | `actor.service.provision` | requested unprovisioned fixed service identity | effective system-scoped Access Administrator grant |

The strict body contains only `service_identity`, opaque `subject`, and required
reason. The issuer is the server-configured canonical Identity Issuer. Response
fields are actor profile ID, service identity, actor/link status, provisioning
method, and timestamps; it returns no subject, issuer, email, raw reason, grant,
token material, or redundant assignment list.

## Acceptance criteria

- Exactly one action becomes active: totals are 65 actions, 10 active and 55
  planned. One generated manifest declaration exists for the route.
- Provisioning atomically creates one active service ActorProfile carrying the
  selected fixed `service_identity`, one active exact issuer/subject link,
  idempotency completion, success evidence, and invalidation evidence. It
  creates no assignment or grant rows.
- Same key/same canonical request returns the original committed result after
  current caller authority is revalidated; mismatch returns
  `idempotency_mismatch`; a new key for an occupied identity or subject returns
  a stable conflict without partial writes.
- Unknown service identities, service callers, agent/space subjects, duplicate
  subjects, SQL/evidence/commit failure, and unavailable persistence create no
  partial actor/link/idempotency/evidence state. Retryable database
  failure is the stable 503 envelope.
- Only the successful human caller verification timestamps advance. A replay,
  denial, conflict, or failure does not fabricate service verification.
- The admin mutation limiter applies; response/log/audit tests prove opaque
  subject, issuer, token, email, and raw reason are not disclosed.
- A separate future typed service dependency may consume fixed service
  identities; this
  chunk does not weaken `get_authorization_actor` or authorize any planned
  artifact action.
- Focused actor and authorization subsystem coverage is at least 90 percent;
  GitHub Backend preserves the repository-wide 78 percent floor.

## Risk and reviewers

L1 / P1. Required: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, and test delta.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests scripts/api_contract_e2e.py)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_actors.py tests/test_auth.py tests/test_authorization.py \
  tests/test_api_controls.py tests/test_api_rate_controls.py)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python scripts/api_contract_e2e.py)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
git diff --check
```

## Human review focus

Review deterministic local service identity, opaque external subject binding,
server-owned issuer/matrix, no service grants, idempotent atomic creation,
privacy, and planned artifact-action denial.

## Stop condition

Stop after merge and signed memory. Do not start AUTH-09C automatically.
