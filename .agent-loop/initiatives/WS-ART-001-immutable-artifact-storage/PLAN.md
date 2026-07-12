# Plan: WS-ART-001 Immutable Artifact Storage

## Contract Precedence

This package proposes the target design. If merged by explicit human approval,
ADR 0013 and `docs/spec_artifact_storage_service.md` become the canonical target
contract. Current runtime docs remain evidence of implemented behavior until
their owning cutover merges. Archival reference specifications remain inputs,
not executable contracts. Flow Node internal design stays owned by that repo;
the versioned artifact-store contract fixtures govern interoperability.

## Architecture

```text
canonical Workstream actor + resource authorization
-> ArtifactUploadSession
-> ArtifactUploadItem per uploaded object
-> synchronous bounded stream outside lifecycle transaction
-> ArtifactStorePort
   -> LocalStorageAdapter (development/CI)
   -> FlowNodeAdapter (production/integration)
-> ArtifactContent + ArtifactReplica + ArtifactOperationReceipt
-> ArtifactBinding to exact Workstream resource and logical role
```

The generic port does not expose CID/DAG/block concepts. Flow Node may return a
manifest CID as an opaque provider manifest ID and preserve DAG details in a
bounded receipt. Workstream computes and trusts its own SHA-256 and byte count.

## Upload And Recovery Sequence

1. Workstream verifies the external token and resolves local authority.
2. Transaction A creates/locks one `ArtifactUploadItem` under an authorized
   upload session, reserves bytes, and owns its unique scoped idempotency key,
   canonical request digest, CAS state, and provider operation reference.
3. After commit, Workstream streams to the configured adapter in bounded chunks
   while computing SHA-256 and byte count independently.
4. The adapter atomically stores the bytes, verifies provider identity, applies
   required retention, and returns a signed/hashed typed receipt.
5. Transaction B locks the session/item, compares digest/size, writes content,
   replica, and receipt records, then marks the item ready. Staging creates no
   `ArtifactBinding`.
6. Optional expected SHA-256 and size are persisted before ingest as client byte
   commitments, not server truth. After observed provider success, byte-less
   recovery may independently hash/count the provider object only against both
   commitments. Ambiguous failure, cancellation, or an incomplete commitment
   makes the item `replay_required` and the
   client must replay the exact bytes under the same idempotency key; Workstream
   hashes the replay and the provider returns the existing exact-replay
   receipt. Receipt-only recovery never creates `ArtifactContent`, and no path
   stores a second provider object.
7. Metadata-only verify/retain/status/reconcile operations use durable outbox
   commands and Celery. Outbox rows never contain bytes or credentials.

Default transient retry policy is full jitter with five-second initial delay,
five-minute cap, eight attempts, and a 30-minute elapsed-time limit before dead
letter. Provider idempotency records live for the artifact lifetime and never
less than 90 days. Authentication, validation, idempotency conflict, and
integrity failures are terminal/quarantined rather than retried.

An upload item is eligible for sealing only when its content exists and at least
one required replica is available, verified, retained, and integrity-valid.
Guide/submission attachment later creates immutable resource bindings.

## Server-Generated Artifact Set

The server seals an upload session before authoritative pre-submit execution.
No later item changes are permitted. Trusted inspection derives normalized
names, roles, media types, archive members, path safety, individual sizes, total
size, and SHA-256 values. Each entry receives a server-derived
`manifest_entry_id` over all semantic entry facts; duplicate entry IDs are
rejected. Entries use the total order `(logical_role, normalized_display_name,
content_id, manifest_entry_id)`. Canonical JSON produces `artifact_set_hash`.

The pre-submit admission record binds:

- actor and task;
- sealed upload session and artifact-set hash;
- locked guide/effective policy/pre-submit checker versions and hashes;
- result and expiry.
- canonical `submission_input_hash` over task ID, artifact-set hash, summary,
  contributor attestation, and upload-session ID.

Submission creation presents those same three request fields, revalidates their
input hash plus current authority and locked context inside one
PostgreSQL transaction, row-locks/CAS-consumes the session and admission, and
creates the immutable submission/bindings. Expired, replayed, cross-task,
cross-actor, changed-policy, or concurrent loser requests fail with no second
submission.

## State Ownership

Workstream:

