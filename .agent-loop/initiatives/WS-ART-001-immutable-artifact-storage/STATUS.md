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

Candidates `e6415886a2474af899eb433c4b42eabea8e794c7`,
`e14376c896f9225a152e932de8789517814ef082`, and
`d2cd73a0debe73930a8311a37b45f3aff4315f11` passed deterministic planning
checks but failed one or more exact-head required review tracks. Candidate
`b5279be1da1b61c161166903d6144719cf29a17e` then passed architecture and had no
remaining senior/security design finding, but QA/test found that its AWS
authorization regression test was not a closed-matrix assertion. Every session
was closed and none of those results is reusable approval. Repair is active on
integrated main `eba7e2b` and remains planning-only.

The repair closes the raw-port/orchestrator bypass, pre-replica acknowledgement
gap, namespace first-writer race, caller-assembled quota scope, AWS activation
and principal boundary, AUTH action-activation ownership, terminal service
authority race, stale-scanner discovery/history/runtime gaps, and cumulative
coverage omissions. The second repair also separates admission, verification,
and recovery chunks; closes dependency-manifest/frontend/Work Queue scanning;
defines separate caller-ARN-bound AWS proof executors; adds per-I/O activation
freshness; and closes service-action, materialization, checker-output binding,
Operator recovery, and capacity-visibility ownership. The current repair makes
the principal/action/resource and bucket-deny matrices machine-checkable and
rejects extra grants, resources, wildcard actions, or altered condition keys. A
new immutable SHA will be recorded only after deterministic checks and every
required internal reviewer pass. External PR review and explicit human merge
approval remain later gates. No later chunk starts automatically.
