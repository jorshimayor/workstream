# Chunk Contract: WS-AUTH-001-05B - Authority Idempotency And Invalidation Foundation

## Status

Inactive until AUTH-05A merges, its post-merge memory is current, and the user
gives a separate explicit start signal.

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Add concurrency-safe authority-mutation reservation/replay and typed success,
denial, and invalidation orchestration on the shared AUTH-05A audit envelope.

## Risk and circuit breaker

- Risk: L1 / SLA P1.
- Inspect scope at 350 changed non-comment production lines.
- Hard stop at 500 changed non-comment production lines, counting
  `backend/app/**` plus migration code.

## Allowed files

```text
backend/app/modules/authorization/**
backend/app/db/models.py
backend/alembic/versions/0019_authority_idempotency.py
backend/tests/test_authorization.py
backend/tests/test_audit.py
backend/tests/test_alembic.py
docs/architecture_data_model.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
routes, dependencies, middleware, or generic unit-of-work wrappers
actor/profile migration or first-access behavior
permissions, grant tables/APIs, or product authorization cutover
invalidation consumers, caches, queues, or external delivery
token-role or IdentityIssuerVerifier/factory changes
raw request/response bodies, URLs, PII, secrets, or arbitrary JSON persistence
workflow, dependency, threshold, skip, or exclusion changes
repository/service commit, rollback, or parallel session creation
```

## Idempotency schema and namespace

Migration `0019_authority_idempotency` uses exact
`down_revision = "0018_authority_audit_evidence"` and creates
`authority_idempotency_records`. Each record contains:

- UUID primary key and canonical UUID idempotency key;
- actor reference kind plus stable opaque actor reference;
- closed operation token;
- canonical request digest using existing
  `app.core.hashing.canonical_json_hash` (`sha256:` plus 64 lowercase hex);
- status `pending` or `committed`;
- typed committed response reference: resource type, resource ID, optional
  version, and successful HTTP status; never a body, URL, or free-form JSON;
- database-owned created/committed timestamps.

The unique replay namespace is
`(actor_ref_kind, actor_ref, operation, idempotency_key)`. Different actors or
reference kinds may reuse a key without collision or visibility. Operation,
target project/resource, and mutation payload are included in the canonical
request object/digest. Request ID, correlation ID, and the idempotency key are
excluded from the digest so legitimate retries may carry new request context.
The raw request is never persisted.

The canonical request object is a typed, bounded JSON-compatible dictionary.
It uses the shared canonical hash helper; no authorization-local encoder is
introduced.

## State machine and transaction ownership

- Reservation runs before any business-state flush.
- `INSERT ... ON CONFLICT` plus a locked read serializes concurrent users of
  one replay namespace.
- A new reservation returns `claimed` with a `pending` row in the caller's
  transaction.
- Same namespace and digest after commit returns `replay` with the existing
  typed committed reference and does not append duplicate success/invalidation
  events.
- Same namespace with a different digest returns a stable `mismatch` outcome;
  caller-owned application orchestration records the required denial event in
  a clean transaction before surfacing `idempotency_mismatch`.
- Completion atomically changes only the caller's pending row to `committed`
  and writes its typed response reference.
- A deferred database constraint rejects commit while a record is still
  pending. Rollback/cancellation removes the reservation and all co-transaction
  business/audit/invalidation rows; retry may then claim normally. A pending
  row is never stolen, expired, or treated as success.
- Repository/service methods may insert, lock, flush, and return typed outcomes
  only. The injected caller session alone commits or rolls back; no parallel
  unit-of-work abstraction or session is introduced.

## Invalidation and denial evidence

Invalidation is an `AuthorityInvalidationRequested` authority-domain
`AuditEvent`, not a second event table. Authorization owns typed orchestration;
AuditRepository remains the persistence owner. The event links its causing
authority event, exact target kind/reference, request/correlation IDs, actor,
reason, and idempotency record when applicable. AUTH-05B introduces persistence
and orchestration only: no cache, worker, adapter, or authority behavior consumes
the event.

Allowed, denied, and invalidation events use stable tokens. Denial/mismatch
orchestration returns a typed result rather than committing or raising inside
the repository; the caller commits the denial evidence before translating the
result to an API error. Denials are not stored as successful replay results.

## Migration custody

- Upgrade preserves all AUTH-05A audit rows and creates no idempotency or
  invalidation evidence.
- Tests assert exact table columns, constraints, indexes, deferred trigger,
  defaults, invalid rows, and database time.
- Downgrade takes writer-blocking locks and refuses without mutation when any
  idempotency row or audit row referencing idempotency/invalidation evidence
  exists. Legacy and AUTH-05A audit rows remain intact.
- Privileged fixture cleanup permits `0019 -> 0018 -> 0019`; re-upgrade restores
  the pending-commit guard. Destructive tests restore `head` in `finally`.

## Acceptance criteria

- Independent-session exact concurrent retries produce one committed result
  and one success/invalidation event set.
- Concurrent mismatched requests produce one winner and one privacy-safe
  mismatch outcome; different actors/kinds remain isolated.
- Injected failure after reservation, synthetic business flush, audit insert,
  invalidation insert, completion, and commit attempt leaves either the complete
  transaction or nothing. Repositories never commit/rollback.
- Retry after rollback claims normally; commit of unfinished pending state
  fails closed and leaves no durable pending row after caller rollback.
- Exact replay never duplicates business, success, or invalidation evidence.
- No route, permission, grant, actor, product authority behavior, or
  invalidation consumer exists.

## Verification

```bash
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && isolated PostgreSQL: pytest -q tests/test_alembic.py::<0019-proof> tests/test_authorization.py tests/test_audit.py)
(cd backend && focused AUTH-05B coverage >= 90 percent)
(cd backend && isolated full suite --cov=app --cov-fail-under=78)
(cd backend && .venv/bin/docstr-coverage --config .docstr.yaml)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_markdown_links.py
python3 scripts/check_internal_review_evidence.py
git diff --check
```

Run the exact migration node before audit/authorization tests on the same
isolated database. Test delta must be additive and all CI integrity controls
remain unchanged.

## Required reviewers

- senior engineering
- QA/test
- security/auth and privacy
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

## Human review focus

Review replay namespace, canonical hashing, pending-commit prevention,
concurrency/rollback behavior, typed result privacy, invalidation causation,
and caller-owned transaction boundaries.

## Stop conditions

Stop if exact concurrency cannot serialize without a committed pending row,
denial evidence requires committing unrelated work, a route/grant/permission
must be introduced, or tests/CI must be weakened. AUTH-05B consumes the merged
05A audit envelope and sole-writer contract without modifying its schema,
triggers, constraints, repository, or writer. A missing audit primitive requires
stop and replan rather than reopening 05A custody.