- upload session state;
- provider-neutral content identity;
- immutable logical binding history;
- operation intent/receipt history;
- actor/project/task/checker provenance;
- authorization, audit, and lifecycle effects.

Provider/replica observations:

- opaque provider object/manifest identifiers;
- verification, retention, availability, and integrity states;
- storage-operation timestamps and bounded provider details.

Flow Node never receives Workstream binding IDs as search authority and never
owns product provenance.

## Failure Matrix

| Phase | Condition | Stable code | Persisted owner/effect | Actor-visible result | Recovery authority |
|---|---|---|---|---|---|
| upload | transient provider/transport failure | `artifact_storage_unavailable` | upload operation retryable; no task change | HTTP 503, retry upload | submitter/client or Operator reconcile |
| upload | expected digest/size differs from server bytes | `artifact_input_mismatch` | session item rejected; no binding | HTTP 422 with bounded details | submitter uploads corrected bytes |
| staging | session expired or already consumed | `artifact_upload_expired` / `artifact_upload_consumed` | session remains terminal | HTTP 409 | create a new session |
| provider | malformed/incomplete/corrupt stored content | `artifact_integrity_failure` | replica quarantined; audit event | concealed 503 for ordinary actor | Operator investigation/reconcile |
| setup | required source replica unavailable | `artifact_storage_unavailable` | existing `ProjectSetupRun.status=failed` plus error code; no activation | setup status reports retryable infrastructure failure | covered Project Manager or Operator repair |
| pre-submit | required staged bytes unavailable | `artifact_storage_unavailable` | no admission and no submission | HTTP 503, not pre-submit failure | retry after storage recovery |
| pre-submit | deterministic artifact policy violation | existing `pre_submission_checker_failed` | blocking results; no submission | existing structured checker response | submitter corrects artifacts |
| post-submit | transient retrieval unavailable | `artifact_storage_unavailable` | existing `CheckerRun.status=failed` plus failure code; task stays `evaluation_pending`; no contributor result/routing | evaluation remains pending | `operations.checker.retry` |
| post-submit | integrity failure | `artifact_integrity_failure` | replica quarantined; checker run failed; task stays `evaluation_pending` | no contributor blame | Operator/security investigation |
| review | required packet bytes unavailable | `artifact_storage_unavailable` | no review mutation | HTTP 503 | later WS-REV retry path |
| catalog/status | provider unavailable | `artifact_storage_unavailable` | reconciliation attempt recorded | HTTP 503, never empty success | Operator reconcile |

None of these storage conditions can create `accept`, `needs_revision`,
`reject`, a contribution, compensation exposure, or reputation event.

## Actor And Service Matrix

| Actor/grant | Artifact action |
|---|---|
| covered Project Manager | capture/manage guide source artifacts after WS-AUTH project cutover |
| exact-project Submitter | create and use own task-scoped upload sessions after WS-AUTH task/submission cutover |
| exact-project Reviewer | no WS-ART attachment API; WS-REV later authorizes packet/evidence access |
| Operator | reasoned retry, reconciliation, quarantine/status inspection under registered operations permissions |
| Audit Authority | authorized metadata/evidence read/export only under owning future route guards |
| Access Administrator | no artifact access by that grant alone |
| checker/setup service principals | fixed least-privilege read/write operations with no fabricated human grants |
| Flow Node service principal view | sees only the Workstream service token and provider operation metadata |

## Service Authentication And Privacy

- First exposed Flow Node byte route requires fail-closed service auth.
- Production: TLS, pinned issuer/algorithms, audience `flow-node`, explicit
  Workstream service subject, per-operation scopes, time/jti checks, rotation,
  and redaction.
- Development: test issuer/key and loopback-only TLS exception under explicit
  development configuration.
- Transport/storage/backups are encrypted in production; local adapter uses
  private 0700 directories and is rejected in production.
- Payloads, secrets, signed URLs, tokens, customer metadata, and private paths
  are excluded from logs/errors/receipts.
- Network announcement, peer retrieval, public discovery, and semantic search
  are disabled for the focused runtime.

## Limits And Retention

Defaults are configurable and policy may tighten them:

- maximum single artifact: 512 MiB;
- maximum upload session: 1 GiB;
- streaming buffer: at most 1 MiB per active transfer;
- staging TTL: 24 hours;
- bounded manifest entries, archive depth, expanded bytes, DAG depth/blocks,
  traversal time, and concurrent transfers.

