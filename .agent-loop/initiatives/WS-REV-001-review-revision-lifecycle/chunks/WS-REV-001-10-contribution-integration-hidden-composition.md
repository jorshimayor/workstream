# Chunk Contract: WS-REV-001-10

## Goal

Install the exact merged CON flush-only participant and create the first hidden
service capable of committing a canonical Review decision atomically with task,
contribution, award, audit, and outbox effects. Production routes remain absent.

## Risk class

L1 canonical judgment, contribution/conditional-compensation, and composition
integrity.

## Allowed files

```text
backend/app/modules/reviews/{schemas,service,router}.py
backend/app/composition/review_lifecycle.py only to install the exact merged CON participant
backend/tests/test_{reviews,contributions,compensation,authorization,api_contract_e2e}.py
backend/scripts/api_contract_e2e.py
docs/operations_reviewer_workflow.md
docs/operations_payment_reputation.md
.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/**
.agent-loop/merge-intents/WS-REV-001-10.json
```

## Not allowed

```text
new contribution policy, rule, award, fulfillment, or projection behavior in review code
ContributionRecordRequested compatibility event
optional or no-op CON participant
ART capability call, provider I/O, or contribution-evidence artifact write in the transaction
production `/api/v1` review-router registration
CON router, repository, policy, outbox, award, fulfillment, or projection edits
submitter contribution for needs_revision or reject
reputation scoring
```

## Acceptance criteria

- `review.decision` uses AUTH's prepared mutation protocol: AUTH locks exact
  reviewer authority; REV locks idempotency, lifecycle fence, queue, lease,
  task, assignment, versioned Submission, predecessor Review, packet/evidence
  facts; REV recomposes final context; AUTH evaluates once and stages evidence;
  REV/task/CON participants flush; the caller commits once.
- Every committed Review creates exactly one reviewer
  `contribution_type=completed_review`. `accept` additionally creates exactly one
  submitter `contribution_type=accepted_submission`; `needs_revision` and
  `reject` create none for the submitter.
- CON receives locked Review, ReviewLease, Submission row/version,
  TaskAssignment, canonical reviewer/submitter, project/task, originating
  AuthorizationDecision, request/correlation references, and the exact frozen
  reviewer/submitter `ContributionPolicyVersion` references.
- The ART submission/checker cutover has persisted a server-derived verified
  `Submission.artifact_hash` on the existing versioned Submission. CON copies it
  to `ContributionRecord.artifact_hash`. Caller `package_hash`, a renamed
  source-digest field, or a live ART lookup cannot substitute.
- Database/transaction validation requires Review/reviewer/lease consistency,
  Review/Submission consistency, Submission contributor/assignment consistency,
  and same project/task lineage. Current TaskAssignment, current project policy,
  or caller-supplied actor/hash facts cannot substitute.
- CON evaluates the frozen ContributionRule. Explicit unpaid creates no award;
  payable creates immutable money and/or project-points CompensationAward rows.
  Adapters fulfill awards after commit and never decide eligibility.
- Derived inserts inside `review.decision` do not invent
  `contribution.materialize` or `compensation.award.materialize` actions.
- Review, findings, ReviewEvidenceArtifact links, resolutions, queue/lease,
  task/assignment effects, contributions, awards, audit, and shared-outbox rows
  commit or roll back together. CON never commits or performs network/provider I/O.
- CON failure rolls back the entire decision. No no-op participant, post-commit
  canonical contribution repair, or Review-only success path exists.
- Exact replay duplicates no Review, contribution, award, audit, or outbox row;
  changed replay conflicts. Replay reauthorizes result disclosure.
- Independent Postgres barriers cover decision versus expiry, reviewer
  revocation, binding-state drift, and duplicate/changed replay in both orders.
  Fault injection after every REV/task/CON/audit/outbox stage proves zero partial
  state and bounded database retry behavior.
- Initial revision-preparation failure on `needs_revision` rolls back Review,
  task/assignment, lease, preparation, reviewer contribution/award, audit, and
  outbox state together.
- Same-reviewer and takeover matrices prove v1 `needs_revision` then v2
  accept/reject follows exact Submission/Review predecessors, attributes each
  reviewer record to the actual Review author, and creates the sole submitter
  record only for accepted v2.
- Forward/backward guide rebase leaves TaskAssignment ContributionPolicyVersion
  unchanged; each Review uses its lease freeze; reviewer award eligibility is
  decision-neutral for the same frozen rule.
- Chain reads expose bounded relationship metadata only. Historical artifact
  bytes remain inaccessible without the active exact packet manifest.
- Internal API contracts use `/api/v1` and stable errors, but production OpenAPI
  proves every lifecycle route absent.
- Every ReviewService construction uses the single fail-closed composition with
  the exact merged CON participant. Review services import no concrete CON or
  ART implementation.
- This chunk supplies hidden decision behavior and its feature-manifest delta.
  AUTH activates `review.decision` only after this chunk merges; REV-13 later
  exposes the route. This chunk changes no action availability.
- Optional contribution-evidence projection is outside this chunk and outside
  core release readiness. Its absence/outage cannot affect canonical truth.

## Verification

```text
cd backend && pytest -q tests/test_reviews.py tests/test_contributions.py tests/test_compensation.py tests/test_authorization.py tests/test_api_contract_e2e.py
cd backend && ruff check app/modules/reviews app/composition/review_lifecycle.py tests/test_reviews.py
(metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78))
cd backend && coverage report --include='app/modules/reviews/*' --precision=2 --fail-under=90
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
reuse/dedup, and test-delta.

## Human review focus

AUTH-first lock/evaluation order, mandatory CON participant, exact immutable
lineage, no ART call, contribution creation matrix, replay, rollback, and route
absence.

## Stop condition

Merge, record automated memory, and stop. Do not start 11.
