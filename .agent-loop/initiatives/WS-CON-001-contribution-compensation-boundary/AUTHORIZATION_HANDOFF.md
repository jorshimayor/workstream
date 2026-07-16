# Authorization Handoff: WS-CON-001

## Status and ownership

Every WS-CON-specific ActionId below is **proposed and currently absent**.
Trusted `main` `9a04434` includes AUTH-08 through PR #131 at `aa0fdcd` and the
later ART-02A2 merge, which changes no authorization contract. The canonical
catalogue contains 74 PermissionIds and 57 non-WS-CON ActionIds: the two
actor-self actions and seven AUTH-08 administrative actions are active; 48
actions remain planned. Neither proposed WS-CON service-only PermissionId is
registered, and none of the 23 proposed WS-CON ActionIds is in the merged
closed enum.

AUTH-08 materially advances, but does not complete, the runtime boundary.
`AuthorizationResourceContext` now has eight closed variants;
`MatchedAuthorityKind` has `actor_self` and `admin_role_grant`; decisions carry
the complete resource-context digest plus matched grant/scope evidence; and the
kernel evaluates the self and administrative families. The current FastAPI
actor dependency still rejects service subjects, ProjectRoleGrant and service
assignment authority are not implemented, and no WS-CON evaluator exists.
Registering an ActionId as planned is therefore intentionally insufficient:
every WS-CON surface still fails with `action_unavailable` until AUTH supplies
its action-specific context, exact candidate-role filter/evaluator, remaining
principal or service assignment, transaction protocol, and active availability.

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

1. After D12 approval, register the exact ActionId, one ActionOwner/activation-
   custody mapping, PermissionId mapping and audit/SQL parity. No feature owner
   or registration PR is a second activation authority. If the human approves
   D4's service expansion, add only the two
   proposed new PermissionIds,
   `outbox.dispatch` and `compensation.fulfillment.report`; all other rows reuse
   the existing PermissionId in the table.
2. Add closed typed resource-context variants for the target families below and
   extend the decision resource type without accepting generic dictionaries,
   client-supplied grants, raw PermissionIds, or CON persistence objects.
3. Extend the current self/admin family dispatch into an explicit closed
   evaluator registry or equivalent AUTH-owned dispatch. No runtime plugin
   discovery, service locator, fallback allow path, CON repository import, or
   action string construction is permitted.
4. Extend matched authority for exact actor-self, AdminRoleGrant,
   ProjectRoleGrant, and service-action-assignment authority as applicable.
   AUTH-08's durable AdminRoleGrant definitions and scope evidence are now
   merged and must be reused; AUTH-09 service actor/assignment truth and
   AUTH-10 project contributor grants must merge before dependent evaluators
   activate. Permission membership alone is not an allow: each action evaluator
   must enforce the exact candidate-role allowlist in the table below. AUTH
   extends its repository/kernel candidate lookup with an evaluator-owned closed
   AdminRole set intersected with `permissions_for(role)` before query; neither
   CON nor request data may supply that set. An actor holding both an excluded
   and eligible role must match the eligible grant deterministically.
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
   mismatched, reused, cross-session or cross-action handles fail closed. The
   final decision preserves AUTH-08's complete `resource_context_digest`, exact
   `matched_grant_id` and covered project scope when grant-backed.
6. For `Q` reads, retain request-scoped `require(action_id,
   typed_resource_context)` while loading canonical authority and applying
   pre-filter/concealment rules. No decision or grant cache survives a request.
   Every route explicitly commits its own read/mutation plus decision evidence;
   the AUTH dependency rolls back an abandoned transaction and never rescues a
   missing feature commit. Hidden CON domain services only flush and never
   commit; REV-13's actual route owners prove the commit/rollback behavior.
   AUTH evidence failure remains the typed retryable service-unavailable path
   introduced by AUTH-08.
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
fold WS-CON permissions/actions into AUTH-09 through AUTH-16 or an unrelated
feature PR without an allowed-file/acceptance/reviewer amendment.

## Proposed AUTH-owned ActionOwner custody

Canonical `ActionOwner` currently means the implementation chunk allowed to
activate a reserved action. Because the user requires authorization activation
to remain in the authorization service, a CON/REV feature chunk cannot also be
the ActionOwner. D12 proposes the following exact AUTH-owned activation chunks;
the AUTH owner and human must approve/add these enum members and chunk contracts
before any registration checkpoint uses them.

