# Chunk Map: WS-ART-001 Immutable Artifact Storage

Each chunk is one PR in one repository. No later chunk starts automatically.

| Chunk | Repository | Goal | Risk | Status |
|---|---|---|---:|---|
| `WS-ART-001-PLAN` | Workstream | Lock canonical target spec, ADR, discovery, decisions, migration/failure matrices, and chunk contracts. | L1 | Active planning |
| `WS-ART-001-01` | Workstream | Add provider contract fixtures, artifact domain records/port, configuration, and LocalStorageAdapter conformance. | L1 | Proposed |
| `FN-ART-001-01` | Flow Node | Add bounded streaming DAG ingest/retrieval primitives without HTTP exposure. | L1 | Proposed |
| `FN-ART-001-02` | Flow Node | Add authenticated idempotent private artifact HTTP ingest/retrieval using the versioned contract. | L1 | Proposed |
| `FN-ART-001-03` | Flow Node | Add bounded recursive verify/retain, replica status, and focused Workstream runtime target. | L1 | Proposed |
| `WS-ART-001-02` | Workstream | Add FlowNodeAdapter, metadata-operation outbox/reconciliation, and pinned local integration. | L1 | Proposed |
| `WS-ART-001-03` | Workstream | Cut guide source bytes onto artifact bindings after the WS-AUTH project cutover. | L1 | Proposed/blocked on WS-AUTH-001-12 |
| `WS-ART-001-04` | Workstream | Add task-scoped upload sessions, sealing, server artifact-set manifests, and admission records. | L1 | Proposed/blocked on WS-AUTH-001-13/14 |
| `WS-ART-001-05` | Workstream | Atomically bind admitted artifact sets to submissions and remove legacy URI/hash contracts. | L1 | Proposed/blocked on WS-AUTH-001-13/14 |
| `WS-ART-001-06` | Workstream | Bind checker inputs/logs/outputs to canonical artifacts without changing checker routing. | L1 | Proposed/blocked on WS-AUTH-001-14 |
| `WS-ART-001-07` | Workstream | Prove local/Flow Node parity, operator recovery, exact-byte pre/post binding, and clean-checkout Compose drill. | L1 | Proposed |

## Dependency Order

```text
WS-ART-001-01
-> FN-ART-001-01
-> FN-ART-001-02
-> FN-ART-001-03
-> WS-ART-001-02
-> WS-ART-001-03 (after WS-AUTH-001-12)
-> WS-ART-001-04 (after WS-AUTH-001-13/14)
-> WS-ART-001-05
-> WS-ART-001-06
-> WS-ART-001-07
```

`ReviewPacketManifest` and `ReviewEvidenceArtifact` are deferred to WS-REV.
Semantic search is deferred to a separate approved initiative.

## Checkpoint Before Checker Expansion

Do not resume pre-submit or post-submit checker feature expansion until
`WS-ART-001-06` proves both phases consume the same immutable artifact-set
commitment.
