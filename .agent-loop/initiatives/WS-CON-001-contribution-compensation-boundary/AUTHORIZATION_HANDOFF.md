# Authorization Handoff: WS-CON-001

## Status and ownership

Every WS-CON-specific ActionId below is **proposed and currently absent**.
Trusted `main` `90eca12` includes AUTH-07B. The canonical catalogue now contains
74 PermissionIds and 50 non-WS-CON ActionIds: only
`actor.profile.read_self` and `actor.profile.update_self` are active; the other
48 are planned. Neither proposed WS-CON service-only PermissionId is registered,
and none of the 23 proposed WS-CON ActionIds is in the merged closed enum.

AUTH-07B also makes the runtime boundary concrete. `AuthorizationService`
currently evaluates only the two actor-self actions;
`AuthorizationResourceContext` accepts only actor-self and system variants;
`MatchedAuthorityKind` contains only `actor_self`; and the current FastAPI
composition dependency rejects service subjects. Registering an ActionId as
planned is therefore intentionally insufficient: every WS-CON surface would
continue to fail with `action_unavailable` until AUTH supplies its typed
context, evaluator, principal/grant or exact service assignment, transaction
protocol, and active availability.

AUTH owns ActionId/ActionOwner and PermissionId registration,
typed/PostgreSQL/audit parity, availability transitions, central evaluator
dispatch, matched-authority types, grant loading, actor/link/grant
revalidation, service ActorProfiles, exact service-action assignments, and the
request/worker/callback authorization composition roots. WS-CON owns canonical
product-row loading, construction of AUTH-approved typed resource facts,
product lifecycle guards, and feature behavior proof. WS-CON never edits AUTH
persistence, catalogue, runtime, grant, evaluator, or kernel files and never
changes an action from planned to active.

## Required AUTH delivery contract

Authorization delivery uses two AUTH-owned checkpoints around one feature-owned
chunk. Before the feature chunk starts, an AUTH registration checkpoint provides
the planned identifier/mapping, typed context contract, principal prerequisites
and prepared protocol. The feature chunk then lands hidden authorization-ready
behavior and its canonical resource composer while the action still fails
closed. Only after that feature commit is merged may an AUTH activation
checkpoint integrate the evaluator, prove end-to-end behavior and change
availability. The feature is not executable production authorization between
those checkpoints.

Across those checkpoints AUTH must provide all applicable items below:

1. Register the exact ActionId, ActionOwner, PermissionId mapping and audit/SQL
   parity. Add only the two approved new PermissionIds,
   `outbox.dispatch` and `compensation.fulfillment.report`; all other rows reuse
   the existing PermissionId in the table.
2. Add closed typed resource-context variants for the target families below and
   extend the decision resource type without accepting generic dictionaries,
   client-supplied grants, raw PermissionIds, or CON persistence objects.
3. Replace the current two-action-only evaluator branch with an explicit closed
   evaluator registry or equivalent AUTH-owned dispatch. No runtime plugin
   discovery, service locator, fallback allow path, CON repository import, or
   action string construction is permitted.
4. Extend matched authority for exact actor-self, AdminRoleGrant,
   ProjectRoleGrant, and service-action-assignment authority as applicable.
   AUTH-08 grant definitions, AUTH-09 service actor/assignment truth, and
   AUTH-10 project contributor grants must be merged before dependent
   evaluators activate.
5. For `T` mutations, provide one caller-session-bound prepared-authorization
   protocol. It accepts the action plus a server-resolved preliminary target,
   locks/revalidates AUTH actor/link/grant or service-assignment rows first,
   returns an opaque non-serializable handle bound to the request, session,
   actor, action and target, then evaluates exactly once against the final
   typed context recomposed from locked product rows. This preserves the PLAN
   lock order and stages one decision without AUTH committing. A prepare-time
   lifecycle/availability/authority denial terminates with that one denial and
   returns no handle; a successful prepare stages no allow until final
   evaluation. Missing,
   mismatched, reused, cross-session or cross-action handles fail closed.
