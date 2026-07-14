# Chunk Contract: WS-ART-001-02C1 Verification Publication And Fencing

Initiative: `WS-ART-001` | Risk: L1 | Status: Proposed after 02B1

## Goal

Add durable complete-object verification publication, PostgreSQL execution
fencing, immutable observations, and receipts without recovery attempts,
Operator routes, or product cutovers.

## Allowed Files

- one verification migration;
- artifact verification models, schemas, repository, service, and contracts;
- Celery verification task and periodic publication scanner;
- `backend/app/core/config.py` for scanner SLA, execution lease, complete-read
  deadline, and persistence margin;
- generic audit repository only when existing audit support is insufficient;
- focused PostgreSQL/Celery/artifact tests;
- `.github/workflows/backend.yml` only to expand the exact 90 percent scoped gate;
- `scripts/test_agent_gates.py` only to assert that backend CI retains this
  chunk's exact scoped coverage sources and fail-closed 90 percent threshold;
- directly related operations docs and chunk memory.

## Not Allowed

- recovery-attempt models, Operator/public routes, or manual retry contracts;
- guide, task, submission, checker, or review cutover;
- provider mutation replay, overwrite, delete, retain, or release;
- task-claim or reviewer-lease changes;
- production dispatch before the exact internal Authorization Service decision
  and service principal are owned by 02D.

## Acceptance Criteria

- provider acknowledgement yields `stored_pending_verification`, never a
  bindable replica;
- Celery performs a fresh complete-object read and verifies Workstream SHA-256
  and byte count;
- a periodic PostgreSQL scanner republishes pending and expired work within a
  configured SLA and duplicate publication is harmless;
- acquisition uses PostgreSQL time, a fresh executor UUID, lease expiry, and an
  atomically incremented execution generation;
- terminal writes require matching executor and generation; stale executors
  write no state, receipt, or audit fact;
- the result matrix handles verified, missing, integrity mismatch, provider
  unavailable, conflict, and stale executor outcomes;
- missing yields `missing/unavailable/unknown`; integrity mismatch yields
  `integrity_mismatch/available/invalid` and cannot reset;
- complete reads enforce a total deadline shorter than the lease by a tested
  persistence margin, including continuously progressing slow streams;
- mechanics remain inactive until 02D registers and tests exact internal
  authorization;
- migrations prove fresh, prior-head, populated, and empty round-trip behavior;
- changed subsystem coverage is at least 90 percent and repository coverage
  remains at least 78 percent;
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
```

## Verification

```bash
docker compose up -d --wait postgres redis minio
(cd backend && .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest tests/test_alembic.py tests/test_artifact_verification.py tests/test_config.py -q --cov=app.modules.artifacts --cov=app.core.config --cov-report=term-missing --cov-fail-under=90)
metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78)
(cd backend && .venv/bin/ruff check app tests)
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/test_agent_gates.py
```

## Required Reviewers

Senior engineering, architecture, QA/test, security/auth, product/ops,
reuse/dedup, CI integrity, test delta, and docs.

## Human Review Focus

- Is verification independent of upload acknowledgement?
- Can any stale or duplicate Celery executor write terminal state?
- Are all timing and publication guarantees explicit and testable?
