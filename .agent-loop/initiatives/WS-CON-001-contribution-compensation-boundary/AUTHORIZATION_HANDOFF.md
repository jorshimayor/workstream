# Authorization Handoff: WS-CON-001

## Current baseline

Trusted `main` is `5d353b6` from merged PR #139. The runtime catalogue still
contains 74 PermissionIds and 57 ActionIds: nine active and 48 planned. No
WS-CON-specific ActionId below is registered. WS-XINT changed planning and
canonical contracts, not runtime authorization.

AUTH owns identifiers, stable mappings, activation custody, typed resource and
principal contexts, grants, fixed ServiceIdentity/static matrix, AUTH-09E
admission, prepared mutation handles, evaluator dispatch, decision evidence,
availability, and parity. CON owns canonical product loaders, typed resource
facts, lifecycle guards, hidden behavior, and feature tests. Neither side
imports the other's repositories or mutates the other's state.

## Required delivery sequence

Every protected CON surface follows:

```text
AUTH registration checkpoint
  planned ActionId + stable PermissionId + AUTH ActionOwner
  principal class + typed context + prepared protocol when mutating
-> CON hidden-behavior checkpoint
  canonical resource loader + guards + behavior, real kernel still denies
-> AUTH activation checkpoint
  exact evaluator + matched authority + negative proof + active availability
-> joint release checkpoint
```

Registration, provisioning, matrix membership, feature behavior, and activation
are distinct. A provisioned service cannot execute a planned action. CON cannot
turn a fake/test decision into a production allow path.

## Principal models

### Human

- task.claim: exact active same-project `submitter` ProjectRoleGrant;
- review.claim and review.decision: exact active same-project `reviewer`
  ProjectRoleGrant plus no-self-review and lifecycle guards;
- contribution self/award self: exact actor-self relationship;
- administrative policy, binding, project reads, and operations: one exact
  eligible AdminRoleGrant selected by the action evaluator.

The shipping path consumes exact `submitter` and `reviewer` grants. There is no
combined grant and no unrelated project/admin grant substitutes. WS-CON adds no
adjudication grant or action and has no adjudication readiness dependency; any
separate global project-role catalogue state remains AUTH-owned and outside
this transaction.

FinalAcceptance creation has no ActionId. It is an internal REV-owned
consequence of an already-authorized `review.decision` with `accept`; CON only
validates and consumes the locked fact when creating `accepted_submission`.

### Fixed service

The only service admission path is:

```text
verified service token
-> active ActorIdentityLink
-> active service ActorProfile
-> immutable closed ServiceIdentity
-> exact static service-action matrix membership
-> AUTH-09E typed service AuthorizationContext
-> CON-composed canonical ResourceContext
-> decision
```

There is no database service grant or action-assignment row. AUTH locks the
profile/link and validates unchanged ServiceIdentity, static membership, and
active action. Human grants cannot satisfy service actions and services cannot
use human grant candidates. Missing provisioned rows deny the request and block
release readiness, but do not fail application startup or provisioning.

## Prepared mutation protocol

For `T` actions AUTH resolves a server-owned preliminary target, locks human
actor/link/grant or fixed-service actor/link authority first, and returns one
opaque non-serializable handle. The handle is bound to request, session, actor,
action, target, and authority snapshot. CON then locks product rows in the
canonical order, recomposes final typed facts, and AUTH evaluates once. AUTH
stages decision evidence and never commits; the route/executor/callback boundary
commits explicitly. Missing, reused, cross-session, cross-action, target-
drifted, or authority-drifted handles deny with zero product mutation.

`Q` reads use request-scoped require plus canonical CON loaders, pre-filtered
pagination, and concealment. No authorization result or grant cache survives a
request.

## Proposed core action mappings

These 22 feature-surface mappings preserve existing stable PermissionIds except
for the two explicitly proposed service-only PermissionIds. They are a product
proposal, not registered runtime. Policy ActionIds use the canonical
`contribution.policy.*` namespace while retaining stable
`compensation.policy.manage` PermissionId compatibility.

