# PR Trust Bundle: WS-ART-001-02A2

## Chunk

`WS-ART-001-02A2` - Committed Source And Local Preparation

Merge intent: `.agent-loop/merge-intents/WS-ART-001-02A2.json`

## Goal

Build the inactive bounded source-preparation boundary that ArtifactStore v2
will consume, while preserving every active v1 behavior.

## Human-Approved Intent

The user explicitly started this chunk after merging the shared external-service
adapter foundation. The approved direction is LocalStorage for development,
MinIO for local/CI S3 proof, AWS S3 for v0.1 production, and Flow Node as a
separate future initiative. This chunk adds no provider or runtime cutover.

## What Changed

- Sealed server commitment plus exact second-pass stream as one non-forgeable
  value.
- Cross-process private scratch reservation ledger with full-max admission,
  private/no-follow files, deadlines, stale cleanup mechanics, and rollback.
- Canonical full-limit root fingerprint, conservative free-space accounting,
  and retryable release ownership.
- Private LocalStorage helper extraction with unchanged public v1 behavior.
- Exact configuration inventory, focused tests, and cumulative CI gates.

## Scope Control

No route, Alembic migration, product record, provider SDK/configuration, MinIO,
AWS, R2, Flow Node, Celery activation, auth implementation, review lifecycle,
contribution, compensation, or ArtifactStore v2 wiring is present.

## Acceptance Criteria Proof

- Workstream computes SHA-256 and exact size while writing the untrusted first
  pass once, then verifies the complete sealed second pass before yielding bytes.
- Client digest/size mismatch fails before any future provider call.
- Every preparation reserves the full 512 MiB maximum under a cross-process
  ledger lock.
- Aggregate bytes, files, concurrency, free-space floor, deadline-before-TTL,
  stale cleanup, cancellation, crash, filesystem safety, and rollback have
  focused regression coverage.
- Existing reservations are included in free-space admission, preventing
  concurrent processes from reusing logically committed headroom.
- Active LocalStorage v1 behavior and all existing factory paths are unchanged.

## Tests And Test Delta

- 105 focused tests passed at 94.24 percent changed-scope coverage.
- `ArtifactPreparationService`/scratch behavior, LocalStorage v1 regression, and
  configuration validation are covered.
- No test was removed, skipped, xfailed, weakened, or newly excluded.
- Repository docstring coverage passed at 92.3 percent.
- GitHub Backend CI owns the authoritative full suite and unchanged 78 percent
  repository coverage floor.

## CI Integrity

- [x] Exact repository-wide 78 percent command remains present.
- [x] Existing artifact and external-service 90 percent gates remain present.
- [x] Exact configuration 90 percent gate was added.
- [x] Agent tests enforce command, source set, threshold, order, and cumulative retention.
- [x] No skip, conditional, `continue-on-error`, exclusion, or threshold bypass was added.
- [ ] GitHub Backend CI must pass the published exact head.

## Reviewer Results

| Reviewer group | Result | Blocking findings |
|---|---:|---|
| Senior engineering, architecture, QA, security/auth | PASS | None |
| Product/ops, reuse/dedup | PASS | None |
| CI integrity, test delta, docs | PASS | None |

All nine final reviewer sessions inspected
`d8b8c8abc7c6dd8cf254d0c8b3d5d7c066c01b46` and are closed. Valid findings
around filesystem durability, root mutation/races, source forging, verification
ordering, descriptor cleanup, release retryability, process-limit drift,
operator documentation, and free-space oversubscription were repaired and
re-reviewed.

## External Review

No PR is open yet. GitHub checks and CodeRabbit begin only after internal
evidence passes and the branch is published. External review supplements these
internal tracks and does not replace them.

## Remaining Risks

- The preparation boundary remains intentionally inactive until `02A3`.
- GitHub Backend CI must run the exact-head full suite and 78 percent floor.
- Provider integration, durable artifact attempts, verification, recovery,
  product bindings, and authorization activation remain separate approved chunks.

## Human Review Focus

- Confirm callers cannot choose a content key without supplying matching bytes.
- Confirm free-space and aggregate admission are safe across processes.
- Confirm LocalStorage v1 remains unchanged and no second active runtime exists.
- Confirm cleanup mechanics exist without hidden startup/Celery activation.

## Human Merge Ownership

Only the user may approve and merge this PR. Publication is not merge approval.
