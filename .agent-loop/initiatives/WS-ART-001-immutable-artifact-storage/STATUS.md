# Status: WS-ART-001 Immutable Artifact Storage

## Current Status

Planning merged through PR #97 on 2026-07-12 as `8644a43`. The reviewed
planning SHA is `f7fbc33`; the final evidence-bound branch head is `c069064`.
Implementation chunk `WS-ART-001-01` merged through PR #101 on 2026-07-12 as
`050eb15`. Its reviewed implementation SHA is `5574bf5`; the final
evidence-bound branch head is `2b8c2a0`. Agent Gates, Backend CI, CodeRabbit,
all nine internal reviewer tracks, and the explicit user approval gate passed.

## Active Chunk

None.

## Proposed Next Implementation Chunk

`WS-ART-001-02`: Flow Node adapter and reconciliation. It remains proposed and
inactive pending a separate explicit user start. Product cutovers remain
blocked on their named WS-AUTH dependencies even if internal storage
foundations finish first.

## Parallel Work

WS-AUTH may continue in its dedicated worktree. WS-ART must rebase on current
`main` before each implementation PR and must not implement or bypass
authorization contracts owned by WS-AUTH.

Dependency gates:

- `WS-ART-001-03` waits for the project mutation authorization cutover.
- `WS-ART-001-04` through `WS-ART-001-06` wait for task, submission, and
  checker authorization cutovers.
- Reviewer attachment APIs remain owned by WS-REV after reviewer
  assignment/lease authority exists.

## Stop Condition

Merge this post-merge memory update and stop. Do not begin `WS-ART-001-02` or
edit Flow Node without a separate explicit user start.
