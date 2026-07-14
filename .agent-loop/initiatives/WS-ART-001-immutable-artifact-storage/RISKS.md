# Risks: WS-ART-001 S3-Compatible Object Storage Amendment

| Risk | Severity | Mitigation |
|---|---:|---|
| Existing key overwritten by concurrent upload | Critical | Content-addressed key plus conditional no-overwrite write and concurrency tests. |
| First writer poisons a known digest key | Critical | Every source is server-hashed in bounded scratch before provider I/O; the port accepts only a sealed committed source; cross-project adversarial tests prove no client-selected digest can choose a key. |
| Provider acknowledgement accepted without exact bytes | Critical | Independent complete-object read/hash before bindability. |
| Multipart semantics diverge across providers | High | v0.1 uses conditional single-request put with a 512 MiB hard limit; multipart is deferred. |
| ETag or provider metadata mistaken for Workstream SHA-256 | Critical | Workstream computes SHA-256; ETag and custom metadata are never authoritative. |
| S3 credential becomes product authority | Critical | Authorization Service decision precedes every product action; credential is transport only. |
| Secret retained in settings errors/logs/jobs | Critical | Secret-safe settings boundary, redaction/object-graph tests, no credential persistence. |
| R2 temporary credential expires or issuer fails | High | Repository-owned locked issuer source/image, private loopback container endpoint, server-fixed scope/TTL/audience, reloadable secret files, advisory-window cached continuation, mandatory-window fail closed before expiry, no expired use, and live private-R2 proof. |
| R2 parent token can mint broader authority | Critical | Restrict it to the exact Cloudflare account and artifact bucket with the narrowest non-admin minting permission, deny cross-bucket scope, and prove rotation/revocation. |
| R2 loopback resolves to the wrong container | Critical | Compose shares Workstream's network namespace with `network_mode: service:<workstream-service>` and Kubernetes uses the same Pod; bridge DNS, separate issuer namespaces, and host ports fail closed. |
| Ambient AWS credential bypasses the R2 sidecar | Critical | R2 startup rejects every higher-precedence credential/profile/metadata/container-relative source, requires exact full loopback URI and token-file path, verifies the resolved container method, and tests poisoned environments/profiles. |
| Public bucket or cached domain leaks evidence | Critical | Provider-specific deployment proof checks AWS public-access controls or R2 public domains and proves anonymous reads fail. |
| Runtime credential can destroy evidence | Critical | Exact bucket/prefix/action scope; denied delete/copy/list/admin/lifecycle/public-access actions; negative tests. |
| Broker publication failure strands verification/recovery | High | Periodic PostgreSQL scanner with bounded SLA and duplicate-safe publication. |
| Duplicate/stale Celery execution writes terminal state | Critical | PostgreSQL clock, fresh executor UUID, generation fencing, and zero-row stale finalization rollback. |
| Slow progressive read outlives execution lease | High | End-to-end verification deadline shorter than lease by a persistence margin. |
| Concurrent prepared artifacts exhaust worker disk | High | Full-max pre-reservation, dedicated quota, cross-process ledger, bounded concurrency, free-space floor, and deadline-before-TTL cleanup. |
| Recovery replay or ancestor reuse creates multiple jobs | High | Canonical request digest plus a lifetime unique source-job constraint return original IDs on exact replay, reject different-key/concurrent reuse, and require chain progression through the immediate retry job. |
| Operator cannot observe retry completion | High | Authorized recovery-attempt GET includes immutable source-job and current retry-job status plus audit IDs. |
| Storage failure becomes contributor failure or review decision | Critical | Stable infrastructure errors; no accept/needs_revision/reject, contribution, payment, or reputation effect. |
| Pre-submit outage strands or duplicates a contributor attempt | High | Bounded Workstream retry, stable 503, sealed unconsumed artifact set, exact request-digest idempotency, and contributor continuation without manager/operator approval. |
| Pre-existing lifecycle rule deletes evidence | Critical | Read-only AWS/R2 lifecycle inspection blocks activation for any deletion/expiration rule intersecting the completed-object prefix. |
| Local adapter reaches production | High | Closed backend enum and production startup rejection. |
| S3-compatible providers differ | High | Local/MinIO conformance plus separate AWS S3 and R2 readiness smoke profiles; no unsupported API dependency. |
| Flow Node remains a hidden v0.1 dependency | High | Separate deferred initiative and stale-contract gate. |
| Route tests overclaim fleet atomicity | Medium | Per-image proof only; deployment barrier documented separately. |
| Large chunks become unreviewable | High | Preparation, v2 cutover, provider profiles, verification, recovery, upload/sealing, pre-submit admission, checker input, and checker output/routing are separate checkpoints with explicit allowed files and stop conditions. |
