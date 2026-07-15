# Authorization Handoff: WS-CON-001

## Status and ownership

Every ActionId below is **proposed and currently absent**. AUTH-07A commit
`3ab25cf` merged to trusted `main` through `e9d72a1`; the canonical catalogue
now contains 74 PermissionIds and 50 planned non-WS-CON ActionIds. Its additive
permission is `review.queue.override`. Neither proposed WS-CON service-only
PermissionId is registered, and none of the proposed WS-CON ActionIds is in the
merged closed enum.

AUTH owns ActionId/ActionOwner registration, PermissionId registration,
typed/PostgreSQL parity, grants, service ActorProfiles and exact service-action
assignments, and kernel behavior. The feature owner below owns canonical
resource composition, lifecycle guards, transaction-time revalidation,
behavioral proof, and activation after AUTH registration merges. WS-CON must not
edit AUTH persistence, catalogue, grant, or kernel files.

## Proposed closed handoff

`T` means authority must be revalidated in the same caller transaction after
the relevant canonical rows are locked. `Q` means request-scoped authorization
is sufficient because the operation is read-only, but resource facts still come
from canonical rows.

| Proposed ActionId | PermissionId | Target | Candidate principal | Canonical facts/mandatory guards | Revalidation | Registry / activation owner |
|---|---|---|---|---|---:|---|
| `contribution.read_self` | existing `contribution.read_self` | ContributionRecord | human contributor | contribution, project, contributor; caller is exact contributor; minimal self disclosure | Q | AUTH / CON-09B; reused by CON-10A |
| `contribution.read_project` | existing `contribution.read_project` | Project contribution collection | Project Manager, Finance Authority, Operator/Audit as separately eligible | exact project role/operational scope; pre-filtered pagination and concealment; Reviewer is self-only and gains no project-wide history | Q | AUTH / CON-09B; reused by CON-10A |
| `compensation.policy.read` | existing `compensation.policy.manage` | CompensationPolicyVersion | Finance Authority candidate only | exact project; version belongs to project; no provider secret or service route data | Q | AUTH / CON-04B |
| `compensation.policy.create_draft` | existing `compensation.policy.manage` | Project compensation policy collection | Finance Authority candidate | exact project; setup state; referenced bindings belong to project/instrument | T | AUTH / CON-04B |
| `compensation.policy.update_draft` | existing `compensation.policy.manage` | draft CompensationPolicyVersion | Finance Authority candidate | same project; draft only; optimistic version and immutable published fields | T | AUTH / CON-04B |
| `compensation.policy.publish` | existing `compensation.policy.manage` | draft CompensationPolicyVersion | Finance Authority candidate | project selector, version, all referenced bindings active; closed rules; no contradictory guide handoff | T | AUTH / CON-04B |
| `compensation.policy.retire` | existing `compensation.policy.manage` | published CompensationPolicyVersion | Finance Authority candidate | same project; preserve frozen work; no selector corruption | T | AUTH / CON-04B |
| `compensation.adapter_binding.read` | existing `compensation.adapter_binding.manage` | CompensationAdapterBinding | Finance Authority candidate | exact project; redact route identity as required; never expose credentials | Q | AUTH / CON-04A |
| `compensation.adapter_binding.create` | existing `compensation.adapter_binding.manage` | Project adapter-binding collection | Finance Authority candidate | project, instrument, adapter capability, canonical active service actor and non-secret route identity | T | AUTH / CON-04A |
| `compensation.adapter_binding.suspend` | existing `compensation.adapter_binding.manage` | CompensationAdapterBinding | Finance Authority candidate | project/binding state; block new freezes/delivery, preserve existing callback obligations | T | AUTH / CON-04A |
| `compensation.adapter_binding.resume` | existing `compensation.adapter_binding.manage` | CompensationAdapterBinding | Finance Authority candidate | actor/link/action assignment and adapter capability are active; no silent backlog mutation | T | AUTH / CON-04A |
| `compensation.adapter_binding.retire` | existing `compensation.adapter_binding.manage` | CompensationAdapterBinding | Finance Authority candidate | no active-policy reference, unfinished frozen assignment/lease, or unfulfilled award; after retirement only exact replay of a previously accepted receipt remains | T | AUTH / CON-10B |
| `compensation.award.read_self` | existing `contribution.read_self` | CompensationAward | human beneficiary | award/project/beneficiary; exact subject match; safe status only | Q | AUTH / CON-10A |
| `compensation.award.read_project` | existing `compensation.award.read` | Project award collection | Finance Authority, Operator/Audit as separately eligible | exact project/ops scope; pre-filtered pagination; no provider refs | Q | AUTH / CON-10A |
| `compensation.delivery.reconcile` | existing `compensation.delivery.reconcile` | CompensationDelivery | Finance Authority or reason-bound Operator candidate | exact project/delivery; immutable event/payload/binding/idempotency identity; distinct finance/operator guards | T | AUTH / CON-10B |
| `compensation.status.read` | existing `operations.status.read` | Compensation operations projection | Operator candidate | bounded operational scope; redacted failure class; no beneficiary/provider secret | Q | AUTH / CON-10B |
| `compensation.reconcile.run` | existing `operations.reconcile.run` | Compensation reconciliation request | reason-bound Operator candidate | bounded project/range; durable request only; immutable truth comparison; never repair canonical awards/receipts; async execution is a shared-outbox handler under fixed dispatch authority | T | AUTH / CON-10B |
| `contribution.projection.rebuild` | existing `operations.projection.rebuild` | Contribution projection rebuild request | reason-bound Operator candidate | bounded project/version; durable request only; rebuild projection only; immutable truth unchanged; async execution is a shared-outbox handler under fixed dispatch authority | T | AUTH / CON-10B |
| `audit.read` | existing `audit.read` | WS-CON audit projection | Audit/Operator candidate | exact project/ops scope; redaction and pagination; append-only truth | Q | AUTH / CON-10B |
| `audit.export` | existing `audit.export` | bounded WS-CON audit export | Audit candidate | exact scope, purpose, maximum range, redaction, export evidence | T | AUTH / CON-10B |
| `compensation.fulfillment.report` | **new service-only `compensation.fulfillment.report`** | frozen CompensationAdapterBinding + Award | exact bound service ActorProfile only | actor/link/action assignment active; route identity, award, project, instrument, frozen binding and receipt state all match | T | AUTH / CON-08B |
| `outbox.dispatch` | **new service-only `outbox.dispatch`** | claimed shared OutboxEvent | fixed `workstream.outbox.dispatcher` ActorProfile only | current claim/lease/generation; immutable event, payload and idempotency identity; handler side effects occur only under this claimed command | T | AUTH + shared outbox / CON-02B prerequisite; consumed by CON-08A |
| `artifact.contribution_evidence.binding.create` | existing `artifact.binding.create` | ContributionRecord evidence role | fixed ART/CON worker service actor | exact contribution/project/role/schema/digest; ART admission/verification receipt; no raw provider ref | T | AUTH + ART / ART prerequisite then CON-09A |

