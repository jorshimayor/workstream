# Decisions: WS-AUTH-001 - Workstream Authorization Service

## D1: Adopt WS-AUTH-001 as the authorization authority source

Status: accepted by the user on 2026-07-11.

`WS-AUTH-001` supersedes the repository's token-role bootstrap and current
multi-profile authorization semantics. Existing code and docs remain evidence
of current behavior, not the target authority contract.

## D2: Preserve `/api/v1`

Status: accepted by the user on 2026-07-11.

The repository's existing `/api/v1` namespace remains canonical. The imported
specification's `/v1` examples will be reconciled during the baseline-adoption
chunk. Workstream will not expose two versioned route trees as permanent
aliases.

## D3: Prioritize authorization foundation

Status: accepted by the user on 2026-07-11.

Authorization remains the priority before later locked runtime hardening. The
user separately directed and merged `WS-POL-002-03` through PR #90 as
`a7aa474`; that completed approval API does not activate `WS-POL-002-04` or
change the authorization priority.

## L0 human approval boundary

The user explicitly approved the authorization direction, source precedence,
API namespace, and priority recorded in D1-D3 on 2026-07-11. On 2026-07-11,
after the planning and post-merge memory PRs merged, the user said "ok start" in
direct response to the recorded D4-D10 approval and separate chunk-start gate.
That response approves D4-D10 and starts only `WS-AUTH-001-01`. Every bounded
implementation chunk remains L1 and retains its own human PR/merge checkpoint.

## D4: No dual canonical authority

Status: accepted by the user on 2026-07-11.

Token roles may be retained as non-authoritative diagnostic input during a
bounded migration only. A protected command must never accept either a token
role or a local permission as interchangeable proof. Cutover chunks replace
authorization for complete resource surfaces and remove the old check.

## D5: Preserve historical actor identifiers where classification is safe

Status: accepted by the user on 2026-07-11.

Existing `ActorIdentity.actor_id` values for externally verified callers are
UUID5 strings and are referenced throughout tasks, submissions, checker runs,
project provenance, and audit rows. For a classified legacy row, that UUID
becomes the canonical `ActorProfile.id`; the new `ActorIdentityLink` receives a
separate UUID. Migration must validate UUID shape and uniqueness before reuse.
Invalid or ambiguous rows fail preflight and are not silently rewritten.

The unrelated UUIDs on legacy typed `actor_profiles` rows are workflow-row IDs,
not actor IDs, and never become canonical profile IDs.

## D6: Existing typed profiles do not become grants

Status: accepted by the user on 2026-07-11.

Observed or active `worker`, `reviewer`, `admin`, or `project_manager` profile
rows do not create `AdminRoleGrant` or `ProjectRoleGrant` records. Skills and
non-authoritative workflow metadata may be preserved under a clearly named
metadata model only when required by an existing workflow.

## D7: Internal workers use explicit system authority

Status: accepted by the user on 2026-07-11.

Project setup, pre-review gating, reconciliation, and repair work use fixed
Workstream system principals and registered system permissions. They do not
receive fabricated human admin roles and do not become normal ActorProfiles.

## D8: Production issuer details remain configuration

Status: accepted by the user on 2026-07-11.

The token adapter will require explicit issuer, audience, JWKS URL, algorithm,
scope, clock-skew, and cache configuration and will fail closed when incomplete.
The real issuer values are required for live production-token proof, not for
deterministic adapter implementation with local JWKS fixtures.

## D9: Authority evidence is foundational

Status: accepted by the user on 2026-07-11 after internal review repair.

Request/correlation context, canonical idempotency records, and the shared
append-only authority-event writer are introduced before canonical actor
persistence and before any authority-changing public API. Every later authority
mutation commits state, idempotency result, audit event, and invalidation event
atomically. The final evidence chunk verifies completeness; it does not invent
or backfill the evidence model.

## D10: Legacy classification uses a versioned supported manifest

Status: accepted by the user on 2026-07-11 after internal review repair.

Non-empty legacy registries require a versioned JSON classification manifest
processed by a supported management/preflight tool. Entries bind exact legacy
actor ID, canonical issuer, opaque subject, and `subject_kind`. The tool rejects
duplicates, stale/missing rows, mismatches, unknown fields, and unsupported
kinds; supports dry-run; emits a checksum-bound report; and never writes grants.
The schema migration consumes only validated staged classification evidence or
fails closed. Manual SQL is not a supported path.

## D11: Contributor is the human product term

Status: accepted by the user on 2026-07-11.

