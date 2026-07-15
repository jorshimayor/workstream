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

Merge SHA `1545d9aa37329c13efa53f7ad9076ffca1fbfaf6` received every
required internal track after `main` advanced through AUTH-05B PR #119: senior
engineering, architecture, QA/test, security/auth, product/ops, reuse/dedup, CI
integrity, test delta, and docs. Valid evidence/status findings are closed in
the permitted post-review files. Every reviewer used `gpt-5.5` with high
reasoning and every reviewer session is closed.

Deterministic proof passes: Ruff; stale artifact, authorization, and Workstream
wording scans; loop-memory state; 75 changed Markdown links; diff hygiene; the
runtime-scope guard; and 44 agent-gate regression tests in a PEP 668-safe,
hash-pinned temporary environment.

Evidence:

- `reviews/WS-ART-001-OBJECT-STORAGE-AMENDMENT-internal-review-evidence.md`
- `reviews/WS-ART-001-OBJECT-STORAGE-AMENDMENT-pr-trust-bundle.md`

The current gate is external review and explicit human merge approval. GitHub
checks and CodeRabbit remain separate from internal review. Do not merge without
the user's approval, and do not start `WS-ART-001-02A1` automatically.
