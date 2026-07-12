# Decisions: WS-ART-001

These are proposed target decisions. Existing accepted ADRs and current runtime
specifications remain authoritative until this planning PR is approved and each
owning cutover chunk merges. Flow Node repository documents control its internal
implementation; the versioned provider contract controls interoperability.

## D1 - Ownership

Workstream owns actor/project/task/review provenance, artifact intent, logical
bindings, authorization, lifecycle effects, operation requests, and receipt
history. Storage providers own bytes and provider operation facts. Flow Node
does not own Workstream product provenance or decisions.

## D2 - Separate Records

- `ArtifactUploadSession`: mutable operational staging authority, owner, scope,
  limits, expiry, sealing, and single-use state.
- `ArtifactUploadItem`: one mutable per-item operation ledger owning logical
  role, byte reservation, idempotency key/request digest, CAS state, provider
  operation reference, content result, and crash reconciliation.
- `ArtifactContent`: immutable provider-neutral SHA-256, byte count, media type,
  and server-generated content identity.
- `ArtifactBinding`: immutable logical association between content and one
  Workstream project/resource/role. Staging is not a binding; replacement creates
  a new binding with `supersedes_binding_id` and never mutates the prior row.
- `ArtifactReplica`: provider-specific artifact/manifest identifiers plus
  `verification_state`, `retention_state`, `availability_state`, and
  `integrity_state`.
- `ArtifactOperationReceipt`: append-only operation, idempotency, request digest,
  response digest, provider reference, outcome, and timestamps.

Verification, retention, availability, and integrity are not binding lifecycle
states.

## D3 - Provider-Neutral Port

`ArtifactStorePort` exposes immutable store/open/stat/verify/retain/release and
operation-receipt semantics. It returns opaque provider artifact/manifest IDs;
CID, DAG, block count, and recursive pin details remain bounded provider receipt
data. Workstream checker truth uses binding/content IDs, SHA-256, and byte count.

## D4 - Ingress Choreography

Byte ingest is synchronous, streaming, idempotent, and outside every lifecycle
transaction:

1. transaction A authorizes and creates/locks the per-item
   `ArtifactUploadItem` operation intent under its `ArtifactUploadSession`;
2. commit A;
3. Workstream streams bytes to the adapter while independently computing
   SHA-256 and byte count;
4. provider atomically stores, verifies, and retains the object or returns a
   typed failure;
5. transaction B locks the item/session, compares receipt digest/size, records
   content/replica/receipt, and marks the item ready; no resource binding exists
   yet;
6. an optional client expected SHA-256 is persisted before ingest as a byte
   commitment, never as server truth. If transaction B fails after provider
   success, recovery may accept the object only by reopening it and matching
   Workstream's independent hash/count to that persisted commitment. When no
   pre-ingest commitment exists, the item becomes `replay_required`; the client
   must replay the exact bytes under the same idempotency key so Workstream can
   recompute the stream and the provider can return the existing exact-replay
   receipt. Receipt-only recovery never creates `ArtifactContent`;
7. incomplete provider temporary objects are provider-owned and removed on
   cancellation/failure; completed orphan receipts are reclaimed only after
   staging expiry and reconciliation.

Bytes never enter PostgreSQL, Redis, Celery messages, or outbox rows. Outbox and
Celery are used only for replayable metadata-only verify, retain, release,
status, and reconciliation operations.

A commitment/receipt/object/replay mismatch, truncated recovery stream, or
changed provider object produces `artifact_integrity_failure`, quarantines the
replica, and cannot create content, a binding, or a submission. An unreplayed
orphan expires through reconciliation and provider cleanup.

## D5 - Submission Commitment

A sealed upload session produces a canonical server-generated
`ArtifactSetManifest`. Each entry has a server-derived `manifest_entry_id` equal
to the SHA-256 of canonical JSON containing its logical role, normalized display
name, content ID, SHA-256, byte count, detected media type, and trusted
archive-member facts. Exact duplicate entry IDs are rejected. Entries are
totally ordered by `(logical_role, normalized_display_name, content_id,
manifest_entry_id)`, so no unresolved ties remain. The SHA-256 of the final
canonical manifest JSON is the `artifact_set_hash`.

