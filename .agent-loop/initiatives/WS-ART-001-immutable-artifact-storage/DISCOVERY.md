# Discovery: WS-ART-001 S3-Compatible Object Storage Amendment

## Repository State

- `WS-ART-001-01` merged through PR #101 as `050eb15`.
- `backend/app/interfaces/artifacts.py` defines `ArtifactStore`.
- `backend/app/adapters/artifacts/local.py` implements LocalStorage.
- `backend/app/modules/artifacts/service.py` coordinates provider I/O outside
  PostgreSQL transactions.
- `backend/app/modules/artifacts/models.py` already contains upload, content,
  replica, receipt, and binding foundations.
- `backend/app/adapters/artifacts/__init__.py` has one resolver with a dormant
  `flow_node` branch that always fails.
- `backend/app/core/config.py` accepts `disabled|local|flow_node`; no
  S3-compatible object-storage configuration exists.
- `backend/pyproject.toml` has no asynchronous S3 SDK dependency.
- `docker-compose.yml` contains Postgres and Redis but no S3-compatible local
  service.

## Contract Mismatch Found

The merged v1 port makes providers own `verify`, `retain`, `release`, and
operation receipts. Those methods reflect the earlier Flow Node design and are
not the correct boundary for S3-compatible byte storage.

For v0.1:

- provider operations are immutable conditional put, open/range read, and
  head/status;
- Workstream independently verifies bytes through the read port;
- PostgreSQL owns operation receipts, bindings, reference state, and audit;
- physical delete is absent.

The v2 port must therefore replace v1 in one clean cut. No adapter alias or
compatibility shim is required because Workstream is still pre-production.

## S3-Compatible Provider Facts Used By The Plan

- AWS S3 defines the native protocol contract. Cloudflare R2 exposes a
  compatible subset and strong read-after-write, metadata, listing, and delete
  consistency through its S3 API.
- R2 supports conditional `PutObject`, `HeadObject`, `GetObject`, and range
  reads. Its documented conditional-header support does not establish atomic
  conditional multipart completion parity with AWS S3.
- Cloudflare R2 action/path-scoped temporary credentials expire and require a
  refresh lifecycle. Workstream can consume them through the standard AWS SDK
  container-credential endpoint contract. Production therefore needs an
  explicitly owned issuer; Chunk 02B2 implements that isolated service and
  Chunk 02B3 owns Workstream integration. The issuer owns the parent secret
  access key and local signing. Cloudflare reuses the
  parent access-key ID as the temporary access-key ID, but Workstream never
  receives the parent secret/signing key.
- R2 does not support S3 Object Lock through the S3 compatibility API.
- R2 does not support `x-amz-sdk-checksum-algorithm`; Workstream must not depend
  on that feature for portable SHA-256 verification.
- R2 supports `Content-MD5`, but ETag is not the Workstream SHA-256 contract.

Canonical references:

- https://developers.cloudflare.com/r2/reference/consistency/
- https://developers.cloudflare.com/r2/api/s3/api/
- https://developers.cloudflare.com/r2/api/s3/temporary-credentials/
- https://developers.cloudflare.com/r2/api/error-codes/
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html

## v0.1 Storage Algorithm

1. Prepare every untrusted source completely, compute Workstream SHA-256 and
   exact size, and reject any mismatched client commitment before provider I/O.
2. Seal that commitment with the exact second-pass stream.
3. Derive the private key
   `artifacts/sha256/<first-two-hex>/<remaining-hex>`.
4. Upload with one conditional no-overwrite `PutObject`; reject objects above
   the v0.1 512 MiB hard maximum before provider I/O.
5. Treat a precondition failure as a replay candidate, not success.
6. Head the existing object, then independently stream and hash the complete
   object before accepting it.
7. Mark the replica bindable only after SHA-256 and size match.

## Recovery Simplification

The S3-compatible object-storage design removes provider retain/release and
physical delete from v0.1.
Durable background work has one class:

- `provider_observation`: complete-object verification through fresh read;

There is no exact provider replay, destructive requeue, or ambiguous logical
provider effect in v0.1 recovery.

Operator authorization creates a reason-bound recovery envelope and linked
verification job. The job is the sole Celery execution owner. PostgreSQL
coordinates its invocations with a fixed lease, fresh executor UUID, and
generation fence. A periodic PostgreSQL scanner guarantees that a committed
job is eventually published even if the first broker call fails.

## Security Boundaries

- Authorization Service owns product decisions.
- S3 credentials authorize transport only and never imply product authority.
- Credentials come from deployment secret injection and never enter Postgres,
  Redis, Celery payloads, logs, receipts, or API responses.
- Product services consume `ArtifactStore` by dependency injection and never
  import the S3 implementation.
- The S3 endpoint is trusted configuration. Production requires HTTPS and a
  private bucket; localhost HTTP is allowed only in local/test MinIO.
- No public bucket, custom-domain cache, or client-visible object key is used.
- Runtime credentials are bucket/prefix/action scoped and cannot delete, list,
  copy, or administer provider configuration.
- Production release evidence proves AWS public-access controls or R2 public-
  domain disablement and an anonymous-read denial.

## Deferred Flow Node

The previous Flow Node analysis is preserved on branch
`codex/ws-art-001-fn01-isolation-amendment`. A new deferred initiative will
retain the provider-conformance, focused-service, adapter, and migration plan.
It cannot block or modify v0.1 S3-compatible object-storage work.
