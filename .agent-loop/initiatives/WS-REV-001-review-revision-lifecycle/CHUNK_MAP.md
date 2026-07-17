# Chunk Map: WS-REV-001 Review And Revision Lifecycle

## Rule

One chunk maps to one PR. No runtime chunk starts until its AUTH, ART, and CON
gates are satisfied on current trusted `main` and the user gives a separate
explicit start signal.

## Chunks

| Chunk | Title | Risk | Gate | Status |
|---|---|---:|---|---|
| `WS-REV-001-PLAN` | Review And Revision Lifecycle Planning | L0 | None | Active; WS-XINT-001 reconciliation in review |
| `WS-REV-001-01` | Canonical Contract Adoption And Dependency Conformance | L1 | Plan approval; current-main refresh; merged WS-XINT-001 handoffs | Proposed |
| `WS-REV-001-02` | Locked Review Policy And Task Lifecycle Alignment | L1 | AUTH canonical actor foundation; ART submission commitment contract stable; canonical rejected/cancelled lifecycle amendment; D6 behavior approved | Proposed |
| `WS-REV-001-03` | Review Queue And Lease Persistence | L1 | 02 merged; WS-CON ContributionPolicyVersion persistence merged | Proposed |
| `WS-REV-001-04` | Immutable Review, Final Acceptance, Findings, And Replay Persistence | L1 | 03 merged; shared transactional-outbox persistence and caller-transaction lifecycle-audit participant merged at exact refreshed SHAs | Proposed |
| `WS-REV-001-05` | Checker Admission, Preferred Routing, And Queue Views | L1 | 04; ART v2 submission/checker cutover; AUTH-10 reviewer grants and AUTH-11 project visibility; actions registered/planned | Proposed |
| `WS-REV-001-06` | Atomic Claims, Release, Preference, And Timers | L1 | 05; AUTH prepared mutation protocol; AUTH-09E plus exact expiry service rows; WS-CON ReviewLease ContributionPolicyVersion freeze participant; actions registered/planned | Proposed |
| `WS-REV-001-07` | Artifact-Backed Review Context And Finding Evidence | L1 | 06; approved and merged ART-owner amendment for v2 packet-read; separately approved `WS-ART-001-REV-EVIDENCE` candidate/finalize capability; `artifact.review_evidence.binding.create` registered/planned with exact binding service row | Proposed |
| `WS-REV-001-08` | Decision, Final Acceptance, And Task-Effect Contract | L1 | 07; AUTH prepared mutation contract; no canonical Review/FinalAcceptance commit until 10 | Proposed |
| `WS-REV-001-09A` | Revision Context Preparation And Resubmission | L1 | 08; ADR 0010 adopted; retired compensation-context field removal merged; AUTH-14 submission cutover | Proposed |
| `WS-REV-001-09B` | Finding Replay, Resolution, And Return Routing | L1 | 09A | Proposed |
| `WS-REV-001-10` | Final Acceptance, WS-CON Atomic Integration, And Hidden Composition | L1 | 09B; approved and merged ART/task-owner `Submission.artifact_hash` amendment; merged CON FinalAcceptance-sourced lineage schema and flush-only contribution/award participant; no mandatory contribution-evidence projection | Proposed |
| `WS-REV-001-11` | Admin Overrides, Reviewer-Revocation Recovery, And Reconciliation | L1 | 10; AUTH invalidation; four proposed REV actions registered/planned; AUTH-09E plus exact reconciliation service row; ART Operator recovery port | Proposed |
| `WS-REV-001-12` | Snapshot Projection, Notifications, And Observability | L1 | 11; ART projection port; outbox foundation; AUTH-09E plus exact artifact-reference/projection service rows | Proposed |
| `WS-REV-001-12A` | Joint Lifecycle Release-Control Foundation | L1 | 12 review drain-observation port; exact core WS-CON hidden-readiness manifest; `review.lifecycle.activation.manage` registered/planned; CON dispatch/callback fence hooks plus fulfillment/outbox drain-observation port | Proposed |
| `WS-REV-001-13` | Coherent Public Release, Live API Drill, And Release Proof | L1 | 12A; every required REV and ART binding action activated by AUTH after hidden behavior; ART/CON/outbox live readiness | Proposed |

## Dependency order

```text
PLAN -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09A -> 09B -> 10 -> 11 -> 12 -> 12A -> 13
```

External initiative gates are inserted without changing same-initiative
successor order:

```text
AUTH canonical human/grant/prepared-mutation contracts
  + merged AUTH-08 transaction/error/timestamp invariants
  + ART v2 stable contracts
  -> WS-REV-001-02

WS-REV-001-02
  -> WS-CON exact attribution consumption and retired compensation-context field removal

WS-REV-001-02 + merged WS-CON ContributionPolicyVersion persistence
  -> WS-REV-001-03

WS-REV-001-03 + merged CON-owned shared transactional-outbox persistence
  -> WS-REV-001-04

merged CON-owned caller-transaction shared lifecycle-audit participant
  -> WS-REV-001-04

WS-REV-001-04 stable Review/FinalAcceptance/lease/Submission schemas
  + merged ART submission/checker cutover with server-derived stabilized
    Submission.artifact_hash
  -> WS-CON exact FinalAcceptance-sourced contribution/award lineage persistence

WS-CON retired compensation-context field removal
  -> WS-REV-001-09A

WS-REV-001-09B + WS-CON exact lineage schema + flush-only contribution/award participant
  -> WS-REV-001-10

WS-CON exact core hidden-readiness manifest + WS-REV-001-12
  -> WS-REV-001-12A hidden joint release-control foundation
  -> AUTH activates each exact action after its hidden behavior
  -> WS-REV-001-13 sole joint product release
```

The merged ART plan does not yet schedule `WS-ART-001-REV-EVIDENCE`. REV-07 is
therefore explicitly blocked until ART owns, approves, and merges that chunk;
REV planning does not create or start it on ART's behalf.

## Chunk boundaries

- 01 changes contracts and active documentation, not runtime behavior.
- 02-04 land persistence and constraints, including immutable FinalAcceptance,
  without public review mutations.
- 05-07 build routing, leases, and evidence consumption behind an unregistered
  production composition boundary.
- 08 freezes decision inputs, validation, task effects, and the
  FinalAcceptance consequence of `accept`, but cannot commit canonical Review
  or FinalAcceptance without the CON participant.
- 09A prepares controlled revision context and immutable resubmission input.
- 09B completes finding replay, resolution, and preferred-return semantics.
- 10 creates the first canonical Review/FinalAcceptance-committing transaction
  and proves WS-CON atomicity in hidden composition.
- 11-12 complete operations, recovery, projection, and observability.
- 12A lands hidden persisted release control and mandatory cross-domain fences.
- 13 performs fail-closed preflight, exposes the already-AUTH-active coherent
  public API set,
  proves the whole lifecycle, and closes generated/user/operator docs.

## Required reviewer tracks

Every chunk: senior engineering, QA/test, security/auth, and product/ops.

Add architecture and reuse/dedup to 01-13. Add docs to PLAN and every chunk that
changes schema, routes, runtime jobs, configuration, or active behavior: 01-13. Add
test-delta to every runtime chunk. Add CI integrity whenever a
workflow, script, dependency, or coverage gate changes.

## Stop condition

Planning is approved and merged AUTH-08/ART-02A2 contracts are reconciled.
Publication still requires final exact-snapshot review and evidence binding. Do
not start 01 automatically; its merge-intent gate remains separate.
