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
| `WS-AUTH-001-03` | Legacy Actor Classification Preflight | L1 | Merged through PR #109 as `f06532e` |
| `WS-AUTH-001-04` | Request, Error, And API Control Foundation | L1 | Split before implementation into 04A and 04B |
| `WS-AUTH-001-04A` | Request And Error Context | L1 | Merged through PR #111 as `90c9a28` |
| `WS-AUTH-001-04B` | PostgreSQL Rate Controls | L1 | Merged through PR #113 as `05a63c8` |
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
-> WS-AUTH-001-04A
-> WS-AUTH-001-04B
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
- Parent chunk 04 was split before implementation. Chunk 04A establishes
  request/correlation and additive error compatibility; chunk 04B later owns
  durable PostgreSQL rate controls and its migration.
- Chunk 05 evolves the shared audit path and idempotency before mutations.
- Chunk 06 establishes canonical actor resolution while preserving only the
  enumerated non-authoritative legacy workflow-eligibility consumers required
  for intermediate-release operability.
- Chunk 07 provides the single authorization engine before grant APIs.
- Chunks 08-10 establish local grant truth before product cutover.
- Chunks 11-15 migrate bounded complete product/system surfaces.
- Artifact upload, read, retention, release/delete, replication, integrity, and
  reconciliation remain mechanically owned by the artifact subsystem but must
  receive centralized AUTH decisions. Chunk 07 owns the permission-registry
  boundary, chunk 09 owns artifact service principals, the applicable 11-15
  resource cutovers attach enforcement, and chunk 16 proves no bypass remains.
- Chunk 16 proves the complete initiative; it does not backfill missing audit
  or idempotency evidence.
- `WS-POL-002-03` merged separately through PR #90 as `a7aa474`. This initiative
  does not own it; post-merge memory completed through PR #94. `WS-POL-002-04`
  remains inactive until the relevant project authorization cutover is complete
  and the user explicitly starts it.

## Stop condition

AUTH-03 post-merge memory merged through PR #110 as `1864867`. The user
explicitly started parent AUTH-04. Required plan review split it before runtime
implementation. AUTH-04A merged through PR #111 as `90c9a28`, and its
post-merge memory merged through PR #112 as `7749f54`. The user explicitly
started AUTH-04B. Its repaired contract passed at `b5dceb1`; bounded
implementation and all required internal review tracks passed, and PR #113
merged as `05a63c8` after Backend, Agent Gates, CodeRabbit, and explicit human
approval passed. AUTH-04B post-merge memory is the current gate. Stop; do not
start AUTH-05 or POL-002-04.
