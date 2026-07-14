# Status: WS-ART-001 S3-Compatible Object Storage Amendment

## Current State

Original planning merged through PR #97 and artifact/LocalStorage foundation
merged through PR #101. No artifact implementation chunk is active.

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

`WS-ART-001-OBJECT-STORAGE-AMENDMENT` is planning-only. It updates intent,
architecture, ADR/spec, chunk contracts, durable memory, and deterministic
stale-contract protection. It does not edit runtime code, configure AWS S3,
operate Flow Node, add a deferred provider, or activate artifact routes.

## Next Proposed Chunk

`WS-ART-001-02A1` is proposed after this amendment merges and the user starts it
explicitly. It installs only the shared typed external-service adapter/factory
foundation. `02A2` adds committed-source preparation and narrows LocalStorage
internals without changing the active port. `02A3` performs the atomic
ArtifactStore v2/LocalStorage/schema cut and removes `flow_node`. `02B1` then
owns MinIO and AWS S3. There is no active R2 chunk.

## Gate

Candidate `e6415886a2474af899eb433c4b42eabea8e794c7` passed deterministic
planning checks but failed exact-head senior engineering, architecture,
QA/test, and security/auth review. Every session was closed and the result is
not reusable approval. Repair is active on integrated main `eba7e2b` and remains
planning-only.

The repair closes the raw-port/orchestrator bypass, pre-replica acknowledgement
gap, namespace first-writer race, caller-assembled quota scope, AWS activation
and principal boundary, AUTH action-activation ownership, terminal service
authority race, stale-scanner discovery/history/runtime gaps, and cumulative
coverage omissions. A new immutable SHA will be recorded only after
deterministic checks and every required internal reviewer pass. External PR
review and explicit human merge approval remain later gates. No later chunk
starts automatically.
