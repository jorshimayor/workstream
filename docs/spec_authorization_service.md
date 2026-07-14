# Workstream Authorization Service Specification

## Status And Scope

This is the canonical repository specification for the target Workstream
authorization service. It reconciles the adopted archival WS-AUTH-001 input
with ADR 0006, ADR 0012, the existing `/api/v1` namespace, and current module
boundaries.

The current backend remains on a staged migration path until the owning
WS-AUTH-001 implementation chunks merge. This specification must not be read as
evidence that an unimplemented route or guard already exists.

## Authority Boundaries

The external Identity Issuer owns authentication. Workstream verifies its
tokens and owns product authorization.

| Boundary | Owner | Rule |
|---|---|---|
| Login, passwords, primary sessions, token issuance | External Flow Identity Issuer | Workstream does not implement them. |
| Signature, issuer, audience, time, subject kind, coarse scope | Existing `AuthVerifier` adapter/dependency boundary | Fail closed; pin algorithms and issuer configuration. |
| Actor identity and identity links | `backend/app/modules/actors` | One canonical profile; issuer/subject links are explicit and revocable. |
| Grants, permissions, idempotency, invalidation, decisions | `backend/app/modules/authorization` | Deny by default; no token-role product authority. |
| Resource facts | Owning feature services/repositories | Repositories return domain records; application services compose `ResourceContext`. |
| Review lifecycle | WS-REV-001 | Authorization supplies actors and permissions but does not invent review outcomes. |
| Contribution and compensation | WS-CON-001 | Authorization does not redefine contribution or payment behavior. |

All public routes use `/api/v1`. The archival short prefix is not an alias.

## Authentication Contract

`VerifiedIssuerToken` contains only verified identity and coarse-access data:

- canonical issuer;
- opaque subject;
- audience;
- issued-at, expiry, optional not-before;
- mandatory token identifier (`jti`);
- subject kind;
- verified coarse scope.

It contains no Workstream product role or permission. Email, display name,
skills, reputation, and relationship metadata are never authorization keys.
During the compatibility period, `/api/v1/auth/me` and actor registration do
not copy issuer email or display name, and those response fields remain null.
Canonical profile metadata is owned by the later actor-profile migration.

Human first access may create a canonical human profile and identity link.
Unknown service subjects, agents, and Spaces are denied without implicit
provisioning. Service actors require explicit pre-provisioning.

## Actor Model

### ActorProfile

`ActorProfile` is the canonical Workstream actor root.

Required concepts:

- UUID identifier;
- kind: human or explicitly provisioned service;
- status: active, suspended, or deactivated;
- contributor domain for human self-service;
- database-time creation/update and immutable historical attribution.

A profile status is a guard, not a grant. Active humans receive only self
profile capability until an administrative or exact-project grant exists.

### ActorIdentityLink

An identity link binds one canonical issuer and opaque subject to exactly one
profile. Link state is active or revoked. Raw tokens, provider credentials, and
full provider claims are never persisted.

Existing classified external actor UUIDs may be preserved as profile IDs.
Legacy typed workflow-profile IDs are unrelated and never promoted.

## Grant Model

### Administrative Grants

| Grant | Scope | Purpose |
|---|---|---|
| `access_administrator` | system | Actor, identity-link, administrative-grant, and permission-catalog administration. |
| `operator` | system | Runtime inspection and explicit recovery operations against canonically resolved resources. |
| `project_manager` | system or exact covered project | Project configuration, task management, and contributor grants. System scope covers all projects but remains resource- and lifecycle-guarded; exact-project scope covers only that project. |
| `finance_authority` | system or exact covered project | Compensation configuration and fulfillment observation owned by WS-CON. |
| `audit_authority` | system or exact covered project | Read-only evidence access and authorized export. |

Administrative grants do not imply contributor capability. An administrator
cannot submit or review by administrative role alone.

### Project Contributor Grants

| Grant | Exact-project capability |
|---|---|
| `submitter` | Minimal project read, task queue read/claim, own submission create/read, own review-chain read. |
| `reviewer` | Minimal project read, review queue/claim/release/decision, submission read for review, review-chain read. |
| `both` | Union of submitter and reviewer candidates, still subject to separation-of-duties and lifecycle guards. |

Contributor is the umbrella human product term. A contributor has an
exact-project `submitter`, `reviewer`, or `both` grant. Celery, checker, setup,
and background workers are internal services, not human product roles.

Grants are immutable history. Replacement revokes the prior active grant and
creates a new row atomically. No observed token role, typed profile, skill,
qualification, or reputation value creates a grant automatically.