An authoritative pre-submit admission record binds actor, task, sealed upload
session, artifact-set hash, effective project submission artifact policy hash,
pre-submit checker bundle hash, expiry, and a canonical
`submission_input_hash` over `summary`, `contributor_attestation`,
`upload_session_id`, task ID, and artifact-set hash. Submission creation must
present the same input, revalidates authority and policy, locks every row, and
consumes the session/admission exactly once. One concurrent attempt wins.

## D6 - Local Parity

`LocalStorageAdapter` and `FlowNodeAdapter` implement the same provider-neutral
contract and test vectors. Local identifiers are opaque and paths never escape.
Local storage is forbidden in production.

## D7 - Service Authentication

The first Flow Node byte route is authenticated. Production requires TLS and a
short-lived issuer-signed service token with:

- pinned issuer and asymmetric algorithms;
- exact audience `flow-node`;
- pre-provisioned Workstream service subject of kind `service`;
- time and token-ID validation;
- per-operation scopes `artifact:ingest`, `artifact:read`, `artifact:verify`,
  `artifact:retain`, `artifact:release`, and `artifact:status`;
- explicit human-subject rejection;
- secret-manager/environment custody, rotation overlap, and redacted logs.

Local development uses a test issuer/key and loopback TLS exception only under
an explicit development environment. Production startup fails closed without
approved issuer/TLS configuration. Human bearer tokens are never forwarded.

Release additionally requires exact retention-reference ownership, approved
retention/legal-hold checks, append-only audit evidence, and negative proof that
read/status/verify/retain-only credentials cannot release content.

## D8 - Privacy And Retention

Workstream evidence is private. Flow Node public announcements, peer retrieval,
public provider discovery, and unrelated search are disabled in the focused
runtime. Production requires TLS, encrypted storage/backup configuration,
restricted file permissions, redacted payload/metadata logs, access auditing,
and an approved retention-policy version.

Staging defaults to 24 hours and is quota-bound. Canonical evaluation evidence
uses an approved retention class and is never automatically released in v0.1.
The sweeper uses compare-and-set so content already bound, or concurrently
being bound, to a resource cannot be released. Legal hold/deletion behavior
must be approved before production deletion exists.

## D9 - Failure Meaning

No new task/review lifecycle state named `evidence_unavailable` is introduced.
Storage conditions use stable error/failure codes on their owning operational
records. Transient storage failure keeps a post-submit task in
`evaluation_pending`, uses existing checker retry handling, creates no
contributor checker result, and cannot route to human review. Integrity failure
quarantines the replica for Operator investigation. No storage problem can
create a review decision, contribution, compensation exposure, or reputation
event.

## D10 - Clean Cutover

Remove obsolete URI and caller-authoritative hash contracts in their owning
cutover chunks. Foundation migrations are additive and tolerate untouched legacy
tables. Guide/submission destructive cutovers fail closed only on rows owned by
that cutover, with a pre-production rebuild runbook. No alias or verified
backfill is added.

## D11 - Flow Node Delivery

Flow Node work uses normal feature branches and PRs into Flow Node `main`. It
adds a focused `workstream-artifact` build/runtime target that excludes unrelated
routes and dependencies from the deployed binary without deleting the broader
Flow Node product. Workstream pins a tested Flow Node image digest/revision.

## D12 - Search And Review Boundaries

Semantic search is out of scope for WS-ART-001. Provider catalog/status is for
internal reconciliation only. `ReviewPacketManifest` and
`ReviewEvidenceArtifact` remain approved names, but their records/APIs are owned
by WS-REV after reviewer assignment/lease authority exists. WS-ART supplies only
generic artifact primitives.

## D13 - Shared Infrastructure Reuse

Artifact services write product/audit evidence through the existing
`AuditEvent` and `AuditRepository` path. `ArtifactOperationReceipt` is provider
operation evidence and must not become a second audit-event framework.

Canonical manifests plus idempotency request/response digests reuse
`app.core.hashing.canonical_json_hash`. If artifact contracts require canonical
JSON values broader than the current helper accepts, that helper is extended
centrally with regression vectors; no artifact-local JSON encoder/hash helper is
introduced. The legacy caller-manifest hash helper is removed in its owning
cutover rather than reused as canonical artifact truth.