Contributor is the umbrella term for a human participating in Workstream. A
contributor has an exact-project `submitter`, `reviewer`, or `both` grant.
Celery, checker, setup, and reconciliation workers are internal services and
background jobs, not human product roles. Existing human-role
values using the old term are migration inputs to remove, not target product
vocabulary or authority concepts.

The field cutover is explicitly owned as follows:

- `WS-AUTH-001-13` renames assignment ownership from legacy `worker_id` to
  `contributor_id` across storage, models, services, schemas, audits, and tests.
- `WS-AUTH-001-14` renames submission ownership/attestation and checker-result
  visibility fields from legacy `worker_*` names to their `contributor_*`
  equivalents across storage, models, services, schemas, audits, and tests. It
  also renames the submission-policy JSON field `worker_facing_fix` to
  `contributor_facing_fix` across derivation schemas, prompts, persistence, and
  compatibility tests.
- Revision replay is not implemented yet and must begin with
  `contributor_claim_status`; it must not introduce the legacy name.
- Contribution and payment records are owned by WS-CON and must begin with
  `contributor_id`; no new legacy column is permitted.

Each owning migration preserves values and immutable attribution, uses only a
bounded transitional storage compatibility layer inside the migration chunk,
exposes no legacy public API alias, and removes the old column/name before that
chunk completes.

## D12: Verified-token production dependencies

Status: accepted by the user on 2026-07-11.

`WS-AUTH-001-02` proposes two exact base dependency changes:

- add `PyJWT[crypto]>=2.13,<3.0` for maintained JOSE/JWK parsing and asymmetric
  signature verification; and
- move the existing `httpx>=0.27,<1.0` requirement from the development extra
  to base dependencies for separately controlled async JWKS and introspection
  clients.

PyJWT's network JWKS client will not be used because Workstream owns redirect,
timeout, streaming-size, cache, and transport-injection policy. The standard
library has no safe equivalent for asymmetric JOSE verification, and
hand-written JOSE or HTTP cryptography is outside the approved design. Chunk
start does not imply dependency approval. No production dependency or runtime
implementation may change until the user explicitly accepts D12 and that
acceptance is recorded here. The user explicitly approved D12 by replying
"ok apporeved" after the final preimplementation plan review passed.

## D13: Identity issuer is the stable verification boundary

Status: accepted by the user on 2026-07-13.

Workstream depends on one provider-neutral `IdentityIssuerVerifier` capability
port. It extends the repository-wide `ExternalServiceAdapter` convention and
is constructed through the typed
`ExternalServiceAdapterFactory[IdentityIssuerVerifier]` foundation being
prepared by `WS-ART-001-02A1`. AUTH must adopt that merged shared foundation; it
must not create a second generic adapter registry or factory.

The `/auth` dependency and product authorization layers must not change when an
additional external identity issuer is configured. Issuer-specific discovery,
JWKS, signature, claim, and introspection behavior remains behind explicit
adapter registration, construction, and configuration; it does not become a
second internal auth system or grant Workstream product authority.

The current `AuthVerifier` port, `FlowAuthVerifier` adapter, and `flow_auth_*`
configuration names are migration inputs rather than the target vocabulary.
Their rename must be one bounded, atomic specification and implementation
chunk covering the port, adapter, factory, configuration compatibility,
tests, operator documentation, and stale-name proof. AUTH-04A does not absorb
that cross-cutting rename because its reviewed request/error scope is already
at the production size circuit breaker. The owning follow-up chunk is blocked
until the shared convention merges, and must then remove the old AUTH factory
entry point and migrate all callers in one clean cut. It must be planned and
reviewed before implementation; no compatibility factory alias, duplicate
verifier, service locator, or public login/session API may be introduced.

## D14: Artifact operations use centralized authorization

Status: accepted by the user on 2026-07-14.

The artifact subsystem owns upload/storage, retention, replication, integrity,
and reconciliation mechanics behind the shared object-storage adapter
foundation. It does not own or infer product authority. Every human-initiated
or internal-service artifact operation must be authorized by Workstream's one
central authorization kernel using an operation-specific permission and the
exact project/resource scope before an adapter performs external I/O.

Human callers resolve through canonical `ActorProfile`, identity-link status,
and the applicable administrative or exact-project contributor grant. Artifact
storage, retention, and reconciliation services authenticate as explicitly
provisioned service principals with registered system permissions; they are not
Contributors and never receive fabricated human roles. Upload, read, retain,
release/delete, replicate, verify, and reconcile authority are distinct and do
not imply one another.

