# Loop State

## Current State

- Active initiative: `WS-POL-001` - Submission Artifact Policy Foundation
- Active planning chunk: none
- Active implementation chunk: `WS-POL-001-03`
- Branch: `codex/ws-pol-001-03-task-locked-context`
- Status: PR #63 awaiting review for `WS-POL-001-03`; internal review complete and external review pending
- Reviewed code SHA: `a3abfac3bc3a91026856c5e42d8fc873e575d757`
- Current gate: GitHub Actions rerun, CodeRabbit refresh, and human PR review checkpoint
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
- PR #63 implements `WS-POL-001-03` from `codex/ws-pol-001-03-task-locked-context` into `main`.
- Internal review evidence for the active chunk is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-internal-review-evidence.md`.
- PR trust bundle for the active chunk is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-pr-trust-bundle.md`.
- External review response for the active chunk is tracked separately at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-external-review-response.md` after external review runs.
