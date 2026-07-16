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
SHA `ae70bc2f10334f649c1af7f210e58ee378695a2b`. All nine required reviewer
tracks pass and every session is closed. The chunk adds only the inactive
bounded preparation/committed-source boundary, private filesystem scratch
ledger and deterministic cleanup mechanics, bounded shared file locking,
LocalStorage private helper refactoring, settings, documentation, and proof.
Active ArtifactStore v1 behavior, provider selection, and product lifecycle
remain unchanged. The ledger is database-independent scratch coordination and
never product or durable artifact state.

## Next Proposed Chunk

`02A2` adds committed-source preparation and narrows LocalStorage internals
without changing the active port. `02A3` performs the atomic
ArtifactStore v2/LocalStorage/schema cut and removes `flow_node`. `02B1` then
owns MinIO and AWS S3. There is no active R2 chunk.

## Gate

Ready PR #129 is open at
`https://github.com/Flow-Research/workstream/pull/129`. Local deterministic
proof and all nine internal reviewer tracks pass for the reviewed code SHA.
The prior published head passed Agent Gates, Backend, and CodeRabbit. Trusted
`main` at AUTH-08 merge `aa0fdcd` was then integrated to resolve the PR's base
conflict. The combined tree passes 154 focused ART tests at 94.40 percent, 38
isolated artifact PostgreSQL tests, and 207 isolated AUTH/authentication/Alembic
tests. All nine exact-revision tracks pass and stale queue wording is repaired.
The current gate is publication followed by fresh Agent Gates, Backend, and
CodeRabbit checks. No later artifact chunk starts automatically, and only the
user may approve merge.
