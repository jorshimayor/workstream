# Status: WS-ART-001 S3-Compatible Object Storage Amendment

## Current State

Original planning merged through PR #97, artifact/LocalStorage foundation
merged through PR #101, the AWS-first object-storage amendment merged through
PR #120 as `4408256`, and the external-service adapter foundation merged
through PR #127 as `f64a8e5`. `WS-ART-001-02A2` merged through PR #129 as
`9a04434` on 2026-07-16.

The Flow Node-focused amendment candidate `6cc422d` passed deterministic checks
but failed internal review on recovery/API completeness. Before repair, the user
approved a first-principle change on 2026-07-14:

```text
v0.1 production bytes -> S3CompatibleArtifactStore -> AWS S3
local/CI proof bytes   -> S3CompatibleArtifactStore -> MinIO
development bytes     -> LocalStorageAdapter
future optional bytes -> Flow Node adapter initiative
```

The failed Flow Node candidate and every reviewer session are closed. It is not
approval or reusable evidence. Its source remains on branch
`codex/ws-art-001-fn01-isolation-amendment` for the deferred Flow Node plan.

## Current Work

No artifact implementation chunk is active. `WS-ART-001-02A3` implementation
and review are complete at `935b1a2` in its isolated worktree and await its own
PR publication. Active ArtifactStore v1 behavior, provider selection, and
product lifecycle remain unchanged until that separate PR merges.

## Next Proposed Chunk

`02A2` added committed-source preparation and narrowed LocalStorage internals
without changing the active port. `02A3` performs the atomic
ArtifactStore v2/LocalStorage/schema cut and removes `flow_node`. `02B1` then
owns MinIO and AWS S3. There is no active R2 chunk.

## Gate

PR #129 merged `WS-ART-001-02A2` as `9a04434`. The current artifact gate is
publication and human review of the already reviewed `WS-ART-001-02A3`
worktree; no PR is attributed here until it is actually opened. No later
artifact chunk starts automatically, and only the user may approve a merge.
