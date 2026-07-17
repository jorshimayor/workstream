# Discovery: WS-AUTH-001 - Workstream Authorization Service

Discovery is read-only. No application code was changed while producing this
artifact.

## Current behavior

### Authentication

`backend/app/api/deps/auth.py` extracts bearer credentials and delegates to an
`AuthVerifier`. `DevelopmentAuthVerifier` is restricted to explicit
development/test environments. `FlowAuthVerifier` supports a local HS256
fixture mode and otherwise fails closed because production issuer/JWKS
verification is not configured.

The verifier returns `ActorContext`, including token-derived roles and a
sanitized claim snapshot. `get_registered_actor()` refreshes local registry
metadata but explicitly returns the token context for route authorization.

### Actor registry

`ActorIdentity` is keyed by a deterministic actor ID derived from issuer and
subject. It stores issuer, subject, display metadata, last-seen roles, and a
sanitized claim snapshot.

`ActorProfile` is currently a repeatable typed workflow row under the identity.
Types include `worker`, `reviewer`, `admin`, `project_manager`, and
`project_owner`; statuses are `observed`, `active`, and `disabled`. These rows
are not the single canonical actor profile required by `WS-AUTH-001`.

### Authorization

`backend/app/core/permissions.py::require_any_role()` intersects allowed roles
with `ActorContext.roles`. Project, task, and checker services define their own
role sets and object-level checks. Examples include:

- `PROJECT_SETUP_ROLES = {"admin", "project_manager"}`
- `TASK_CLAIM_ROLES = {"worker"}`
- `CHECKER_TRIGGER_ROLES = {"admin", "project_manager"}`
- `can_admin_or_task_creator_manage()`

This is a bootstrap model, not the adopted Workstream-owned grant model.

### Internal actors

Project setup and pre-review checker workers create fixed internal
`ActorContext` instances. Project setup currently assigns human-style
`admin/project_manager` roles to its internal actor. The pre-review gate uses a
separate `workstream_system` role and identity checks.

### Audit and errors

Task audit events preserve actor ID, external subject/issuer, actor roles, claim
snapshot, event type, state transition, reason, and payload. They do not yet
provide the complete authority-change event envelope, matched-grant evidence,
idempotency key, or correlation ID required by the adopted specification.

FastAPI errors mostly use the standard `detail` response. Authentication
failures collapse to `Invalid bearer token`. The adopted contract requires
stable structured authentication and authorization codes.

## Relevant files/modules

| Path | Purpose | Notes |
|---|---|---|
| `backend/app/interfaces/auth.py` | Auth verifier port | Extend with verified issuer-token contract without SDK leakage. |
| `backend/app/adapters/auth/flow.py` | Flow token adapter | Local HS256 only; production JWKS work is absent. |
| `backend/app/adapters/auth/dev.py` | Development verifier | Must remain fail-closed outside local/test. |
| `backend/app/api/deps/auth.py` | Bearer and registry dependencies | Current dependency returns token roles as authority. |
| `backend/app/schemas/auth.py` | Actor request context and claim sanitation | Role-bearing context must be replaced by verified-token plus local authorization context. |
| `backend/app/core/permissions.py` | Coarse role helper | Must not remain an alternate authority path after cutover. |
| `backend/app/modules/actors/models.py` | Current identity/profile tables | Cardinality and semantics conflict with adopted model. |
| `backend/app/modules/actors/repository.py` | Registry persistence | Useful repository pattern; current upsert mirrors token data. |
| `backend/app/modules/actors/service.py` | Registration/profile activation | Must evolve into actor resolution and administration services. |
| `backend/app/modules/projects/service.py` | Project setup authorization | Contains many token-role checks and approval-role provenance. |
| `backend/app/modules/tasks/authorization.py` | Task object helper | Creator/role semantics must become canonical resource guards. |
| `backend/app/modules/tasks/service.py` | Task/submission authorization | Worker token roles and active worker profile currently gate work. |
| `backend/app/modules/checkers/service.py` | Checker authorization/system actor | Worker/operator visibility and trigger rules need permission-based cutover. |
| `backend/app/modules/tasks/models.py::AuditEvent` | Current audit row | Needs authority evidence or a shared audit evolution. |
| `backend/alembic/versions/0012_actor_identity_profile_registry.py` | Current actor schema migration | Existing rows lack reliable subject-kind classification. |
| `backend/app/api/router.py` | Versioned API composition | `/api/v1` remains canonical by human decision. |
| `backend/tests/test_auth.py` | Auth boundary tests | Covers fail-closed defaults but not production JWKS. |
| `backend/tests/test_actors.py` | Actor registry tests | Encodes the old multiple-profile and token-observation behavior. |
| `backend/tests/test_projects.py` | Project auth/setup tests | Extensive fixtures currently depend on token roles. |
| `backend/tests/test_tasks.py` | Task authorization/lifecycle tests | Extensive worker/operator role fixtures and object-concealment tests. |
| `backend/tests/test_checkers.py` | Checker authorization tests | Covers worker redaction and operator-only actions. |
| `docs/reference_specs/WS-AUTH-001-actor-profile-role-and-authorization-service-specification.md` | Adopted authority contract | `/v1` is overridden to `/api/v1` by human decision. |

