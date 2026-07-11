# WS-ART-001-03: Guide Source Artifact Cutover

Parent: `WS-ART-001` | Repository: Workstream | Risk: L1 | SLA: P1

Dependency: merged WS-AUTH project mutation cutover (`WS-AUTH-001-12` or
approved replacement).

## Goal

Capture every guide source item through artifact bindings and make setup agents
consume immutable retrieved bytes.

## Allowed Files

- `backend/app/modules/projects/**`, artifact integration, project workers
- one guide-owned migration
- `backend/tests/test_projects.py`, `test_alembic.py`, artifact tests
- exact guide/source architecture, glossary, operations, API docs/templates

## Not Allowed

No submission/checker/review cutover, signed URL/query persistence, mutable
remote reads after capture, `content_cid` alias, or authorization bypass.

## Acceptance Criteria

- Covered Project Manager authority is revalidated for capture/mutation.
- Source bytes become content/replica/binding records before snapshot use.
- Bundle manifest references binding/content IDs and verified SHA-256/size, not
  provider locator as truth.
- Setup uses immutable retrieval; unavailable source sets existing
  `ProjectSetupRun.status=failed` with `artifact_storage_unavailable` and no
  activation.
- Existing source snapshots cause fail-closed pre-production rebuild; fresh,
  refusal, downgrade-empty, and re-upgrade tests pass.
- Old source identity fields and wording are removed in owned surfaces.

## Verification

```bash
cd backend && .venv/bin/ruff check app tests scripts
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q tests/test_projects.py tests/test_artifacts.py tests/test_alembic.py
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_markdown_links.py
git diff --check
```

Reviewers: all required tracks.

Human focus: project authority, immutable source capture, rebuild boundary, and
setup failure semantics. Stop after this PR.

