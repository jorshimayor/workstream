# Status: WS-ART-001 Immutable Artifact Storage

## Current Status

Planning merged through PR #97 on 2026-07-12 as `8644a43`. The reviewed
planning SHA is `f7fbc33`; the final evidence-bound branch head is `c069064`.
No implementation chunk is active.

## Active Chunk

None.

## Proposed First Implementation Chunk

`WS-ART-001-01` after this post-merge memory update and a separate explicit user
start. Product cutovers remain blocked on their named WS-AUTH dependencies even
if internal storage foundations finish first.

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

Stop after the post-merge memory update. Do not edit Flow Node or implement an
artifact chunk until the user separately starts `WS-ART-001-01`.