Tests override limits to prove empty input, exact boundary, oversized input,
cancellation, partial write, disk exhaustion, provider disconnect, temporary
cleanup, archive expansion limits, cyclic/hostile DAG rejection, and bounded
memory.

Production ingestion remains disabled until a retention-policy version,
encrypted storage/backup controls, and quotas are configured. Staging cleanup
uses CAS and cannot release bound content.

## Migration Matrix

| Chunk | Prior data allowed | Change | Populated database behavior | Downgrade |
|---|---|---|---|---|
| WS-ART-001-01 | all current legacy rows | additive artifact tables/config only | succeeds; no legacy rows promoted | drops only new empty/unreferenced tables in tests |
| WS-ART-001-03 | guide rows/snapshots | replace guide source byte identity with bindings | fails closed when source snapshots exist; pre-production rebuild required | schema-only on empty rebuilt data; no false reconstruction |
| WS-ART-001-04 | legacy submission tables unchanged | additive upload session/admission tables | succeeds without interpreting old submissions | drops additive tables in tests |
| WS-ART-001-05 | submissions/evidence/checker runs plus approved/effective artifact policies, compiled pre-submit bundles, and locked/active tasks using rejected transport/hash fields | remove legacy artifact request/persistence fields, policy/compiler transport choices, and add relational bindings | fails closed when any incompatible submission/evidence/checker/policy/bundle/locked-task rows exist; rebuild/regeneration required | schema-only on empty rebuilt data |
| WS-ART-001-06 | canonical bound submissions and checker rows with artifact-set IDs/hashes | add checker input/output binding references and snapshots | deterministically creates snapshots only from canonical artifact sets; refuses missing canonical context | ordinary tested downgrade |

Every migration test covers fresh upgrade, prior-head upgrade, populated refusal
where specified, downgrade, and re-upgrade. No declaration is backfilled as
verified evidence.

Flow Node migration proof is separate:

| Chunk | Prior state | Expected behavior | Downgrade/re-upgrade |
|---|---|---|---|
| FN-ART-001-02 | existing block store and legacy published/discovered metadata | additive artifact catalog/idempotency schema; preserves blocks; promotes no legacy metadata to verified artifact | downgrade refuses non-empty new artifact catalog in production and is tested on empty fixture; re-upgrade passes |
| FN-ART-001-03 | authenticated artifact catalog from FN-ART-001-02 | additive retention/reference/status records; verifies existing artifact rows before retain eligibility | downgrade refuses active retention references; empty downgrade/re-upgrade passes |

## Required Concurrency Proof

- Two transactions consuming one sealed session/admission: exactly one creates
  one submission and binds each artifact once; the loser returns 409 and changes
  zero rows.
- Session expiry versus consume: both lock/CAS the same session using database
  time; one terminal transition wins and no bound content is released.
- Duplicate metadata-operation workers: one provider effect/idempotency receipt,
  one monotonic replica state, one claimed attempt row; crash/retry produces
  exactly one additional attempt row and no additional provider effect.
- Crash after provider success before transaction B: with a persisted expected
  digest, reconciliation independently hashes/counts the referenced object and
  accepts only an exact match; without one, the item is `replay_required` until
  an exact client replay proves the original commitment. Both paths create no
  second provider object; altered receipt/object/replay bytes produce zero
  content/binding rows and quarantine.
- Reconciliation racing retry: unique scoped operation key/request digest
  prevents contradictory receipts.
- Duplicate checker execution: one authoritative run/input snapshot; attempts
  remain append-only and cannot route partial evidence; exactly one run reaches
  the authoritative terminal result.
- Upload versus seal: if seal locks first, upload returns 409 and creates zero
  content/replica rows; if upload transaction B locks first, seal includes that
  one ready item. No intermediate item is included.
- Seal versus expiry and consume versus expiry: exactly one terminal session
  state wins under database time; loser returns 409 and changes zero rows.
- Cancellation versus sweeper: one terminal transition and at most one
  metadata-only release operation; bound content has zero release operations.

Tests assert exact counts for upload sessions, contents, bindings, replicas,
receipts, submissions, checker runs, and provider effects.

## Legacy Field Replacement Matrix

