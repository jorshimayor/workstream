# Chunk Contract: WS-REV-001-08

## Goal

Freeze the immutable review-decision request, pure validation, task-effect
participant, lock/fact contract, and CON participant input for all three
decisions. Do not create a canonical Review-committing service before CON merges.

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
any code path that commits a canonical Review without the exact CON participant
remote storage calls inside the transaction
mutation of prior Submission, Review, ReviewFinding, or FindingResolution
reputation or fulfillment logic
```

## Acceptance criteria

- The frozen transaction contract rechecks exact reviewer grant, lease ownership/
  expiry, no-self-review, queue state, idempotency, predecessor chain, packet
  manifest, evidence relations, and stabilized binding facts using database time.
- The command declares planned `review.decision`. Mutation choreography is AUTH
  prepare/authority lock -> REV locks and final fact recomposition -> one AUTH
  evaluation -> REV/task/CON participants flush -> route commit once. No plain
  mutation-time `require()` or serialized authorization handle substitutes.
- Decision/finding/evidence/resolution rules match the canonical spec.
- Task effects use the task-owned `TaskReviewEffectsParticipant` with the
  caller's AsyncSession. It flushes without commit, reuses TaskRepository and
  lifecycle guards internally, and is the only path for review-driven task or
  assignment effects; review code never imports TaskRepository.
- Accept effects complete assignment and target `accepted`; needs revision keeps
  assignment active; human reject blocks only that assignment and targets
  canonical `rejected` with reason. Administrative closure is not a decision.
- Pure tests prove the future atomic write set: Review, findings,
  ReviewEvidenceArtifact links, resolutions, queue/lease, task effects, audit,
  projection event, CON records, awards, and outbox. This chunk does not expose a
  service capable of committing that set.
- Exact replay contract returns the Review after REV-10; changed replay fails.
- Idempotency is bound to actor, operation, lease, submission, and canonical
  payload. Replay reauthorizes disclosure for the same actor without requiring
  a consumed lease to remain active; cross-actor, revoked-disclosure, or changed
  payload replay fails without revealing the prior result.
- The decision actor is the active canonical human `ActorProfile.id` that owns
  the exact ReviewLease. UUID shape alone is insufficient; a service actor,
  system principal, legacy ID, or external subject cannot decide a Review.
- No hidden or production composition can commit a Review. Absence of the exact
  CON participant fails construction; no optional/no-op path exists.
- This chunk proves command-specific lock planning and the task participant. Full
  decision races, participant rollback, and canonical commits move to REV-10
  after CON merges.
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

Complete decision input/effect contract, no premature canonical commit, route
absence, and no contribution or storage side-effect gap hidden by tests.

## Stop condition

Merge, record automated memory, and stop. Do not start 09A.
