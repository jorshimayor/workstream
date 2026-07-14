# Decisions: WS-ART-001 S3-Compatible Object Storage Amendment

## D1 - v0.1 Provider

AWS S3 and Cloudflare R2 are both supported production providers through one
`S3CompatibleArtifactStore`. Initial provider selection is configuration only.
Every replica persists immutable provider profile and storage namespace; a
populated deployment changes provider only through a separate verified
maintenance migration. MinIO proves the S3-compatible contract locally and in
CI. Each AWS S3 or R2 profile becomes production-eligible only after its own
private-bucket, least-privilege, and anonymous-read-negative live proof.
LocalStorage remains a development/test adapter. Flow Node is deferred.

## D2 - Provider Boundary

The provider stores immutable bytes only. Workstream/PostgreSQL owns content
identity, bindings, references, lifecycle, receipts, audit, idempotency,
authorization evidence, and recovery state.

## D3 - ArtifactStore v2

ArtifactStore v2 accepts only a server-sealed `CommittedArtifactSource`, plus
committed-put recovery, open/range, and head. v1 provider
verify/retain/release/receipt methods are removed without compatibility aliases.
Workstream verifies by reading exact bytes.

## D4 - Required Commitments

Every untrusted source is fully prepared and server-hashed before provider I/O.
Any client commitment is checked before upload. Object keys use only that
server-computed digest and contain no product or customer identity.

## D5 - No Direct Upload

Workstream streams upload bytes. v0.1 has no presigned URL, signed upload
capability, browser-to-provider path, or client provider credential.

## D6 - Verification Before Binding

Provider acknowledgement sets the upload item to
`stored_pending_verification` and creates a pending replica, never a binding.
Celery independently reads and hashes the complete object. Only a matching
object becomes bindable.

## D7 - No Physical Deletion

v0.1 retains completed objects indefinitely. There is no provider delete,
garbage collector, automatic bucket deletion rule, legal-hold emulation, or
release API. A later initiative owns deletion policy and implementation.

## D8 - Recovery Ownership

Operator may authorize retry only for an exhausted terminal
`provider_unavailable` verification job. Celery executes under a fixed system
principal.
PostgreSQL coordinates Celery invocations with database time, executor UUID,
lease expiry, and generation fencing. Product task/review leases are unrelated.

## D9 - Closed Recovery Class

Recovery is read-only provider observation. No v0.1 recovery operation repairs
generic PostgreSQL facts, replays a provider mutation, or creates a destructive
effect.

## D10 - Durable Publication

Post-commit Celery publication is best effort, and a periodic PostgreSQL scanner
must republish pending/expired work within a configured SLA. Startup-only
scanning is insufficient.

## D11 - Observable Recovery

The recovery-attempt read route has an exact Authorization Service decision and
returns immutable source-job status plus current retry-job status. Operators
can observe eventual success or failure after retry without direct database
access.

## D12 - Shared Adapter Convention

S3CompatibleArtifactStore and LocalStorageAdapter are registered explicitly
through
`ExternalServiceAdapterFactory[ArtifactStore]`. Product services and Celery
receive the port through composition-root dependency injection. No service
locator, plugin discovery, concrete import, fallback constructor, or dual
factory exists.

## D13 - Private S3 Deployment

Production uses HTTPS and a private bucket. No public bucket, custom-domain
cache, signed URL, provider object key, endpoint, or credential appears in an
API response. R2 Object Lock and unsupported checksum extensions are not
assumed.

R2 production uses only refreshable action/path-scoped temporary credentials
served through the standard SDK container-credential endpoint contract. Chunk
02B2 implements a deployment-owned issuer as a locked, digest-pinned, non-root
infrastructure service; Chunk 02B3 connects Workstream to its exact image. The
issuer signs credentials, fixes scope server-side, and owns the parent secret
access key/signing material. Cloudflare local signing reuses
the parent access-key ID as the temporary access-key ID; Workstream may receive
that non-secret ID but never receives or stores the parent secret, signs
credentials, or implements a broker protocol. Static credentials are local/CI
MinIO only.

## D14 - Clean Cut

The `flow_node` backend value and ArtifactStore v1 contract are removed in
02A3. Pre-production data may be rebuilt. No backward compatibility is retained.

## D15 - Route Deployment Claims

Application tests prove one exact image/build. They do not prove rolling-fleet
atomicity. Public activation requires homogeneous compatible instances or an
external fleet activation barrier.

## D16 - Deferred Flow Node

`FN-ART-002` keeps a full future adapter plan. It is inactive, does not operate
Flow Node, and cannot block the S3-compatible v0.1. Later adoption requires the
same v2 conformance suite and an explicit no-fallback maintenance cutover.
