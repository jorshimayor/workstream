# Chunk Contract: WS-ART-001-02D Operator Artifact Operations

Initiative: `WS-ART-001` | Risk: L1 | Status: Proposed after 02C2 and AUTH-15

## Goal

Expose exact authorized Operator read/retry/recovery/audit APIs and add
fail-closed production-readiness inspection without activating a provider
profile or product cutover.

## Allowed Files

- artifact router and public/internal schemas
- artifact service/repository read and retry methods
- API router composition root
- S3-compatible provider-profile readiness checks; profiles remain inactive
- artifact call sites consuming the exact existing Authorization Service
  permissions mapped below; no Authorization Service owner files
- focused route, authorization, redaction, readiness, and real-API tests
- `.github/workflows/backend.yml` only to expand the exact 90 percent scoped gate
- `scripts/test_agent_gates.py` only to assert the exact workflow command,
  source set, threshold, and cumulative retention
- directly related operations docs and chunk memory

## Not Allowed

- contributor, reviewer, or project-owner artifact operations;
- guide, task, submission, checker, review, contribution, payment, or
  reputation cutover;
- database-inspection-only operational proof;
- provider object references, endpoints, credentials, signed URLs, or raw
  provider bodies in responses;
- provider delete/retain/release or Flow Node.
- Authorization Service implementation, permission registration, or policy
  changes.

## Acceptance Criteria

- exact Operator APIs exist for resource-scoped binding discovery, replicas,
  receipts, verification job, retry, recovery-attempt read, and artifact audit
  listing.
- AUTH-07, AUTH-08, AUTH-09, and AUTH-15 are merged before this chunk starts,
  providing the registry, Operator grants, service principals, and exact
  artifact worker permissions; this chunk registers no permission and creates
  no authority fallback.
- binding, replica, receipt, verification-job, and recovery-attempt reads use,
  respectively, `artifact.binding.read`, `artifact.replica.read`,
  `artifact.receipt.read`, `artifact.verification_job.read`, and
  `artifact.recovery_attempt.read`; provider-job retry uses
  `artifact.verification_job.retry`, recovery execution uses
  `artifact.recovery_attempt.execute`, and artifact audit listing uses
  `artifact.audit.read`.
- internal verification uses a provisioned service principal with
  `artifact.verification.execute`; periodic scan publication uses
  `artifact.pending_work.scan`. These permissions remain separate and do not
  imply one another.
- every route calls an exact Authorization Service action/resource decision;
  broad role checks are not authority.
- retry requires a reason, client idempotency key, and expected source-job CAS
  version, accepts
  only exhausted terminal `provider_unavailable`, and returns `202` with
  recovery-attempt, source-job, and retry-job IDs. Exact request replay returns
  those original IDs; altered replay conflicts. Every other job state fails
  without side effects.
- recovery-attempt GET returns immutable source-job status, current retry-job
  status, terminal mapping, chain identity, and audit IDs.
- binding discovery starts from an exact known product resource and exposes the
  stable Workstream IDs needed for diagnosis/recovery; audit filters are exact.
- cross-project and unauthorized callers are denied without leaking existence.
- responses are bounded, paginated where needed, and contain no provider
  internals or secrets.
- the AWS S3 production profile instantiates the adapter through the typed
  factory; LocalStorage and invalid production profiles fail closed.
- exact internal service-principal authorization activates every verification
  provider read, periodic scan publication, and recovery job; no 02C1 or 02C2
  mechanic runs before this gate.
- readiness exposes every prerequisite for private-bucket, credential,
  anonymous-read-negative, and completed-prefix lifecycle proof, but no profile
  becomes production-active in this chunk. Chunk 07 owns live proof and
  AWS activation.
- readiness does not write or mutate provider objects.
- real HTTP tests prove the full Operator path without direct database reads.
- changed subsystem coverage is at least 90 percent and repository coverage
  does not decrease.
- backend CI installs this chunk's exact focused 90 percent gate, preserves
  every earlier scoped 90 percent gate, and retains the exact 78 percent
  repository command below; `scripts/test_agent_gates.py` fails on workflow
  command, source-set, threshold, or cumulative-retention drift.

## Exact CI Coverage Gates

```bash
coverage report --include='app/adapters/artifacts/*,app/interfaces/artifacts.py,app/modules/artifacts/*' --precision=2 --fail-under=90
coverage report --include='app/interfaces/external_services.py' --precision=2 --fail-under=90
coverage report --include='app/core/config.py' --precision=2 --fail-under=90
coverage report --include='app/workers/*' --precision=2 --fail-under=90
coverage report --include='app/api/router.py' --precision=2 --fail-under=90
```

## Verification

```bash
docker compose up -d --wait postgres redis minio
(cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest tests/test_artifact_operator_api.py tests/test_artifact_authorization.py tests/test_config.py -q --cov=app.modules.artifacts --cov=app.adapters.artifacts --cov=app.api.router --cov-report=term-missing --cov-fail-under=90)
metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78)
(cd backend && .venv/bin/ruff check app tests)
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/test_agent_gates.py
```

## Required Reviewers

Senior engineering, architecture, QA/test, security/auth, product/ops,
reuse/dedup, CI integrity, test delta, and docs.

## Human Review Focus

- Are the Operator actions and resources exact?
- Can operations be understood without database access?
- Do readiness results keep AWS S3 inactive until its live proof succeeds?
