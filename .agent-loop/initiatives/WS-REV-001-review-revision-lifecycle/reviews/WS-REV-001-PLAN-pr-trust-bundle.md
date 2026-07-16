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

- Reconciled merged AUTH-08 PR #131 actor, administrative-grant, kernel,
  permission, and 57-action contracts plus the later AUTH-owned 57-to-61
  action-parity gate.
- Verified AUTH-08 resolved generic dependency auto-commit, decision-evidence
  SQL error mapping, and canonical verification-timestamp blockers; retained
  them as REV consumer regression invariants.
- Reconciled ART and CON ownership boundaries without importing sibling runtime
  code or treating uncommitted sibling work as merged contracts.
- Reconciled merged ART-02A2 PR #129 as inactive committed-source/private-scratch
  preparation only, explicitly excluding ART scratch/source implementation from
  REV and retaining later ART product capability gates.
- Added a generation-aware joint lifecycle release-control chunk, phase graph,
  command matrix, typed drain observations, callback/dispatch fencing, and
  remote provider-I/O handoff requirements.
- Updated the conformance matrix and affected chunk contracts so implementation
  can proceed as separately approved, reviewable units.

## Why It Changed

Trusted `main` now contains AUTH-08, the shared ADR-0014 adapter foundation, and
ART-02A2 committed-source/local-preparation foundation.
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

The historical evidence binding is replaced only after the final merged-ART
planning snapshot receives all required internal reviewers. The evidence-only
publication commit then binds that exact reviewed code SHA and must make
`check_internal_review_evidence.py` pass before push.

The AUTH/REV accounting check proves 74 PermissionIds and 57 registered
ActionIds split into 9 active actions and 48 planned actions. All 20 existing
revised-spec actions are present but planned, four additive actions are absent
and gated, and all 24 WS-REV dependencies are inactive. The four later REV
additions require exact 57-to-61 parity and produce 9 active and 52 planned
while all 24 dependencies remain inactive until their owning chunks.

AUTH-08 merged through PR #131 at trusted-main
`aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`, final branch head
`0832358a0262805f553d05b50b0d778e6e6ad995`. Its evidence records 275 focused
behavior tests, 90.17 percent branch-aware focused coverage, 17 isolated
Alembic tests, and green final Backend, Agent Gates, and CodeRabbit checks.

ART-02A2 merged through PR #129 at trusted-main
`9a04434e2f23c5dec8939dadb943bba4d85110c0`, final branch head
`32aab89262a3944f305e9e5dc4c65a2d31e2e144`. Its evidence records 154 focused
tests at 94.40 percent scoped coverage, 38 isolated artifact PostgreSQL tests,
207 isolated AUTH/authentication/Alembic tests, and green final Backend, Agent
Gates, and CodeRabbit checks. Active ArtifactStore v1 remains unchanged.

## Test Delta

No product tests change because this is a planning-only chunk. Repository policy
and evidence-gate tests are rerun against the publication commits.

## CI Integrity

No workflows, package scripts, test thresholds, skips, coverage settings, or
merge controls change.

## Reviewer Results

Historical PLAN and AUTH-08 refresh reviews remain durable evidence. The final
merged-ART planning snapshot receives senior engineering, QA/test,
security/auth, product/ops, architecture, docs, and reuse/dedup review before
its exact code SHA is bound in the internal-review evidence.

Final exact-snapshot results: senior engineering/architecture/reuse passed with
low risks; QA/test and product/ops passed; security/auth, docs, and CI integrity
passed after the provider-state wording repair. Reviewed code SHA is
`f729438e063da65add1c5b712f27ffe628ef189f`; detailed results and reviewer IDs
are recorded in `WS-REV-001-PLAN-internal-review-evidence.md`.

## External Review

The earlier PR revision passed Backend, Agent Gates, and CodeRabbit. The final
AUTH-08/ART-02A2 dependency refresh requires fresh PR checks and human review
after the reviewed branch is published.

## Remaining Risks

AUTH, ART, CON, shared-outbox, digest/context, compensation, drain-observation,
and dispatch/callback contracts remain hard merged-SHA gates at their owning
chunks. Joint lifecycle activation remains Operator-controlled and cannot occur
until recovery, operations, and live-drill proof are complete.

REV runtime consumers must preserve AUTH-08's rollback-only dependency teardown,
typed authorization-evidence `503` mapping, and route-owned canonical
verification-timestamp behavior. Missing or regressed proof blocks activation.

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
