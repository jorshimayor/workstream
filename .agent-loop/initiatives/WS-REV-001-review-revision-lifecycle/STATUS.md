# Status: WS-REV-001 Review And Revision Lifecycle

## Current status

`WS-REV-001-PLAN` merged through PR #128 at trusted main
`0302bcf854a565d429e232ad6b076a1931ea74e4`. The user explicitly started
`WS-REV-001-01`, which is active on `codex/ws-rev-001-01` from that exact base.
No runtime review or revision behavior is active in this chunk.

Chunk 01 adopts `docs/spec_review_lifecycle.md` as the active normative
contract, preserves the supplied WS-REV and WS-IMP archival Markdown/PDF bytes,
reconciles active documentation, and adds a fail-closed stale review-contract
gate. It changes no backend, migration, AUTH, ART, or CON runtime code.

## Dependency state

- AUTH-08 remains the historical 74-PermissionId, 57-ActionId snapshot: 9
  active and 48 planned. Current trusted main after AUTH-09A has 74
  PermissionIds and 65 ActionIds: 9 active and 56 planned.
- All 24 REV lifecycle action dependencies remain unavailable: planned
  `submission.create`, 19 planned review actions, and four approved but
  unregistered REV additions. The separately proposed ART evidence-binding
  service action is not included in those 24.
- AUTH owns registration, service identity admission, evaluator integration,
  activation, and prepared-mutation authority. REV publishes immutable feature
  manifests and hidden behavior evidence; it does not activate actions.
- ART-02A2 remains preparation-only. Review consumes only later approved ART v2
  typed packet-read and evidence candidate/finalize ports. It never consumes
  ART scratch, v1 store, provider, or repository APIs.
- CON must provide frozen contribution policy persistence and the ordered
  two-operation flush-only participant before a canonical Review can commit.
  Every valid Review creates reviewer contribution; only an accept-created
  FinalAcceptance creates submitter contribution.
- AUTH-owned contributor-field foundations, ART submission commitment and
  packet-read contracts, CON persistence/participant contracts, and the
  remaining per-chunk gates stay external prerequisites exactly as listed in
  `CHUNK_MAP.md`.

## Canonical lifecycle boundary

- Every valid reviewer decision appends an immutable Review. Submitted findings
  and later finding resolutions are also immutable history.
- `accept` additionally creates one internal immutable FinalAcceptance. The
  submitter `accepted_submission` contribution consumes that fact rather than
  inferring acceptance from `Review.decision`.
- `needs_revision` prepares a controlled next-attempt context. An exact match
  with the currently active Project Guide identity and activation sequence keeps
  context; any different internally consistent active pair rebases forward or
  backward; missing or inconsistent active context blocks preparation.
- The reviewer always uses the Project Guide context stamped on the exact leased
  Submission and never performs a separate review-guide rebase.
- `reject` blocks the submitter assignment and sets the Task to `rejected`.
  Approved administrative revision-obligation closure uses `cancelled` with a
  bounded reason.
- Adjudication remains disabled and unimplemented in v0.1. Reputation mutation
  is deferred to its owning future initiative. Interfaces retain typed lineage
  so either can be added later without changing the immutable Review contract.

## Chunk 01 evidence state

Candidate `9b2fc11c12e8c0cb19914c9772f95ba4e9814688` passed the final L1
plan review, deterministic evidence gate, and all nine required exact-SHA
internal reviewer tracks with no blocking findings. The evidence record and PR
trust bundle are under `reviews/WS-REV-001-01-*`.

Chunk 01 is internally reviewed and ready for PR publication. External CI,
CodeRabbit, and human review remain required. This status does not activate a
review action or endpoint and does not authorize merge.

## Stop condition

After Chunk 01 is reviewed, merged with explicit human approval, and automated
merge memory records it, stop. Do not start `WS-REV-001-02` without a separate
explicit user instruction.
