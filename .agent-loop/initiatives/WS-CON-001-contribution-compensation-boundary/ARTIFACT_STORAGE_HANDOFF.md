# Artifact Storage Handoff: WS-ART-001-CON-EVIDENCE

## Ownership and gate

This is a proposed ART-owned prerequisite before CON-09A. ART owns the chunk,
raw ArtifactStore composition, prepared-byte admission, provider I/O,
verification, ArtifactBinding/receipt persistence, retry recovery, and provider
conformance. CON owns only the deterministic contribution-evidence schema,
projection status, canonical owner facts, and disclosure guards.

Merged ART-02A2 PR #129 is a foundation, not this capability. It adds the
inactive `ArtifactPreparationService`, canonical `ArtifactScratchManager`, and
sealed `PreparedArtifact`/`CommittedArtifactSource` lifecycle while preserving
ArtifactStore v1 and all active runtime behavior. It adds no admission,
provider, verification, binding, contribution, action or permission behavior.
The named capability remains separately approved. Its exact gate is AUTH-09
fixed verifier/scanner/resolver registration, service identities and assignments
-> merged ART 02A3, 02B1, 02C1, 02C2 and 02C3 -> ART-02D hidden resource/
behavior composition -> AUTH-owned evaluator integration and activation of
`artifact.verification.execute`, `artifact.pending_work.scan` and
`artifact.put_attempt.resolve` -> `WS-ART-001-CON-EVIDENCE`. ART-02D proves and
consumes those authorities but never writes action availability; the later
contribution binding action cannot substitute for the internal executor actions.
Before ART-02D starts, D12 must transfer all eight existing ART-02D Operator
actions to `AUTH_ART_02D_OPERATOR` and the three internal actions to
`AUTH_ART_02D_INTERNAL`, or bind the same exact mappings in a separate closed
activation-custody type. Operator recovery separately requires AUTH activation
of `artifact.verification_job.retry`; the internal actions do not imply it.

## Required typed capabilities

- `ContributionEvidenceWritePort.prepare_source(request)` runs before D10 and
  before every database mutation lock. It accepts contribution/project/schema/
  logical-role identity, exact media type
  `application/vnd.workstream.contribution-evidence+json;version=1`,
  expected canonical `sha256:<hex>`, exact expected byte count, stable
  idempotency identity, and a bounded deterministic async byte source. ART's
  canonical `ArtifactPreparationService` writes the complete first pass once to
  private scratch, computes the server commitment, and rejects an unsupported
  media type, digest/size mismatch or source-limit breach before admission or
  provider I/O.
- Preparation returns only a port-defined opaque
  `PreparedContributionEvidenceWrite` async-context value with a read-only
  commitment view. The ART implementation retains the raw `PreparedArtifact`;
  the request/value contains no scratch path, descriptor,
  `ArtifactScratchManager`, `PreparedArtifact`, `CommittedArtifactSource`,
  provider reference or raw ArtifactStore and is never serialized to Celery or
  persisted.
- The caller then starts Transaction A, asks AUTH to prepare D10 and lock its
  authority rows, locks/reloads CON projection and immutable contribution rows,
  regenerates the canonical evidence facts/digest from that locked snapshot,
  and requires exact equality with the ART server commitment. Only then does
  `ContributionEvidenceWritePort.stage(prepared, request)` accept the caller
  `AsyncSession`, D10 handle and final canonical facts. ART locks admission
  state after AUTH and CON, composes its full typed context, completes the
  handle's single final AUTH evaluation, and stages the decision plus durable
  admission/put-attempt. It flushes but never commits or performs provider I/O.
- `stage` returns an opaque same-process ART continuation. The caller explicitly
  commits Transaction A and then calls
  `ContributionEvidenceWritePort.execute_after_commit(continuation)`. ART opens
  a fresh transaction to prove/claim the committed durable attempt before it
  consumes the retained `CommittedArtifactSource.stream()` exactly once and
  calls the provider outside every database transaction. No caller signal alone
  authorizes I/O.
- Commit failure, rollback, pre-commit drift, caller cancellation and exact-
  replay short-circuit close the ART-owned preparation cancellation-resistently.
  A close/release failure retains explicit ART cleanup and quota custody until
  retry succeeds. Process loss serializes no handle: the durable attempt remains
  the only authority, stale scratch cleanup reclaims abandoned custody, and the
  dispatcher/outbox replay regenerates deterministic bytes through
  `prepare_source`, rechecks the exact commitment and either resumes the same
  attempt or conflicts. Provider acknowledgement loss is resolved first by
  read-only observation; it does not replay a write. CON never performs or
  schedules scratch cleanup.
- The high-level ART flow eventually returns bounded verified
  ArtifactBinding/receipt data. Before CON marks its projection `projected`, it
  requires exact digest, byte count, media type, owner/project/logical-role,
  schema and idempotency identity equality and never receives a provider ref.
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

CON resolves a read-only server snapshot and deterministic bytes, then ART
prepares them before D10 or any mutation lock. In Transaction A, CON asks AUTH
to prepare the handle first, locks/reloads its projection/contribution rows and
recomputes the exact evidence commitment before ART locks admission and performs
the final evaluation. Missing/reused/mismatched handles, commitment mismatch or
fact drift close the opaque preparation before any durable provider attempt is
executable. CON never loads an ART row, composes ART admission facts, calls the
evaluator, instantiates raw ART preparation, or handles a committed source.

## Provider and proof boundary

LocalStorage is focused dev/test, MinIO is local/CI S3-protocol proof, AWS S3 is
production, and R2/Flow Node are deferred. Contract tests must reject raw store
or provider imports in CON, raw provider-reference disclosure, changed bytes
under one idempotency identity, cross-owner/project binding, and recovery rows
or executor leases owned by CON.
They must also prove unsupported media and expected digest/size mismatch produce
zero admission/provider calls; no AUTH/CON/ART database lock is held during the
first pass; locked fact drift closes preparation; the second-pass source is
consumed once only after a committed durable-attempt claim; Transaction-A
rollback, provider failure, cancellation and replay either release scratch or
retain explicit ART cleanup custody until retry succeeds; process loss/replay
serializes no handle; verified output matches every identity/commitment fact;
and no CON API/model/event/persistence field exposes preparation details.
ART-02A2's focused tests do not replace this capability-level conformance.