| Proposed AUTH custodian | ActionId | PermissionId | Principal / target | Revalidation | Feature owner |
|---|---|---|---|---:|---|
| `AUTH_CON_OUTBOX` | `outbox.dispatch` | proposed `outbox.dispatch` | fixed outbox dispatcher / claimed event | T | shared outbox 02B |
| `AUTH_CON_BINDING` | `compensation.adapter_binding.read` | `compensation.adapter_binding.manage` | Finance / ProjectCompensationAdapterBinding | Q | CON-04A |
| `AUTH_CON_BINDING` | `compensation.adapter_binding.create` | `compensation.adapter_binding.manage` | Finance / project binding collection | T | CON-04A |
| `AUTH_CON_BINDING` | `compensation.adapter_binding.suspend` | `compensation.adapter_binding.manage` | Finance / active binding | T | CON-04A |
| `AUTH_CON_BINDING` | `compensation.adapter_binding.resume` | `compensation.adapter_binding.manage` | Finance / suspended binding | T | CON-04A |
| `AUTH_CON_OPERATIONS` | `compensation.adapter_binding.retire` | `compensation.adapter_binding.manage` | Finance / dependency-free binding | T | CON-10B |
| `AUTH_CON_POLICY` | `contribution.policy.read` | `compensation.policy.manage` | Finance / ContributionPolicyVersion | Q | CON-04B |
| `AUTH_CON_POLICY` | `contribution.policy.create_draft` | `compensation.policy.manage` | Finance / project policy collection | T | CON-04B |
| `AUTH_CON_POLICY` | `contribution.policy.update_draft` | `compensation.policy.manage` | Finance / draft version | T | CON-04B |
| `AUTH_CON_POLICY` | `contribution.policy.publish` | `compensation.policy.manage` | Finance / complete draft version | T | CON-04B |
| `AUTH_CON_POLICY` | `contribution.policy.retire` | `compensation.policy.manage` | Finance / published version | T | CON-04B |
| `AUTH_CON_CALLBACK` | `compensation.fulfillment.report` | proposed `compensation.fulfillment.report` | exact bound service / award and binding | T | CON-08B |
| `AUTH_CON_CONTRIBUTION_READS` | `contribution.read_self` | `contribution.read_self` | contributor / own record | Q | CON-10A |
| `AUTH_CON_CONTRIBUTION_READS` | `contribution.read_project` | `contribution.read_project` | exact eligible AdminRole / project collection | Q | CON-10A |
| `AUTH_CON_AWARD_READS` | `compensation.award.read_self` | `contribution.read_self` | beneficiary / own award | Q | CON-10A |
| `AUTH_CON_AWARD_READS` | `compensation.award.read_project` | `compensation.award.read` | D11 role set / project award collection | Q | CON-10A |
| `AUTH_CON_OPERATIONS` | `compensation.delivery.reconcile` | `compensation.delivery.reconcile` | D11 role set / delivery request | T | CON-10B |
| `AUTH_CON_OPERATIONS` | `compensation.status.read` | `operations.status.read` | Operator / bounded status | Q | CON-10B |
| `AUTH_CON_OPERATIONS` | `compensation.reconcile.run` | `operations.reconcile.run` | reason-bound Operator / durable request | T | CON-10B |
| `AUTH_CON_OPERATIONS` | `contribution.projection.rebuild` | `operations.projection.rebuild` | reason-bound Operator / durable request | T | CON-10B |
| `AUTH_CON_OPERATIONS` | `audit.read` | `audit.read` | D11 role set / bounded WS-CON audit | Q | CON-10B |
| `AUTH_CON_OPERATIONS` | `audit.export` | `audit.export` | D11 role set / bounded export | T | CON-10B |

The proposed AUTH custodian names are exact candidates for AUTH-owned chunk
contracts. AUTH may adjust chunk grouping before registration, but every action
must have exactly one AUTH ActionOwner and unchanged PermissionId mapping.

## Core resource guards

- Policy publish locks one active ContributionPolicy selector, draft version,
  both exact ContributionRules, award definitions, and referenced active same-
  project/instrument bindings. Published content is immutable.
- Binding create validates canonical service actor, approved adapter capability,
  project/instrument, and non-secret route identity. Suspend blocks new freezes
  and deliveries but preserves valid callbacks for already-issued awards.
- Binding retire denies any active policy reference, unfinished frozen
  assignment/lease, or unfulfilled award. After retirement only exact replay of
  a previously accepted receipt may be acknowledged.
- Contribution self/project and award self/project reads use canonical record
  ownership, pre-filtered project scope, stable pagination, and concealment.
  They expose no provider reference, secret, balance, or ledger data.
- Callback requires exact actor/link/ServiceIdentity/static row, binding route,
  award, project, instrument, and receipt-state match. Rate limits bind actor
  plus binding, not shared IP alone.
