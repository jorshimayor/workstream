# Status: WS-REV-001 Review And Revision Lifecycle

## Current status

`WS-REV-001-PLAN` merged through PR #128 at trusted main
`0302bcf854a565d429e232ad6b076a1931ea74e4`. The user explicitly started
`WS-REV-001-01`, which is active on `codex/ws-rev-001-01` from that exact base.
No runtime review or revision behavior is active in this chunk.

While Chunk 01 was under review, CON planning PR #142 merged to main at
`a947b8693a97bdb94c9dc63202a51e197834d613`. The branch pulled that merge and
reconciled its shared active documents. PR #142 changes planning/contracts only;
no CON runtime behavior became active.

AUTH-09B PR #143 then merged to main at
`053242b90d927ace3fab92eeca72da27a61cecec`. The branch pulled it cleanly;
only the shared agent-gate test file overlapped. AUTH-09B activates controlled
`actor.service.provision`, not service admission or any REV action.

Chunk 01 adopts `docs/spec_review_lifecycle.md` as the active normative
contract, preserves the supplied WS-REV and WS-IMP archival Markdown/PDF bytes,
reconciles active documentation, and adds a fail-closed stale review-contract
gate. It changes no backend, migration, AUTH, ART, or CON runtime code.

## Dependency state

- AUTH-08 remains the historical 74-PermissionId, 57-ActionId snapshot: 9
  active and 48 planned. Current trusted main after AUTH-09B has 74
  PermissionIds and 65 ActionIds: 10 active and 55 planned.
- All 24 REV lifecycle action dependencies remain unavailable: planned
  `submission.create`, 19 planned review actions, and four approved but
  unregistered REV additions. The separately proposed ART evidence-binding
  service action is not included in those 24.
- AUTH owns registration, service identity admission, evaluator integration,
  activation, and prepared-mutation authority. REV publishes immutable feature
  manifests and hidden behavior evidence; it does not activate actions.
- Merged AUTH-09B supplies controlled provisioning only for identities already
  in AUTH's closed registry. None of REV's six identities exists yet; their
  exact extensions, provisioning, AUTH-09E admission, and feature activation
  remain downstream gates.
- ART-02A2 remains preparation-only. Review consumes only later approved ART v2
  typed packet-read and evidence candidate/finalize ports. It never consumes
  ART scratch, v1 store, provider, or repository APIs.
- CON must provide frozen contribution policy persistence and the ordered
  two-operation flush-only participant before a canonical Review can commit.
  Every valid Review creates reviewer contribution; only an accept-created
  FinalAcceptance creates submitter contribution.
- Merged CON PLAN3 now publishes that exact two-operation boundary and the
  shared release order. Its implementation chunks remain proposed/inactive and
  still gate REV runtime composition.
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

Candidate `6da45b2765de68dc5a0628024bdfeacb98d1ea85` passed all nine required
tracks against trusted current main
`053242b90d927ace3fab92eeca72da27a61cecec`: senior engineering, QA/test,
security/auth, product/ops, architecture, docs, reuse/dedup, test delta, and CI
integrity. All 80 current-main agent tests and seven REV additions are retained;
87 agent-gate tests and the deterministic contract gates pass.

Chunk 01 is published as PR #145. Its initial Agent Gates run found a
successor-heading/merge-intent title mismatch; the exact metadata repair is
under internal review and awaits replacement CI after the reviewed repair is
pushed. CodeRabbit was rate-limited and produced no findings. This chunk
activates no review action or endpoint and does not authorize merge.

## Stop condition

After Chunk 01 is reviewed, merged with explicit human approval, and automated
merge memory records it, stop. Do not start `WS-REV-001-02` without a separate
explicit user instruction.
