# Chunk Map: WS-ART-001 S3-Compatible Object Storage

Each chunk is one PR. No later chunk starts automatically.

| Chunk | Goal | Risk | Status |
|---|---|---:|---|
| `WS-ART-001-PLAN` | Original artifact planning. | L1 | Merged through PR #97 |
| `WS-ART-001-01` | Artifact domain and LocalStorage v1 foundation. | L1 | Merged through PR #101 |
| `WS-ART-001-OBJECT-STORAGE-AMENDMENT` | Replace Flow Node-first v0.1 with S3-compatible object storage, simplify provider ownership, and defer Flow Node. | L1 | Active planning only |
| `WS-ART-001-02A1` | Install only ADR 0014's small typed external-service adapter/factory foundation without migrating a capability. | L1 | Proposed after amendment merge and explicit start |
| `WS-ART-001-02A2` | Add bounded committed-source preparation and inactive scratch-cleanup mechanics without changing the active v1 port. | L1 | Proposed after 02A1 |
| `WS-ART-001-02A3` | Replace ArtifactStore v1 with byte-only v2, activate API-startup and Celery Beat scratch cleanup, migrate schema/callers/factory, and remove `flow_node` in one atomic clean cut. | L1 | Proposed after 02A2 |
| `WS-ART-001-02B1` | Implement the S3-compatible adapter, MinIO integration, and AWS S3 production profile. | L1 | Proposed after 02A3 |
| `WS-ART-001-02B2` | Implement the isolated deployment-owned R2 temporary-credential issuer. | L1 | Proposed after 02B1 |
| `WS-ART-001-02B3` | Connect Workstream's R2 production profile to the exact issuer image through the standard container-credential endpoint contract. | L1 | Proposed after 02B2 |
| `WS-ART-001-02C1` | Add durable verification publication, PostgreSQL execution fencing, complete-object observation, and immutable receipts without recovery attempts or routes. | L1 | Proposed after 02B3 |
| `WS-ART-001-02C2` | Add the recovery-attempt model and exact idempotent source-job to retry-job chain without public or Operator routes. | L1 | Proposed after 02C1 |
| `WS-ART-001-02D` | Add exact authorized Operator content/job/retry/recovery/audit APIs and production-readiness checks; provider profiles remain inactive. | L1 | Proposed after 02C2 plus merged AUTH-07, AUTH-08, and AUTH-09 |
| `WS-ART-001-03` | Store and bind guide-source bytes; add same-snapshot setup recovery through the authorized artifact reader. | L1 | Proposed after 02D and named auth/setup contracts |
| `WS-ART-001-04A` | Add task-scoped upload sessions/items, trusted archive inspection, independent verification, immutable sealing, and artifact-set manifests. | L1 | Proposed after 03 and named auth contracts |
| `WS-ART-001-04B` | Execute authoritative pre-submit against sealed artifact sets and persist exact admissions with bounded infrastructure continuation. | L1 | Proposed after 04A |
| `WS-ART-001-05` | Atomically bind admitted artifact sets to submissions and remove legacy URI/hash/finalization contracts. | L1 | Proposed after 04B |
| `WS-ART-001-06A` | Persist checker input snapshots and materialize authorized immutable bytes into bounded checker workspaces. | L1 | Proposed after 05 and named auth contracts |
| `WS-ART-001-06B` | Ingest checker logs/outputs as artifacts and route successful post-submit execution to the WS-REV boundary. | L1 | Proposed after 06A and named auth/WS-REV contracts |
| `WS-ART-001-07` | Prove Local/MinIO plus AWS S3/R2 configuration readiness, Operator recovery, and exact-byte guide/pre/post-submit behavior through real APIs. | L1 | Proposed after 06B |

## Dependency Order

```text
OBJECT-STORAGE-AMENDMENT
-> 02A1 shared adapter/factory foundation
-> 02A2 committed-source preparation and LocalStorage internals
-> 02A3 ArtifactStore v2/LocalStorage/schema clean cut
-> 02B1 S3-compatible adapter, MinIO, and AWS profile
-> 02B2 deployment-owned R2 credential issuer
-> 02B3 Workstream R2 container-credential profile
-> 02C1 verification publication and fencing
-> 02C2 recovery attempt and idempotency chain
-> 02D Operator and production readiness
-> 03 guide source cutover
-> 04A upload/inspection/sealing
-> 04B pre-submit admission and outage continuation
-> 05 submission cutover
-> 06A checker input/materialization
-> 06B checker output/post-submit routing
-> 07 live proof
```

`FN-ART-002` is deferred and is not in this dependency graph.
`ReviewPacketManifest` and `ReviewEvidenceArtifact` remain owned by WS-REV.
Physical deletion and semantic search require separate approved initiatives.

## Checkpoint Before Checker Expansion

Do not resume checker feature expansion until `WS-ART-001-06B` proves pre-submit
and post-submit consume the same immutable artifact-set commitment.
