# Chunk Contract: WS-REV-001-10

## Goal

Join the reviewed WS-CON-07 transaction participant to the decision kernel and
prove the complete internal API composition while production lifecycle routes
remain unregistered.

## Risk class

L1 payment, canonical judgment, and composition integrity.

## Allowed files

```text
backend/app/modules/reviews/{schemas,service,router}.py
backend/app/composition/review_lifecycle.py only to install the exact merged WS-CON participant
backend/tests/test_{reviews,contributions,compensation,authorization,api_contract_e2e}.py
backend/scripts/api_contract_e2e.py
docs/operations_reviewer_workflow.md
docs/operations_payment_reputation.md
.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/**
.agent-loop/merge-intents/WS-REV-001-10.json
```

## Not allowed

```text
new contribution, award, compensation, or fulfillment policy in review code
ContributionRecordRequested compatibility event
route activation with optional/no-op production participant
production `/api/v1` review-router registration
submitter contribution for needs_revision or reject
reputation scoring
```

## Acceptance criteria

- Every committed Review creates exactly one reviewer contribution.
- Accept additionally creates exactly one submitter contribution tied to the
  accepted Submission version; other decisions create none for the submitter.
- The reviewer ContributionRecord maps exactly to
  `contribution_type=completed_review`, `contributor_id=Review.reviewer_id`,
  `source_review_id=Review.id`,
  `source_review_lease_id=Review.review_lease_id`,
  `source_task_assignment_id=Submission.task_assignment_id`,
  the CON-03C-adopted Submission row/version fields identifying
  `Review.submission_id`, the constrained project/task,
  `source_submission_artifact_digest` from the adopted immutable verified
  Submission packet-digest field, and
  `compensation_policy_version_id=ReviewLease.reviewer_compensation_policy_version_id`.
- The accept-only submitter ContributionRecord maps exactly to
  `contribution_type=accepted_submission`,
  `contributor_id=Submission.contributor_id` (the final AUTH-14 canonical
  Submission owner field), `source_review_id=Review.id`, null
  `source_review_lease_id`, the same Submission/TaskAssignment/project/task and
  verified packet digest, and
  `compensation_policy_version_id=TaskAssignment.submitter_compensation_policy_version_id`.
  It is tied to the accepted Submission version, not a mutable task projection.
- Database/transaction validation requires Review reviewer/lease consistency,
  Review/Submission consistency, Submission contributor/assignment consistency, and
  same project/task lineage. Frozen lease-versus-assignment policy sources drive
  deterministic WS-CON awards; current project policy is never substituted.
- `Review.reviewer_id`, `Submission.contributor_id`, and
  `TaskAssignment.contributor_id` are canonical human `ActorProfile.id` values.
  The participant rejects external
  subjects, legacy profile IDs, service/system actors, or merely UUID-shaped
  values that are not the exact constrained human lineage.
- CON-03C, CON-07, and this chunk use one identical schema vocabulary for the
  Submission row/version and packet digest. This chunk is blocked if CON-01 has
  not reconciled the current `submission_id`/`submission_version_id` and
  `package_hash`/`source_submission_artifact_digest` drift or if ART has not
  supplied the verified digest binding.
- Review, task/assignment effects, contributions, awards/instructions, audit,
  and transactional outbox commit or roll back together.
- Exact decision replay duplicates no contribution, award, or outbox effect.
- Internal decision API contract uses `/api/v1`, stable error codes, and
  required idempotency while production OpenAPI proves the router absent.
- Chain reads expose authorized versions, reviews, findings, responses,
  resolutions, guide transitions, and bounded lease summaries. They expose
  historical artifact metadata only as binding ID, relation purpose/kind,
  media type, verification/availability state, and required/optional class.
  They exclude content/digest, provider locators/keys/CIDs, signed capabilities,
  replica/receipt details, service scopes, and credentials. Content outside the
  caller's active current packet is never returned.
- OpenAPI and end-to-end contract tests prove the production participant cannot
  be omitted from the internal composition and no public lifecycle route is
  registered.
- Every hidden ReviewService/router construction uses the single fail-closed
  composition assembly with the exact merged WS-CON participant; no concrete
  WS-CON import in review services and no optional/no-op constructor exists.
- Claims, releases, declines, preference/lease expiry, administrative closure,
  artifact failure, and projection failure create no contribution, award,
  fulfillment, or payment instruction.
- Independent real-Postgres fault injection after reviewer contribution,
  submitter contribution, award/instruction, audit, and shared-outbox stages
  proves zero partial Review/task/lease/CON/audit/outbox state. Concurrent exact
  replay returns one result; concurrent changed replay conflicts, with no
  duplicated participant output.
- Integrated initial-preparation failure on `needs_revision` rolls back Review,
  task/assignment, lease, preparation, reviewer contribution/award, audit, and
  outbox state together.
- End-to-end same-reviewer and takeover matrices prove v1 `needs_revision` then
  v2 accept/reject links Review(v2) to Review(v1) through the exact Submission
  predecessor, creates one reviewer contribution for each exact Review and its
  actual reviewer, and creates the sole submitter contribution only for accepted
  v2 and its submitter. Crossed CON Review/Submission/actor references fail.
- Direct participant tests also cross assignment, lease, compensation-policy,
  packet-digest, project, and task references and require atomic rejection.
- Forward and backward Project Guide rebase tests prove submitter compensation
  remains the TaskAssignment freeze, each Review uses its own lease freeze, and
  reviewer award calculation is decision-neutral across `accept`,
  `needs_revision`, and `reject`.

## Verification

```text
cd backend && pytest -q tests/test_reviews.py tests/test_contributions.py tests/test_compensation.py tests/test_authorization.py tests/test_api_contract_e2e.py
cd backend && ruff check app/modules/reviews app/modules/contributions app/modules/compensation app/api/router.py tests/test_reviews.py
(metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78))
cd backend && coverage report --include='app/modules/reviews/*' --precision=2 --fail-under=90
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
reuse/dedup, and test-delta.

## Human review focus

Atomic money boundary, exact creation matrix, replay, rollback, composition
fail-closed behavior, and continued public absence.

## Stop condition

Merge, record automated memory, and stop. Do not start 11.