| Old surface | Replacement | Owner |
|---|---|---|
| `SubmissionCreate.package_uri` | `upload_session_id` | WS-ART-001-05 |
| platform `required_packet_fields = [summary, artifact_hash_manifest, worker_attestation]` | `[summary, contributor_attestation, upload_session_id]`, bound by admission input hash | WS-ART-001-05 |
| `SubmissionCreate.worker_attestation` | `contributor_attestation` | WS-ART-001-05 |
| `SubmissionCreate.package_hash` | server `ArtifactContent.sha256` and `artifact_set_hash` | WS-ART-001-05 |
| `SubmissionCreate.artifact_hash_manifest` | server `ArtifactSetManifest` | WS-ART-001-05 |
| `EvidenceItemCreate.uri/hash/size_bytes` | upload-item logical roles; server content facts and later bindings | WS-ART-001-05 |
| `Submission.package_uri/package_hash/artifact_hash_manifest` | relational artifact set/bindings | WS-ART-001-05 |
| `Submission.worker_attestation` | `contributor_attestation` | WS-ART-001-05 |
| `EvidenceItem.uri/hash/size_bytes` | `artifact_binding_id` plus bounded label/type metadata | WS-ART-001-05 |
| checker copied package/hash declarations | `CheckerRun.artifact_set_id/artifact_set_hash` bridge, with declaration columns removed | WS-ART-001-05 |
| canonical checker artifact-set bridge | `CheckerInputSnapshot` with content/binding IDs, SHA-256, size, policy and implementation hashes | WS-ART-001-06 |
| guide item `content_cid` as future placeholder | artifact content/binding/replica references | WS-ART-001-03 |
| project-policy `manifest_required` / `artifact_hash_required` / `artifact_hash_algorithm` | unconditional platform-managed sealed artifact set and SHA-256 invariants | WS-ART-001-05 |
| project-policy `allowed_storage_schemes` | configured `ArtifactStorePort`; projects cannot select or weaken storage providers | WS-ART-001-05 |
| compiler primitives `enforce_storage_scheme` / `verify_hash` / `require_manifest_field` | trusted `validate_sealed_artifact_set` platform primitive plus project artifact/evidence rules | WS-ART-001-05 |

Owning chunks must update schemas, models, migrations, services, audit payloads,
tests, `docs/spec_chunk_5_submission_packet_foundation.md`, architecture data and
checker documents, glossary, submission/checker/review templates, API examples,
and stale-contract scans.

WS-ART-001-05 also updates the project-agent schema/prompt and ADR 0011. Once
that cutover merges, ADR 0013 supersedes ADR 0011 only for artifact transport,
caller-provided manifest/hash fields, storage-scheme policy, and their compiler
primitives; ADR 0011 continues to control project-level policy derivation,
approval, locking, and deterministic checker compilation.

## WS-AUTH Dependencies

- Internal artifact foundations and Flow Node work may proceed independently.
- Guide source API cutover waits for WS-AUTH project mutation cutover
  (`WS-AUTH-001-12`) or its approved replacement.
- Upload session and submission cutovers wait for task/submission/checker
  authorization cutovers (`WS-AUTH-001-13` and `WS-AUTH-001-14`).
- Reviewer packet/evidence APIs remain in WS-REV and wait for reviewer
  assignment/lease authority.

## Delivery And Contract Versioning

- Workstream owns `contracts/artifact-store/version_1/` JSON/OpenAPI fixtures, stable
  error codes, receipt schemas, limits, and conformance vectors.
- Flow Node copies the exact version and records its source digest; provider CI
  runs those vectors.
- Workstream adapter CI runs the same vectors against a pinned Flow Node image
  digest/revision.
- Additive compatible changes create new optional fields; breaking changes
  require `v2`, coordinated PRs, and an explicit human checkpoint.
- Flow Node changes merge normally to Flow Node `main`; a focused runtime target
  is built and pinned. Security updates rebase through ordinary mainline PRs.

## Real API Proof

The final Workstream chunk owns Docker build/config needed to start Postgres,
Redis, Workstream API, Celery, and focused Flow Node from a clean checkout. It
uses supported APIs plus a documented local test issuer and deterministic
project setup fixture; no production OpenAI credential is required for storage
contract proof. Fault controls are test-only and unavailable in production.

The report records request/response summaries, opaque IDs, redacted hashes,
polling deadlines, row-count invariants exposed through APIs, outage recovery,
and proof that pre/post checks used the same artifact-set commitment.
