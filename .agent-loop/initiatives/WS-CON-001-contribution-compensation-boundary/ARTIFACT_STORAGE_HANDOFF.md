# Artifact Storage Handoff: WS-ART-001-CON-EVIDENCE

## Ownership and gate

This is a proposed ART-owned prerequisite before CON-09A. ART owns the chunk,
raw ArtifactStore composition, prepared-byte admission, provider I/O,
verification, ArtifactBinding/receipt persistence, retry recovery, and provider
conformance. CON owns only the deterministic contribution-evidence schema,
projection status, canonical owner facts, and disclosure guards.

## Required typed capabilities

- `ContributionEvidenceWritePort.write(request)` accepts the caller
  `AsyncSession`, D10 prepared handle, contribution/project/schema identity,
  media type, expected digest, stable idempotency identity, and bounded
  deterministic bytes or byte source. In durable Transaction A it locks ART
  admission state after AUTH and CON locks, composes the full typed context,
  completes the handle's single final AUTH evaluation, stages the decision and
  admission/put-attempt continuation, and never commits or performs provider
  I/O. After the caller commits, only ART-owned continuation/executor authority
  may perform provider I/O, verification and binding. The high-level capability
  eventually returns bounded verified ArtifactBinding/receipt data and never a
  provider reference.
- `ContributionEvidenceReadPort.read(request)` accepts a Workstream
  ArtifactBinding id and already-authorized contribution context. It verifies
  binding/digest and returns bounded bytes or a stream, never provider authority.
- `ArtifactOperatorRecoveryPort.retry_verification(request)` remains the only
  operator recovery entry. Only exhausted `provider_unavailable` verification
  jobs are eligible; one recovery attempt creates a new retry job, leaves the
  exhausted source job unchanged, and exact replay returns the same attempt and
  retry-job ids.

## Authorization dependency

AUTH registers `artifact.contribution_evidence.binding.create` mapped to the
existing `artifact.binding.create` PermissionId, reuses the canonical fixed
`workstream.artifact.binding` ActorProfile/link, adds only this exact action to
that principal's closed assignment set, adds the typed service evaluator and
prepared `T` protocol, and alone changes availability to active. A new generic
CON/ART worker identity or broader artifact assignment is not allowed without a
reviewed AUTH amendment. ART owns the canonical contribution/project/role/
schema/digest resource composer and capability behavior consumed by that
evaluator. Public reads continue to use `contribution.read_self` or
`contribution.read_project`; there is no `artifact.retrieve` action.

CON prepares the AUTH handle from a server-resolved contribution/evidence-role
target before it locks its projection/contribution rows. It passes only that
opaque handle, canonical CON facts and deterministic bytes through the typed
port. ART then locks its own admission rows, adds ART-owned facts and completes
the one final evaluation in Transaction A. Missing/reused/mismatched handles or
fact drift fail before any durable provider attempt is executable. CON never
loads an ART row, composes ART admission facts or calls the evaluator itself.

## Provider and proof boundary

LocalStorage is focused dev/test, MinIO is local/CI S3-protocol proof, AWS S3 is
production, and R2/Flow Node are deferred. Contract tests must reject raw store
or provider imports in CON, raw provider-reference disclosure, changed bytes
under one idempotency identity, cross-owner/project binding, and recovery rows
or executor leases owned by CON.
