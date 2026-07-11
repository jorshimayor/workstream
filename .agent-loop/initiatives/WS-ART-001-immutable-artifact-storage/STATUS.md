# Status: WS-ART-001 Immutable Artifact Storage

## Current Status

Planning in progress on `codex/ws-art-001-artifact-storage-planning`.

## Active Chunk

`WS-ART-001-PLAN` only.

## Proposed First Implementation Chunk

`WS-ART-001-01` after planning review, external review, merge, memory update,
and a separate explicit user approval. Product cutovers remain blocked on their
named WS-AUTH dependencies even if internal storage foundations finish first.

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

Stop after the planning PR. Do not edit Flow Node or implement an artifact
chunk until the planning package is approved and merged.
