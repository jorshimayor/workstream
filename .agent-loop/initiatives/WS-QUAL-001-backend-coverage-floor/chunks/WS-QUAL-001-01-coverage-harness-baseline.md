# Chunk Contract: WS-QUAL-001-01 Coverage Harness And Baseline

## Goal

Create reproducible full-backend coverage measurement, isolate the test
database from concurrent worktrees, record the clean main baseline, and enforce
an initial floor that later chunks may only raise.

## Risk and SLA

- Risk: L1 CI/test infrastructure
- SLA: P1

## Allowed files

```text
backend/pyproject.toml
backend/tests/conftest.py
backend/tests/test_coverage_contract.py
backend/tests/test_api_contract_e2e.py
backend/scripts/coverage_policy.py
backend/scripts/run_isolated_tests.py
backend/scripts/api_contract_e2e.py
backend/scripts/week2_api_e2e.py
.github/workflows/backend.yml
docs/operations_backend_testing.md
.agent-loop/initiatives/WS-QUAL-001-backend-coverage-floor/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
backend/app/**
backend/alembic/**
public API or schema changes
coverage omit/include rules that exclude application modules
coverage pragmas
test deletion or weakened assertions
```

## Acceptance criteria

- `pytest-cov` is a development dependency with compatible bounds.
- Coverage source is exactly `app`; the report includes every importable
  application module and fails below the configured floor.
- CI runs the same complete-suite coverage command used locally.
- `WORKSTREAM_TEST_DATABASE_URL` is the authoritative child-process URL. The
  runner accepts the admin DSN only from `WORKSTREAM_TEST_ADMIN_DATABASE_URL`,
  validates local Postgres, provisions only a name matching
  `^workstream_test_[a-f0-9]{12}$`, sets child test/runtime URLs, and terminates
  and drops only its owned database in `finally` cleanup.
- `test_coverage_contract.py` and `test_api_contract_e2e.py` are statically
  proven DB-free before their direct focused command; every DB-capable command
  runs through the provisioner.
- API drills accept that strict local derived name; ordinary proof rejects the
  nonlocal write-risk override. Credentials and credentialed URLs never appear
  in output or evidence.
- Coverage JSON is checked against the complete `backend/app/**/*.py` inventory.
  The policy rejects omit/include/exclusion rules, application coverage pragmas,
  narrowed `--cov`, and missing modules.
- A clean `origin/main` evidence summary records tree SHA, exact covered/total
  statements, six-decimal percentage/floor, tool versions, safe database name,
  and Alembic head.
- The policy compares the configured floor and evidence with the merge base and
  fails any decrease; unchanged denominators also require non-decreasing covered
  statements.
- The policy preserves the existing install, full Ruff, docstring, complete
  pytest, and API drill workflow gates and rejects bypass flags or test narrowing.
- `docs/operations_backend_testing.md` documents safe local provisioning and
  cleanup, env-only credentials, URL redaction, exact local/CI commands, ratchet
  updates, API drill use, and troubleshooting without the write-risk override.
- No production file changes.

## Verification commands

```bash
(cd backend && .venv/bin/python -m pip check)
(cd backend && .venv/bin/python -m ruff check tests scripts)
(cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=<local-admin-dsn> .venv/bin/python scripts/run_isolated_tests.py -- .venv/bin/python -m pytest -q --cov=app --cov-report=term-missing --cov-report=json:coverage.json)
(cd backend && .venv/bin/python scripts/coverage_policy.py --coverage-json coverage.json --base-ref origin/main --initialize --minimum-milestone=<six-decimal-baseline> --max-implementation-lines=500 --check-test-delta)
(cd backend && .venv/bin/python -m pytest -q tests/test_coverage_contract.py tests/test_api_contract_e2e.py)
(cd backend && .venv/bin/python -m pip check)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
```

## Required reviewers

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

## Human review focus

Confirm the measurement includes all application code, database isolation is
real, the initial ratchet matches clean evidence, and no gate was weakened.

## Stop condition

Stop if reproducible measurement requires production changes, application
exclusions, suppression pragmas, or shared mutable database state.
After merge, update and merge initiative status/evidence plus global loop state,
queue, and review log; chunk 02 remains inactive until that memory completes and
the user gives a separate start signal.