| Proposed enum member | Exact ActionOwner value / AUTH activation chunk | Exact ActionIds |
|---|---|---|
| `AUTH_CON_OUTBOX` | `WS-AUTH-001-CON-OUTBOX` | `outbox.dispatch` |
| `AUTH_CON_BINDING` | `WS-AUTH-001-CON-BINDING` | `compensation.adapter_binding.read`, `compensation.adapter_binding.create`, `compensation.adapter_binding.suspend`, `compensation.adapter_binding.resume` |
| `AUTH_CON_POLICY` | `WS-AUTH-001-CON-POLICY` | `compensation.policy.read`, `compensation.policy.create_draft`, `compensation.policy.update_draft`, `compensation.policy.publish`, `compensation.policy.retire` |
| `AUTH_CON_CALLBACK` | `WS-AUTH-001-CON-CALLBACK` | `compensation.fulfillment.report` |
| `AUTH_CON_EVIDENCE` | `WS-AUTH-001-CON-EVIDENCE` | `artifact.contribution_evidence.binding.create` |
| `AUTH_CON_CONTRIBUTION_READS` | `WS-AUTH-001-CON-CONTRIBUTION-READS` | `contribution.read_self`, `contribution.read_project` |
| `AUTH_CON_AWARD_READS` | `WS-AUTH-001-CON-AWARD-READS` | `compensation.award.read_self`, `compensation.award.read_project` |
| `AUTH_CON_OPERATIONS` | `WS-AUTH-001-CON-OPERATIONS` | `compensation.adapter_binding.retire`, `compensation.delivery.reconcile`, `compensation.status.read`, `compensation.reconcile.run`, `contribution.projection.rebuild`, `audit.read`, `audit.export` |

This table maps all 23 proposed WS-CON ActionIds exactly once. A registration
PR may reserve an action for its named future activation chunk, but only that
exact ActionOwner may later change availability after the feature gate. The
feature resource owner remains the CON/ART owner in the handoff table below and
does not gain catalogue custody.

The same semantic conflict already exists for the two review actions consumed
here: merged `review.claim` is owned by `REV_06` and `review.decision` by
`REV_08`, while the repaired choreography requires AUTH-owned activation after
REV composition. D12 therefore also proposes `AUTH_REV_CLAIM =
WS-AUTH-001-REV-CLAIM` and `AUTH_REV_DECISION =
WS-AUTH-001-REV-DECISION`, with a reviewed AUTH registration amendment that
transfers those planned actions before activation. Alternatively, the human may
choose a global, reviewed redefinition of ActionOwner as feature/resource
owner—but then AUTH must introduce a separate closed activation-custody type.
Leaving the current dual meaning or allowing both AUTH and product chunks to
activate is forbidden.

Under the recommended transfer model, AUTH atomically removes the now-unused
`ActionOwner.REV_08` after moving its only row, `review.decision`, to
`AUTH_REV_DECISION`. `REV_06` remains because it still owns the other review
release/decline/expiry actions. Closed enum/definition/SQL/audit parity tests
must reject an unused old owner or a missing new owner.

The ART prerequisite exposes the same conflict: the merged catalogue assigns
all eleven 02D Operator/internal actions to `ActionOwner.ART_02D`, while this
plan and the user require AUTH to own availability. D12 therefore also proposes
the following complete transfer while every action is still planned. No
ActionId or PermissionId changes, and ART-02D remains the feature/resource
owner only.

| Proposed enum member | Exact ActionOwner value / AUTH activation chunk | Existing ActionId -> PermissionId mappings transferred from `ART_02D` |
|---|---|---|
| `AUTH_ART_02D_OPERATOR` | `WS-AUTH-001-ART-02D-OPERATOR` | `artifact.binding.read` -> `artifact.binding.read`; `artifact.replica.read` -> `artifact.replica.read`; `artifact.receipt.read` -> `artifact.receipt.read`; `artifact.verification_job.read` -> `artifact.verification_job.read`; `artifact.verification_job.retry` -> `artifact.verification_job.retry`; `artifact.recovery_attempt.read` -> `artifact.recovery_attempt.read`; `artifact.audit.read` -> `artifact.audit.read`; `operations.artifact_storage_admission.read` -> `operations.status.read` |
| `AUTH_ART_02D_INTERNAL` | `WS-AUTH-001-ART-02D-INTERNAL` | `artifact.verification.execute` -> `artifact.verification.execute`; `artifact.pending_work.scan` -> `artifact.pending_work.scan`; `artifact.put_attempt.resolve` -> `artifact.put_attempt.resolve` |

AUTH-09 owns the fixed internal ActorProfiles, links and exact assignments. After
ART-02D merges hidden resources, guards, calls and behavior proof, the two AUTH
activation chunks integrate the closed evaluators and alone change availability.
The Operator retry action is an independent human action; activating the three
service actions does not activate `artifact.verification_job.retry`. If D12
instead adopts global feature-owner semantics, these same eleven mappings must
appear in the separate closed activation-custody type before ART-02D starts.
Partial transfer, `ART_02D` plus AUTH dual writers, or a generic ART activation
owner is forbidden.

