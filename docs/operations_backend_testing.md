# Backend Testing Operations
Workstream's backend suite uses a new local Postgres database per invocation. The
provisioner owns a strict `workstream_test_<12 lowercase hex>` database, migrates it,
and creates an ephemeral login without superuser, database/role creation, replication,
or row-security-bypass authority. It drops both after success, failure, timeout, or interruption.

## Local full suite
Keep the admin URL in the environment with `postgresql+asyncpg` and a loopback host.
Never put real or shared credentials in arguments, logs, evidence, or configuration.

```bash
cd backend
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT
export WORKSTREAM_TEST_ADMIN_DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@localhost:5433/postgres'
.venv/bin/python -m pytest -q tests/test_isolated_database_runner.py
.venv/bin/python scripts/run_isolated_tests.py --metadata-json "$tmp_dir/database.json" -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py
unset WORKSTREAM_TEST_ADMIN_DATABASE_URL
```

Run both phases. The second can exceed three hours locally; CI allows 300 minutes.

The runner removes the admin URL before child launch, overwrites both child database URLs,
removes the nonlocal override, redacts complete URLs, and writes only credential-free metadata.

## Focused checks
The API-guard tests are statically DB-free:

```bash
.venv/bin/python -m pytest -q tests/test_api_contract_e2e.py
```

Runner lifecycle tests require the same admin environment variable:

```bash
.venv/bin/python -m pytest -q tests/test_isolated_database_runner.py
```

Run the destructive API drill only against `workstream_test`, `test_workstream`, or a runner-derived local name:

```bash
WORKSTREAM_DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@localhost:5433/workstream_test' .venv/bin/python scripts/api_contract_e2e.py
```

Do not use `WORKSTREAM_ALLOW_NONLOCAL_E2E_DATABASE` for ordinary proof.

If provisioning fails, confirm the local admin can create/drop databases and roles, terminate owned sessions, and reach the named admin database. Diagnostics omit credentials.
