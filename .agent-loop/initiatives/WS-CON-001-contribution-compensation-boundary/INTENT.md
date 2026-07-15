# Intent: WS-CON-001 Contribution Record And Compensation Boundary

## Human-level goal

Implement an evidence-backed contribution and compensation boundary that joins
the canonical human Review transaction without taking ownership of
authentication, authorization, provider payment execution, a points ledger, or
reputation scoring.

The supplied revised WS-CON Markdown/PDF pair is an input to reconcile, not an
authority to accept blindly. The active contract must conform to the repository,
the live WS-AUTH action/permission catalogue, the parallel WS-REV plan, and the
accepted artifact-storage and external-adapter decisions.

## Why now

The backend currently stops at `review_pending`. The parallel review initiative
needs real compensation-policy persistence before ReviewLease creation, a
transaction participant that freezes compensation terms, and an atomic
contribution/award participant before it can expose review decisions.

## Success state

- Every valid Review records one immutable reviewer contribution.
- `accept` additionally records one immutable submitter contribution; the other
  canonical decisions do not.
- Contributions and awards use compensation terms frozen before the work.
- Review, task/assignment effects, contributions, awards, audit, and shared
  outbox events commit or roll back together.
- Money and project-points awards remain project-scoped obligations. Provider
  payment attempts, balances, point ledgers, and settlement stay outside
  Workstream.
- Fulfillment delivery, acknowledgement, callback receipts, and rebuildable
  status projections are distinct.
- Contribution evidence is produced after commit through an ART-owned typed
  capability and Workstream `ArtifactBinding`, never through a raw artifact
  provider in contribution code.
- Every public or service operation consumes the merged WS-AUTH
  `AuthorizationService.require(ActionId, typed ResourceContext)` boundary.
- Public APIs use `/api/v1` only.

## Non-goals

- Workstream-owned login, sessions, passwords, or token-role authority.
- AUTH catalogue/kernel/grant/service-actor implementation in this initiative.
- Provider-specific payment SDKs, payment attempts, payout batching, settlement,
  beneficiary onboarding, balances, point ledgers, credits, or blockchain work.
- Reputation scores, aggregates, adjudication, reversals, or contribution
  mutation.
- A second artifact store, direct `ArtifactStore` injection into contribution
  services, Flow Node, R2, semantic-search authority, or public provider refs.
- Frontend work before backend contracts and guards are proven.

## Business/product/engineering context

Workstream must certify useful human work independently from whether an external
provider has paid or credited it. Reviewer work is itself a contribution for
every valid completed review. This creates a durable economic and reputation
input while preserving the separation between human judgment, contribution
recognition, compensation authorization, external fulfillment, and future
reputation policy.

## Human judgment required

1. Approve the recommended active-contract model: preserve both supplied
   reference generations byte-for-byte and create a separately reconciled
   `docs/spec_contribution_compensation.md`, instead of editing archival input.
2. **Approved 2026-07-15:** remove `PaymentPolicy` completely because
   `CompensationPolicyVersion` supersedes it. The removal must migrate every
   project/task/submission/checker/schema/API/doc consumer, preserve no fallback
   alias, and leave CompensationPolicyVersion as the only economic policy.
3. Approve the additive WS-AUTH dependency: granular WS-CON ActionIds map to
   existing broad PermissionIds wherever safe, while the exact bound adapter
   shared outbox dispatch and inbound callbacks require two new service-only
   PermissionIds, `outbox.dispatch` and `compensation.fulfillment.report`,
   owned and implemented by WS-AUTH. The shared-outbox owner activates dispatch;
   CON-08A only consumes the claimed command.
4. Approve the cross-initiative sequence, including REV-13 as the sole joint
   production-route activation/live-drill owner after AUTH, ART, REV, shared
   outbox, and WS-CON participants are mandatory and proven.

## Initial risk class

L0 for architecture direction and contract adoption. Each approved runtime
chunk is L1 because it touches payment, permissions, lifecycle, audit, schema,
and cross-domain transactions.