## Permission Catalog

The initial registered catalog includes:

```text
actor.profile.read_self
actor.profile.update_self
actor.profile.read_any
actor.profile.suspend
actor.profile.reactivate
actor.profile.deactivate
actor.identity_link.read
actor.identity_link.revoke
actor.identity_link.reactivate
actor.service.provision

admin_role.read
admin_role.grant
admin_role.revoke

project.create
project.read
project.update
project.archive
project.guide.manage
project.effective_policy.manage
project.task.manage
project.review_policy.manage
project.role_grant.read
project.role_grant.manage

task.queue.read
task.claim
submission.create
submission.read_own
submission.read_for_review

review.queue.read
review.queue.inspect
review.claim
review.release
review.decline_preference
review.decision
review.lease.force_release
review.chain.read

contribution.read_self
contribution.read_project

compensation.policy.manage
compensation.adapter_binding.manage
compensation.award.read
compensation.delivery.reconcile

operations.status.read
operations.timer.run
operations.reconcile.run
operations.outbox.retry
operations.projection.rebuild
operations.task.start_override
operations.submission_gate.repair
operations.checker.retry

artifact.binding.read
artifact.replica.read
artifact.receipt.read
artifact.verification_job.read
artifact.verification_job.retry
artifact.recovery_attempt.read
artifact.recovery_attempt.execute
artifact.audit.read
artifact.guide_source.ingest
artifact.upload_session.create
artifact.upload_item.write
artifact.upload_session.seal
artifact.binding.create
artifact.verification.execute
artifact.pending_work.scan
artifact.guide_source.read
artifact.checker_input.materialize
artifact.checker_output.write

audit.read
audit.export
```

Artifact permissions are deliberately resource- and operation-specific.
`artifact.*.read` permissions do not authorize retry or recovery, human
Operator permissions do not authorize internal execution, and internal service
permissions do not authorize Operator APIs. AUTH-07 owns this closed registry,
AUTH-08 owns the Operator grant definitions, AUTH-09 owns the service
principals, and WS-ART consumes the resulting decisions without registering
permissions or inferring authority. AUTH-11 maps project-guide source ingest,
AUTH-14 maps contributor upload actions, and AUTH-15 maps fixed system-worker
actions for binding, verification, pending-work publication, guide-source reads,
and checker input/output artifact handling.

Adding a permission requires a specification/ADR update and human approval.
Routers cannot invent identifiers or evaluate grant unions.

## Authorization Algorithm

For every protected operation:

1. Verify the external token through the existing verifier boundary.
2. Resolve an active identity link and active actor profile.
3. Build request-scoped `AuthorizationContext` without token-role authority.
4. Load the canonical resource through its owning repository/service.
5. Compose `ResourceContext` in the application service.
6. Load active candidate grants using database time.
7. Expand only registered permission candidates compatible with grant scope.
8. Apply actor, exact-project, ownership, assignment, separation-of-duties,
   task-ban, and lifecycle guards.
9. For sensitive mutations, revalidate authority inside the same transaction
   immediately before commit.
10. Return allow or a stable denial code without leaking hidden resources.

Authorization decisions are request-scoped and are not cached across requests.
List filtering occurs before counts and pagination cursors.

## Separation And Recovery Rules

- An actor cannot grant or revoke their own authority through an administrative
  grant operation.
- A submitter cannot act as the sole reviewer of their own work.
- Project Manager authority is limited to its grant scope. A system-scoped
  Project Manager covers all projects but remains subject to resource and
  lifecycle guards; an exact-project grant covers only that project. Only a
  system-scoped Project Manager may create a project because no project scope
  exists before creation.
- Administrative roles alone cannot claim contributor work, submit, or review.
- Operator recovery is distinct from Project Manager management.
- `operations.task.start_override`,
  `operations.submission_gate.repair`, and `operations.checker.retry` require an
  exact reason, canonical resource scope, matched permission/grant, and
  append-only evidence.
- Recovery cannot erase checker evidence, mutate immutable submissions, create
  a human review decision, rewrite contribution history, or bypass compensation
  guards.
- `review.lease.force_release` is governed by WS-REV-001.

## System Work

Internal system workers use fixed Workstream system principals with explicit
registered system permissions. They never receive fabricated human grants.
Serialized requester identity is provenance only. Actor-attributed jobs reload
current actor/link/grant state before committing.

## Bootstrap And Final-Administrator Safety

The first Access Administrator is created through a local management command
for an existing active human. There is no public bootstrap endpoint or shared
bootstrap bearer secret.

