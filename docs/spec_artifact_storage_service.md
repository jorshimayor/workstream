# Workstream Immutable Artifact Storage Specification

## Status And Scope

This is the canonical target contract for WS-ART-001 under ADR 0013. Runtime
schemas change only when their owning implementation chunk merges.

The specification covers provider-neutral immutable byte storage, independent
verification, guide/submission/checker binding, Operator observability, and
durable recovery. It does not implement review decisions, contribution,
payment, reputation, semantic search, public publication, physical deletion,
or Flow Node.

## Architecture

```text
FastAPI and Celery composition roots
-> ExternalServiceAdapterFactory[ArtifactStore]
-> ArtifactStore v2
   -> LocalStorageAdapter
   -> S3CompatibleArtifactStore
      -> MinIO integration
      -> AWS S3 production option
      -> Cloudflare R2 production option
-> ArtifactService
-> PostgreSQL records, bindings, receipts, audit, jobs, and recovery
```

Initial provider selection changes only composition-root configuration.
Product services never import a concrete storage adapter. Replicas persist
provider profile and storage namespace, so changing a populated deployment
requires an explicit verified migration rather than a hot endpoint switch.

## Ownership

| Concern | Owner |
|---|---|
| authorization and exact resource permission | Authorization Service |
| content identity, product provenance, binding, lifecycle, audit | Workstream |
| verification result and recovery coordination | Workstream/PostgreSQL |
| private immutable bytes and protocol observations | configured object store |
| review packet and reviewer evidence aggregates | WS-REV using artifact bindings |

Provider credentials grant transport access only. They are not actor identity,
product role, product authorization, or proof of stored content.

## Canonical Records

### ArtifactUploadSession

Fields include id, actor, project, optional task/guide, permitted logical roles,
state, item/byte limits and totals, sealed artifact-set hash, expiry, consumed
timestamp, database timestamps, and CAS version.

States are `open`, `sealed`, `consumed`, `expired`, and `cancelled`.

### ArtifactUploadItem

One per staged object. Fields include session, logical role, normalized display
name, expected SHA-256, expected byte count, canonical request digest, scoped
idempotency key, CAS version, content ID, failure code, and timestamps.

States are `reserved`, `uploading`, `replay_required`,
`stored_pending_verification`, `ready`, `failed`, and `cancelled`.

### ArtifactContent

An immutable provider-neutral fact identified by canonical SHA-256 and exact
byte count. It also records detected media type and creation time. A display
name is presentation metadata and is not content identity.

### ArtifactReplica

One content copy in one adapter/provider. Fields include content ID, adapter
name, immutable provider profile, immutable storage-namespace ID, opaque
provider object reference, verification state, availability state, integrity
state, latest verification receipt, and observation timestamps.

Replica states are independent closed fields:

```text
verification_state = pending | verified | missing | integrity_mismatch
availability_state = unknown | available | unavailable
integrity_state    = unknown | valid | invalid
```

Transaction B sets the upload item to `stored_pending_verification` and creates
the replica as `pending/unknown/unknown`. A matching complete read sets the item
to `ready` and replica to `verified/available/valid`. A provider-unavailable or
conflict job result does not fabricate a replica observation.

A confirmed absent object sets the replica to
`missing/unavailable/unknown`. Before any binding exists, and only while the
original upload session/item remains eligible, an exact replay by the original
authorized uploader may move that same replica to `pending/unknown/unknown`,
set the item back to `stored_pending_verification`, append a new operation
receipt, and create a new verification job. After a binding exists, the missing
replica is terminal and cannot return to pending in v0.1. A digest/size mismatch
sets the replica to `integrity_mismatch/available/invalid`, fails the pre-binding
item when applicable, and quarantines access; it never returns to pending.

Provider references are internal. They never appear in contributor, reviewer,
project-owner, or public API responses.

### ArtifactBinding

An immutable relation from content to project, resource type/id, logical role,
actor/service attribution, scope version, timestamp, and optional superseded
binding. Upload staging is not a binding. Replacement appends a new binding and
preserves history.

### ArtifactOperationReceipt

Append-only Workstream evidence for one operation identity: adapter,
operation, idempotency key, request digest, bounded provider observation,
outcome, correlation/attempt references, and provider/database timestamps.
Credentials, signed headers, endpoints, raw provider responses, and product
secrets are forbidden.

