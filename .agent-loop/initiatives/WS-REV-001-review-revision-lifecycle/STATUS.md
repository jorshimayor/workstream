# Status: WS-REV-001 Review And Revision Lifecycle

## Current status

Trusted main is `f18b620932bb257dc1dc355bc0504271813dc6b1`, merge of REV
parent chunk 02 through PR #147. Parent 02 is a merged non-executable split
record. `WS-REV-001-02A-PREP` is the active planning/specification-only refresh.
No backend runtime, migration, model, repository, service, route, or persistence
test is authorized in this chunk.

The user previously started 02A preparation, then accepted AUTH's runtime block
and explicitly authorized continued planning/read-only work. After this refresh,
02A requires a renewed explicit start because its exact runtime dependencies are
not merged.

## Trusted dependency truth

- Single Alembic head: `0025_artifact_store_v2`.
- Both retired task-subsystem contributor-identity fields remain on trusted main.
- AUTH catalogue: 74 PermissionIds, 65 ActionIds, 12 active, 53 planned.
- All 24 REV lifecycle action dependencies remain unavailable.
- AUTH-09D-A/`0026` exists only in an unmerged worktree. The human-approved
  contributor clean cut has no trusted-main chunk ID/PR/SHA/migration.
- ART v2 LocalStorage merged through PR #141 at `a10d901`, but ART has no
  scheduled review packet-read, review-evidence candidate/finalize, or
  server-derived Submission artifact-digest owner chunk.
- CON-01 merged its specification. CON runtime chunks 02A onward remain
  proposed on trusted main. Unmerged CON outbox work also claims `0026`; it is
  not consumable and must rebase/renumber after the winning migration merges.
- Sibling AUTH/ART/CON status files contain stale post-merge wording. REV records
  actual merge facts but does not edit owner initiative memory.

## Plan-refresh results

- 02A now owns only activation sequence, Project-first publication/screening,
  immutable Task guide triplet, and unchanged superseded-candidate denial.
- Proposed 02A2 owns prepared-authorized, `If-Match` protected superseded-guide
  reactivation after AUTH-PREP and AUTH-12. This preserves backward rebase
  without broadening the legacy public route.
- Existing oversized parent contracts are non-executable split records. Only
  the children in `CHUNK_MAP.md` may later receive implementation contracts.
- Chunk 08 is pure contract/validation only. Chunk 10 remains the first canonical
  Review/FinalAcceptance/CON transaction.
- Revision uses immutable task-owned `RevisionObligation` with exactly one
  `human_review` or `checker_run` origin. Checker-caused `needs_revision` remains
  a supported path and never fabricates Review/finding/reviewer contribution.
- Limit/deadline exhaustion cannot be repaired around; only exact D6 close may
  terminate that frozen obligation.
- Persisted release phase denies command execution. It does not unregister
  routers, change AUTH action availability/static membership, or replace
  scheduler operations.

## Canonical lifecycle

- Every valid reviewer decision appends immutable Review history; findings and
  later resolutions are also immutable.
- Every decision creates reviewer `completed_review` through CON.
- Accept alone creates immutable FinalAcceptance, accepts Task/completes exact
  assignment, and creates submitter `accepted_submission` from that fact.
- Needs revision creates no FinalAcceptance/submitter contribution and atomically
  creates a human-rooted revision obligation/preparation.
- Reject blocks the exact reviewed Submission assignment and rejects Task; it
  creates no FinalAcceptance/submitter contribution.
- Checker needs revision atomically creates a checker-rooted obligation/
  preparation and no Review/CON record.
- Adjudication and reputation mutation remain deferred and unimplemented.

## Human-owned gates

- A real merged AUTH contributor/canonical-human foundation with exact ID,
  PR/SHA, migration, constraints, and tests before 02A.
- Separate 02A start after this refresh merges.
- Exact positive `review_preference_window_seconds` and
  `review_lease_duration_seconds` before 02B. Neither derives from `sla_hours`.
- Every later external owner dependency and child start as listed in the map.

## Stop condition

Publish only `WS-REV-001-02A-PREP`, let automated memory name 02A with an
explicit-start gate, and stop. Do not implement 02A, 02A2, or 02B from this PR.