- Reconciliation/rebuild create bounded durable requests and never repair
  immutable contribution, award, or receipt truth.

## Service execution gaps that must be closed

The 22 mappings above cover human/public queries, management requests, the
callback, and generic outbox dispatch. They do not authorize protected feature
handler execution. `workstream.outbox.dispatcher` with `outbox.dispatch` can
only claim, invoke, and finalize events; it cannot transitively receive every
handler's mutation/provider authority.

Before CON-02B/08A/10C protected execution, AUTH and the human must approve
exact ServiceIdentity/ActionId/static-row contracts. CON-08B independently
requires the authenticated callback identity/action/static-row contract:

| Boundary | Discovery candidate identity | Discovery candidate action | Required result |
|---|---|---|---|
| outbox mechanics | `workstream.outbox.dispatcher` | `outbox.dispatch` | exact closed identity and singleton static row |
| outbound fulfillment delivery | `workstream.compensation.delivery` | `compensation.delivery.execute` | independent feature authority; never inherited from dispatcher |
| async compensation reconciliation | `workstream.compensation.reconciler` | `compensation.reconcile.execute` | exact bounded execution action or approved dual-principal evaluator |
| async contribution projection rebuild | `workstream.contribution.projection_rebuilder` | `contribution.projection.rebuild.execute` | exact bounded execution action or approved dual-principal evaluator |
| fulfillment callback | `workstream.compensation.fulfillment_reporter` | `compensation.fulfillment.report` | one approved fixed identity/static row or an explicitly specified closed set |

Candidate strings are not approved identifiers. If AUTH reuses an existing
request ActionId for fixed-service execution, it must specify a closed dual-
principal evaluator and prove human/service isolation. CON must not infer that
design. Each new identity requires closed enum/static-matrix changes, controlled
ActorProfile/ActorIdentityLink provisioning, service_identity constraint
migration custody, AUTH-09E admission, exact cross-service negative tests, and
activation only after hidden behavior merges.

## Upstream review and task actions

`task.claim` is an upstream AUTH action mapped to existing `task.claim`; it
requires the exact submitter grant and task guards before CON-05A participates.
`review.claim` and `review.decision` are current planned actions; CON-06/07
provide hidden participants, REV supplies canonical composition, and AUTH
activates only after the complete behavior merges.

AUTH must reconcile all 19 current review actions as one complete activation-
custody transfer under `WS-XINT-001/AUTH_REV_HANDOFF.md`. WS-CON declares only
its two dependencies and must not remove or retain individual REV ActionOwner
members locally. The four proposed additive review actions remain absent until
their own registration contract.

Likewise, the complete 25-action ART transfer belongs to
`WS-XINT-001/AUTH_ART_HANDOFF.md`. WS-CON has no core ART dependency and does not
repeat an eleven-action subset.

## Optional evidence action

If optional contribution-evidence projection is separately approved, one
additional action may be proposed:

```text
artifact.contribution_evidence.binding.create
  -> existing artifact.binding.create
  -> existing workstream.artifact.binding ServiceIdentity
```

AUTH would extend that identity's static row by exactly this action only after a
reviewed ART capability contract exists. This optional action is outside the 22
core proposal and outside release readiness. It cannot be used to authorize
core ContributionRecord creation or reads.

## D11 AdminRole decisions

Before CON-10A/10B registration, the human must choose exact candidates for:

- Project Manager inclusion in project award detail;
- reason-bound Operator delivery recovery in addition to Finance Authority;
- audit read/export role sets.

Any difference from merged AUTH definitions is implemented by AUTH through an
action-owned closed role intersection before grant query. Mixed eligible and
excluded grants select only the eligible grant. CON receives matched decision
evidence and contains no role branch.

## Activation and release proof

AUTH proof must cover planned denial, exactly one custodian per action,
PermissionId parity, evaluator/context completeness, exact human grants,
ServiceIdentity/static-matrix membership, AUTH-09E admission, cross-service
denial, same-token revocation, prepared-handle misuse, transaction-time
revalidation, and decision-evidence failure. Feature proof covers canonical
facts, lifecycle guards, commit/rollback, and no AUTH persistence import.

Startup may fail on closed code/catalogue/static-matrix/evaluator/active-
behavior drift. Runtime and release readiness deny on missing provisioned
service rows. Administrative provisioning remains available.

This handoff changes no AUTH runtime and starts no AUTH or CON chunk.