The authorization decision and operation receipt must share bounded request/
correlation evidence, resource identity, operation, and service principal.
Receipts prove that storage work occurred; they do not create authority. AUTH-07A
registers exact artifact permissions and planned actions, AUTH-07B introduces
the central kernel, AUTH-08 defines applicable Operator
grants, and AUTH-09 provisions fixed service principals. Each owning WS-ART
feature chunk supplies the canonical resource composer, guards, surface
declaration, and behavior tests that activate its exact actions. AUTH-12,
AUTH-14, and AUTH-15 are not alternate artifact activation paths. AUTH-04B adds
no artifact permission or route attachment.

## D15: Adopt a staged typed action and resource catalogue

Status: accepted by the user on 2026-07-14 after repository mapping and internal
design review.

AUTH-07A introduces a closed typed action registry, and AUTH-07B activates the
first bounded actions. Each active `ActionId` binds
one already approved `PermissionId` to one canonical authorization target,
candidate authority sources, mandatory guards, principal class, and
transaction-revalidation rule. Multiple closed actions may map to one retained
broad permission while using distinct targets and guards; routes cannot supply
arbitrary permission/target pairs. Creates authorize against an existing parent
or `system` target. Feature
repositories remain persistence owners; feature application services or
feature-owned loaders compose closed, typed per-resource `ResourceContext`
variants and register at the composition root without making AUTH a second
domain-query layer. Guard definitions declare their required resource facts;
unknown, missing, extra, or mistyped facts fail closed.

Each protected route or asynchronous command declares one primary registered
action as its authorization entry point. Domain invariants remain owned by the
feature service. Human bearer tokens are never executable worker authority,
and collection filtering occurs before counts or cursors. Catalogue adoption is
staged: AUTH-07A owns identifiers and planned metadata, AUTH-07B owns the first
self-route definitions, every later route-owning chunk through AUTH-15 owns
declarations during its feature cutover, and
AUTH-16 owns the aggregate generated route/command completeness manifest and
final no-bypass proof.

Reserved planned metadata contains only stable `ActionId`, approved
`PermissionId`, owning specification/chunk, and availability. It cannot
authorize and does not predefine a foreign-domain target, facts, guards, or
composer. An owning cutover chunk activates an action only with its adopted
domain contract, canonical resource composer, route or command declaration,
allow/deny behavior proof, and generated manifest-delta proof.

`ActionId` is security-significant evidence. AUTH-07A adds typed/PostgreSQL
audit parity; AUTH-07B adds it to `AuthorizationDecision`, bounded logs/metrics,
and allowed/denied authority events. Historical events may remain null; every
AUTH-07B-or-later action-based decision event requires a registered identifier.
Planned IDs can be registered before activation because they encode
only identifier, approved permission, owner, and availability, not foreign
resource design.

The reviewed proposal did not receive independent normative precedence. Its
`/v1` prefix, broad-permission replacement, compatibility deletion, and invented
artifact, review, contribution, and compensation resources were rejected. The
adopted `/api/v1` namespace and original 52 approved permission identifiers
were unchanged by that catalogue review. The later approved artifact-storage
contract added 21 exact identifiers, making the pre-D17 closed total 73.
AUTH-05A currently enforces a 49-identifier typed/PostgreSQL audit base; the
three already approved Operator recovery identifiers and 21 artifact
identifiers remain planned and non-executable until AUTH-07A adds typed/SQL audit
parity and the paired owning feature activates each action. Other permission additions or renames still
require an approved specification/ADR change, typed and PostgreSQL registry
migration, audit-history treatment, cutover ownership, and rollback proof.
WS-REV, WS-CON, and the artifact-storage specification continue to own their
resources and state transitions.

Migration custody is reconciled with merged main: AUTH-05A owns `0018`, AUTH-05B
solely owns `0019`, AUTH-06 uses `0020`, AUTH-07A action evidence uses `0021`,
AUTH-08 uses `0022`, AUTH-10 uses `0023`, AUTH-12 uses `0024`, AUTH-13 uses
`0025`, and AUTH-14 uses `0026`.

## D16: Split AUTH-07 at the catalogue and executable-kernel boundary

Status: accepted as a required L1 preimplementation repair on 2026-07-15.

Required architecture, security/auth, and QA/CI plan review found that the
combined AUTH-07 contract placed grant-backed administrative APIs before
AUTH-08, project capability composition before AUTH-10, and mixed the audit
migration with executable kernel/API behavior. No runtime code had started.

At the split boundary, AUTH-07A owned only the exact 73-PermissionId catalogue,
30 four-field
planned ActionId definitions, including both later self actions, and
action-aware audit migration `0021`. AUTH-07B
later owns the minimal deny-by-default kernel and activates only
`actor.profile.read_self` and `actor.profile.update_self`. Permission and
admin-role definition APIs move to AUTH-08; project-scoped authorization
context moves to AUTH-10. Each child retains its own merge and explicit-start
gate.