Under the recommended transfer model, AUTH atomically removes the now-unused
`ActionOwner.ART_02D` after all eleven definitions move to the two new AUTH
owners. The closed invariant remains
`{definition.owner} == set(ActionOwner)`. Under the global alternative,
`ART_02D` and `REV_08` remain feature owners in action definitions and the new
separate activation-custody catalogue—not `ActionOwner`—must independently have
exact closed coverage. The two models cannot be mixed.

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
| `compensation.award.read_project` | existing `compensation.award.read` | Project award collection | D11 candidate: Finance Authority and Operator/Audit; Project Manager inclusion unresolved | exact project/ops scope; pre-filtered pagination; no provider refs | Q | AUTH / CON-10A |
| `compensation.delivery.reconcile` | existing `compensation.delivery.reconcile` | CompensationDelivery | D11 candidate: Finance Authority plus reason-bound Operator if approved | exact project/delivery; immutable event/payload/binding/idempotency identity; distinct finance/operator guards | T | AUTH / CON-10B |
| `compensation.status.read` | existing `operations.status.read` | Compensation operations projection | Operator candidate | bounded operational scope; redacted failure class; no beneficiary/provider secret | Q | AUTH / CON-10B |
| `compensation.reconcile.run` | existing `operations.reconcile.run` | Compensation reconciliation request | reason-bound Operator candidate | bounded project/range; durable request only; immutable truth comparison; never repair canonical awards/receipts; async execution is a shared-outbox handler under fixed dispatch authority | T | AUTH / CON-10B |
| `contribution.projection.rebuild` | existing `operations.projection.rebuild` | Contribution projection rebuild request | reason-bound Operator candidate | bounded project/version; durable request only; rebuild projection only; immutable truth unchanged; async execution is a shared-outbox handler under fixed dispatch authority | T | AUTH / CON-10B |
| `audit.read` | existing `audit.read` | WS-CON audit projection | D11 candidate set unresolved against broader merged roles | exact project/ops scope; redaction and pagination; append-only truth | Q | AUTH / CON-10B |
| `audit.export` | existing `audit.export` | bounded WS-CON audit export | D11 candidate set unresolved against Access Administrator/Audit permission candidates | exact scope, purpose, maximum range, redaction, export evidence | T | AUTH / CON-10B |
| `compensation.fulfillment.report` | **new service-only `compensation.fulfillment.report`** | frozen CompensationAdapterBinding + Award | exact bound service ActorProfile only | actor/link/action assignment active; route identity, award, project, instrument, frozen binding and receipt state all match | T | AUTH / CON-08B |
| `outbox.dispatch` | **new service-only `outbox.dispatch`** | claimed shared OutboxEvent | fixed `workstream.outbox.dispatcher` ActorProfile only | current claim/lease/generation; immutable event, payload and idempotency identity; handler side effects occur only under this claimed command | T | AUTH / CON-02B shared-outbox prerequisite; consumed by CON-08A |
| `artifact.contribution_evidence.binding.create` | existing `artifact.binding.create` | ContributionRecord evidence role | existing fixed `workstream.artifact.binding` service ActorProfile only | exact contribution/project/role/schema/digest; ART admission/verification receipt; no raw provider ref | T | AUTH / ART capability + CON-09A composer |

## Merged AUTH-08 role-matrix reconciliation

AUTH-08 proves the five AdminRole definitions and exact permission candidates,
but one merged row conflicts with the reconciled candidate WS-CON human
authority matrix. `finance_authority` contains
`compensation.delivery.reconcile`; `operator` does not. The candidate proposes
both a covered Finance Authority and a reason-bound system-scoped Operator for
the exact `compensation.delivery.reconcile` action, but only D2 has explicit
human approval. D11 therefore remains a human decision. If the Operator
behavior is approved, a reviewed AUTH-owned successor must add the **existing**
`compensation.delivery.reconcile` PermissionId to the closed Operator
definition, update definition/API/kernel matrix tests, and retain the action-
specific reason/scope guards. If it is rejected, the active WS-CON contract and
handoff must remove the Operator candidate before registration. No new
PermissionId is needed in either case, and CON must not query roles or emulate
the missing candidate locally.

The inverse constraint is equally important, but is also unresolved rather than
implicitly approved. The merged Project Manager definition contains
`compensation.award.read`, while the candidate WS-CON matrix excludes Project
Manager from monetary award/fulfillment detail. Merged audit permissions also
cover broader roles than the candidate Audit/Operator and Audit-only surfaces.
D11 must choose the exact action-specific role sets. If a narrower set is
approved, AUTH evaluators filter candidate AdminRole values before resource
guards, preserve the exact matched grant/scope, and prove every excluded,
foreign-project, revoked-grant, wrong-scope and mixed excluded+eligible case. If
the merged role candidates are preserved, CON-01 updates the active matrix and
tests that exact wider set. Neither outcome may be inferred from PermissionId
membership or implemented as CON role logic.

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
| Operations | full D11 human decision plus any required AUTH role-matrix/evaluator amendment; planned retire/reconcile/status/rebuild/audit actions, typed contexts, prepared protocol and exact chosen candidate-role filters | CON-10B | CON-11 |

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