Bootstrap locks `AuthorityControl(id = 1) FOR UPDATE`, checks that no effective
Access Administrator exists, and writes the initial grant, one-time state, and
audit event atomically. Every later bootstrap attempt returns a stable audited
conflict.

Bootstrap and every grant/profile/link operation that could remove the final
effective Access Administrator use the same row lock and transaction-local
effective count.

## Revocation And Invalidation

Suspension, deactivation, identity-link revocation, and grant revocation take
effect on the next request and on the next sensitive transaction recheck. Each
mutation writes an invalidation event atomically with state and evidence.

Assignment reconciliation preserves immutable work history. A revoked actor's
ordinary claimed/in-progress assignment may be released by the owning later
chunk. A `needs_revision` task retains a durable revision obligation and cannot
be returned as ordinary ready work.

## Idempotency And Authority Evidence

Authority-changing APIs require canonical request hashing and idempotency keys.
An exact replay returns the committed result; a mismatched replay is rejected.

Authority events are append-only and include, when applicable:

- schema/event version;
- request and correlation identifiers;
- acting and target actor references;
- matched grant and permission;
- exact project/resource reference;
- required reason;
- idempotency key;
- bounded before/after state;
- database time.

Business state, idempotency result, authority event, and invalidation event
commit in one `AsyncSession` transaction. Missing evidence is not backfilled
later.

## API Families

Canonical route families use `/api/v1`:

```text
GET|PATCH /api/v1/actors/me
GET|PATCH /api/v1/actors/{actor_profile_id}
POST /api/v1/actors/{actor_profile_id}/suspend|reactivate|deactivate
GET /api/v1/actors/{actor_profile_id}/identity-links
POST /api/v1/actor-identity-links/{link_id}/revoke|reactivate
POST /api/v1/service-actors

POST|GET /api/v1/admin-role-grants
GET /api/v1/actors/{actor_profile_id}/admin-role-grants
POST /api/v1/admin-role-grants/{grant_id}/revoke

POST|GET /api/v1/projects/{project_id}/role-grants
GET /api/v1/projects/{project_id}/role-grants/{grant_id}
POST /api/v1/projects/{project_id}/role-grants/{grant_id}/revoke
```

Exact request/response/error contracts are introduced by their owning chunks.
No route may accept role or scope from request JSON as canonical authority.

## Migration And Compatibility

The implementation order is fixed by the WS-AUTH-001 chunk map:

1. canonical docs and ADR;
2. verified issuer token/JWKS boundary;
3. legacy actor classification;
4. request/error/rate controls;
5. authority evidence/idempotency;
6. canonical actor/link migration;
7. authorization kernel;
8. bootstrap/admin grants;
9. actor/link state and service actors;
10. project contributor grants;
11-14. complete resource-family cutovers;
15. obsolete authority removal and scanner enforcement;
16. conformance, observability, concurrency, and live API proof.

Temporary compatibility mechanisms are explicitly named, enumerated, and
shrinking. They grant no canonical product authority and are deleted by their
assigned removal chunk. No implementation chunk may create a second canonical
actor root, verifier hierarchy, audit ledger, unit-of-work abstraction, or
authorization engine.

## Error And Privacy Contract

Errors use a stable envelope and denial codes. They do not contain raw
exceptions, tokens, full claims, secrets, JWKS material, private artifact
content, or unnecessary personal data. Unauthorized resources are concealed
where existence itself is sensitive.

First access and administrative mutations are rate-controlled through
Postgres-backed fail-closed controls before their public APIs become available.

## Conformance Requirements

Each owning chunk must prove:

- allow and deny cases for every permission path;
- migrated surfaces derive product authority only from local grants and guards;
- cross-project and concealed-resource behavior;
- immediate same-token revocation;
- state/grant/link and final-administrator concurrency;
- idempotent exact replay and mismatched replay rejection;
- append-only allowed and denied evidence;
- preserved current intake lifecycle through the full backend suite and API
  contract drill;
- no test skip, xfail, assertion weakening, dependency override, fabricated
  authorization context, or direct grant insertion as product proof.

The final live drill must operate through supported APIs/commands without
direct database authority edits.

## Precedence And Non-Goals

This specification and ADR 0012 supersede active token-role and typed-profile
authorization claims. ADR 0006 still controls authentication ownership.
WS-REV-001 and WS-CON-001 control their own product behavior.

This specification does not add Workstream login, implement runtime code,
change review decision values, define contribution/payment behavior, add a
frontend, enable blockchain settlement, add source adapters, automate routing,
or create an agent workspace.
