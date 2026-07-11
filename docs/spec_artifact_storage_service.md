# Workstream Immutable Artifact Storage Specification

## Status And Scope

This is the proposed canonical target specification for WS-ART-001. It becomes
controlling when ADR 0013 and the planning PR are explicitly approved. Until an
owning cutover merges, current runtime schemas remain implementation evidence.

It covers provider-neutral artifact storage, local/Flow Node interoperability,
staging, exact-byte binding, checker artifacts, and recovery. It does not
implement review decisions, contribution, compensation, reputation, semantic
search, or public content publication.

## Ownership

| Concern | Owner |
|---|---|
| actor/project/resource provenance, authority, lifecycle meaning | Workstream |
| upload intent, content digest, logical binding, receipt history | Workstream |
| immutable bytes and provider operation facts | configured storage provider |
| CID/DAG/block traversal and recursive pins | Flow Node implementation |
| review packet/evidence aggregates | later WS-REV records referencing bindings |

## Canonical Records

### ArtifactUploadSession

Required concepts: id, actor, project, optional task/guide, permitted roles,
state, maximum/current bytes and items, sealed artifact-set hash, expiry,
consumed timestamp, database time, and CAS version.

States: `open`, `sealed`, `consumed`, `expired`, `cancelled`.

### ArtifactUploadItem

One per-session artifact operation ledger. Fields include session, logical role,
normalized display name, byte reservation, expected digest where supplied,
unique scoped idempotency key, canonical request digest, CAS version, provider
operation reference, resulting content ID, error code, and timestamps.

States: `reserved`, `uploading`, `provider_committed`, `replay_required`,
`ready`, `failed`, `cancelled`. The unique operation key is scoped to session
and item; a session may contain many items.

### ArtifactContent

Immutable provider-neutral SHA-256, byte count, detected media type, normalized
display name where allowed, and creation time.

### ArtifactBinding

Immutable project, resource type/id, logical role, content ID, actor/service
attribution, created time, and optional `supersedes_binding_id`. Upload staging
is represented by upload items, not bindings. Resource attachment creates the
binding once; replacement creates a new row and leaves history unchanged.

### ArtifactReplica

Content ID, adapter/provider, opaque provider artifact and optional manifest
IDs, verification state, retention state, availability state, integrity state,
last reconciliation time, and current receipt reference. These states are
provider observations, not task or review states.

### ArtifactOperationReceipt

Append-only operation, service principal, scoped idempotency key, canonical
request digest, bounded response digest/details, provider reference, outcome,
attempt/correlation references, and provider/database timestamps.

## Provider-Neutral Port

Async operations:

```text
store(stream, expected_sha256, maximum_bytes, metadata, idempotency)
open(provider_artifact_id, byte_range?)
stat(provider_artifact_id)
verify(provider_artifact_id, expected_sha256, expected_size, idempotency)
retain(provider_artifact_id, retention_class, idempotency)
release(provider_artifact_id, retention_reference, idempotency)
get_operation_receipt(idempotency)
```

DTOs expose opaque provider IDs, SHA-256, size, media type, typed states, and
stable errors. Provider-specific receipt details are bounded and never required
for domain decisions.

Canonical JSON and SHA-256 operations reuse Workstream's shared
`app.core.hashing.canonical_json_hash` implementation (extended centrally if
needed). Artifact modules do not create a parallel JSON canonicalizer. Product
audit events for binding, release, quarantine, and reconciliation use the
existing `AuditEvent`/`AuditRepository`; provider operation receipts remain a
separate provider-evidence record, not a replacement audit framework.

## Versioned Provider Contract

Workstream owns `contracts/artifact-store/version_1/` request/response schemas, stable
HTTP/error matrix, limits, idempotency rules, malformed receipt fixtures, and
conformance vectors. Flow Node copies the exact version with source digest.
Workstream pins the tested provider image digest/revision. Breaking changes
require a new major version and coordinated human approval.

