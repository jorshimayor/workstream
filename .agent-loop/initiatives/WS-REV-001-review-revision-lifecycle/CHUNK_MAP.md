# Chunk Map: WS-REV-001 Review And Revision Lifecycle

## Rule

One chunk maps to one PR. No runtime chunk starts until its AUTH, ART, and CON
gates are satisfied on current trusted `main` and the user gives a separate
explicit start signal.

## Chunks

| Chunk | Title | Risk | Gate | Status |
|---|---|---:|---|---|
| `WS-REV-001-PLAN` | Review And Revision Lifecycle Planning | L0 | None | Human-approved; AUTH-08/ART-02A2 refresh complete; final review/evidence/PR refresh required |
| `WS-REV-001-01` | Canonical Contract Adoption And Dependency Conformance | L1 | Plan approval; current dependency refresh | Proposed |
| `WS-REV-001-02` | Locked Review Policy And Task Lifecycle Alignment | L1 | AUTH DoD on current main; retain merged AUTH-08 transaction/error/timestamp invariants; ART contract stable; D6 behavior approved | Proposed |
| `WS-REV-001-03` | Review Queue And Lease Persistence | L1 | 02 merged; WS-CON-03B compensation-policy persistence merged | Proposed |
| `WS-REV-001-04` | Immutable Review, Findings, And Replay Persistence | L1 | 03 merged; WS-CON-02A shared outbox persistence and 02C lifecycle-audit participant merged | Proposed |
| `WS-REV-001-05` | Checker Admission, Preferred Routing, And Queue Views | L1 | 04; ART submission/checker cutover; AUTH queue reads | Proposed |
| `WS-REV-001-06` | Atomic Claims, Release, Preference, And Timers | L1 | 05; AUTH mutation decisions; WS-CON-06 ReviewLease freeze participant merged; lock order approved | Proposed |
| `WS-REV-001-07` | Artifact-Backed Review Context And Finding Evidence | L1 | 06; ART read/intake/retention/recovery contracts | Proposed |
| `WS-REV-001-08` | Immutable Decision Kernel And Task Effects | L1 | 07; AUTH decision/revocation contract | Proposed |
| `WS-REV-001-09A` | Revision Context Preparation And Resubmission | L1 | 08; ADR 0010 decision adopted; WS-CON-05A/05B legacy PaymentPolicy removal merged | Proposed |
| `WS-REV-001-09B` | Finding Replay, Resolution, And Return Routing | L1 | 09A | Proposed |
| `WS-REV-001-10` | WS-CON Atomic Integration And Hidden API Composition | L1 | 09B; WS-CON-03C exact lineage/digest schema and WS-CON-07 atomic participant merged | Proposed |
| `WS-REV-001-11` | Admin Overrides, Revocation Recovery, And Reconciliation | L1 | 10; AUTH invalidation plus merged revision-obligation-close/repair/legacy-close ActionIds; ART operator recovery port | Proposed |
| `WS-REV-001-12` | Snapshot Projection, Notifications, And Observability | L1 | 11; ART projection; outbox foundation | Proposed |
| `WS-REV-001-12A` | Joint Lifecycle Release-Control Foundation | L1 | 12 review drain-observation port; exact WS-CON-11 hidden-readiness manifest; AUTH exact 61-action parity (9 active, 52 planned) including inactive lifecycle control before this owning chunk; CON dispatch/callback fence hooks plus fulfillment/outbox drain-observation port | Proposed |
| `WS-REV-001-13` | Coherent Public Activation, Live API Drill, And Release Proof | L1 | 12A; AUTH/ART/CON/outbox live readiness | Proposed |

## Dependency order

```text
PLAN -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09A -> 09B -> 10 -> 11 -> 12 -> 12A -> 13
```

External initiative gates are inserted without changing same-initiative
successor order:

```text
AUTH definition of done + merged AUTH-08 transaction/error/timestamp invariants
  + ART stable contracts
  -> WS-REV-001-02

WS-REV-001-02
  -> WS-CON-05A/05B exact attribution consumption and PaymentPolicy removal

WS-REV-001-02 + merged WS-CON-03B compensation-policy persistence
  -> WS-REV-001-03

WS-REV-001-03 + merged WS-CON-02A shared transactional-outbox persistence
  -> WS-REV-001-04

merged WS-CON-02C caller-transaction shared lifecycle-audit participant
  -> WS-REV-001-04

WS-REV-001-04 stable Review/lease/Submission schemas
  + merged ART/CON/REV adoption of one verified Submission packet-digest field,
    representation, derivation, and database binding
  -> WS-CON-03C exact contribution/award lineage persistence

WS-CON-05A/05B
  -> WS-REV-001-09A

WS-REV-001-09B + WS-CON-03C exact lineage/digest schema + WS-CON-07 atomic Review transaction participant
  -> WS-REV-001-10

WS-CON-11 exact hidden-readiness manifest + WS-REV-001-12
  -> WS-REV-001-12A hidden joint release-control foundation
  -> WS-REV-001-13 sole joint activation
```

## Chunk boundaries

- 01 changes contracts and active documentation, not runtime behavior.
- 02-04 land persistence and constraints without public review mutations.
- 05-07 build routing, leases, and evidence consumption behind an unregistered
  production composition boundary.
- 08 builds the full internal decision transaction but exposes no production
  lifecycle route.
- 09A prepares controlled revision context and immutable resubmission input.
- 09B completes finding replay, resolution, and preferred-return semantics.
- 10 proves WS-CON atomicity in hidden composition.
- 11-12 complete operations, recovery, projection, and observability.
- 12A lands hidden persisted release control and mandatory cross-domain fences.
- 13 performs fail-closed preflight, activates the coherent public API set,
  proves the whole lifecycle, and closes generated/user/operator docs.

## Required reviewer tracks

Every chunk: senior engineering, QA/test, security/auth, and product/ops.

Add architecture and reuse/dedup to 01-13. Add docs to PLAN and every chunk that
changes schema, routes, workers, configuration, or active behavior: 01-13. Add
test-delta to every runtime chunk. Add CI integrity whenever a
workflow, script, dependency, or coverage gate changes.

## Stop condition

Planning is approved and merged AUTH-08/ART-02A2 contracts are reconciled.
Publication still requires final exact-snapshot review and evidence binding. Do
not start 01 automatically; its merge-intent gate remains separate.