6. For `Q` reads, retain request-scoped `require(action_id,
   typed_resource_context)` while loading canonical authority and applying
   pre-filter/concealment rules. No decision or grant cache survives a request.
7. Add a service-capable composition dependency for fixed workers and bound
   callbacks. Human grants never satisfy a service-only action, service
   assignments never imply a human role, and suspended/revoked/deactivated
   actor or link state fails closed.
8. Change availability to active only after the named CON/ART resource composer
   and hidden behavior implementation is merged. The AUTH activation change
   owns central integration tests against that exact merged implementation.
   Startup parity must reject missing or extra
   identifiers, mappings, evaluators, service identities, assignments, or
   active actions without executable behavior.

These are AUTH implementation requirements, not authorization behavior that a
CON chunk may reproduce locally. A CON feature chunk may use an explicit test
decision/fake below its authorization boundary to prove domain behavior, but no
test or production fallback may make a planned action executable through the
real kernel.

The current WS-AUTH chunk map has no WS-CON registration or activation chunks.
The AUTH owner must first add and internally review bounded chunk contracts for
the registration checkpoint, the shared prepared protocol if not delivered by
an earlier AUTH foundation, and each activation wave below. Do not silently
fold WS-CON permissions/actions into AUTH-08 through AUTH-16 or an unrelated
feature PR without an allowed-file/acceptance/reviewer amendment.

## Proposed closed handoff

`T` means the AUTH-owned prepared protocol locks authority first and the feature
then evaluates against facts recomposed from its locked product rows in the same
caller transaction. `Q` means request-scoped authorization is sufficient
because the operation is read-only, but resource facts still come from
canonical rows.

| Proposed ActionId | PermissionId | Target | Candidate principal | Canonical facts/mandatory guards | Revalidation | AUTH activation / feature resource owner |
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
| `outbox.dispatch` | **new service-only `outbox.dispatch`** | claimed shared OutboxEvent | fixed `workstream.outbox.dispatcher` ActorProfile only | current claim/lease/generation; immutable event, payload and idempotency identity; handler side effects occur only under this claimed command | T | AUTH / CON-02B shared-outbox prerequisite; consumed by CON-08A |
| `artifact.contribution_evidence.binding.create` | existing `artifact.binding.create` | ContributionRecord evidence role | existing fixed `workstream.artifact.binding` service ActorProfile only | exact contribution/project/role/schema/digest; ART admission/verification receipt; no raw provider ref | T | AUTH / ART capability + CON-09A composer |

## Existing product-action dependency

`task.claim` is not one of the 23 WS-CON-specific actions, but current trusted
`main` contains only its PermissionId; no `ActionId.TASK_CLAIM` exists. Before
CON-05A can integrate compensation freezing, AUTH-13 or a reviewed AUTH-owned
successor must register and activate ActionId `task.claim` mapped to existing
PermissionId `task.claim`, using the canonical project/task target,
exact-project submitter-or-both grant, actor/link/grant revalidation, and the
prepared `T` protocol. CON-05A adds only the compensation-policy product guard
and frozen-version participant to the already authorized task-owned claim
transaction.

Likewise, registered review actions such as `review.claim` and
`review.decision` remain unusable while planned. Their sequence is AUTH
registration/typed/prepared contract -> CON capability/participant -> REV
hidden resource composition and final-context integration while the real kernel
still denies -> AUTH evaluator integration/activation. Only then may the
already-merged hidden composition execute outside explicit test boundaries.
WS-CON and WS-REV do not activate them.

## Activation waves

