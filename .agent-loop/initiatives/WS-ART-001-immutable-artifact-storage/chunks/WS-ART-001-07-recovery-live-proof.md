# Chunk Contract: WS-ART-001-07 Real API And Provider Proof

Initiative: `WS-ART-001` | Risk: L1 | Status: Proposed after 06B

## Goal

Prove the complete artifact lifecycle through real HTTP APIs, PostgreSQL,
Redis/Celery, LocalStorage, MinIO, and a secret-free AWS S3 readiness profile
without direct database inspection or Terminal Benchmark product coupling.

## Allowed Files

- real API drill under `examples/artifact_lifecycle/proof_tools/` using
  standalone sanitized fixture material
- professional generated evidence report inputs and committed bounded PDF
- provider conformance/readiness harness and operations runbook
- focused proof-only tests under `examples/artifact_lifecycle/tests/` that
  cannot load in production and are excluded from the executable-tooling
  coverage source
- `.github/workflows/backend.yml` changes needed to run bounded proof
- `scripts/test_agent_gates.py` only to assert both exact Chunk 07 workflow
  commands, source sets, thresholds, and cumulative retention
- related chunk memory and trust evidence

## Not Allowed

- new product behavior or schema;
- Snorkel/Termius paths, names, private material, or live work references;
- committed AWS credentials or provider object references;
- direct database setup/inspection as proof of API behavior;
- Flow Node runtime;
- production test hooks, corruption routes, or unbounded logs in Git.

## Acceptance Criteria

- a standalone project guide is ingested, verified, snapshotted, and processed
  through setup using real APIs and visible async status.
- a contributor uploads exact artifacts, seals them, runs pre-submit, creates a
  submission, and automatically enters `evaluation_pending`.
- post-submit reads the same immutable artifact-set commitment and stores
  checker logs/outputs as verified artifacts.
- post-submit remains `evaluation_pending` while execution or infrastructure
  retry is active. Durable completion preserves the existing checker-owned
  route to `needs_revision` with `outcome_source = auto_checker` or to
  `review_pending`; the proof creates no WS-REV aggregate, queue, lease,
  assignment, or decision.
- provider outage produces infrastructure pending/retry, not contributor or
  review outcomes; restart recovers through the periodic scanner.
- pre-submit outage exhausts to `pre_submission_infrastructure_unavailable`,
  preserves the exact sealed unconsumed attempt, and continues on contributor
  retry without manager/operator approval; post-submit outage separately keeps
  `evaluation_pending` and uses checker retry infrastructure.
- changed/truncated/missing bytes and stale/duplicate Celery executions are
  proven safely.
- Operator observes jobs, retries with a reason, and reads terminal recovery
  through APIs only.
- LocalStorage and real MinIO pass conformance. AWS S3 requires a
  workload-identity private live smoke, least-privilege negative-action
  proof, anonymous-read denial, and read-only proof that no enabled lifecycle
  deletion/expiration rule can match the completed-object prefix before that
  profile is declared production-eligible. Unproved AWS remains inactive.
- no test-only route or control exists in the production application image.
- the evidence PDF is concise, structured, redacted, and includes request/
  response summaries, async timelines, immutable hashes, failures, and final
  invariants without private provider details.
- executable proof tooling lives in the dedicated
  `examples/artifact_lifecycle/proof_tools/` package and remains at least 90
  percent covered; tests and fixtures are outside that measured source, and
  repository coverage does not decrease.
- backend CI installs this chunk's exact focused 90 percent gates, preserves
  every earlier scoped 90 percent gate, and retains the exact 78 percent
  repository command below; `scripts/test_agent_gates.py` fails on workflow
  command, source-set, threshold, or cumulative-retention drift.
- this chunk owns an isolated `examples/artifact_lifecycle/docker-compose.yml`
  with digest-pinned API, Celery worker, Postgres, Redis, and MinIO services;
  earlier chunks never rely on services they do not own.

## Exact CI Coverage Gates

```bash
coverage report --include='app/adapters/artifacts/*,app/interfaces/artifacts.py,app/modules/artifacts/*' --precision=2 --fail-under=90
coverage report --include='app/interfaces/external_services.py' --precision=2 --fail-under=90
coverage report --include='app/core/config.py' --precision=2 --fail-under=90
coverage report --include='app/workers/*' --precision=2 --fail-under=90
coverage report --include='app/api/router.py' --precision=2 --fail-under=90
coverage report --include='app/modules/projects/*' --precision=2 --fail-under=90
coverage report --include='app/modules/tasks/*' --precision=2 --fail-under=90
coverage report --include='app/modules/checkers/*' --precision=2 --fail-under=90
coverage report --include='app/adapters/project_agents/*,app/interfaces/project_agents.py' --precision=2 --fail-under=90
python -m pytest examples/artifact_lifecycle/tests -q --cov=examples/artifact_lifecycle/proof_tools --cov-report=term-missing --cov-fail-under=90
```

## Verification

```bash
docker compose -f examples/artifact_lifecycle/docker-compose.yml up -d --build --wait
backend/.venv/bin/python -m examples.artifact_lifecycle.proof_tools.real_api_drill
(cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest tests/test_artifact_store_conformance.py tests/test_artifact_real_api.py -q --cov=app.modules.artifacts --cov=app.adapters.artifacts --cov-report=term-missing --cov-fail-under=90)
backend/.venv/bin/python -m pytest examples/artifact_lifecycle/tests -q --cov=examples/artifact_lifecycle/proof_tools --cov-report=term-missing --cov-fail-under=90
metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78)
WORKSTREAM_ARTIFACT_PROOF_PROFILE=aws_s3 backend/.venv/bin/python -m examples.artifact_lifecycle.proof_tools.provider_live_smoke
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_markdown_links.py
python3 scripts/test_agent_gates.py
```

## Required Reviewers

Senior engineering, architecture, QA/test, security/auth, product/ops,
reuse/dedup, CI integrity, test delta, and docs.

## Human Review Focus

- Does the proof resemble real human/API use rather than database-assisted
  testing?
- Is all example material standalone and legally safe?
- Is AWS S3 viability proved without claiming unexecuted provider proof?
