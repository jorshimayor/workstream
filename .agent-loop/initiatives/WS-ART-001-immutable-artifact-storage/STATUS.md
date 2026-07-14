# Status: WS-ART-001 S3-Compatible Object Storage Amendment

## Current State

Original planning merged through PR #97 and artifact/LocalStorage foundation
merged through PR #101. No artifact implementation chunk is active.

The Flow Node-focused amendment candidate `6cc422d` passed deterministic checks
but failed internal review on recovery/API completeness. Before repair, the user
approved a first-principle change on 2026-07-14:

```text
v0.1 production bytes -> S3CompatibleArtifactStore -> AWS S3 or Cloudflare R2
development bytes     -> LocalStorageAdapter
future optional bytes -> Flow Node adapter initiative
```

The failed Flow Node candidate and every reviewer session are closed. It is not
approval or reusable evidence. Its source remains on branch
`codex/ws-art-001-fn01-isolation-amendment` for the deferred Flow Node plan.

## Active Work

`WS-ART-001-OBJECT-STORAGE-AMENDMENT` is planning-only. It updates intent,
architecture, ADR/spec, chunk contracts, durable memory, and deterministic
stale-contract protection. It does not edit runtime code, configure AWS S3/R2, operate
Flow Node, or activate artifact routes.

## Next Proposed Chunk

`WS-ART-001-02A1` is proposed after this amendment merges and the user starts it
explicitly. It installs only the shared typed external-service adapter/factory
foundation. `02A2` adds committed-source preparation and narrows LocalStorage
internals without changing the active port. `02A3` performs the atomic
ArtifactStore v2/LocalStorage/schema cut and removes `flow_node`. `02B1` then
owns MinIO/AWS S3, `02B2` owns the isolated deployment R2 credential issuer,
and `02B3` owns Workstream's R2 container-credential integration.

## Gate

The committed amendment is in exact-head internal repair and review. Prior
review established the canonical pre/post-submit materializer, coverage-phase
binding, R2 scope/network isolation, and scratch-cleanup ownership. Current
candidate closes structured deployment-configuration and CI-environment gaps. A
final immutable SHA will be recorded only after all required reviewers pass.
The remaining gate is complete exact-head internal reviewer fanout and evidence,
external PR review, and explicit human merge approval. No later chunk starts
automatically.