### ArtifactVerificationJob

A durable complete-object observation request. Fields include content/replica,
expected digest/size, status, attempt count, publication timestamps, next run,
automatic attempt limit, retry-exhausted timestamp, executor UUID, execution
lease expiry, execution generation, terminal error, immutable receipt
reference, and CAS version.

Statuses are:

```text
pending
running
verified
missing
integrity_mismatch
provider_unavailable
conflict
```

Only `pending`, expired `running`, and non-exhausted `provider_unavailable` jobs
may be re-published automatically. `verified`, `missing`,
`integrity_mismatch`, and `conflict` are terminal and cannot be retried through
the Operator route. Only an exhausted `provider_unavailable` job is eligible
for an authorized recovery attempt that creates a new job. Every other status
fails closed without creating an attempt, job, or audit success record.

### ArtifactRecoveryAttempt

A reason-bound Operator authorization/audit envelope to retry one verification.
Fields include requester actor/profile, authorization decision evidence,
reason, recovery class, target type/id, `source_verification_job_id`,
`retry_verification_job_id`, optional `parent_recovery_attempt_id`, client
idempotency key, canonical request digest, status, terminal result, audit IDs,
and timestamps. It has no Celery executor, lease, or generation; the retry
`ArtifactVerificationJob` is the sole execution owner.

Statuses are `requested`, `succeeded`, and `failed`. One eligible exhausted
`provider_unavailable` source has exactly zero or one recovery attempt across
its lifetime, enforced by a unique source-job constraint. The retry job's
terminal transaction updates the envelope and terminal audit. `verified` maps
to `succeeded`; `provider_unavailable`, `missing`, `integrity_mismatch`, and
`conflict` map to `failed` with the exact terminal code. The source job never
changes. A subsequently exhausted retry job may be the source of a new chained
attempt. The earlier source can never be reused, including after the first
attempt succeeds or fails and regardless of a different idempotency key.

## ArtifactStore v2 Port

The asynchronous port is:

```text
put(source: CommittedArtifactSource)
recover_put(commitment: ArtifactCommitment)
open(provider_object_ref, byte_range?)
head(provider_object_ref)
```

`CommittedArtifactSource` contains the server-computed canonical digest, exact
size, media type, and bounded second-pass stream as one sealed value. Only the
Workstream preparation service constructs it; callers cannot pair an arbitrary
stream with an arbitrary digest. `put` and `recover_put` return opaque provider
references and bounded protocol observations. `open` returns a bounded
asynchronous byte stream. `head` returns
existence, exact provider-reported size when available, media type when
available, and bounded metadata needed for protocol handling.

The port has no `verify`, `retain`, `release`, delete, list, signed URL, search,
product binding, SQLAlchemy, audit, authorization, or provider-receipt lookup.
Workstream verifies using `open` and owns receipts in PostgreSQL.

### Range Semantics

A byte range has zero-based offset and optional nonnegative length with an
exclusive end. Offset equal to object size returns an empty stream. Offset past
the end is invalid. A partial read never establishes complete-object integrity.

### Stable Adapter Errors

The port maps provider behavior to stable typed errors:

```text
artifact_storage_unavailable
artifact_object_missing
artifact_precondition_failed
artifact_input_mismatch
artifact_integrity_failure
artifact_range_invalid
artifact_operation_conflict
artifact_limit_exceeded
```

No error exposes a bucket, provider key, endpoint, credential, signed header,
or raw provider body.

## S3-Compatible Adapter

The concrete production adapter is named `S3CompatibleArtifactStore`. It works
with AWS S3 and Cloudflare R2. MinIO proves the same protocol contract in local
integration tests and CI.

Configuration includes:

- provider profile `aws_s3`, `cloudflare_r2`, or `minio`;
- explicit AWS region, R2 region value `auto`, or configured MinIO region;
- optional endpoint URL for native AWS S3 and required endpoint for R2/MinIO;
- private bucket and private prefix;
- addressing style;
- credential mode, optional access-key ID/secret/session token, and no resolved
  credential persistence;
- connect/read/write/pool timeouts;
- total verification deadline and maximum buffered bytes.

