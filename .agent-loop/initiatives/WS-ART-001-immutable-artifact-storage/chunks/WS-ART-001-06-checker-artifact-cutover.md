# WS-ART-001-06: Checker Artifact Cutover

Parent: `WS-ART-001` | Repository: Workstream | Risk: L1 | SLA: P0

Dependency: `WS-ART-001-05` and merged WS-AUTH checker cutover.

## Goal

Make pre-submit and post-submit checker execution retrieve the same immutable
artifact-set commitment and persist input/log/output artifact bindings.

## Allowed Files

- `backend/app/modules/checkers/**`, checker workers, artifact integration
- one checker-owned migration
- checker/artifact/task tests and exact checker docs

## Not Allowed

No checker routing redesign, partial-result routing change, review lifecycle,
generated checker DSL change, or provider status as checker truth.

## Acceptance Criteria

- `CheckerInputSnapshot` uses binding/content IDs, SHA-256, size,
  `artifact_set_hash`, locked policies, and checker implementation identity;
  provider IDs are replica details only.
- Runner retrieves and independently verifies exact bytes before execution.
- Pre/post proof records the same artifact-set hash.
- Logs/outputs are generic artifact bindings; Postgres stores bounded metadata.
- `artifact_storage_unavailable` and `artifact_integrity_failure` use existing
  `CheckerRun.status=failed`/failure code, keep task `evaluation_pending`, create
  no contributor result, and never route partial evidence.
- Duplicate checker workers/retry races produce one authoritative run outcome
  and bounded append-only attempt/receipt evidence.

## Verification

```bash
cd backend && .venv/bin/ruff check app tests scripts
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q tests/test_checkers.py tests/test_tasks.py tests/test_artifacts.py
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_markdown_links.py
git diff --check
```

Reviewers: all required tracks.

Human focus: same-byte proof, provider/domain separation, failure meaning,
duplicate execution, and unchanged routing. Stop after this PR.