## Service Authentication

Production requires pinned issuer/asymmetric algorithms, audience exactly
`flow-node`, a pre-provisioned Workstream service subject of kind `service`,
time/JTI validation, endpoint scopes `artifact:ingest`, `artifact:read`,
`artifact:verify`, `artifact:retain`, `artifact:release`, and
`artifact:status`, TLS, rotation, and redaction. Human subjects and unrelated
services are denied.

Release requires exact retention-reference ownership, approved retention and
legal-hold checks, append-only audit evidence, and negative tests proving other
scopes cannot release content.

Local test issuer/key is permitted only in explicit development mode;
production fails closed.

## Ingest Transactions

1. Transaction A authorizes and commits/locks one per-item upload operation.
2. Outside any DB transaction, Workstream streams bounded chunks while
   independently hashing/counting bytes.
3. Provider atomically stores/verifies/retains or removes partial temporary
   state and returns a receipt.
4. Transaction B locks session/item, compares provider facts, and writes
   content/replica/receipt/item readiness. No resource binding exists yet.
5. Optional expected SHA-256 is persisted before ingest as a client byte
   commitment, not server truth. Crash recovery may independently open/hash/count
   provider bytes against that commitment. Without a pre-ingest commitment, the
   item becomes `replay_required` and the client must replay the exact bytes
   under the same idempotency key; Workstream hashes the replay and the provider
   returns the existing exact-replay receipt. Receipt-only recovery never
   creates content. Altered commitment/receipt/object/replay bytes are
   quarantined with `artifact_integrity_failure`; no background process guesses
   a local path.

Metadata-only provider operations use outbox/Celery. Bytes and credentials never
enter outbox, Redis, or PostgreSQL.

## Limits And Confidentiality

Default ceilings are 512 MiB per artifact, 1 GiB per session, and a 1 MiB
stream buffer per active transfer. Project policy may tighten them.

Production requires TLS, encrypted provider volumes/backups, access auditing,
redacted logs, quotas, and an approved retention-policy version. Local adapter
directories use restrictive permissions and are prohibited in production.

Public announcement, peer retrieval, provider discovery, and semantic search
are disabled in the focused Flow Node runtime.

## Exact Submission Binding

Sealing generates a canonical `ArtifactSetManifest` from trusted server facts.
Each entry has a `manifest_entry_id` derived from canonical JSON of every
semantic entry field; exact duplicate entry IDs are rejected. Entries are
totally ordered by logical role, normalized display name, content ID, and entry
ID. The manifest SHA-256 commits only to the sealed artifact set. A separate
pre-submit admission record binds that hash to upload session, actor, task,
policy, checker, result, expiry, and a canonical hash of the exact summary,
contributor attestation, upload-session ID, task ID, and artifact-set hash.
Submission creation transactionally revalidates the same input and authority,
locks/CAS-consumes every record once, and creates exact immutable resource
bindings.

The public submission request after cutover is:

```json
{
  "summary": "...",
  "contributor_attestation": "...",
  "upload_session_id": "..."
}
```

Clients do not provide package URI, canonical digest manifest, evidence IDs,
artifact-set hash, or provider identifiers.

### Workstream API Families

```text
POST   /api/v1/tasks/{task_id}/artifact-upload-sessions
GET    /api/v1/artifact-upload-sessions/{session_id}
POST   /api/v1/artifact-upload-sessions/{session_id}/artifacts
POST   /api/v1/artifact-upload-sessions/{session_id}/seal
DELETE /api/v1/artifact-upload-sessions/{session_id}
POST   /api/v1/tasks/{task_id}/submission-precheck
POST   /api/v1/tasks/{task_id}/submissions
```

Session creation accepts no provider IDs. Artifact upload is multipart with a
server-approved logical role, display name, optional expected SHA-256, and file
stream. The response returns the Workstream upload-item ID and content ID,
server SHA-256, byte count, detected media type, and readiness without provider
internals. It returns no binding ID because staging does not bind content to a
product resource.

