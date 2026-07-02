# Loop State

## Current State

- Active initiative: `WS-POL-001` - Submission Artifact Policy Foundation
- Active planning chunk: none
- Active implementation chunk: `WS-POL-001-03`
- Branch: `codex/ws-pol-001-03-task-locked-context`
- Status: `WS-POL-001-01` and `WS-POL-001-02` merged; `WS-POL-001-03` implementation and internal review evidence prepared
- Reviewed code SHA: `df468066cc3c6180c12735daf5e4dd8de654bef7`
- Current gate: final evidence gate, PR creation, external review, and human PR review checkpoint
- Next chunk: inactive until `WS-POL-001-03` is reviewed and merged by the user

## Operating Rule

Workstream engineering chunks move through:

```text
Intent -> Discovery -> Plan -> Chunk Map -> Chunk Contract -> Implementation -> Evidence -> Internal Review -> PR -> Human Checkpoint -> Memory Update -> Stop
```

This branch implements the third backend foundation chunk for submission intake
policy. It moves task readiness and submission creation onto the locked project
guide-source snapshot, effective project submission artifact policy, and
compiled project `PreSubmitCheckerPolicy` bundle. It does not implement
frontend behavior, payment, reputation, settlement, blockchain integrations,
post-submit policy splitting, or revision resubmission drill behavior.

## Last Review State

- Last completed initiative: `WS-ENG-001` Codex zero-trust engineering loop bootstrap.
- PR #23 merged into `main` on 2026-06-20.
- PR #24 updated post-merge loop memory on `main`.
- PR #25 added Terminal Benchmark example material under `examples/`.
- PR #26 approved and merged WS-POL-001 planning into `main` on 2026-06-27.
- PR #27 updated WS-POL post-merge memory on `main`.
- PR #28 implemented `WS-POL-001-01` and was merged into `main`.
- PR #61 implemented `WS-POL-001-02` and was merged into `main`.
- Current implementation branch: `codex/ws-pol-001-03-task-locked-context`.
- Internal review evidence for the active chunk is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-internal-review-evidence.md`.
- PR trust bundle for the active chunk is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-pr-trust-bundle.md`.
- External review response for the active chunk is tracked separately at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-external-review-response.md` after external review runs.
