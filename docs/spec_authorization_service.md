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
artifact.audit.read
artifact.guide_source.ingest
artifact.upload_session.create
artifact.upload_session.read
artifact.upload_item.write
artifact.upload_session.seal
artifact.upload_session.cancel
artifact.upload_session.expire
artifact.binding.create
artifact.verification.execute
artifact.pending_work.scan
artifact.put_attempt.resolve
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
permissions or inferring authority. Artifact actions activate only through the
paired feature model below; AUTH-12, AUTH-14, and AUTH-15 do not activate or
attach artifact actions on behalf of WS-ART.

These are 73 approved `PermissionId` values. `ActionId` values are a separate
closed registry layer and are not included in that permission count. AUTH-05A's current typed and
PostgreSQL audit registry accepts 49. The three approved Operator recovery
identifiers `operations.task.start_override`,
`operations.submission_gate.repair`, and `operations.checker.retry`, plus the
21 artifact identifiers above, are reserved planned metadata. AUTH-07 adds
their matching typed/SQL audit parity without making them executable. An
artifact action becomes active only when the owning WS-ART chunk supplies its
canonical resource composer, guards, surface declaration, behavior tests, and
transaction-local revalidation where required. Both halves are mandatory;
registry presence alone never grants authority.

The paired artifact activation matrix is closed:

| Owning WS-ART chunk | Actions activated by that chunk |
|---|---|
| `WS-ART-001-02D` | Operator binding/replica/receipt/verification-job/recovery-attempt/audit reads; the operations-domain `operations.artifact_storage_admission.read` action mapped to `operations.status.read`; verification retry; `artifact.verification.execute`; `artifact.pending_work.scan`; and `artifact.put_attempt.resolve` |
| `WS-ART-001-03` | `artifact.guide_source.ingest`, `artifact.guide_source.read`, and `artifact.guide_source.binding.create` mapped to `artifact.binding.create` |
| `WS-ART-001-04A` | upload-session create/read/seal/cancel/expire and upload-item write |
| `WS-ART-001-04B` | `artifact.pre_submit.checker_input.materialize` mapped to `artifact.checker_input.materialize` |
| `WS-ART-001-05` | `artifact.submission.binding.create` mapped to `artifact.binding.create` |
| `WS-ART-001-06A` | `artifact.post_submit.checker_input.materialize` mapped to `artifact.checker_input.materialize` |
| `WS-ART-001-06B` | `artifact.checker_output.write` and `artifact.checker_output.binding.create` mapped to `artifact.binding.create` using the checker-run resource |

Every row requires AUTH-07's registry, AUTH-08's applicable Operator grant
definition, and AUTH-09's applicable fixed service principal to be present
first. Feature code receives centralized decisions; it never queries grants or
constructs permission identifiers dynamically.

The following table is the single source of truth for reserved artifact-related
`ActionId` metadata. AUTH-07 registers each row as `planned`; the owning WS-ART
chunk may activate it only with its canonical resource composer, guards,
surface declaration, and behavior tests. A mapping is not a permission alias:
authorization still evaluates the listed registered `PermissionId` against the
listed canonical resource and principal class.

| ActionId | PermissionId | Principal class | Canonical resource | Owning WS-ART chunk |
|---|---|---|---|---|
| `artifact.binding.read` | `artifact.binding.read` | Operator | artifact binding | `02D` |
| `artifact.replica.read` | `artifact.replica.read` | Operator | artifact replica | `02D` |
| `artifact.receipt.read` | `artifact.receipt.read` | Operator | artifact receipt | `02D` |
| `artifact.verification_job.read` | `artifact.verification_job.read` | Operator | verification job | `02D` |
| `artifact.verification_job.retry` | `artifact.verification_job.retry` | Operator | exhausted verification job | `02D` |
| `artifact.recovery_attempt.read` | `artifact.recovery_attempt.read` | Operator | recovery attempt | `02D` |
| `artifact.audit.read` | `artifact.audit.read` | Operator | artifact audit scope | `02D` |
| `operations.artifact_storage_admission.read` | `operations.status.read` | Operator | deployment artifact-storage namespace | `02D` |
| `artifact.guide_source.ingest` | `artifact.guide_source.ingest` | authorized project actor | guide-source snapshot item | `03` |
| `artifact.guide_source.read` | `artifact.guide_source.read` | fixed guide-reader service | guide-source snapshot item | `03` |
| `artifact.upload_session.create` | `artifact.upload_session.create` | assigned contributor | task | `04A` |
| `artifact.upload_session.read` | `artifact.upload_session.read` | assigned contributor | upload session | `04A` |
| `artifact.upload_item.write` | `artifact.upload_item.write` | assigned contributor | upload item | `04A` |
| `artifact.upload_session.seal` | `artifact.upload_session.seal` | assigned contributor | upload session | `04A` |
| `artifact.upload_session.cancel` | `artifact.upload_session.cancel` | assigned contributor | upload session | `04A` |
| `artifact.upload_session.expire` | `artifact.upload_session.expire` | fixed scheduler service | upload session | `04A` |
| `artifact.guide_source.binding.create` | `artifact.binding.create` | fixed binding service | guide-source snapshot item | `03` |
| `artifact.submission.binding.create` | `artifact.binding.create` | fixed binding service | submission | `05` |
| `artifact.checker_output.binding.create` | `artifact.binding.create` | fixed binding service | checker run | `06B` |
| `artifact.verification.execute` | `artifact.verification.execute` | fixed verifier service | verification job | `02D` |
| `artifact.pending_work.scan` | `artifact.pending_work.scan` | fixed scheduler service | system pending-work scope | `02D` |
| `artifact.put_attempt.resolve` | `artifact.put_attempt.resolve` | fixed put-resolver service | put attempt | `02D` |
| `artifact.pre_submit.checker_input.materialize` | `artifact.checker_input.materialize` | fixed materializer service | sealed upload session and task | `04B` |
| `artifact.post_submit.checker_input.materialize` | `artifact.checker_input.materialize` | fixed materializer service | checker run and immutable bindings | `06A` |
| `artifact.checker_output.write` | `artifact.checker_output.write` | fixed checker-output service | checker run | `06B` |

