# Chunk Contract: WS-QUAL-001-01B Coverage Policy And Baseline

## Goal

Turn the isolated complete-backend coverage measurement into a reproducible,
non-decreasing CI policy with machine-readable baseline evidence. This chunk
establishes the ratchet; it does not add tests merely to raise coverage.

## Risk And Scope

- Risk: L1 CI/test policy and evidence integrity
- SLA: P1
- Implementation cap: 500 changed lines outside `.agent-loop`
- Allowed:
  - `backend/pyproject.toml`
  - `backend/scripts/coverage_policy.py`
  - `backend/tests/test_coverage_contract.py`
  - `.github/workflows/backend.yml`
  - `docs/operations_backend_testing.md`
  - `.agent-loop/initiatives/WS-QUAL-001-backend-coverage-floor/evidence/coverage-baseline.json`
  - WS-QUAL/global loop memory and review evidence
- Forbidden:
  - `backend/app/**`, migrations, schemas, public APIs, auth, product behavior,
    runner/API-drill implementation, unrelated tests, coverage exclusions or
    pragmas, skipped/xfail tests, weakened assertions, or threshold reduction

## Acceptance Criteria

- `pytest-cov==7.1.0` remains an explicit development dependency. Coverage
  measures statements for exactly `app`, with report precision six and one
  configured `fail_under` equal to the initialized six-place baseline floor.
- Coverage policy inventories every `backend/app/**/*.py` file and requires a
  corresponding file entry in coverage JSON. It rejects missing files, a
  narrowed `--cov`, `omit`, `include`, `source`, `exclude_lines`,
  `exclude_also`, and application coverage pragmas.
- The configured floor, current measured percentage, and evidence percentages
  use `Decimal` or integer arithmetic. The initialized floor is the current
  covered-statements percentage truncated, never rounded up, to six places.
- Baseline evidence is canonical sorted JSON with a trailing newline at the
  allowed evidence path. Schema v1 contains exactly `schema_version`,
  `base_merge_sha`, `measured_tree_sha`, `covered_lines`, `num_statements`,
  `measured_percent`, `configured_floor`, `minimum_milestone`,
  `python_version`, `coverage_version`, `pytest_cov_version`, `database_name`,
  and `alembic_head`. Decimal strings have six places; SHAs are full lowercase
  hex; no URL, password, credential, or role secret is stored.
- Initialization is allowed only when the merge base lacks baseline evidence.
  It requires runner metadata for current `HEAD`, exactly one current Alembic
  head, a strict derived database name, and a clean implementation tree before
  writing evidence. Later validation requires branch and base evidence.
- `measured_tree_sha` names the commit containing all final non-evidence code,
  test, config, workflow, and runbook changes. Evidence/status/review-only
  commits may follow it; executable changes after it invalidate the binding.
- Base comparison prevents a lower configured floor or measured covered count
  when the application denominator is unchanged. Denominator changes fail
  closed and require explicit CI-integrity review in a separately amended
  contract rather than an implicit bypass.
- The policy imports `changed_files`, `numstat`, and `diff_text` from the root
  `scripts/workstream_agent_gate.py`; it does not duplicate Git-diff parsing.
  It enforces allowed scope, the 500-line implementation cap, and test-delta
  integrity for deleted assertions, skips/xfail, selection narrowing, coverage
  pragmas, and CI bypass tokens.
- CI preserves install, full Ruff, docstring, all 16 runner lifecycle tests,
  all remaining provisioned tests, artifact 90 percent coverage, and the real
  API drill. The provisioned phase writes coverage JSON and runner metadata to
  a shell-owned temporary directory, then runs the policy with no `|| true`,
  `continue-on-error`, test narrowing, or threshold override.
- Policy tests assert stable diagnostics and exit codes for valid initialization
  and validation plus malformed/missing evidence, inventory loss, exclusion
  config/pragmas, narrowed coverage command, below-floor measurement, base
  regression, denominator drift, stale metadata/tree SHA, unsafe database name,
  missing Alembic head, scope overflow, test weakening, and CI bypasses.
- No test is added solely to execute uncovered application lines. This chunk's
  tests protect the coverage and CI policy boundary itself.
- The runbook documents two-pass bootstrap, canonical validation, evidence
  updates, ratchet behavior, safe temporary outputs, and failure recovery.

## Bootstrap And Verification

1. Run a threshold-disabled isolated candidate measurement into an OS temporary
   directory and compute the candidate floor without writing evidence.
2. Write final configuration, policy, tests, workflow, and runbook; commit every
   non-evidence file.
3. On that exact clean commit, run the canonical isolated complete suite with
   the configured floor and initialize baseline evidence from the same coverage
   JSON and runner metadata.
4. Commit only evidence/status/review files after the reviewed implementation
   SHA. Re-run policy validation and the internal evidence gate.

```text
(cd backend && .venv/bin/python -m pip check)
(cd backend && .venv/bin/python -m ruff check tests scripts)
(cd backend && .venv/bin/python -m pytest -q tests/test_coverage_contract.py)
(cd backend && tmp_dir=$(mktemp -d) && trap 'rm -rf "$tmp_dir"' EXIT && WORKSTREAM_TEST_ADMIN_DATABASE_URL=<local-admin-dsn> .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$tmp_dir/database.json" -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-report=json:"$tmp_dir/coverage.json" && .venv/bin/python scripts/coverage_policy.py --coverage-json "$tmp_dir/coverage.json" --database-metadata "$tmp_dir/database.json" --base-ref origin/main --minimum-milestone=<baseline> --max-implementation-lines=500 --check-test-delta)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
git diff --check
```

## Review And Stop

Required tracks: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, and test delta.

Human review focus: full-app inventory, exact floor arithmetic, initialization
provenance, non-decreasing base comparison, CI non-bypass, and no line-chasing
tests or production changes.

Stop on scope expansion, production changes, exclusions, shared database state,
unreviewed denominator drift, a missed floor, more than 500 implementation
lines, or any need to weaken CI/tests. Do not start chunk 02.
