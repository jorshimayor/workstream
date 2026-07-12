# ADR 0013: Immutable Artifact Storage Boundary

## Status

Accepted through explicit human approval of the WS-ART-001 planning PR.

## Context

Workstream currently accepts contributor-declared artifact URIs and hashes.
Those declarations do not prove that Workstream stored, verified, retained, or
checked the referenced bytes. Flow Node contains useful content-addressed
storage primitives, but its current REST publish path stores metadata only and
is unauthenticated.

ADR 0008 correctly requires an object-storage abstraction, but does not define
the Workstream records, exact-byte admission, provider receipt, retry,
authorization, or clean-cutover contracts now required.

## Decision

Workstream owns artifact intent, provider-neutral content identity, logical
resource bindings, actor/project/task/review provenance, authorization,
operation intent, receipt history, audit, and every lifecycle effect.

Storage providers own bytes and provider operation facts. Flow Node is the
production provider for immutable storage, provider manifests, verification,
retention, retrieval, and internal catalog status. It cannot accept, reject,
route, review, create contributions, or change compensation/reputation.

The Workstream model separates `ArtifactUploadSession`, per-object
`ArtifactUploadItem`, `ArtifactContent`, immutable `ArtifactBinding`,
`ArtifactReplica`, and `ArtifactOperationReceipt`. Staging exists on the upload
item; a binding is created only when content is attached to an exact Workstream
resource and logical role.

The provider-neutral contract uses SHA-256, byte count, opaque provider IDs,
typed operation results, verification, retention, availability, and integrity.
CID, DAG, blocks, and recursive pin details are Flow Node receipt details, not
checker truth or generic port types.

Byte ingest is synchronous and streaming after an authorized upload-intent
transaction commits and before the receipt transaction begins. Workstream
computes SHA-256 and byte count independently. A stable idempotency key permits
receipt lookup after a crash. Byte-less recovery can accept independently
re-read bytes only after observed provider success and against both persisted
pre-ingest expected SHA-256 and size. Ambiguous failure, cancellation, or an
incomplete commitment requires exact replay under the same key. A provider
receipt alone is never content truth. Celery/outbox handles only replayable
metadata-only verification, retention, status, release, and reconciliation.

Submission intake uses a sealed, server-generated artifact-set commitment and
an admission record bound to actor, task, policy, checker, and expiry. Exactly
one transaction may consume it into a submission.

## Authentication And Privacy

Flow Node accepts only a pre-provisioned Workstream service identity with exact
audience, issuer, asymmetric algorithms, time/JTI validation, and
per-operation scopes over TLS, including a distinct destructive
`artifact:release` scope. Human bearer tokens are rejected and never forwarded.

Evaluation evidence is private. Public announcement, peer retrieval, provider
discovery, and semantic search are disabled in the focused runtime. Production
requires encrypted storage and encrypted backups, redacted logs, quotas, and an
approved retention-policy version.

## Failure Meaning

Storage does not introduce a new task or review state. Stable operational codes
include `artifact_storage_unavailable`, `artifact_input_mismatch`,
`artifact_upload_expired`, `artifact_upload_consumed`, and
`artifact_integrity_failure`.

Transient post-submit retrieval failure keeps the task in
`evaluation_pending`, uses existing checker retry handling, and creates no
contributor result or routing. Integrity failure quarantines the replica.
Storage conditions cannot create a review decision, contribution, compensation
exposure, or reputation event.

## Clean Cutover

Rejected URI and caller-authoritative hash contracts are removed in their
owning guide/submission chunks. No aliases or fake verified backfills are
created. Additive foundation migrations tolerate existing pre-production rows;
destructive cutovers fail closed on their own incompatible rows and require the
documented pre-production rebuild.

## Review And Search Boundaries

WS-REV owns `ReviewPacketManifest` and `ReviewEvidenceArtifact` records and APIs
after reviewer assignment/lease authority exists. Both will reference generic
artifact bindings. Semantic search is outside WS-ART-001.

## Precedence

- ADR 0008 continues to require provider-neutral object-storage semantics.
- This ADR refines immutable artifact identity, provider integration, and
  exact-byte lifecycle binding.
- At the WS-ART submission cutover, this ADR supersedes ADR 0011 only for
  caller-provided manifest/hash fields, project-selectable storage schemes, and
  the compiler primitives that enforce those rejected transport declarations.
  ADR 0011 continues to govern project-level policy derivation, approval,
  locking, and deterministic checker compilation.
- ADR 0012 controls Workstream authorization.
- WS-REV controls review records and decisions.
- `docs/spec_artifact_storage_service.md` is the canonical target
  implementation contract after this ADR is accepted.
- Archival reference specifications remain non-executable inputs.

## Consequences

Positive:

- checkers and reviewers reference the exact same bytes;
- local and production storage share one provider-neutral contract;
- provider failure cannot blame contributors;
- Flow Node remains an evidence provider rather than a product authority.

Tradeoffs:

- upload staging and receipt reconciliation add operational records;
- cross-repository contract fixtures and pinned provider revisions are required;
- product cutovers must wait for their WS-AUTH dependencies;
- pre-production legacy data must be rebuilt rather than silently trusted.
