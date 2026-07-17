# WS-CON-001-PLAN3 PR Trust Bundle

## Chunk

`WS-CON-001-PLAN3` - AUTH PR 140 Reconciliation.

## Goal

Reconcile the contribution and compensation plan with trusted `main` at merged
AUTH PR #140 (`d541521`) before any CON runtime implementation begins.

## Human-approved intent

- The current compensation-policy model completely supersedes the retired
  policy model; no compatibility path returns.
- The v0.1 accept path is `Review(accept) -> FinalAcceptance ->
  accepted_submission` with no adjudication lifecycle.
- REV owns Review and FinalAcceptance orchestration and the single transaction;
  CON is a mandatory flush-only contribution/award participant.
- AUTH owns identifiers, grants, evaluator integration, ActionOwner custody,
  evidence, and activation. CON must validate upstream planning rather than
  copy speculative identifiers.
- Pull and reconcile merged AUTH work before publishing this plan; do not start
  CON runtime work automatically.

## What changed

- Rebased CON authorization assumptions on AUTH PR #140 while preserving PR
  #139 as the underlying cross-initiative boundary.
- Replaced the older prepared-authorization description with the exact opaque,
  single-use handle binding and authority-first lock protocol.
- Corrected `task.claim`: only its stable PermissionId exists; no task-claim
  ActionId is registered.
- Ordered task work as AUTH-10/PREP and the task seam, then CON-05A hidden
  policy freeze plus task composition, then AUTH-13 enumeration, registration,
  evaluator integration, and activation.
- Preserved planned `review.claim` and `review.decision` actions and their
  dependency on hidden CON participants, REV composition, and later AUTH
  activation.
- Removed speculative `AUTH_CON_*` ActionOwner candidates. The 22 CON surface
  mappings remain unregistered, non-final proposals.
- Added the reviewed PLAN3 contract and one schema-v2 merge intent naming
  `WS-CON-001-01` as the same-initiative successor with an explicit start gate.

## Why

Treating a PermissionId as an existing ActionId would invert the safe rollout:
AUTH could activate task claim before the assignment captured its immutable
contribution-policy version. The corrected order keeps the feature unavailable
until hidden behavior and rollback proof are merged.

## Design and boundaries

AUTH locks current actor/link/exact-grant authority first and prepares one
opaque handle bound to session, ActionId, actor-reference kind/reference,
idempotency key, and canonical request digest. The feature then locks product
rows and recomposes final facts. AUTH consumes the handle, evaluates once, and
stages evidence. Participants flush only and the owning request/command commits
once. A failed substitution attempt does not consume an otherwise valid handle.

ServiceIdentity, static-matrix membership, and action availability are
code-owned validations, not database lock targets. No AUTH persistence, grant
query, evaluator, identifier registration, or availability writer moves into
CON.

FinalAcceptance remains an internal REV-derived fact with no public API or
separate authorization action. No adjudication policy, state, action, queue,
lease, contribution, or release dependency is added.

## Alternatives rejected

- Activating task claim before CON-05A: rejected because assignment policy
  lineage would not be guaranteed.
- Treating `task.claim` as an existing ActionId: rejected by runtime catalogue
  evidence.
- Retaining `AUTH_CON_*` planning labels: rejected because PR #140 approves no
  such ActionOwner values.
- Giving CON an authorization evaluator or commit: rejected because those
  responsibilities remain AUTH- and request-owned.
- Adding a FinalAcceptance action or adjudication branch: rejected by the
  approved v0.1 lifecycle.

## Scope

PLAN3 itself changes 24 planning/merge-intent files with 412 insertions and 143
deletions. It changes no backend, migration, test, workflow, script, dependency,
runtime catalogue, or active product document. The full planning branch is 65
files with 7,633 insertions and 91 deletions against `origin/main`; most of that
delta is the original reference transcription and durable planning/review
record.

The circuit-breaker passed with a documentation-only size exception: the branch
is one coherent specification initiative, its runtime boundary is empty, and
the earlier planning snapshots retain their own review evidence. The user-owned
deletion of the archival CON PDF is unstaged and excluded.

## Acceptance-criteria proof

- Runtime catalogue verified at 74 PermissionIds and 57 ActionIds: nine active,
  48 planned, no CON-specific ActionId, and no task-claim ActionId.
- Prepared-handle wording matches merged AUTH PR #140.
- The task and review activation sequences explicitly require hidden feature
  behavior before AUTH-only activation.
- Reviewer and submitter contribution lineage remains Review and
  FinalAcceptance respectively, inside the REV-owned transaction.
- The 22 CON mappings are explicitly unregistered/non-final; only the two
  proposed service PermissionIds remain identified as proposals.
- Merge-intent validation passes for successor `WS-CON-001-01`.

## Tests and checks

```text
Markdown link check: PASS (57 changed Markdown files)
Stale Workstream wording: PASS
Stale authorization documentation: PASS
Stale artifact contracts: PASS at foundation phase
Loop-memory state: PASS
Agent gates: PASS (80 tests)
PLAN3 commit diff check: PASS
Working-tree diff check: PASS
PLAN3 backend/.github/scripts delta: none
Merge-intent schema-v2 validation: PASS
Local roadmap workbook: not present, so no sheet-export check applies
```

## Test delta and CI integrity

PLAN3 changes no test or CI file, removes no assertion, skips no test, changes
no threshold, and adds no bypass. Existing agent-gate coverage remains intact.

## Internal reviewer results

The exact reviewed code SHA and complete reviewer table are recorded in
`WS-CON-001-PLAN3-internal-review-evidence.md`. The initial QA/security finding
that `task.claim` was incorrectly described as an existing ActionId was fixed
before the exact-SHA review. A final process-only rebind authorized
parser-complete provenance addenda for the older PLAN/PLAN2 evidence files
validated by the cumulative PR gate. No blocking finding remains.

## External review

Pending PR publication. CodeRabbit, GitHub checks, and human PR review supplement
but do not replace the completed internal review.

## Risks and follow-up

- AUTH-13 must be refreshed to consume the merged CON-05A/task-composition
  manifest before task-claim registration or activation.
- Future CON actions need complete feature manifests and exact AUTH-owned
  registration/activation contracts; the proposed table is not a registry.
- `review.claim` and `review.decision` remain unavailable until their complete
  REV/CON composition and AUTH gates merge.
- CON-01 remains a separate explicit human start after this planning PR.

## Human review focus

Confirm the corrected task-claim ordering, the exact prepared-handle contract,
the removal of speculative ActionOwner labels, and the unchanged
Review/FinalAcceptance/contribution transaction. Also confirm that the 65-file
planning PR is acceptable as one coherent specification record.

## Human merge ownership

This bundle does not authorize publication or merge. The user must explicitly
approve this specific PR for merge. No successor chunk starts automatically.
