# Risks: WS-ART-001

Risk class: L1

SLA: P1

Work type: architecture, data ownership, storage infrastructure, migration,
security, async execution, API, and integration.

Required reviewers: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, and test delta as applicable to
each chunk.

Human gate: required before every chunk and every merge in both repositories.

Budget posture: high reasoning; use `gpt-5.6-sol` high for internal reviewers.

## Risk Register

| Risk | Severity | Control |
|---|---:|---|
| Checked bytes differ from submitted bytes | Critical | Server-owned upload items, sealed artifact-set commitment, bound submission-input digest, and atomic immutable resource bindings. |
| Partial DAG pin or verification | Critical | Recursive traversal, corruption tests, receipt block counts. |
| Unauthorized artifact disclosure | Critical | Workstream resource authorization before retrieval/status disclosure. |
| Human token forwarded to Flow Node | High | Dedicated service principal/audience only. |
| Provider outage becomes contributor failure | High | Stable `artifact_storage_unavailable` on existing owning records. |
| External call inside lifecycle transaction | High | Two-transaction upload choreography; metadata-only outbox work. |
| Local adapter differs from production | High | Shared port contract and adapter conformance suite. |
| Public network announcement leaks evidence | High | Focused private runtime; announcements disabled. |
| Legacy URI/hash compatibility persists | High | Clean schema/API removal and stale-contract scan. |
| Cross-repository contract drift | High | Workstream-owned v1 vectors, copied source digest, pinned image, and provider/consumer tests. |
| Large uploads exhaust memory | High | Streaming, limits, bounded temporary files, cancellation cleanup. |
| Orphan staging consumes storage | Medium | TTL sweeper and reconciliation without deleting canonical evidence. |
| Provider receipt accepted for altered bytes | Critical | Workstream independently computes SHA-256/size during ingest; crash recovery compares an independent provider read to a persisted commitment or requires exact client replay when no commitment exists. |
| Retention/deletion race | High | Separate replica retention state, reference ownership, production policy gate, and CAS sweeper. |
| Unauthenticated first Flow Node route | Critical | Service auth is part of the first HTTP exposure chunk. |