## Current tests

| Test path | What it covers | Gaps |
|---|---|---|
| `backend/tests/test_auth.py` | Bearer failures, dev guard, local token checks, coarse permission helper | No asymmetric JWKS, subject kind, scope, `jti`, cache refresh, or typed unavailable errors. |
| `backend/tests/test_actors.py` | Identity upsert, observed/active typed profiles, refresh behavior | Tests the superseded profile semantics; no canonical actor/link state or provisioning race. |
| `backend/tests/test_projects.py` | Project role restrictions and setup lifecycle | Uses token `admin/project_manager`; no durable grant scope. |
| `backend/tests/test_tasks.py` | Worker/operator access, assignment ownership, privacy, concurrency | Uses token `worker` plus active worker profile; no exact-project submitter grant. |
| `backend/tests/test_checkers.py` | Checker trigger/read authorization and worker redaction | No registered permission matrix or local revocation proof. |
| `backend/tests/test_alembic.py` | Migration forward/backward behavior | No canonical actor/grant/authority-control constraints. |

The repository contains 352 backend test functions. Static wording, Markdown
link, agent-gate, loop-memory, and internal-review evidence checks passed during
discovery. The full backend suite was not rerun because this checkout currently
has no `backend/.venv` and local Postgres/Redis services are not running.

## Dependencies/integrations

- Identity Issuer final tokens and issuer-owned JWKS.
- FastAPI bearer dependencies.
- Postgres canonical actor, grant, idempotency, and audit state.
- Celery workers that must distinguish system authority from request evidence.
- Redis as Celery delivery infrastructure only, never authority state.
- Existing project, task, submission, and checker resource relationships.

A maintained JWT/JWK cryptography dependency and async HTTP client will be
required unless already supplied transitively. Production dependency selection
requires explicit review in the token-verifier chunk.

## Risks discovered

| Risk | Why it matters | Suggested handling |
|---|---|---|
| Issuer-role escalation | Legacy issuer role metadata currently grants product authority. | Remove role claims from authorization context and prove every protected surface uses local grants. |
| Dual authority during migration | Old and new checks could disagree. | Define a one-way cutover; never accept either path as sufficient. |
| Legacy subject-kind ambiguity | Existing registry rows do not prove human versus service. | Fail closed on unclassified non-empty data and require an audited classification/remediation input. |
| Actor ID rewrite | Historical task/checker/audit attribution uses strings. | Preserve valid actor IDs and avoid broad FK conversion in early chunks. |
| Final administrator race | Concurrent revocation/suspension could remove all access administrators. | Singleton authority-control row plus `FOR UPDATE` and PostgreSQL race tests. |
| Cross-project IDOR | Request bodies can claim a project different from the resource. | Canonical resource loaders derive scope from database relationships. |
| Stale queued authority | Jobs may carry authority that has been revoked. | Re-resolve actor/grant state before actor-attributed commits. |
| Claim/PII leakage | Current registry persists sanitized claim snapshots and role observations. | Minimize persisted identity data; never persist raw token/JWKS material. |
| Namespace drift | New specs say `/v1`; repo uses `/api/v1`. | Record `/api/v1` as the adopted repository override and update generated/reference artifacts coherently. |
| Current initiative interruption | `WS-POL-002` is incomplete after chunk 02. | Mark it paused, do not implement chunk 03 until auth foundation is ready. |

## Unknowns/questions for human

No blocking product questions remain for planning. The user explicitly adopted
`WS-AUTH-001`, retained `/api/v1`, and prioritized auth before
`WS-POL-002-03`.

Production deployment inputs remain externally supplied:

| Input | Why it matters | Needed before chunk? |
|---|---|---|
| Canonical issuer URL and JWKS URL | Exact verification and live proof | Token adapter supports configuration without values; real-token drill requires values. |
| Allowed signing algorithms | Prevent algorithm confusion | Adapter defaults must fail closed; deployment must configure approved values. |
| Canonical subject-kind and scope claim form | Required token validation | Contract supports the adopted names; issuer integration test requires a fixture or issuer documentation. |
| Introspection/revocation policy | Determines whether signature validation alone is sufficient | May remain disabled only through explicit secure configuration and documented issuer policy. |
| Legacy non-test actor classification manifest | Safe migration of existing rows | Required before applying the actor migration to any non-empty persistent environment; format and tool are defined by chunk 03. |

## Existing conventions to preserve

