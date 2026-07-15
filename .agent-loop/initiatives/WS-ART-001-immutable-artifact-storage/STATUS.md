# Status: WS-ART-001 S3-Compatible Object Storage Amendment

## Current State

Original planning merged through PR #97, artifact/LocalStorage foundation
merged through PR #101, and the AWS-first object-storage amendment merged
through PR #120 as `4408256`. The user explicitly started
`WS-ART-001-02A1` on 2026-07-15.

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

`WS-ART-001-02A1` implementation and all nine required internal reviewer tracks
are complete at reviewed code SHA `8224d8c`. The chunk installs only the shared
typed external-service adapter/factory foundation and does not migrate any
capability. It is ready for PR publication, GitHub Backend CI, external review,
and the human merge checkpoint.

## Next Proposed Chunk

`WS-ART-001-02A1` installs the shared typed external-service adapter/factory
foundation. `02A2`
adds committed-source preparation and narrows LocalStorage internals without
changing the active port. `02A3` performs the atomic
ArtifactStore v2/LocalStorage/schema cut and removes `flow_node`. `02B1` then
owns MinIO and AWS S3. There is no active R2 chunk.

## Gate

PR #120 is merged. `WS-ART-001-02A1` awaits external and human review. No later
artifact chunk starts automatically, and only the user may approve merge.