## Adapter service-identity invariant

Each CompensationAdapterBinding persists an `adapter_actor_id` referencing a
canonical service ActorProfile, project, instrument, adapter capability, and a
non-secret route identity. AUTH creates the exact
`compensation.fulfillment.report` service-action assignment. Human
AdminRoleGrant or ProjectRoleGrant records can never satisfy this action, and
WS-CON never fabricates such grants.

Under the canonical lock order a callback revalidates actor state, identity-link
state, exact service-action assignment, route identity, award, project,
instrument, frozen binding, binding state, and delivery/receipt state. Controls
are rate-limited and idempotent per actor plus binding, not by shared IP alone.

- Active binding: new freeze, delivery, and valid callback are eligible.
- Suspended binding: no new freeze or delivery; a valid callback for an award
  already frozen/issued to that binding may still fulfill it.
- Retirement is denied while an active policy references the binding or any
  unfinished frozen assignment/lease or unfulfilled award depends on it.
  Retired binding: no new freeze, delivery, or receipt; only byte-for-byte exact
  replay of a receipt already accepted before retirement is acknowledged.
- Callback before local acknowledgement creates the terminal receipt/status and
  suppresses later delivery without regressing state or changing identities.

Actor suspension/revocation and identity-link revocation always deny; these are
distinct from adapter-binding suspension.

## Shared-outbox and ART prerequisites

CON-08A is an outbox handler, not an independently authorized compensation
command. The shared-outbox owner must register and provision `outbox.dispatch`
for the fixed dispatcher before CON-08A activates; human
`operations.outbox.retry` authority can request recovery but can never execute
delivery. CON-09A similarly consumes a narrow ART-owned capability after ART
registers `artifact.contribution_evidence.binding.create`; CON never receives a
raw storage port or an artifact-recovery execution authority.
