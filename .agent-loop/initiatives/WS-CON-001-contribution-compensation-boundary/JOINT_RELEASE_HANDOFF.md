# Joint REV/CON Release Handoff

## Boundary

REV owns Review decisions, queue/lease/task effects, release-control state, and
the single route commit. CON owns ContributionPolicy, ContributionRecord,
CompensationAward, fulfillment, shared outbox participation, and CON
audit/projections. AUTH owns all authorization and activation.

The canonical cross-boundary source is merged
`WS-XINT-001/REV_CON_HANDOFF.md`. Sibling worktree state is discovery only until
reviewed and merged to trusted `main`.

## Required decision composition

```text
AUTH prepares review.decision with exact reviewer grant
-> REV locks and recomposes canonical facts
-> AUTH evaluates once
-> REV stages Review/lease/queue/task effects
-> CON flush-only participant creates reviewer contribution
-> on accept only, CON creates submitter contribution
-> CON evaluates frozen ContributionRules and creates applicable awards
-> CON stages audit/outbox rows
-> REV route commits once
```

No no-op participant, post-commit repair, ART call, evidence projection, or
provider I/O exists in this transaction. CON copies stabilized artifact-hash
lineage from REV facts.

## Release prerequisites

- ContributionPolicy publish/freeze and adapter-binding behavior are merged.
- TaskAssignment and ReviewLease carry exact frozen policy-version IDs.
- Shared outbox/audit participants and CON-07 are mandatory and merged.
- REV hidden claim/decision composition consumes CON-06/07 and has no fallback.
- AUTH complete REV custody transfer, exact evaluators, reviewer grant path,
  prepared protocol, and activation are merged.
- Every public/service CON action has exact AUTH registration, evaluator,
  principal path, and activation after hidden behavior.
- Protected outbox handlers have their own exact service authority; dispatcher
  authority is not inherited.
- CON-owned fulfillment dispatch/callback fence ports and same-session drain
  observation are injected through composition without REV importing CON/outbox
  repositories.
- Exact migrations, handler registry, task IDs, route inventory, and retained
  tests are bound to merged SHAs.

ART storage and optional contribution-evidence projection are not prerequisites.

## Startup and readiness

Startup fails on closed catalogue/static-matrix/context/evaluator/active-feature
parity drift. Missing provisioned fixed-service ActorProfile/link rows do not
stop startup or administrative provisioning, but runtime calls deny and release
readiness remains false until exact rows exist.

## Joint live proof

The release drill covers accept, needs_revision, reject, explicit unpaid,
money+points, frozen-version changes, repeated/revision Reviews, no-self-review,
grant revocation, atomic rollback, adapter outage/replay, callback-before-ack,
failure then fulfillment, reconciliation, drain fencing, and hidden-to-active
route transition. It asserts zero ART calls in core contribution creation.

## Ownership and stop

CON-11 publishes the hidden dependency manifest but registers no route. The
reviewed REV release chunk consumes that manifest and owns public activation and
the joint live drill. This handoff starts neither chunk automatically.
