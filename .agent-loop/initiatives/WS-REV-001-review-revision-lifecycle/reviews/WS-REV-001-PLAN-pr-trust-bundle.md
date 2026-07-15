# PR Trust Bundle: WS-REV-001-PLAN

## Chunk

`WS-REV-001-PLAN` - Review And Revision Lifecycle Planning

## Goal

Reconcile the revised review/revision specification with trusted `main` and
publish an executable, dependency-aware implementation plan without changing
runtime behavior.

## Human-Approved Intent

On 2026-07-15 the human approved D6 limit/deadline behavior, reviewer-current
work precedence, coherent joint lifecycle activation, the proposed chunk
sequence, and publication of this planning chunk. The approval does not start
`WS-REV-001-01`; that remains a separate post-merge decision.

## What Changed

- Reconciled merged AUTH-07B actor, minimal-kernel, contributor, permission, and
  action contracts plus the prospective AUTH-owned 57-to-61 action-parity gate
  after unmerged AUTH-08.
- Added hard AUTH-owned repair gates for generic dependency auto-commit,
  decision-evidence SQL error mapping, and canonical verification timestamps.
- Reconciled ART and CON ownership boundaries without importing sibling runtime
  code or treating uncommitted sibling work as merged contracts.
- Added a generation-aware joint lifecycle release-control chunk, phase graph,
  command matrix, typed drain observations, callback/dispatch fencing, and
  remote provider-I/O handoff requirements.
- Updated the conformance matrix and affected chunk contracts so implementation
  can proceed as separately approved, reviewable units.

## Why It Changed

Trusted `main` now contains AUTH-07B and the shared ADR-0014 adapter foundation.
The plan needed exact canonical identities, action accounting, integration
ownership, and an operable joint activation/shutdown contract before runtime
work could safely begin.

## Design Chosen

The plan retains one task-bound Project Guide context, ART-mediated immutable
submission evidence, AUTH-owned authorization/action catalogues, CON-owned
contribution effects, and PostgreSQL-canonical joint lifecycle control. Remote
provider calls occur outside database transactions and lifecycle locks, with
durable fenced finalization.

## Alternatives Rejected

- A separate reviewer guide or reviewer-side guide rebase.
- Synthetic human `reject` decisions at revision limits or deadlines.
- Review-owned contribution, artifact, authorization, or shared-outbox logic.
- Runtime plugin discovery, service locators, or a second adapter factory path.
- Partial public activation before coherent REV/CON fencing and live proof.

## Scope Control

Only the initiative planning tree, its single existing merge intent, and the
exact canonical WS-REV reference filename/checksum repair are in scope. No
backend, active product documentation, dependency, migration, or runtime
behavior changes are included.

## Product Behavior

None changes in this chunk. It defines future contracts for `accept`,
`needs_revision`, and `reject`, guide rebase, evidence disclosure, reviewer
leases, contribution effects, shutdown, recovery, and activation.

## Acceptance Criteria Proof

The source manifest records Markdown/PDF provenance; discovery maps current
subsystem boundaries; decisions and risks separate approved behavior from hard
dependency gates; the conformance matrix covers specification sections
25.1-25.9; every proposed chunk has bounded scope and verification; and the
single merge intent names `WS-REV-001-01` with explicit-start required.

## Tests/Checks Run

```text
git diff --check
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_loop_memory_state.py
python3 scripts/check_internal_review_evidence.py
python3 scripts/test_agent_gates.py
```

The AUTH/REV accounting check proves 74 PermissionIds and 50 registered
ActionIds split into 2 active actor-self actions and 48 planned actions. All 20
existing revised-spec actions are present but planned, four additive actions are
absent and gated, and all 24 WS-REV dependencies are inactive.

AUTH-08 remains unmerged. Its amended contract projects 57 actions with 9 active
and 48 planned; the four later REV additions require exact 57-to-61 parity and
produce 9 active and 52 planned while all 24 REV dependencies remain inactive
until their owning chunks.

## Test Delta

No product tests change because this is a planning-only chunk. Repository policy
and evidence-gate tests are rerun against the publication commits.

## CI Integrity

No workflows, package scripts, test thresholds, skips, coverage settings, or
merge controls change.

## Reviewer Results

Senior engineering, QA/test, security/auth, product/ops, architecture, docs, and
reuse/dedup all passed after valid findings were repaired. The detailed evidence
and reviewer run IDs are recorded in the internal-review evidence and review log.

## External Review

The earlier PR revision passed Backend, Agent Gates, and CodeRabbit. The
AUTH-07B/ART dependency refresh requires new checks and human review before the
PR is updated or merged.

## Remaining Risks

AUTH, ART, CON, shared-outbox, digest/context, compensation, drain-observation,
and dispatch/callback contracts remain hard merged-SHA gates at their owning
chunks. Joint lifecycle activation remains Operator-controlled and cannot occur
until recovery, operations, and live-drill proof are complete.

AUTH must also repair generic dependency auto-commit, authorization-evidence
SQL error mapping, and canonical verification timestamps before any REV runtime
consumer is activated.

## Follow-Up Work

After this PR merges, a human may separately activate `WS-REV-001-01`. Each
successor chunk requires its own contract, dependency refresh, implementation,
evidence, reviewer fanout, and merge approval.

## Human Review Focus

Review D6 behavior, Project Guide authority/rebase, reviewer-current precedence,
AUTH action parity, ART/CON ownership boundaries, joint lifecycle fencing, and
the fact that no runtime chunk is activated by this PR.

## Human Merge Ownership

Only the human may approve and merge this PR. The agent stops after publication
and does not start the successor automatically.
