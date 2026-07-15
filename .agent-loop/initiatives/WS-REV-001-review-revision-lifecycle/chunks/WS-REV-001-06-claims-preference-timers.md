# Chunk Contract: WS-REV-001-06

## Goal

Implement atomic claim, reviewer release, preferred decline, preference expiry,
lease expiry, and lazy recovery with one global active reviewer lease.

## Risk class

L1 authorization and concurrency.

## Allowed files

```text
backend/app/modules/reviews/{repository,schemas,service,router}.py
backend/app/workers/{celery_app,reviews}.py
backend/app/core/config.py only for bounded timer settings
backend/tests/test_{reviews,authorization,artifacts,config}.py
docs/operations_queue_policy.md
docs/operations_reviewer_workflow.md only for timer/configuration rollout
.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/**
.agent-loop/merge-intents/WS-REV-001-06.json
```

## Not allowed

```text
review decision or finding writes
admin override or force release
new authorization or artifact semantics
remote provider call while queue/lease rows are locked
reviewer capacity greater than one
production `/api/v1` review-router registration
```

## Acceptance criteria

- Evidence preflight occurs before row locks; claim transaction revalidates
  canonical binding/preflight identity and current authorization.
- Claim eligibility is re-evaluated inside the transaction before any private
  context is disclosed: canonical active human actor, project reviewer grant,
  required permissions, project match, no self-review against submitter,
  creator, or current/prior task assignees, eligible queue state, and no global
  active lease. Cross-project, suspended/revoked, self, creator, and assigned
  reviewer negatives create no lease or artifact mutation.
- The claim transaction reselects and locks the reviewer's canonical
  preferred-first/FIFO current offer and requires any submitted queue ID to
  match it. Arbitrary, guessed, stale, lower-priority open, and concurrently
  superseded IDs fail without disclosure or mutation.
- Concurrent claims create exactly one lease per entry and per reviewer.
- Lease compensation-policy freeze required by WS-CON is present and is
  resolved for the newly created lease through the merged WS-CON capability.
  It is independent of decision outcome and any forward/backward Project Guide
  rebase. A later lease may freeze a newer reviewer compensation version, but a
  prior lease is never rewritten.
- Release, decline, preference expiry, and lease expiry use distinct immutable
  audit facts and preserve `first_queued_at`.
- Claim, release, decline, preference expiry, and lease expiry declare,
  respectively, `review.claim`, `review.release`,
  `review.decline_preference`, `review.preference_expiry.run`, and
  `review.lease_expiry.run`. Each calls the transaction-aware
  `AuthorizationService.require` boundary and persists canonical
  AuthorizationDecision linkage; denial or revocation commits no
  lease/routing/audit/outbox effect.
- Lease expiry clears stickiness and uses PostgreSQL time.
- Sweeps are idempotent and lazy recovery invokes the same transition service.
- Expected uniqueness races map to stable 409 codes, never 500.
- Claim, release, decline, preference expiry, and lease expiry follow the
  canonical lock order; real-Postgres tests use independent sessions/barriers,
  both operation permutations, and rollback fault injection.
- Services and internal route tests exist, but production OpenAPI remains free
  of every lifecycle mutation through chunk 09B.
- Operator docs enumerate every timer environment variable, bounded default,
  Celery beat/worker command, lazy-recovery behavior, alert, and rollout rule.
- Timer jobs reuse `run_async_task`, the existing fresh engine/session disposal
  pattern, stable Celery task IDs, and `sync_task_settings`; no second async
  bridge, session factory helper, queue configuration, or fallback execution
  path is introduced.

## Verification

```text
cd backend && pytest -q tests/test_reviews.py tests/test_authorization.py tests/test_artifacts.py tests/test_config.py
cd backend && ruff check app/modules/reviews app/workers/reviews.py tests/test_reviews.py
(metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78))
cd backend && coverage report --include='app/modules/reviews/*,app/workers/reviews.py' --precision=2 --fail-under=90
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
reuse/dedup, and test-delta.

## Human review focus

Database-time races, lock ordering, preflight freshness, compensation freeze,
and retry-safe worker behavior.

## Stop condition

Merge, record automated memory, and stop. Do not start 07.