Backend is exactly `disabled`, `local`, or `s3_compatible`. Credential modes
are `aws_workload_identity`, `container_temporary`, and `local_static`. AWS S3
production uses `aws_workload_identity`; R2 production uses
`container_temporary`; MinIO supports `local_static` only in local/CI.
Production static credentials are forbidden.

An AWS S3 deployment selects exactly one workload-identity method:
`assume-role-with-web-identity`, `container-role`, or `iam-role`. Workstream
validates the configuration required by the selected method, constrains the
pinned botocore credential resolver to that provider before any provider is
loaded, and verifies the resolved method. Explicit credentials, environment
access keys, shared credential/config files, credential processes, login/SSO,
legacy EC2/Boto sources, and every unselected workload provider are rejected.
Tests poison every nonselected source and prove that it is never read, executed,
or contacted. This is an allowlisted workload-identity contract, not authority
to use the ambient SDK default chain.

Chunk 02B1 pins the async S3 SDK pair to `aiobotocore==3.7.0` and
`botocore==1.43.0`. An SDK upgrade is a reviewed contract change because
credential-provider precedence and refresh windows are operational behavior.

R2 uses the AWS SDK standard container-credential endpoint contract through
`AWS_CONTAINER_CREDENTIALS_FULL_URI` and
`AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE`. Workstream permits only a pinned
loopback URI and reads the bearer token from a private deployment-mounted file.
A deployment-owned issuer implemented in Chunk 02B2 is an independently
packaged, locked, digest-pinned, non-root service in this repository. Chunk 02B3
connects Workstream to that exact release image through the standard endpoint.
The issuer locally signs R2 temporary credentials and fixes account, bucket,
prefix, exact actions (`PutObject`,
`HeadObject`, `GetObject`), minimum/maximum TTL, and audience server-side. The
sidecar owns the parent secret access key/signing material; Cloudflare local
signing reuses the parent access-key ID as the temporary access-key ID. The
Workstream process may
therefore receive that non-secret ID with the derived temporary secret access
key and session token, but it never receives the parent secret/signing key and
cannot ask to widen scope. The minimum issued TTL exceeds the pinned SDK
advisory refresh window plus request and scheduling margin. Refresh is
single-flight. An advisory-window refresh failure may continue with the cached
unexpired set; a mandatory-
window refresh failure propagates and blocks provider I/O before nominal expiry.
Expired credentials are never used, and Workstream performs no per-request
sidecar liveness probe. Endpoint redirection, a non-loopback URI, token
rejection, malformed response, timeout, audience mismatch, or required refresh
failure maps to `artifact_storage_unavailable` according to those SDK windows.
Workstream never extends credential validity.

The parent token is scoped to the exact Cloudflare account and artifact bucket,
has only the narrowest non-admin permission capable of minting the fixed child
credentials, and cannot address another bucket. Rotation and revocation are
tested operational contracts. Compose uses
`network_mode: service:<workstream-service>` and Kubernetes places both
containers in the same Pod. The issuer binds only `127.0.0.1`; bridge-network
DNS, a separate issuer network namespace, and host/public ports are rejected.

The issuer is not a Workstream product service. It has no product routes,
database access, actor authority, request-selected scope, public/host port, or
outbound-network requirement. Deployment injects parent material and the bearer
token through separate private read-only reloadable files. The issuer runs
non-root, records only secret-free issuance audit, and has explicit image
provenance, health, rotation, timeout, availability, and live private-R2 proof.
The parent secret and signing code never enter `backend/app/`.

