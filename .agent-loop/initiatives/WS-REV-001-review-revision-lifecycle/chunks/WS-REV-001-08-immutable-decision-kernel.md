# Chunk Contract: WS-REV-001-08

## Goal

Implement the internal immutable review-decision transaction for all three
decisions, including findings, resolutions, task/assignment effects, audit, and
the shared-outbox projection event, without production route activation.

## Risk class

L1 canonical judgment and transaction integrity.

## Allowed files

```text
backend/app/modules/reviews/{repository,schemas,service}.py
backend/app/modules/tasks/{models,review_participant}.py only for caller-transaction decision effects
backend/app/composition/review_lifecycle.py only to install the exact task participant
backend/tests/test_{reviews,tasks,authorization,artifacts,audit}.py
.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/**
.agent-loop/merge-intents/WS-REV-001-08.json
```

## Not allowed

```text
public decision route
production no-op WS-CON participant
remote storage calls inside the transaction
mutation of prior Submission, Review, ReviewFinding, or FindingResolution
reputation or fulfillment logic
```

## Acceptance criteria

- Transaction rechecks current authorization, lease ownership/expiry, grant,
  self-review, queue state, idempotency, predecessor chain, and stabilized
  binding facts using database time.
- The command declares `review.decision` and runs through the transaction-aware
  `AuthorizationService.require` boundary. The Review, audit event, and shared
  outbox payload retain the canonical ActionId-bearing AuthorizationDecision
  link.
- Decision/finding/evidence/resolution rules match the canonical spec.
- Task effects use the task-owned `TaskReviewEffectsParticipant` with the
  caller's AsyncSession. It flushes without commit, reuses TaskRepository and
  lifecycle guards internally, and is the only path for review-driven task or
  assignment effects; review code never imports TaskRepository.
- Accept completes assignment and accepts task; needs revision keeps assignment
  active; reject blocks only that assignment and closes task with reason.
- Review, findings, evidence relations, resolutions, queue close, lease consume,
  task effects, audit, and projection request commit or roll back together.
- Exact replay returns the Review; changed replay fails.
- Idempotency is bound to actor, operation, lease, submission, and canonical
  payload. Replay reauthorizes disclosure for the same actor without requiring
  a consumed lease to remain active; cross-actor, revoked-disclosure, or changed
  payload replay fails without revealing the prior result.
- The decision actor is the active canonical human `ActorProfile.id` that owns
  the exact ReviewLease. UUID shape alone is insufficient; a service actor,
  system principal, legacy ID, or external subject cannot decide a Review.
- Decision-versus-expiry, revocation-versus-decision, binding-state, and duplicate
  decision races are deterministic on PostgreSQL.
- Production composition cannot invoke the kernel without the later WS-CON
  participant gate.
- The transaction follows the canonical lock order. Independent Postgres
  sessions/barriers exercise decision versus expiry, revocation, binding-state,
  duplicate decision, and opposite-order attempts, with participant-by-
  participant rollback fault injection and bounded deadlock retry proof.
- Audit, outbox, dead-letter, alerts, and error details contain only bounded
  typed projections: no finding body, private artifact metadata, signed access,
  provider path, or unrestricted identity value.
- Audit uses the shared caller-transaction participant with request/correlation
  and AuthorizationDecision linkage; no review-private audit persistence exists.

## Verification

```text
cd backend && pytest -q tests/test_reviews.py tests/test_tasks.py tests/test_authorization.py tests/test_artifacts.py tests/test_audit.py
cd backend && ruff check app/modules/reviews app/modules/tasks tests/test_reviews.py tests/test_tasks.py
(metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78))
cd backend && coverage report --include='app/modules/reviews/*' --precision=2 --fail-under=90
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture,
reuse/dedup, and test-delta.

## Human review focus

Atomic state matrix, route remains closed, race resolution, and no contribution
or storage side effect gap hidden by tests.

## Stop condition

Merge, record automated memory, and stop. Do not start 09A.