## D17: Adopt canonical review actions without moving review behavior into AUTH

Status: accepted by the user on 2026-07-15 after mapping the revised WS-REV
source against the implemented AUTH and ART contracts and completing internal
architecture, docs/security, and test/migration review.

AUTH-07A expands the closed catalogue to exactly 74 PermissionIds and 50
planned ActionIds. `review.queue.override` is the only additive PermissionId and
is explicitly the 25th post-`0020` permission; the historical 49-value set does
not change. Twenty planned actions are added: canonical `submission.create`
owned by `WS-AUTH-001-14`, plus 19 review actions owned by exact
`WS-REV-001-05`, `06`, `07`, `08`, `09A`, `11`, and `12` chunks. All additions
remain four-field planned metadata and cannot authorize until their owner
supplies resource composition, guards, candidates, surface declarations,
revalidation, and behavior tests.

Initial and revision submissions share the same `submission.create` action,
permission, and route. There is no `submission.revise`, `review.assign`,
`review_revision.record`, or separately callable revision-preparation action.
Revision preparation is an internal participant and lifecycle guard of the
canonical submission command. Finding and finding-response evidence intake use
distinct actions mapped to existing `review.decision` and `submission.create`
permissions because each is a protected human command that can create artifact
state before the final transaction.

`artifact_recovery.request` is rejected. Operator recovery consumes the already
registered `artifact.verification_job.retry` action through the ART-owned
`ArtifactOperatorRecoveryPort`; ART retains recovery-attempt, execution,
fencing, and idempotency ownership. REV owns no projection dispatch/retry action
because the shared outbox owns dispatch, attempts, retry, dead-letter, and
delivery state. Immediate grant-revocation recovery remains a participant of
the originating AUTH mutation, while missed recovery uses the planned
`review.reconcile.run` action.

AUTH-07B must expose one stable public feature boundary: a request-scoped
`AuthorizationService` bound to the current `AuthorizationContext` and
caller-owned `AsyncSession`. Feature modules call
`require(action_id, typed_resource_context)`; the bound session is the only
transaction source. The service returns and stages one bounded decision, never
commits, and never accepts a raw
PermissionId, candidate grant, or guard. REV owns its ResourceContext composers
and lifecycle invariants and may import only that public AUTH interface and
closed types, never AUTH persistence or grant queries.

## D18: Administrative actions and grants activate together in AUTH-08

Status: accepted as the required L1 contract repair after AUTH-08's explicit
start on 2026-07-15.

AUTH-08 adds no PermissionId. It adds exactly seven ActionIds owned by AUTH-08:
`authorization.permission_catalogue.read`,
`authorization.admin_role_definitions.read`, `admin_role_grant.list`,
`actor.admin_role_grant_history.read`, `admin_role_grant.issue`,
`admin_role_grant.revoke`, and `admin_role_grant.bootstrap`. They map to the
existing `admin_role.read`, `admin_role.grant`, or `admin_role.revoke`
permissions. This preserves D15's one canonical target, candidate, guard set,
and principal type per action instead of collapsing definition reads, scoped
history reads, human mutations, and the local trust root. They activate only
with the one-time local bootstrap, exact five-role permission matrix, immutable
AdminRoleGrant persistence, grant-backed central-kernel evaluation, scoped
definition/history APIs, audit/idempotency parity, and final-administrator
locking in the same reviewed chunk. The merged 50-action catalogue therefore
becomes 57 actions with exactly nine active actions after AUTH-08; every other
action remains planned.

The local bootstrap command declares `admin_role_grant.bootstrap` in its command
manifest but does not fabricate a bearer AuthorizationContext or human grant.
HTTP surfaces continue to use only request-scoped
`AuthorizationService.require(action_id, typed_resource_context)`. System scope
is not superuser authority, token roles never become candidates, and AUTH-09
remains the owner of actor/link lifecycle mutations that must later reuse the
AuthorityControl-first final-administrator lock order.

For the two admin-grant mutations, this decision supersedes AUTH-05B's generic
grant-resource `effective=true -> false` invalidation placeholder. Issue
invalidates the target actor authority projection `false -> true`; revoke
invalidates it `true -> false`. AUTH-08 must update typed and PostgreSQL audit
validation together and prove both directions. Human-readable bounded grant and
revocation reasons live on immutable AdminRoleGrant history; request digests
remain in idempotency evidence, and audit reasons remain closed classifications.
