# Chunk Contract: WS-REV-001-04

## Goal

Add immutable Review, finding, submitter response, resolution, evidence
relation, decision idempotency, and projection-request persistence.

Chunk start requires the merged shared transactional-outbox contract. All
projection requests below use that shared foundation.

## Risk class

L1 schema, audit, and evidence ownership.

## Allowed files

```text
backend/app/modules/reviews/{models,repository,schemas}.py
backend/app/modules/tasks/models.py only for relationships/FKs
backend/app/db/models.py
backend/alembic/versions/<activation-next>_review_chain.py
backend/tests/test_{alembic,audit,reviews}.py
docs/operations_reviewer_workflow.md only for deployment/rollback/immutability notes
.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/**
.agent-loop/merge-intents/WS-REV-001-04.json
```

## Not allowed

```text
public routes, decision service, task effects, or workers
artifact provider implementation
grant or permission implementation
contribution/compensation models
mutable Review/finding/resolution rows
review-private outbox or delivery queue
```

## Acceptance criteria

- One Review per Submission and synchronized predecessor-chain constraints.
- `ReviewEvidenceArtifact` is an immutable REV semantic relation over one
  finalized ART binding. Before decision it is identified by exact lease,
  operation kind, evidence slot, and idempotency identity; after decision it may
  be linked set-once to the exact ReviewFinding or SubmissionFindingResponse.
  Binding identity and scope never change. This is not artifact byte storage,
  a provider reference, or a mutable ReviewAttempt.
- `Review.reviewer_id` is the exact canonical human `ActorProfile.id` on its
  ReviewLease; a composite constraint rejects a crossed lease/reviewer and no
  external subject, email, legacy profile ID, service actor, or system principal
  may be persisted as the human reviewer.
- Database constraints require `Review(Sn).prior_review_id` to identify the
  Review whose Submission is `Submission(Sn).supersedes_submission_id`; crossed
  task, version, Submission, or Review predecessor chains fail under direct SQL.
- Immutable findings use only blocking/advisory severity.
- Finding responses and resolutions are immutable and uniquely scoped.
- Evidence relation rows reference canonical ArtifactBinding IDs and are unique.
- Decision idempotency commits only with one canonical Review and detects changed
  payload reuse.
- `ReviewDecisionRequest` reuses `canonical_json_hash`, shared request and
  correlation identifiers, and the reserve/lock/complete transaction shape,
  while keeping a review-specific operation/response matrix. No cloned JSON
  canonicalizer or second generic idempotency framework is added.
- One canonical shared-outbox projection event commits with Review. Shared
  outbox delivery state and ART receipts are reused; no review-private
  projection request/status table exists.
- The reject-Review reference on TaskAssignment is added now that the Review
  table exists and is constrained to a reject Review for the same task/current
  assignment.
- Database triggers or equivalent guards prevent prohibited update/delete of
  canonical review-chain records.
- Review events append through the merged shared AuditEvent participant in the
  caller transaction. No `ReviewAuditEvent`, review-private audit repository, or
  commit-owning audit writer exists.
- Deployment notes define ordering, historical-row handling, rollback limits
  after immutable rows exist, and proof queries without synthetic backfill.

## Verification

```text
cd backend && alembic upgrade head
cd backend && pytest -q tests/test_alembic.py tests/test_audit.py tests/test_reviews.py
cd backend && ruff check app/modules/reviews app/modules/audit tests/test_reviews.py tests/test_audit.py tests/test_alembic.py
(metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78))
cd backend && coverage report --include='app/modules/reviews/*' --precision=2 --fail-under=90
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
reuse/dedup, and test-delta.

## Human review focus

Immutability enforcement, predecessor integrity, evidence ownership, and
idempotency atomicity. Multi-version/takeover chain negatives receive explicit
human attention.

## Stop condition

Merge, record automated memory, and stop. Do not start 05.
