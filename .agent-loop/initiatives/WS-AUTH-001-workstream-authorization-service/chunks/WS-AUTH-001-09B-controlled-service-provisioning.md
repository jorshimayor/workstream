# Chunk Contract: WS-AUTH-001-09B - Controlled Service Actor Provisioning

## Goal

Activate only `actor.service.provision` and let an effective Access
Administrator bind one opaque Identity Issuer subject to one unprovisioned
fixed service ActorProfile whose authority is derived from the closed matrix.

## Why this chunk exists

AUTH-09A established stable fixed identities and inert matrix candidates but
created no supported binding path. This chunk lets one already-authorized human
administrator bind the configured Identity Issuer to one fixed local service
principal without admitting that principal to runtime authorization.

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
scripts/test_agent_gates.py
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
compatibility aliases, fallback constructors, dual issuer paths, or a second
service identity model
```

## Exact surface

| Route | ActionId | PermissionId | Canonical target | Candidate |
|---|---|---|---|---|
| `POST /api/v1/service-actors` | `actor.service.provision` | `actor.service.provision` | requested unprovisioned fixed service identity | effective system-scoped Access Administrator grant |

The strict body contains only `service_identity`, opaque `subject`, and required
`reason`. `service_identity` is the closed `ServiceIdentity` enum. `subject` is
preserved byte-for-byte as one non-empty 200-character identity anchor and is
never normalized, logged, returned, or placed in evidence. `reason` is bounded
to 1-500 UTF-8 bytes and only its canonical digest enters idempotency input.

The issuer is the exact issuer on the successfully verified caller's active
server-owned identity link. The request cannot select or override it. A new
service ActorProfile receives a random UUID independent of issuer or subject;
the fixed `service_identity` is its stable local name. `created_by` and
`linked_by` are the authorized human ActorProfile ID.

The response contains only `actor_profile_id`, `service_identity`, fixed active
actor/link statuses, `manual_service_provisioning`, `created_at`, and
`linked_at`. It returns no identity-link ID, subject, issuer, email, raw reason,
grant, token material, or redundant assignment list.

## Transaction and evidence contract

The route first reserves the caller/operation/idempotency namespace, then the
kernel locks `AuthorityControl`, the caller's exact identity link and profile,
and the matched system Access Administrator grant. After an allowed decision,
actor persistence serializes the fixed service identity and exact issuer/subject
before checking occupancy. ActorProfile, ActorIdentityLink, idempotency
completion, `service_actor_provisioned`, and authority-invalidation evidence
flush in the same caller-owned transaction; the route commits once.

The success and invalidation events bind to `actor.service.provision`, the
matched Access Administrator grant, the created ActorProfile, and the exact
idempotency record. They contain fixed lifecycle facts and request digests only,
never issuer, subject, raw reason, token claims, email, or matrix memberships.
The invalidation transition is ineffective-to-effective for the new local actor
record; it does not claim that any service ActionId is executable.

Conflict codes are closed: `service_identity_already_provisioned` for an
occupied fixed identity, `identity_subject_already_linked` for an occupied exact
issuer/subject, and `idempotency_mismatch` for key/request drift. SQL,
authorization-evidence, invalidation-evidence, or commit failure maps to the
retryable `service_unavailable` 503 envelope after rollback.

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
- Replay revalidates the current human caller and matched grant, reconstructs
  the original committed response from immutable creation facts, and does not
  touch the service ActorProfile or service identity-link verification fields.
- The admin mutation limiter applies; response/log/audit tests prove opaque
  subject, issuer, token, email, and raw reason are not disclosed.
- Provisioning confers no executable service authority. Only AUTH-09E may add
  fixed-service admission after 09C and 09D merge; this chunk does not weaken
  `get_authorization_actor`, admit a service caller, or authorize any planned
  artifact action.
- Focused actor and authorization subsystem coverage is at least 90 percent;
  GitHub Backend preserves the repository-wide 78 percent floor.

## Migration and compatibility boundary

No schema migration is required: migration `0023` already owns the fixed
identity column and constraints, while `0021`/`0022` audit parity already knows
the action/permission pair and service creation operation. AUTH-09B changes the
typed availability row only. Historical migrations remain immutable. No old
route, alias, inferred identity, token-role authority, or fallback path is
retained or introduced.

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
