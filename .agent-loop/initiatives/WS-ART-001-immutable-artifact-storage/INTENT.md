# Intent: WS-ART-001 Immutable Artifact Storage

## Problem Being Solved

Workstream currently records caller-supplied artifact URIs and hashes without
owning the exact bytes. Flow Node contains content-addressed storage primitives,
but its REST API does not use them and is not a production Workstream boundary.

## Why This Work Matters

Pre-submit and post-submit checks, reviewers, revisions, and audit records must
all reference the same immutable bytes. A declared hash or local path is not
evidence that Workstream stored, verified, retained, or checked those bytes.

## Current Behavior

- Guide source manifests and hashes are stored in Postgres; source bytes are not.
- Submission requests accept `package_uri`, `package_hash`, artifact hash lists,
  and evidence URIs from contributors.
- Checkers validate metadata declarations and cannot retrieve exact bytes.
- Flow Node REST publish computes a CID and records metadata but does not store
  bytes through its existing DAG/block service.
- No runtime `ArtifactStorePort`, `ArtifactBinding`, `LocalStorageAdapter`, or
  `FlowNodeAdapter` exists in Workstream.

## Target Behavior

```text
client bytes
-> Workstream-authorized streaming upload
-> ArtifactStorePort
-> LocalStorageAdapter (development/CI) or FlowNodeAdapter (production)
-> Workstream-computed digest/size + provider receipt
-> ArtifactUploadItem + ArtifactContent + ArtifactReplica
-> sealed artifact-set commitment
-> immutable ArtifactBinding created at exact resource attachment
-> exact content locked to guide/submission/checker/review context
```

Workstream owns artifact meaning, actor/project/resource provenance,
authorization, lifecycle bindings, operation intent, and receipt history. A
storage provider owns immutable bytes and provider operation facts. Flow Node
implements storage, verification, retention, and retrieval without owning
Workstream product provenance.

## Design Chosen

- Separate upload-session/item, provider-neutral content, immutable logical
  binding, provider-replica, and append-only receipt records. Staging is owned
  by the upload item and never represented as a binding.
- Use `ReviewPacketManifest` for the system-generated reviewer packet and
  `ReviewEvidenceArtifact` for reviewer attachments; both reference
  `ArtifactBinding`.
- Stream uploads through Workstream in v0.1. Do not introduce direct-upload or
  presigned capability complexity before the authority path is proven.
- Persist Workstream-computed SHA-256 and byte count independently of opaque
  provider identifiers. Flow Node CID/DAG details remain provider receipts.
- Require full-provider-object verification and durable retention; Flow Node
  maps these to bounded recursive DAG verification and pinning.
- Keep Workstream evidence private and disable Flow Node network announcement by
  default.
- Add a focused Flow Node build/runtime target through ordinary PRs to Flow Node
  `main`; the deployed target contains only the Workstream evidence surface
  while the broader Flow Node product remains preserved.
- Make a clean pre-production cutover. Remove obsolete URI/hash contracts and
  rebuild incompatible local data; do not add compatibility aliases.

## Alternatives Considered

- Trust contributor URIs and hashes: rejected because checkers cannot prove the
  bytes.
- Store artifact bytes in Postgres: rejected because Postgres owns lifecycle
  state, not object bytes.
- Let clients upload directly to Flow Node immediately: deferred because secure
  one-time upload capabilities add an unnecessary second authority path.
- Copy Flow Node storage code into Workstream: rejected because it breaks the
  external evidence boundary.
- Keep every existing Flow Node feature in the Workstream deployment: rejected;
  the focused runtime target must expose only required evidence capabilities.

## Boundaries Preserved

- Identity Issuer authenticates; Workstream authorizes product access.
- Human bearer tokens are never forwarded to Flow Node.
- Workstream remains the sole lifecycle authority.
- Flow Node cannot accept, reject, route, or advance work.
- PostgreSQL stores bindings and receipts, never artifact bytes.
- Redis remains coordination, never canonical evidence state.

## Expected Risks

- Cross-repository contract drift.
- Partial DAG pinning or verification.
- Checking different bytes from those later submitted.
- Provider outage being misclassified as contributor failure.
- Artifact disclosure through retrieval or provider status surfaces.
- Large uploads exhausting API memory or worker capacity.
- Legacy pre-production records conflicting with the clean schema.

## What Must Not Change

- Review decision values remain `accept`, `needs_revision`, and `reject`.
- WS-AUTH authority remains local grants plus resource/lifecycle guards.
- Existing checker outcome meaning is not redesigned in storage foundation
  chunks.
- The broader Flow Node product remains intact; only the focused deployed target
  excludes unrelated capabilities.
- No blockchain settlement, marketplace, or public artifact publication.

## How This Will Be Proven

- One adapter contract suite runs against local and Flow Node adapters.
- Ingest/retrieve proves byte-for-byte equality for small, multi-chunk, and tree
  artifacts.
- Workstream-computed SHA-256 and byte count are compared with provider facts.
- Recursive pin and corruption/missing-block tests pass.
- Pre-submit failure creates no submission and cannot swap checked bytes.
- Post-submit checker input references the same immutable binding.
- Flow Node outage produces stable `artifact_storage_unavailable` on existing
  owning records, never a new task/review state, contributor failure, review
  decision, contribution, compensation, or reputation event.
- Unauthorized retrieval leaks no artifact metadata or counts.
- Docker Compose runs Postgres, Redis, Workstream, Celery, and focused Flow Node
  locally for a real API drill.

## Human Decisions Required

- Approve this plan and each implementation chunk separately.
- Approve the eventual production service-token issuer/audience configuration.
- Approve retention/legal-hold policy and quotas before production ingestion.
