# Status: WS-POL-001 - Submission Artifact Policy Foundation

## Current Status

`WS-POL-001-01` and `WS-POL-001-02` are merged to `main`. `WS-POL-001-03` is
active on branch `codex/ws-pol-001-03-task-locked-context`.

Internal review, external review, and GitHub Actions passed for `WS-POL-001-02`
before merge. `WS-POL-001-03` now owns the task locked-context and submission
creation runtime migration.

## Active Chunk

`WS-POL-001-03` - Task Locked Context And Submission Creation

## Chunk Status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-POL-001-01` | Merged | `codex/ws-pol-001-01-submission-artifact-policy` | 28 | Implements guide-source snapshots, guide sufficiency reports, submission artifact policy, effective project policy, project pre-submit checker contract, activation guards, and key-based artifact policy merge. |
| `WS-POL-001-02` | Merged | `codex/ws-pol-001-02-agent-runtime-compiler` | 61 | Adds async guide sufficiency / derivation agents, runtime port, OpenAI Agents SDK adapter boundary, trusted compiler path, and server-owned provenance guards. |
| `WS-POL-001-03` | Active | `codex/ws-pol-001-03-task-locked-context` | - | Moves task locked-context and submission runtime to the effective policy and project checker bundle. |
| `WS-POL-001-04` | Planned | - | - | Splits post-submit checker policy provenance. |
| `WS-POL-001-05` | Planned | - | - | Proves revision resubmission and real API drill. |

## Blockers

| Blocker | Owner | Next action |
|---|---|---|
| None | - | Continue `WS-POL-001-03` implementation under the approved chunk contract. |

## Follow-Ups

| Item | Source | Priority |
|---|---|---|
| Add task locked guide-source snapshot/effective-policy/pre-submit bundle references before `READY` | Chunk map | High for Chunk 3 |
