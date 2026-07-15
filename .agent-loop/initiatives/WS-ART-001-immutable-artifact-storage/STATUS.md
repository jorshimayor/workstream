# Status: WS-ART-001 S3-Compatible Object Storage Amendment

## Current State

Original planning merged through PR #97, artifact/LocalStorage foundation
merged through PR #101, the AWS-first object-storage amendment merged through
PR #120 as `4408256`, and the external-service adapter foundation merged
through PR #127 as `f64a8e5`. The user explicitly started
`WS-ART-001-02A2` on 2026-07-15.

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

## Active Work

`WS-ART-001-02A2` implementation and internal review are complete at reviewed
SHA `d8b8c8abc7c6dd8cf254d0c8b3d5d7c066c01b46`. All nine required reviewer
tracks pass and every session is closed. The chunk adds only the inactive
bounded preparation/committed-source boundary, private filesystem scratch
ledger and deterministic cleanup mechanics, LocalStorage private helper
refactoring, settings, documentation, and proof. Active ArtifactStore v1
behavior and factory wiring remain unchanged. The ledger is
database-independent scratch coordination and never product or durable artifact
state.

## Next Proposed Chunk

`02A2` adds committed-source preparation and narrows LocalStorage internals
without changing the active port. `02A3` performs the atomic
ArtifactStore v2/LocalStorage/schema cut and removes `flow_node`. `02B1` then
owns MinIO and AWS S3. There is no active R2 chunk.

## Gate

PR #127 is merged. `WS-ART-001-02A2` is ready for publication, external checks,
and the human merge checkpoint. No later artifact chunk starts automatically,
and only the user may approve merge.
