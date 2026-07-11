# Discovery: WS-ART-001 Immutable Artifact Storage

## Repositories Inspected

- Workstream `main` after PR #93, merge commit `772af1d`.
- Flow Node `main` at `2399eb4`.

## Workstream Current Behavior

- `backend/app/modules/projects/models.py` stores
  `GuideSourceSnapshot`/`GuideSourceSnapshotItem` metadata and optional
  `content_cid`; it does not ingest source bytes.
- `ProjectService._create_guide_source_snapshot_model` builds a canonical JSON
  manifest from supplied material and stores it in Postgres.
- `SubmissionCreate` accepts `package_uri`, `package_hash`,
  `artifact_hash_manifest`, and evidence URIs.
- `TaskService.create_submission` persists those declarations directly.
- `CheckerService._build_checker_run` copies declared hashes; checker workers
  have no artifact adapter.
- `checker.runner._evidence_integrity_outcome` validates declaration shape, not
  stored bytes.
- No artifact module, storage port, storage adapter, outbox, provider receipt,
  or authorized artifact retrieval API exists.

## Flow Node Current Behavior

Useful primitives:

- `ContentId`: CIDv1 with SHA-256 and verification.
- `BlockStore`: RocksDB immutable blocks and single-block pin state.
- `DagBuilder`/`DagReader`: chunking, DAG-CBOR manifests, and reconstruction.
- `storage::content::ContentService`: real publish and fetch behavior.
- local/network providers and low-level round-trip tests.

Disconnected runtime:

- REST uses `storage::content::api_service::ContentService`, a second class with
  the same name that only writes metadata.
- `POST /api/v1/content/publish` does not store bytes in the block store.
- `GET /api/v1/content/{cid}` returns metadata, not bytes.
- No verify, recursive pin, receipt, provenance, or Workstream artifact routes.
- Existing REST routes are public; the JWT extractor is unused.
- `Node`/`AppState` do not share the real block store/content service used by
  the network manager.
- Pinning one root block does not protect child chunks.
- Search can turn provider failure into an empty success response.

## Existing Contracts To Reconcile

- ADR 0008 requires an object-storage abstraction and rejects local paths as
  business contracts.
- `docs/reference_specs/WS-IMP-001...` defines `ArtifactStorePort`,
  `SemanticIndexPort`, `ArtifactBinding`, Flow Node failure semantics, and local
  adapter parity, but is archival input rather than the canonical runtime spec.
- The updated WS-AUTH baseline requires Workstream-local authorization and
  explicit service principals; human tokens are not provider credentials.

## Data And Contract Gaps

- Caller-declared hashes are not authoritative; some tests use invalid tokens
  such as `sha256:package-v1`.
- `package_uri`, evidence `uri`, `content_cid`, and hash-manifest entries overlap
  without one artifact identity.
- Evidence rows use `delete-orphan`; provider retention must not inherit that
  deletion behavior.
- No checker input snapshot binds a run to retrieved bytes.
- Checker logs/results have no artifact identity.
- Review packet/evidence models are not implemented yet.
- No storage environment configuration rejects local storage in production.

## Security And Operational Risks

- Flow Node routes are unauthenticated.
- Flow Node DAG publishing announces to DHT/GossipSub by default; evaluation
  evidence must remain private.
- Manifest CID and original-byte digest have different meanings.
- Manifest timestamps can make otherwise identical manifests differ.
- Provider failure must not become “no results” or contributor failure.
- External calls cannot hold Workstream lifecycle transactions open.
- At-least-once dispatch requires idempotent provider operations and immutable
  receipts.

## Conventions To Preserve

- FastAPI/Pydantic/SQLAlchemy/Alembic in Workstream.
- Rust/Axum and existing DAG/block primitives in Flow Node.
- PostgreSQL for Workstream lifecycle state.
- Celery/Redis for durable Workstream background execution.
- `/api/v1` route namespace.
- No backward compatibility for rejected pre-production contracts.

## Unknowns Deferred To Owning Chunks

- Final production Flow Node issuer/audience and optional mTLS.
- Retention duration, legal hold, and deletion policy.
- Whether remote peer retrieval is enabled after local evidence storage is
  proven.
- Whether semantic indexing is enabled for every artifact kind.