R2 mode does not accept the SDK's ambient provider chain as authority. Startup
rejects explicit/static credential parameters, `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, session/security-token variables, role/web-identity or
SSO/profile selection, `login_session`, credential-process configuration,
shared credential/config files, `AWS_CREDENTIAL_FILE` and the legacy
`OriginalEC2Provider`, login-token cache access, Boto2 configuration, instance
metadata,
`AWS_CONTAINER_CREDENTIALS_RELATIVE_URI`, and direct
`AWS_CONTAINER_AUTHORIZATION_TOKEN`. Deployment supplies empty isolated config
paths and disables instance metadata. Workstream validates that
`AWS_CONTAINER_CREDENTIALS_FULL_URI` exactly equals the configured pinned
loopback sidecar URI and that `AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE` exactly
equals the configured private mounted token-file path. After loading, it also
verifies that the resolved credential method is the container provider. Any
endpoint, authorization source, or method mismatch fails startup before
artifact I/O. Tests poison every competing variable/profile and assert the
actual endpoint and authorization source, not only `credentials.method`.

The pinned resolver inventory is explicit: `env`, `assume-role`,
`assume-role-with-web-identity`, `sso`, `shared-credentials-file`, `login`,
`custom-process`, `config-file`, `ec2-credentials-file`, `boto-config`,
`container-role`, and `iam-role`. After validating the forbidden configuration
above and before credential loading, R2 composition constrains the resolver to
the single `container-role` provider and fails if the pinned inventory/order is
not the reviewed one. Tests instrument every competing provider and prove no
file, process, cache, metadata endpoint, or network source is accessed before
failure or successful container resolution.

Tests cover advisory failure with cached continuation, mandatory failure before
expiry, expiry, rotation, concurrent refresh, replay, scope escalation,
parent-secret/signing-key absence, correct reuse of the non-secret access-key
ID, and error/log/object-graph redaction. No bespoke
Workstream broker client or product route exists.

Production rejects `local`, plaintext HTTP, loopback/local endpoints, invalid
credential-mode/profile combinations, and unknown provider profiles.
Validation errors, resolved credentials, and exception object graphs must not
retain secrets.

### Object Identity

Production writes require a sealed `CommittedArtifactSource` before provider
I/O. The object key uses its server-computed canonical digest:

```text
<private-prefix>/sha256/<hex[0:2]>/<hex[2:]>
```

The key contains no actor, customer, project, task, filename, media type, or
secret. Workstream stores it as an opaque provider reference.

### Conditional Write

The adapter uses conditional no-overwrite semantics. A precondition failure is
an exact replay candidate, not success. The adapter heads and then opens the
existing object; Workstream independently verifies it before reuse.

v0.1 uses conditional single-request `PutObject` only and enforces
`expected_size <= 512 MiB` before I/O. Multipart upload, CopyObject publication,
and provider-specific finalization algorithms are deferred. A future multipart
initiative must prove one atomic no-overwrite algorithm independently against
AWS S3 and R2 before changing this limit.

The runtime principal is restricted to the exact bucket and completed-object
prefix and only the actions required for conditional put, head, and get. It has
no delete, copy, list, bucket administration, lifecycle mutation, public-access
mutation, or cross-prefix permission. AWS uses a least-privilege role/policy;
R2 uses path- and action-scoped temporary credentials.

Production activation requires provider-specific deployment proof. AWS proof
checks effective Block Public Access plus policy/ACL state. R2 proof checks that
`r2.dev` is disabled and no public custom domain is attached. Both profiles run
an anonymous-read negative test against a known object.

The same deployment proof reads the provider lifecycle configuration and fails
activation when any enabled rule can delete/expire a completed object under the
configured private prefix. AWS inspection covers `Expiration` and
`NoncurrentVersionExpiration` for every rule whose filter can intersect the
prefix. R2 inspection covers `deleteObjectsTransition` for every enabled rule
whose prefix can intersect it. Storage-class transitions and abort-incomplete-
multipart rules are not completed-object deletion. These checks use a separate
read-only deployment identity; the runtime principal is not granted bucket
administration merely to inspect policy or lifecycle configuration.

AWS S3 and R2 are peer production options, not primary/fallback providers. Each
configuration profile remains inactive until its own live proof succeeds; a
successful AWS proof never activates R2, and a successful R2 proof never
activates AWS.

### Integrity Rules

Workstream computes SHA-256 and byte count while ingesting and while performing
the independent verification read. ETag, Content-MD5, provider checksum
headers, and user metadata are not canonical integrity facts.

AWS S3 and R2 have separate configuration/live-smoke profiles because their
supported S3 API subsets differ. The shared adapter uses only the intersection
proved by conformance tests.

## LocalStorage Adapter

LocalStorage implements the same v2 port and conformance vectors. It uses a
private configured root, opaque content-derived paths, exclusive no-overwrite
publication, bounded off-event-loop file I/O, no-follow path handling, private
permissions, full read verification, and sanitized failures.

The v1 local provider metadata for retain/release/provider receipts is removed
in the v2 clean cut. No compatibility adapter or dual format remains.

## Ingest Choreography

1. Authorization Service permits the exact upload action and resource.
2. Workstream writes the complete untrusted source to bounded private scratch,
   computes digest/size, and rejects a mismatched client commitment before any
   provider call.
3. Transaction A reserves the item and commits the server-computed digest,
   size, media type, operation identity, canonical request digest, limits, and
   CAS.
4. Workstream passes the sealed `CommittedArtifactSource` to the adapter outside
   the transaction.
5. The adapter conditionally stores or resolves an exact replay candidate.
6. Transaction B validates the reservation/CAS, records content, replica, and
   operation receipt, sets the item to `stored_pending_verification`, and sets
   the replica to `pending/unknown/unknown`.
7. The transaction creates an outbox/publication obligation for one
   verification job.
8. Celery independently opens and hashes the complete object.
9. A fenced transaction records the immutable verification receipt and marks
   the replica bindable only when digest and size match.

No provider call occurs inside a PostgreSQL transaction. No product binding is
created before independent verification.

### Prepared Byte Sources

Contributor uploads, fetched guide material, and generated checker logs/outputs
do not have a trusted server commitment before production. They all use a
bounded two-pass `PreparedArtifact`
boundary: first write to a private process-owned ephemeral scratch file while
hashing/counting and enforcing the same 512 MiB per-object limit; close the
file; compare any supplied commitment; then seal the computed commitment and
second-pass stream together as `CommittedArtifactSource`.

The scratch manager uses one private dedicated root and a cross-process locked
reservation ledger. Because the first pass does not know actual size, every
preparation atomically reserves the full 512 MiB per-object maximum before file
creation. Configuration fixes aggregate reserved bytes, file count, preparation
concurrency, reservation TTL, and a minimum-free-space floor below the volume
quota. Exhaustion or `ENOSPC` fails with a stable infrastructure error and no
provider call. One total preparation-plus-upload deadline is strictly shorter
than the reservation TTL by a cleanup margin; v0.1 has no scratch heartbeat or
lease renewal. Scratch
files use private permissions, no-follow path handling, random opaque names,
and are never authoritative or referenced by product records. The owning job
releases its reservation after in-flight I/O closes. The named periodic Celery
Beat cleanup task removes a reservation/file only while holding the ledger lock and
only after its database-independent wall-clock expiry; a conforming live
operation must already have cancelled before that point. Startup performs the
same idempotent cleanup. Chunk 02A2 implements the cleanup mechanics without
activating them. Chunk 02A3 wires API-startup cleanup and one named Celery Beat
task as the periodic owner. Tests cover concurrent processes, full-max quota
boundaries, low disk, slow active work versus cleanup, deadline cancellation,
crash, stale cleanup, and symlink/non-regular entries.

The same canonical `ArtifactScratchManager` also owns checker-workspace
allocations. Authoritative pre-submit introduces one authorized artifact
materializer, and post-submit reuses it without a second workspace manager.
The materializer accepts only authorized Workstream bindings, reserves the
complete workspace against the same aggregate ledger and quotas, streams exact
provider bytes into private no-follow paths, and recomputes SHA-256 and byte
count for every file. Any mismatch becomes an artifact incident before checker
execution. After successful verification, files are sealed read-only before the
checker receives an opaque workspace handle. Success, failure, cancellation,
and crash/stale cleanup use the same API-startup and Celery Beat ownership; a
checker never receives provider references, credentials, or a writable verified
input.

After ambiguous provider completion, recovery first calls `recover_put` with
the persisted commitment; it does not regenerate bytes speculatively. If no
object exists and the owning durable source can be regenerated, Workstream
prepares it again and compares the complete digest/size. Identical bytes may
replay the original operation. Changed bytes abandon the old operation and
create a new source snapshot/setup generation or checker-run attempt; they
never reuse the old operation, snapshot, or binding identity. A generator that
cannot reproduce exact bytes fails its old infrastructure attempt instead of
fabricating replay. Bytes are never placed in PostgreSQL, Redis, Celery
payloads, logs, or audit.

## Durable Publication And Execution

Post-commit Celery publication is an optimization. A periodic PostgreSQL
scanner is the durable guarantee. It finds pending jobs whose publication
deadline passed and running jobs whose execution lease expired, then publishes
them duplicate-safely within a configured SLA.

Celery acquisition uses the PostgreSQL clock and atomically writes a fresh
executor UUID, lease expiry, and incremented execution generation. A configured
end-to-end verification deadline covers the complete stream, not only socket
inactivity. It is derived from maximum object size and minimum supported
throughput and must be shorter than the lease by a result-persistence margin.
The execution cancels at that deadline even when bytes continue arriving. v0.1
uses no heartbeat.

Terminal writes require the same executor UUID and generation. A zero-row
update means the execution is stale; it writes no terminal state or audit event.

## Verification Result Matrix

| Observation | Job result | Replica effect | Retry meaning |
|---|---|---|---|
| complete bytes match digest and size | `verified` | bindable, available, valid | none |
| object absent after bounded consistency/retry policy | `missing` | `missing/unavailable/unknown` | terminal after binding; before binding exact same-item replay resets to `pending/unknown/unknown` and creates a new job |
| size or digest mismatch | `integrity_mismatch` | `integrity_mismatch/available/invalid`, quarantined | unrecoverable in v0.1; security incident and no overwrite |
| timeout/throttle/retryable provider failure | `provider_unavailable` | unchanged/not bindable | bounded automatic retry, then Operator |
| request/identity/CAS contradiction | `conflict` | unchanged/not bindable | security/data incident; no generic repair |
| stale executor/generation | no terminal write | no effect | current execution owns outcome |

Storage failures never become contributor checker findings, review decisions,
contribution records, payment exposure, or reputation events.

## Operator Recovery

The recovery class is closed:

```text
provider_observation
```

`provider_observation` creates a fresh verification job. It cannot write a
`verified` result without reading the complete object. Contradictory PostgreSQL
facts yield terminal `conflict` and an incident; v0.1 exposes no generic record-
repair operation. Recovery does not mutate, overwrite, retain, release, or
delete provider bytes.

The retry command accepts only a terminal `provider_unavailable` job whose
automatic attempt budget is exhausted. It rejects `pending`, `running`,
`verified`, `missing`, `integrity_mismatch`, `conflict`, and a non-exhausted
provider-unavailable job. Rejection tests prove that no recovery attempt, new
job, or initiation-success audit is created for those states.

Each verification job may be the source of at most one recovery attempt for its
entire lifetime. Exact request replay returns that attempt. A different key,
post-terminal ancestor reuse, or concurrent second request against the same
source conflicts without creating an attempt, job, or audit effect. Further
recovery must target the immediate retry job, and only when that job independently
exhausts `provider_unavailable`.

Operator authorizes recovery and provides a bounded non-empty reason. Celery
executes under the fixed `workstream.artifact.verifier` service principal.
The requester is never presented to the provider as execution authority.

### Recovery API Contract

These internal Operator APIs are introduced before product cutovers:

```text
GET  /api/v1/operator/artifacts/bindings?resource_type={type}&resource_id={id}
GET  /api/v1/operator/artifacts/contents/{content_id}/replicas
GET  /api/v1/operator/artifacts/replicas/{replica_id}/receipts
GET  /api/v1/operator/artifacts/verification-jobs/{job_id}
POST /api/v1/operator/artifacts/verification-jobs/{job_id}/retry
GET  /api/v1/operator/artifacts/recovery-attempts/{attempt_id}
GET  /api/v1/operator/artifacts/audit-events
```

Every route requires the exact Authorization Service action/resource decision
defined by the owning chunk. A retry request supplies a reason, client
idempotency key, and expected source-job CAS version. The transaction creates
the recovery envelope and retry verification job and returns `202` with
attempt, source-job, and retry-job IDs. Idempotency scope is requester, source
job, recovery class, and client key; a canonical request digest makes exact
replay return the original IDs and altered replay conflict without side
effects. The recovery-attempt GET returns its own status, immutable source-job
status, current retry-job status, terminal code, chain identity, and audit IDs
so no database inspection is required.

The binding lookup is the discovery entry point from a known project, guide,
task, submission, checker run, or future review resource. It requires exact
resource scope, supports an optional logical-role filter, and returns bounded
binding/content summaries plus replica and current verification-job IDs. Audit
listing supports exact project/resource/content/job/attempt filters and returns
those stable Workstream IDs.

No route returns provider object references, bucket/key, endpoint, credentials,
signed URLs, or raw provider responses. Pagination is bounded and stable.

## Exact Artifact-Set Admission

Sealing generates `ArtifactSetManifest` from trusted server facts. Entries are
deterministically ordered and commit to logical role, normalized display name,
content ID, SHA-256, and byte count. Exact duplicates are rejected.

The pre-submit admission binds the artifact-set hash to actor, task, effective
project policy, project pre-submit checker, summary, contributor attestation,
expiry, and upload session. Submission creation locks and consumes that exact
admission and session in one transaction. A changed field or changed artifact
requires a new precheck.

Artifact reads during authoritative pre-submit have a bounded Workstream-owned
transient retry budget. Exhaustion returns:

```text
HTTP 503
code = pre_submission_infrastructure_unavailable
```

This is infrastructure state, not a checker result, review decision, or
contributor outcome. It creates no admission, submission, checker finding,
payment, contribution, or reputation effect. The sealed upload session and
artifact set remain sealed, unconsumed, and reusable until normal expiry; only
the infrastructure attempt and audit are persisted. Idempotency scope is actor,
task, sealed session/artifact set, locked context, client key, and canonical
request digest. Exact replay continues or returns the same attempt, changed
replay conflicts, and concurrent replay cannot create duplicate attempts or
admissions. After retry-after or storage recovery, the contributor continues
that same exact attempt without Project Manager or Operator approval.

Before authoritative pre-submit invokes the checker, the shared authorized
materializer reads every bound object into a canonical scratch-manager
workspace, recomputes its SHA-256 and byte count, compares them with the binding,
and seals verified files read-only. The checker executes only that verified
workspace. A mismatch is an artifact incident; quota exhaustion or transient
read failure is infrastructure state and creates no checker result or admission.

After cutover, the public request is:

```json
{
  "summary": "...",
  "contributor_attestation": "...",
  "upload_session_id": "..."
}
```

Clients do not provide package URI, provider reference, canonical digest
manifest, artifact-set hash, or server content IDs.

### Product Upload APIs

```text
POST   /api/v1/tasks/{task_id}/artifact-upload-sessions
GET    /api/v1/artifact-upload-sessions/{session_id}
POST   /api/v1/artifact-upload-sessions/{session_id}/artifacts
POST   /api/v1/artifact-upload-sessions/{session_id}/seal
DELETE /api/v1/artifact-upload-sessions/{session_id}
POST   /api/v1/tasks/{task_id}/submission-precheck
POST   /api/v1/tasks/{task_id}/submissions
```

The upload APIs return Workstream IDs, canonical SHA-256, byte count, detected
media type, verification/readiness, and bounded artifact summaries. They never
return provider internals. Session cancellation is logical staging cleanup; it
does not physically delete a completed content-addressed object.

Every ID-addressed session read or mutation uses concealed deny/not-found
behavior. Cross-actor, cross-project, revoked, expired, cancelled, consumed,
and random IDs cannot be used as an existence oracle.

## Guide And Checker Binding

Guide-source ingestion stores each source item as immutable artifact content.
`GuideSourceSnapshot` binds its canonical manifest to those content records.
Sufficiency and policy-derivation agents read through an authorized Workstream
artifact reader, never direct provider URLs.

When guide-source verification fails transiently, artifact recovery success
automatically re-publishes the same persisted `ProjectSetupRun` continuation
only when project, guide version, source snapshot ID/hash, and setup generation
still match. There is no Project Manager setup-resume command in v0.1:
Workstream owns this infrastructure continuation. An Operator may authorize
artifact verification recovery but does not approve guide sufficiency or
policy. Recovery authorization and automatic setup continuation write separate
audit events. A changed snapshot creates a new setup run and cannot resume the
old one.

`CheckerInputSnapshot` references binding/content IDs, digest, byte count,
artifact-set hash, locked policy/checker identities, and checker implementation
identity. Pre-submit and post-submit consume the same sealed artifact-set hash.
Checker logs and generated outputs become artifact bindings.

Transient post-submit storage unavailability leaves the task in
`evaluation_pending` and uses checker retry infrastructure. A provider object
confirmed missing after its content was bound is a terminal artifact incident
in v0.1: the immutable binding remains, evaluation stays blocked, and no
contributor, Project Manager, or Operator route may replace or rebind the
bytes. A future separately approved backup/replica-repair initiative may
restore the exact content from an independently verified copy. Integrity
mismatch on an existing content-addressed key is likewise unrecoverable in
v0.1: the replica remains quarantined, evaluation stays blocked, and a security
incident is required. Recovery never overwrites the poisoned key.

Pre-submit and post-submit outage continuation are distinct contracts. The
former preserves a sealed, unconsumed attempt and returns the stable 503 above;
the latter preserves `evaluation_pending` and uses checker retry
infrastructure. Neither path fabricates `accept`, `needs_revision`, or `reject`.

## Authorization Dependencies

Artifact mechanics may be implemented independently, but no production route,
adapter dispatch, background provider read, binding, retry, or recovery becomes
active until the Authorization Service owns the exact action/resource decision
and the internal service-principal contract.

Provider credentials cannot satisfy this dependency. Development shortcuts are
forbidden in production.

## Migration And Removal

Implementation is a clean cut:

- committed-source preparation and LocalStorage private refactoring land first
  without changing the active v1 port;
- ArtifactStore v1 methods, active callers, LocalStorage's public adapter
  surface, and schema then migrate atomically in the v2 clean-cut chunk;
- `flow_node` is removed from configuration without an alias;
- obsolete caller-owned URI/hash and storage-scheme fields are removed in
  their owning guide/submission cutovers;
- the misleading submission `/finalize` repair route is replaced by
  `POST /api/v1/operator/submissions/{submission_id}/pre-review-gate-repair`;
  normal submission creation still enters evaluation automatically;
- no dual write, nullable shadow field, fake verified backfill, fallback
  adapter, compatibility constructor, or second factory remains;
- pre-production data is rebuilt when authoritative bytes are unavailable.

Every migration proves fresh upgrade, prior-head upgrade, populated-state
preservation or explicit refusal, empty downgrade/re-upgrade, and no artifact
bytes in PostgreSQL.

## Verification Strategy

- one conformance suite runs against LocalStorage and real MinIO;
- separate secret-free live smoke profiles prove AWS S3 and R2 configuration;
- integration tests use real S3-compatible API calls, not monkeypatching;
- concurrent puts cannot overwrite existing bytes;
- acknowledgement loss, exact replay, oversized-object refusal, truncation,
  changed bytes, missing object, range reads, timeout, throttle, and provider
  differences are covered;
- credential-sidecar failure, periodic re-publication, duplicate Celery delivery, expired
  execution lease, a continuously progressing stream that exceeds the total
  deadline, stale finalization, and Operator retry are covered;
- least-privilege runtime credentials, denied delete/list/admin actions, AWS
  public-access controls, R2 public-domain controls, and anonymous-read denial
  are covered by provider-specific deployment proof;
- cross-resource authorization and secret non-retention are covered;
- new or materially changed backend subsystems remain at least 90 percent
  covered and repository coverage does not fall below the current baseline;
- backend CI runs the single exact full-suite 78 percent repository command,
  then applies stable dedicated 90 percent `coverage report` steps separately
  to every accumulated changed subsystem using the full suite's coverage data.
  This avoids freezing partial test lists while later chunks expand a package;
- independently executable services/examples retain their own exact 90 percent
  test-and-coverage steps. `ARTIFACT_COVERAGE_PHASE` advances only after Agent
  Gates proves the expected unconditional steps occur exactly once in the
  backend `test` job, after the full-suite test step, with no
  `continue-on-error`, condition, shell, environment, working-directory, raw-
  text, or source-only bypass;
- final proof uses real HTTP APIs and visible jobs/recovery, not direct database
  inspection.

Application route tests prove one exact application image. They do not claim
rolling-fleet atomicity. Public activation requires homogeneous compatible
instances or an external deployment barrier.

## Deferred Flow Node Adapter

`FN-ART-002` is a separate inactive initiative. It may later implement the same
ArtifactStore v2 port and conformance vectors. It cannot change product records
or services, cannot introduce a runtime fallback, and requires an explicit
maintenance cutover after v0.1 is proven.

## Provider Contract References

- [Amazon S3 conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html)
- [Amazon S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
- [Cloudflare R2 S3 API compatibility](https://developers.cloudflare.com/r2/api/s3/api/)
- [Cloudflare R2 temporary credentials](https://developers.cloudflare.com/r2/api/s3/temporary-credentials/)
- [Cloudflare R2 public bucket controls](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [Cloudflare R2 object lifecycle rules](https://developers.cloudflare.com/r2/buckets/object-lifecycles/)
