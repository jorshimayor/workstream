# Chunk Contract: WS-AUTH-001-09D-A - Profile Lifecycle And Evidence Repair

Initiative: `WS-AUTH-001` | Risk: L1 / P1 | Status: preimplementation review

## Goal

Repair lifecycle evidence parity and activate exact Access Administrator
profile suspension, reactivation, and terminal deactivation with atomic replay,
audit, invalidation, and final-admin safety.

## Why This Chunk Exists

AUTH-09C supplies privacy-bounded exact-target reads. Administrators now need
safe profile lifecycle controls before service admission or project cutovers.
The existing schema pre-registers lifecycle operations, but it lacks profile
reactivation provenance and incorrectly forces reactivation invalidation from
`effective=true` to `effective=false`.

## Allowed Files

```text
backend/alembic/versions/0026_actor_profile_lifecycle.py
backend/app/db/models.py
backend/app/modules/actors/**
backend/app/modules/authorization/**
backend/app/modules/audit/**
backend/app/api/router.py
backend/app/api/deps/authorization.py
backend/tests/test_actors.py
backend/tests/test_auth.py
backend/tests/test_authorization.py
backend/tests/test_audit.py
backend/tests/test_api_controls.py
backend/tests/test_api_rate_controls.py
backend/tests/test_alembic.py
backend/scripts/api_contract_e2e.py
scripts/test_agent_gates.py
docs/spec_authorization_service.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-09D-A.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not Allowed

```text
identity-link lifecycle routes or action activation
new identity link or actor replacement
deactivation reversal or actor/link deletion
service admission or service-action evaluation
AdminRoleGrant, ProjectRoleGrant, Contributor, task, review, revision, artifact,
payment, or reputation mutation
compatibility route, response alias, fallback path, or old migration edit
```

## Exact Surface And Authority

```text
POST /api/v1/actors/{actor_profile_id}/suspend
POST /api/v1/actors/{actor_profile_id}/reactivate
POST /api/v1/actors/{actor_profile_id}/deactivate
```

The routes declare and activate only the identically named ActionIds and
PermissionIds. Each requires an effective system-scoped Access Administrator,
the admin mutation limiter, a UUID `Idempotency-Key`, and one strict reason body.
Audit Authority, project-scoped authority, service callers, token roles, and
every other candidate deny before target lookup.

The lifecycle reason is trimmed at its two ends, must contain 1 to 500 UTF-8
bytes after trimming, and is then frozen for persistence and digest derivation.
Unknown fields, blank input, invalid UTF-8 length, and rejected values return a
non-echoing 422 response.

The request body is exactly `{ "reason": "..." }`; `reason` is required and no
other request field is accepted.

## Public Response

Success and exact replay return exactly:

```json
{
  "resource_type": "actor_profile",
  "resource_id": "uuid",
  "version": null,
  "http_status": 200
}
```

No event ID, grant, issuer, subject, contact data, raw reason, lifecycle actor,
or internal digest is returned. The idempotency record stores only this typed
resource reference; replay does not claim to return an evidence reference.

## State And Field Contract

| Operation | Allowed state | Mutation | New-key conflict |
|---|---|---|---|
| suspend | `active` | set `suspended`; write caller, database time, normalized reason; preserve prior reactivation provenance | `actor_already_suspended` or `actor_deactivated_terminal` |
| reactivate | `suspended` | set `active`; clear suspension fields; write profile reactivation caller/time/reason; never touch grants | `actor_not_suspended` or `actor_deactivated_terminal` |
| deactivate | `active` or `suspended` | set terminal `deactivated`; write caller/time/reason; preserve suspension/reactivation provenance | `actor_deactivated_terminal` |

Human and fixed-service profiles are valid targets. Self-suspend and
self-deactivate return 403 `resource_guard_denied` before target disclosure.
A missing target returns 404 `actor_not_found` only after the caller has a
matching effective permission. Deactivated profiles never reactivate.

Each domain conflict rolls back the pending reservation and staged allow
decision, then commits one privacy-safe denial in a clean transaction. It does
not consume the idempotency key. The exact committed success is the only replay.

## Migration 0026

Migration `0026_actor_profile_lifecycle`:

- adds nullable `reactivated_by`, `reactivated_at`, and `reactivation_reason`
  columns to `actor_profiles` with all-null/all-present parity;
- adds all-null/all-present parity for existing identity-link reactivation
  attribution and database UTF-8 byte bounds for lifecycle reasons;
- replaces profile/link lifecycle guards so terminal fields and attribution
  cannot be rewritten without an allowed state transition;
- expands the closed denial vocabulary with
  `identity_link_already_revoked` and `identity_link_not_revoked` for 09D-B;
- replaces current linked-evidence validation so profile and link reactivation
  require `effective=false -> effective=true`, while suspension, deactivation,
  and link revocation remain `effective=true -> effective=false`;
- makes link lifecycle invalidation target the owning ActorProfile authority
  projection while the success response remains the exact link;
- updates typed validators and PostgreSQL functions together without editing
  historical migrations.

Downgrade fails closed if profile reactivation provenance or committed profile/
link reactivation evidence exists. Otherwise it restores the prior functions,
closed denial vocabulary, constraints, guards, and columns. AUTH-10 through
AUTH-15 shift to migrations `0027` through `0032`.

## Reservation, Lock, And Transaction Order

For every new request:

1. validate and freeze the canonical request;
2. reserve idempotency as the first database write;
3. authorize the exact action;
4. inside authorization, lock `AuthorityControl(id=1)`, caller profile, caller
   link, and exact matched caller grant;
5. only after permission match, lock the target profile, its exact link, and any
   active system Access Administrator target grant;
6. disclose replay/mismatch only after current authority succeeds;
7. enforce target state and final-admin safety;
8. mutate state, touch only the verified caller, append success and exactly one
   invalidation obligation, complete idempotency, and commit once.

All lifecycle mutations, including reactivation, take the singleton lock. This
preserves authorization-before-target-lookup concealment and gives profile,
link, and grant paths one caller-first order. The singleton serializes competing
final-admin changes, so cross-target actor-ID sorting is neither required nor
permitted as an alternate path. Target locks never advance target verification
timestamps.

Suspension or deactivation of a currently effective Access Administrator fails
with 409 `last_access_administrator` when the post-transition count would be
zero. The check uses an active human profile, active exact link, and active
system Access Administrator grant. Grant revoke already uses the same singleton,
so crossed profile/grant loss cannot commit both transitions.

## Replay, Failure, And Timestamp Contract

- Exact replay reauthorizes, returns the stored resource reference even if the
  target later changed state, and advances only the successful human caller's
  verification timestamps.
- Changed reason, target, or operation returns `idempotency_mismatch` only after
  reauthorization. Replay after authority loss denies without disclosure.
- Validation, rate limit, denial, missing target, conflict, mismatch, and every
  SQL/evidence/completion/commit failure advance no timestamp.
- Authorization evidence, target lookup, reservation, state flush, caller
  touch, success event, invalidation event, idempotency completion, and commit
  failures return the stable retryable 503 envelope with no partial state,
  evidence, timestamp, or pending claim.
- Reactivation is administration, not identity verification. Target
  `last_seen_at` and link `last_verified_at` never advance.

## Acceptance Criteria

- Exactly three actions activate: catalogue totals become 65 actions, 15 active
  and 50 planned. One generated manifest declaration exists per route.
- Profile state, readable attribution, exact action decision, success evidence,
  ActorProfile invalidation, and idempotency completion commit atomically.
- Real PostgreSQL proof covers same-key replay, different-key same transition,
  suspend/deactivate, reactivate/deactivate, profile/grant revoke, and
  different-target final-admin loss without sleeps or deadlocks.
- Behavior matrices cover human/service targets, every state, self operations,
  target concealment, replay/mismatch, caller authority changes, rollback,
  timestamps, rate limits, OpenAPI, manifest parity, and privacy canaries.
- Responses, errors, logs, OpenAPI, and denial evidence exclude issuer, subject,
  email, token data, raw reason, attribution IDs, matched-grant internals, and
  stored digests.
- Focused actor and authorization branch coverage is at least 90 percent.
  GitHub Backend preserves the repository-wide 78 percent floor.

## Verification Commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests scripts/api_contract_e2e.py)
(metadata_dir="$(mktemp -d)"; trap 'rm -rf "$metadata_dir"' EXIT; \
  cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=<local-admin-db> \
  .venv/bin/python scripts/run_isolated_tests.py \
  --metadata-json "$metadata_dir/migration.json" --timeout-seconds 1800 -- \
  bash -lc '.venv/bin/alembic downgrade -1 && .venv/bin/alembic upgrade head && \
  .venv/bin/python -m pytest -q tests/test_alembic.py')
(metadata_dir="$(mktemp -d)"; trap 'rm -rf "$metadata_dir"' EXIT; \
  cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=<local-admin-db> \
  .venv/bin/python scripts/run_isolated_tests.py \
  --metadata-json "$metadata_dir/focused.json" --timeout-seconds 3600 -- \
  .venv/bin/python -m pytest -q \
  tests/test_actors.py tests/test_authorization.py tests/test_audit.py \
  tests/test_api_controls.py tests/test_api_rate_controls.py tests/test_alembic.py \
  tests/test_auth.py::test_actor_profile_lifecycle_real_postgres_matrix \
  tests/test_auth.py::test_actor_profile_lifecycle_real_postgres_concurrency)
(metadata_dir="$(mktemp -d)"; trap 'rm -rf "$metadata_dir"' EXIT; \
  cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=<local-admin-db> \
  .venv/bin/python scripts/run_isolated_tests.py \
  --metadata-json "$metadata_dir/actor-coverage.json" --timeout-seconds 3600 -- \
  bash -lc '.venv/bin/coverage erase && .venv/bin/coverage run --branch \
  --source=app/modules/actors -m pytest -q tests/test_actors.py tests/test_auth.py \
  -k "actor_profile_lifecycle" && \
  .venv/bin/coverage report --precision=2 --fail-under=90')
(metadata_dir="$(mktemp -d)"; trap 'rm -rf "$metadata_dir"' EXIT; \
  cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=<local-admin-db> \
  .venv/bin/python scripts/run_isolated_tests.py \
  --metadata-json "$metadata_dir/authorization-coverage.json" --timeout-seconds 3600 -- \
  bash -lc '.venv/bin/coverage erase && .venv/bin/coverage run --branch \
  --source=app/modules/authorization -m pytest -q tests/test_authorization.py \
  tests/test_auth.py -k "actor_profile_lifecycle or admin_role" && \
  .venv/bin/coverage report --precision=2 --fail-under=90')
(metadata_dir="$(mktemp -d)"; trap 'rm -rf "$metadata_dir"' EXIT; \
  cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=<local-admin-db> \
  .venv/bin/python scripts/run_isolated_tests.py \
  --metadata-json "$metadata_dir/api-contract.json" --timeout-seconds 3600 -- \
  .venv/bin/python scripts/api_contract_e2e.py)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
python3 scripts/test_agent_gates.py
python3 scripts/update_post_merge_memory.py validate-merge-intent --base-ref origin/main
git diff --check
```

The two named PostgreSQL nodes are created by this chunk and are mandatory
before implementation review; missing nodes make the proof command fail.

## Required Reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, CI
integrity, docs, reuse/dedup, and test delta.

## Human Review Focus

Review terminal deactivation, reactivation provenance, truthful invalidation
direction, reserve-before-authorize replay ordering, singleton-first serialized
authority, final-admin safety, caller-only timestamps, and rollback atomicity.

## Stop Condition

Stop after merge and signed memory. Do not start `WS-AUTH-001-09D-B` or
`WS-AUTH-001-09E` automatically.