- Thin FastAPI routers, service-owned business rules, repository-owned queries.
- Async SQLAlchemy and Postgres-enforced uniqueness/concurrency.
- Pydantic request models with `extra="forbid"`.
- Fail-closed production defaults and non-production dev auth guard.
- Object-concealing not-found behavior for unauthorized resource reads.
- Append-only audit facts for lifecycle and authority changes.
- Fixed internal system actors for server-owned automation.
- One PR-sized chunk at a time with deterministic evidence and internal review.

## AUTH-05 Delta Discovery (2026-07-14)

- Current migration head is `0017_api_controls`; the original AUTH-05
  `0017_*` allowance collides and cannot be implemented.
- `AuditEvent` remains in `tasks.models`. `AuditRepository` owns a shared insert
  implementation, while `TaskRepository` still duplicates insert/read logic
  used by task/checker services.
- Legacy audit rows require non-null external issuer/subject, token-role, and
  claim fields. Authority events need a conditional privacy-safe envelope that
  preserves legacy rows without copying those identity-provider fields.
- The combined shared-audit schema/writer, append-only database custody,
  idempotency state machine, and concurrency proof cross two persistent
  subsystem boundaries. Required L1 plan review split them into 05A (`0018`)
  and 05B (`0019`) before runtime implementation.
- D13 provider-neutral verifier adoption does not block either child and remains
  a separate reviewed chunk after the shared external-service adapter
  foundation exists.

## AUTH-04 Delta Discovery (2026-07-13)

### Current behavior

- `backend/app/main.py` only customizes FastAPI request-validation errors. It
  has no request/correlation context, HTTP/unhandled exception envelope, or
  response ID headers.
- Existing HTTP errors primarily expose FastAPI `detail`. Two bounded task
  domain errors expose top-level `code/details`; existing tests rely on these
  fields, so AUTH-04 must add the canonical nested envelope without deleting
  compatibility fields.
- `backend/app/api/deps/auth.py` already distinguishes missing, invalid, and
  unavailable authentication conditions internally, but its public responses
  do not carry stable machine codes or correlation evidence.
- No rate-control model, query, service, or dependency exists. Redis is Celery
  delivery infrastructure and is not an authority or API-control store.
- No first-access or admin-mutation endpoint exists yet. Their control
  dependencies must be prepared here and attached only by the later owning
  chunks; unrelated legacy reads must not consume those limits.

### Current migration and ownership boundary

- Current `main` migration head is `0016_artifact_domain`; the original AUTH-04
  `0016_*` filename allowance is stale after parallel artifact integration.
- AUTH-04 therefore owns `0017_api_controls` with down revision
  `0016_artifact_domain`.
- Existing feature modules use `models -> repository -> service`, with
  `backend/app/db/models.py` importing feature models for Alembic metadata.
  `backend/app/modules/api_controls` must follow that pattern and own SQL and
  transaction behavior.

### Required compatibility and security properties

- Request/correlation headers require bounded canonical UUID parsing, duplicate
  rejection, safe generation, and no reflection of invalid bytes.
- The adopted fallback envelope is
  `error.code/message/details/correlation_id/retryable`; raw exceptions, token
  material, claims, provider responses, SQL, secrets, and PII are excluded.
- Existing `detail` and coded-domain fields remain additive compatibility
  surfaces in this chunk; current intake assertions may not be weakened.
- Privacy-safe rate keys require keyed HMAC rather than persisted raw issuer,
  subject, actor, token, network, or email values.
- Cross-replica fixed-window increments require one PostgreSQL atomic upsert
  driven by database time. Missing configuration or database failure must fail
  closed for the protected dependency.

### Proof gaps owned by AUTH-04

- Header absence/propagation, malformed/duplicate values, success and every
  error class, unhandled exception redaction, and legacy-field compatibility.
- Allowed, exact-limit, exceeded, expiry-reset, concurrent, cross-session,
  distinct-scope/key, missing-secret, and database-unavailable rate behavior.
- Prior-head upgrade, downgrade, re-upgrade, constraints, unique key, indexes,
  and database-time fields for migration `0017`.
- Full backend and API-contract regression proof without modifying product
  authorization or attaching future controls to unrelated routes.

### Required plan-review split

The first combined AUTH-04 plan failed required preimplementation review before
any runtime edit. Request/error compatibility and durable rate consumption each
need an independently reviewable contract and production-code budget.

- `WS-AUTH-001-04A` owns pure-ASGI request/correlation context, bounded additive
  error envelopes, legacy response/header compatibility, and OpenAPI proof.
- `WS-AUTH-001-04B` later owns HMAC-keyed PostgreSQL counters, a dedicated
  committed transaction, atomic database-time windows, `0017_api_controls`,
  configuration failure behavior, and migration/concurrency proof.
- 04B is not activated by this split. It requires 04A merge/memory and a
  separate explicit user start.