| Authority family | AUTH registration checkpoint | Feature-owned hidden implementation | AUTH activation must merge before |
|---|---|---|---|
| Shared-outbox service | planned `outbox.dispatch`, new permission, typed contract, fixed actor/link/assignment and prepared protocol | CON-02B dispatcher integrates the prepared seam but remains disabled/fail-closed | CON-08A or any dispatcher enablement |
| Binding management | planned binding read/create/suspend/resume actions, typed contracts, applicable grant definitions and prepared protocol; retire may be registered but stays planned; plus the planned callback ActionId/new PermissionId and active callback service actor/link/exact assignment needed to validate a binding (the callback action remains unavailable) | CON-04A read/create/suspend/resume only | CON-04B; retire activates only in the operations wave after CON-10B |
| Policy management | planned policy actions, typed contracts, Finance grant definition, prepared protocol | CON-04B | CON-05A |
| Task claim | planned `task.claim` registration plus typed/prepared contract | AUTH-13 task resource composer, guards and behavior | AUTH evaluator/activation in AUTH-13 or a reviewed successor before CON-05A |
| Review authority | existing planned `review.claim`/`review.decision` plus typed/prepared prerequisites | CON-06 + REV-06 hidden claim composition; CON-07 + REV-10 hidden decision composition, all real-kernel fail-closed | any production execution, CON-11 or REV-13 |
| Bound callback service | callback identity/action registration already required before CON-04A; typed callback context and prepared protocol complete before CON-08B | CON-08B | CON-11 |
| Contribution evidence service | planned evidence-binding action/service contract, prepared protocol plus ART capability | ART prerequisite + CON-09A composer/handler integrates the prepared seam | CON-11 |
| Contribution reads | planned self/project read actions and typed contexts | CON-09B | CON-10A |
| Award reads | planned self/project award actions and typed contexts | CON-10A | CON-10B |
| Operations | planned retire/reconcile/status/rebuild/audit actions, typed contexts, grants and prepared protocol | CON-10B | CON-11 |

No row authorizes public route registration. CON-11 proves the hidden action
manifest and REV-13 remains the sole joint public activation owner.

## Adapter service-identity invariant

Each CompensationAdapterBinding persists an `adapter_actor_id` referencing a
canonical service ActorProfile, project, instrument, adapter capability, and a
non-secret route identity. AUTH creates the exact
`compensation.fulfillment.report` service-action assignment. Human
AdminRoleGrant or ProjectRoleGrant records can never satisfy this action, and
WS-CON never fabricates such grants.

That callback identity is a binding-creation prerequisite, not an executable
callback. Before CON-04A, AUTH must register the planned ActionId and new
PermissionId and create an active service ActorProfile/link with the exact
assignment so CON can validate canonical identity. The action remains planned
and fail-closed until CON-08B supplies the callback composer/behavior and the
later AUTH activation gate passes.

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
command. After CON-02B merges its hidden dispatcher, AUTH must integrate and
activate `outbox.dispatch` for the fixed dispatcher before CON-08A activates;
human
`operations.outbox.retry` authority can request recovery but can never execute
delivery. CON-09A similarly consumes a narrow ART-owned capability after AUTH
registers the planned `artifact.contribution_evidence.binding.create` and adds
that exact assignment to the existing fixed `workstream.artifact.binding`
principal; a separately invented evidence worker is forbidden absent a reviewed
AUTH amendment. AUTH may activate it only after the ART capability and CON
composer merge. CON never receives a raw storage port or an artifact-recovery
execution authority.

Both service mutations use D10 at their owning call sites. CON-02B prepares
`outbox.dispatch` from a server-resolved event target before locking the claimed
OutboxEvent, then evaluates exactly once against final locked claim facts.
CON-09A prepares the evidence-binding action before locking its CON-owned
projection/contribution rows, then passes the handle and canonical CON facts to
the narrow ART capability. ART locks/composes its own admission facts and
performs the handle's one final evaluation in durable Transaction A before that
transaction stages admission/put-attempt state and commits; CON never imports
ART persistence or evaluates ART facts. Provider I/O and verification occur
only after Transaction A commits under ART-owned continuation/executor
authority. Later AUTH activation integrates the evaluators against those seams;
it does not retrofit or edit feature code.
