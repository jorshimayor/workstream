# Status: WS-ART-001 Immutable Artifact Storage

## Current Status

Planning merged through PR #97 on 2026-07-12 as `8644a43`. The reviewed
planning SHA is `f7fbc33`; the final evidence-bound branch head is `c069064`.
Implementation chunk `WS-ART-001-01` is implemented and internally reviewed on
its dedicated branch. The reviewed implementation SHA is `d67ccf1`. All nine
required reviewer tracks passed and their sessions are closed. The chunk is
ready for PR publication, external checks, and the user-owned approval gate.

## Active Chunk

`WS-ART-001-01`: artifact domain and local adapter, awaiting external and human
review. Do not merge without explicit user approval.

## Proposed First Implementation Chunk

`WS-ART-001-02` after `WS-ART-001-01` is merged through an explicit human
checkpoint. Product cutovers remain blocked on their named WS-AUTH dependencies
even if internal storage foundations finish first.

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

Stop after the `WS-ART-001-01` PR reaches its human checkpoint. Do not begin
`WS-ART-001-02` or edit Flow Node in this chunk.