Sealing returns `upload_session_id`, `artifact_set_hash`, state, expiry, and
bounded artifact summaries. `/submission-precheck` retains its canonical route
and accepts the same `summary`, `contributor_attestation`, and
`upload_session_id` fields used by submission creation. It returns the existing
checker response contract or a stable storage error. A passing admission is
bound to the canonical hash of those exact inputs; changing any field requires
a new precheck.

### Flow Node Provider API Families

The versioned contract defines authenticated service routes equivalent to:

```text
POST /api/v1/artifacts
GET  /api/v1/artifacts/{provider_artifact_id}
GET  /api/v1/artifacts/{provider_artifact_id}/status
POST /api/v1/artifacts/{provider_artifact_id}/verify
PUT  /api/v1/artifacts/{provider_artifact_id}/retentions/{reference}
DELETE /api/v1/artifacts/{provider_artifact_id}/retentions/{reference}
GET  /api/v1/artifact-operations/{idempotency_key}
```

Successful new ingest is 201; exact replay is 200; accepted metadata-only
operation may be 202. Stable failures include 400 malformed, 401 invalid service
identity, 403 wrong audience/scope, 404 unknown provider artifact, 409
idempotency mismatch or retention conflict, 413 limit exceeded, 422 digest or
integrity mismatch, 429 throttled, and 503 provider unavailable.

Idempotency records are scoped by service subject, operation, canonical request
reference, and request digest. They remain available for the provider artifact's
lifetime and never less than 90 days. Auth, validation, conflict, and integrity
failures are not retried. Transient timeout/429/5xx retries use full jitter,
default five-second initial delay, five-minute cap, eight attempts, and a
configurable 30-minute elapsed-time limit before operator-visible dead letter.

Receipt outcomes are immutable. Verification moves from pending to verified or
integrity-failed. Retention moves from unretained to retained and may reach
released only through an authorized reference-counted release. Availability is
a mutable observation. Quarantined integrity can return to valid only through a
new audited repair/verification receipt; history is never overwritten.

## Checker Binding

`CheckerInputSnapshot` references binding/content IDs, SHA-256, byte count,
artifact-set hash, locked policy/checker identities, and checker implementation
identity. Provider identifiers remain replica details.

Pre-submit and post-submit must prove the same artifact-set hash. Checker logs
and generated outputs are artifact bindings. Storage unavailability uses
existing failed-run/retry mechanics and keeps the task `evaluation_pending`;
it creates no contributor result or routing.

## Failure Contract

Stable codes and exact effects are defined in the WS-ART-001 plan failure
matrix. They are operational/domain errors on upload sessions, setup runs,
checker runs, or API responses; none is a new task/review decision state.

## Migration And Removal

Foundation schema is additive. Guide and submission cutovers own their exact
fail-closed preflight and rebuild runbook. No URI/hash declaration is promoted
to verified evidence. Removed names are enforced by
`scripts/check_stale_artifact_contracts.py` in their owning cutover.

Project submission-artifact policy remains project-scoped and retains semantic
required-artifact/evidence, forbidden-artifact, attestation, limit, and
packaging rules. It no longer accepts transport/provider or caller-hash choices:
`manifest_required`, `artifact_hash_required`, `artifact_hash_algorithm`, and
`allowed_storage_schemes` are removed. Workstream's sealed artifact set,
server-computed SHA-256, and configured `ArtifactStorePort` are unconditional
platform invariants. The trusted compiler replaces the legacy
storage-scheme/hash/manifest primitives with `validate_sealed_artifact_set`.

## Authorization Dependencies

Guide cutover waits for project mutation authorization. Upload, submission, and
checker cutovers wait for their WS-AUTH resource-family cutovers. Reviewer
attachments remain deferred to WS-REV assignment/lease authority.
