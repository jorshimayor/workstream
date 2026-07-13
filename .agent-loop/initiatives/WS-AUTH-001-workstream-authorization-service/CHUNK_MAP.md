# Chunk Map: WS-AUTH-001 - Workstream Authorization Service

## Rule

Only one chunk may be active at a time. Do not start the next chunk until the
current chunk is implemented, verified, internally reviewed, externally
reviewed, merged by explicit human approval, followed by a memory update, and
stopped.

## Chunks

| Chunk | Title | Risk | Status |
|---|---|---:|---|
| `WS-AUTH-001-PLAN` | Authorization Service Planning | L0 | Merged through PR #91 as `ad6d644` |
| `WS-AUTH-001-01` | Adopt Authorization Baseline And Repository Contracts | L1 | Merged through PR #93 as `772af1d` |
| `WS-AUTH-001-02` | Verified Issuer Token And JWKS Boundary | L1 | Merged through PR #107 as `060b780` |
| `WS-AUTH-001-03` | Legacy Actor Classification Preflight | L1 | Active after explicit user start; plan review passed |
| `WS-AUTH-001-04` | Request, Error, And API Control Foundation | L1 | Proposed |
| `WS-AUTH-001-05` | Authority Evidence And Idempotency Foundation | L1 | Proposed |
| `WS-AUTH-001-06` | Canonical Actor Profile And Identity Link | L1 | Proposed |
| `WS-AUTH-001-07` | Authorization Kernel And Permission Registry | L1 | Proposed |
| `WS-AUTH-001-08` | Bootstrap And Administrative Role Grants | L1 | Proposed |
| `WS-AUTH-001-09` | Actor State, Identity Revocation, And Service Actors | L1 | Proposed |
| `WS-AUTH-001-10` | Project Qualification And Contributor Role Grants | L1 | Proposed |
| `WS-AUTH-001-11` | Project Identity, Guide, Source, And Visibility Cutover | L1 | Proposed |
| `WS-AUTH-001-12` | Project Policy And Setup Mutation Cutover | L1 | Proposed |
| `WS-AUTH-001-13` | Task Management And Assignment Cutover | L1 | Proposed |
| `WS-AUTH-001-14` | Submission, Checker, And Audit Visibility Cutover | L1 | Proposed |
| `WS-AUTH-001-15` | Remaining System Worker Cutover And Obsolete Authority Removal | L1 | Proposed |
| `WS-AUTH-001-16` | Conformance, Observability, And Live API Proof | L1 | Proposed |

## Dependency order

```text
WS-AUTH-001-PLAN
-> WS-AUTH-001-01
-> WS-AUTH-001-02
-> WS-AUTH-001-03
-> WS-AUTH-001-04
-> WS-AUTH-001-05
-> WS-AUTH-001-06
-> WS-AUTH-001-07
-> WS-AUTH-001-08
-> WS-AUTH-001-09
-> WS-AUTH-001-10
-> WS-AUTH-001-11
-> WS-AUTH-001-12
-> WS-AUTH-001-13
-> WS-AUTH-001-14
-> WS-AUTH-001-15
-> WS-AUTH-001-16
```

## Boundary notes

- Chunk 02 authenticates tokens but grants no product authority.
- Chunk 03 provides a supported classification gate before schema migration.
- Chunk 04 establishes request/error/rate controls.
- Chunk 05 evolves the shared audit path and idempotency before mutations.
- Chunk 06 establishes canonical actor resolution while preserving only the
  enumerated non-authoritative legacy workflow-eligibility consumers required
  for intermediate-release operability.
- Chunk 07 provides the single authorization engine before grant APIs.
- Chunks 08-10 establish local grant truth before product cutover.
- Chunks 11-15 migrate bounded complete product/system surfaces.
- Chunk 16 proves the complete initiative; it does not backfill missing audit
  or idempotency evidence.
- `WS-POL-002-03` merged separately through PR #90 as `a7aa474`. This initiative
  does not own it; post-merge memory completed through PR #94. `WS-POL-002-04`
  remains inactive until the relevant project authorization cutover is complete
  and the user explicitly starts it.

## Stop condition

`WS-AUTH-001-02` merged through PR #107 as `060b780`. The user explicitly
started `WS-AUTH-001-03` in its separate worktree while coverage work continues
independently. Do not publish until deterministic proof and all required
implementation reviewers pass. Do not start `WS-AUTH-001-04` or
`WS-POL-002-04`; both retain separate explicit start signals and prerequisites.