The fixed internal service identities and their complete artifact action sets
are also closed:

| Service identity | Allowed artifact actions |
|---|---|
| `workstream.artifact.verifier` | `artifact.verification.execute` |
| `workstream.artifact.put_resolver` | `artifact.put_attempt.resolve` |
| `workstream.artifact.scheduler` | `artifact.pending_work.scan`, `artifact.upload_session.expire` |
| `workstream.artifact.binding` | `artifact.guide_source.binding.create`, `artifact.submission.binding.create`, `artifact.checker_output.binding.create` |
| `workstream.artifact.guide_reader` | `artifact.guide_source.read` |
| `workstream.artifact.materializer` | `artifact.pre_submit.checker_input.materialize`, `artifact.post_submit.checker_input.materialize` |
| `workstream.artifact.checker_output` | `artifact.checker_output.write` |

AUTH-09 persists these exact service actors and assignments before any WS-ART
execution chunk activates them. Composition startup proves registry, service
actor, action, and PermissionId parity and fails closed on a missing or extra
assignment. Negative authorization tests prove each service identity is denied
every artifact action outside its row. Human authorization remains attached to
the initiating product command; an internal service identity never inherits a
human grant or role.

Adding a permission requires a specification/ADR update and human approval.
Routers cannot invent identifiers or evaluate grant unions.

### Action And Resource Registration

The permission catalog is consumed through a closed, typed action registry.
Each active action definition has its own stable `ActionId` and binds one
approved `PermissionId` to:

- one canonical authorization target resource type;
- the rule for resolving that target, including the existing parent or `system`
  target used when the requested operation creates a new resource;
- the allowed human or service principal class and authority-candidate sources;
- registered global, resource, ownership, assignment, separation-of-duties, and
  lifecycle guards; and
- the closed, typed resource facts required by each guard; and
- whether authority must be revalidated inside the committing transaction.

Multiple closed actions may map to one approved broad permission while having
different canonical targets and guards. For example, create and update actions
may share an approved management permission but target an existing parent and
an existing child respectively. Routes declare `ActionId`, never an arbitrary
permission/target pair. Splitting a broad permission into new permission tokens
still requires the separate approval and migration rule above.

The registry does not own domain persistence or state transitions. Feature
repositories return their domain records, and feature application services or
feature-owned loaders compose the bounded `ResourceContext`. Loader
implementations may be registered at the application composition root, but the
authorization module must not duplicate feature queries or import a parallel
resource repository. Resource contexts use closed per-resource variants rather
than a free-form attribute bag. Registration rejects undeclared facts, and
authorization fails closed when a required fact is absent or has the wrong
type. Request bodies, query values, and path combinations remain untrusted
hints; canonical parent, project, owner, assignment, and state facts come from
PostgreSQL.

Each protected FastAPI route and asynchronous command declares one primary
registered action. That declaration selects the authorization target and
mandatory guards; it does not replace domain invariants or permit a route-local
secondary policy. Internal jobs declare fixed Workstream service authority and
never serialize a human bearer token as executable authority. Collection
actions authorize and filter against their canonical parent scope before
counts, cursors, facets, or distinct values are computed.

Registration and completeness are staged with the approved chunk map. Chunk 07
introduces the types and registry. Reserved action metadata contains only the
stable `ActionId`, approved `PermissionId`, owning specification/chunk, and
`planned` availability; it is not executable and does not predefine a
foreign-domain target, facts, or guards. Every route-owning chunk from 07
through 15 may promote an action to active only when its owning domain contract,
feature-owned resource composition, surface declaration, and behavior tests
exist. Each such chunk generates a manifest-delta proof for every surface it
migrates. Chunk 16 aggregates and verifies the complete route/command manifest
rather than first discovering missing declarations there.
Resources and transitions owned by WS-REV, WS-CON, or the artifact-storage
specification are not invented by AUTH; their owning specification must first
approve the resource facts and operation before a corresponding permission is
added under the approval rule above.

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

`AuthorizationDecision` carries the stable `ActionId` in addition to permission,
resource, scope, matched authority, and denial information. The action identifier
is included in bounded logs/metrics and every action-based allowed or denied
authority event emitted by AUTH-07 or a later chunk. AUTH-07 adds nullable
historical storage and exact typed/SQL registry parity; legacy rows remain null,
while new action-based decision events must contain a registered identifier. A
new action identifier requires the same approved typed/PostgreSQL registry and
migration treatment as a permission.

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
- registered action identifier for action-based decisions;
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
- every protected route and asynchronous command migrated by that chunk has one
  primary registered action declaration, a canonical target derived through its
  owning feature boundary, and allow/deny tests for its mandatory guards.

Final chunk 16 proof includes a generated `/api/v1` route and asynchronous
command manifest. It fails closed on an unknown permission or resource type, a
duplicate or missing primary declaration, or an unregistered guard. The manifest
is conformance evidence, not a second policy source.

Each activating chunk must also prove its authorization-subsystem changes at or
above 90 percent coverage and preserve the repository-wide 78 percent baseline.

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
