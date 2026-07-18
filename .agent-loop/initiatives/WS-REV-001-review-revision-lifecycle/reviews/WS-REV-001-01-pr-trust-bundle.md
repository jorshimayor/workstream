# WS-REV-001-01 PR Trust Bundle

## Chunk

`WS-REV-001-01`: Canonical Contract Adoption And Dependency Conformance.

## Goal

Preserve the supplied WS-REV and WS-IMP archival pairs byte-for-byte, adopt one
reconciled active review/revision contract, and align every active contract and
gate before runtime implementation.

## Human-Approved Intent

Every valid reviewer decision, submitted finding, and later resolution is
immutable. Accept additionally creates FinalAcceptance, which alone sources the
submitter contribution. Needs-revision prepares the next attempt against the
current Project Guide when required. Adjudication and reputation mutation are
not v0.1 behavior.

## What Changed

- Added `docs/spec_review_lifecycle.md` as the active normative contract.
- Reconciled architecture, ADRs, operations, templates, roadmaps, and diagrams.
- Added a fail-closed stale review-contract scanner and adversarial gate tests.
- Added registered structural regressions for canonical accept ordering,
  CheckerRun admission, and checker-versus-human revision lineage.
- Preserved and proved all supplied archival inputs.
- Added deterministic pinned rendering for the lifecycle and two changed
  context diagrams.
- Reconciled merged AUTH-09B's controlled provisioning capability and exact
  `65 / 10 active / 55 planned` catalogue without activating any REV identity
  or action.
- Reconciled merged CON-01's active specification and ADR 0016 while retaining
  its no-runtime status and downstream persistence/participant gates.

## Why It Changed

Merged AUTH, ART, CON, and WS-XINT boundaries superseded parts of the archival
specification and older active docs. Runtime work needs one exact contract with
no contradictory status, transaction, identity, storage, or contribution
semantics.

## Design Chosen

REV owns immutable Review and FinalAcceptance facts plus lifecycle
orchestration. AUTH owns prepared authority and activation. ART v2 owns bytes
and typed artifact capabilities. CON joins the REV-owned caller transaction as
an ordered flush-only participant. The route or service command commits once.

## Alternatives Rejected

Editing archival inputs, direct Review-to-submitter contribution, review-time
guide rebasing, raw ArtifactStore access, CON-owned commits, synthetic reject,
mandatory payment, v0.1 adjudication/reputation, and early action activation
were rejected because they violate approved ownership or lifecycle boundaries.

## Scope Control

This is an L1 specification/architecture chunk. It changes no backend,
migration, frontend, AUTH, ART, or CON runtime implementation. All changed paths
are listed by the chunk contract; exactly one merge intent is present.

## Product Behavior

No endpoint or action becomes available. The contract fixes the future behavior
for concealed current-work reads, claims, immutable decisions, accept,
needs-revision, reject, revision preparation, evidence access, contributions,
and payable-only awards.

## Acceptance Criteria Proof

Literal archive hashes and trusted-base diffs pass. Active documents and
roadmaps are scanner-clean. AUTH PREP and lock ordering are exact. Diagrams and
the architecture PDF reproduce byte-for-byte with the pinned renderer. Local
roadmap exports remain absent.

## Tests/Checks Run

`87 agent gate tests passed`; Ruff format/lint, four stale-contract families,
Markdown links, archive checksums/base diffs, PDF attributes, pinned double
render, spreadsheet absence, merge-intent count, and `git diff --check` passed.

## Test Delta

The agent-gate suite gains table-driven prohibited-category coverage,
adversarial lexical decoys, exact archival classification, and fail-closed
discovery coverage. No test or assertion was removed or weakened.

## CI Integrity

No workflow, package script, coverage threshold, or existing gate was weakened.
This chunk adds a mandatory scanner invoked by the existing agent-gate suite.

## Reviewer Results

All nine required tracks passed exact SHA
`b20b766f5aa1f87373ac0f4e575d2e0671ad42a5` against trusted main
`053242b90d927ace3fab92eeca72da27a61cecec`: senior engineering, QA/test,
security/auth, product/ops, architecture, docs, reuse/dedup, test delta, and CI
integrity. No blocking findings remain.

## External Review

PR #145's initial Agent Gates run found a successor-heading/merge-intent title
mismatch. The heading was aligned to the existing reviewed title and the exact
validator and internal loop were rerun. CodeRabbit did not review because its
organization rate limit was reached; it produced no findings. Backend and
replacement PR checks remain external gates. External checks supplement the
completed internal review and do not replace it.

## Remaining Risks

Runtime database, concurrency, rollback, and dependency integration proof is
deferred to its owning implementation chunks. Scanner fixtures may need updates
when future terminology changes.

## Follow-Up Work

`WS-REV-001-02` is the same-initiative successor but requires a separate
explicit human start after this PR merges and automated merge memory records it.

## Human Review Focus

Confirm archival provenance, active-contract precedence, AUTH/ART/CON ownership,
FinalAcceptance lineage, rebase semantics, unavailable v0.1 boundaries, and the
absence of unintended runtime work.

## Human Merge Ownership

Only the human may approve and merge this PR. Internal and external PASS results
do not authorize merge.
