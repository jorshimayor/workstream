# Artifact Storage Handoff: WS-ART-001-CON-EVIDENCE

## Ownership and gate

This is a proposed ART-owned prerequisite before CON-09A. ART owns the chunk,
raw ArtifactStore composition, prepared-byte admission, provider I/O,
verification, ArtifactBinding/receipt persistence, retry recovery, and provider
conformance. CON owns only the deterministic contribution-evidence schema,
projection status, canonical owner facts, and disclosure guards.

## Required typed capabilities

- `ContributionEvidenceWritePort.write(request)` accepts contribution/project/
  schema identity, media type, expected digest, stable idempotency identity, and
  bounded deterministic bytes or byte source. It returns bounded verified
  ArtifactBinding/receipt data and never a provider reference.
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
existing `artifact.binding.create` PermissionId. ART provisions the fixed
service actor and activates exact contribution/project/role/schema/digest facts.
Public reads continue to use `contribution.read_self` or
`contribution.read_project`; there is no `artifact.retrieve` action.

## Provider and proof boundary

LocalStorage is focused dev/test, MinIO is local/CI S3-protocol proof, AWS S3 is
production, and R2/Flow Node are deferred. Contract tests must reject raw store
or provider imports in CON, raw provider-reference disclosure, changed bytes
under one idempotency identity, cross-owner/project binding, and recovery rows
or executor leases owned by CON.
