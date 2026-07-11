# WS-ART-001-04: Upload Session And Admission Foundation

Parent: `WS-ART-001` | Repository: Workstream | Risk: L1 | SLA: P0

Dependency: merged WS-AUTH task/submission cutovers (`WS-AUTH-001-13/14`).

## Goal

Add task-scoped upload sessions, bounded streaming upload APIs, sealing,
server-generated artifact-set manifests, and authoritative admission records.

## Allowed Files

- artifact module/router, task read integration, authorization resource context
- `backend/app/modules/checkers/router.py`
- `backend/app/modules/checkers/service.py`
- `backend/app/modules/checkers/schemas.py`
- one additive migration
- focused artifact/task/auth tests
- exact upload API and artifact-set docs

## Not Allowed

No submission schema cutover, legacy-field removal, post-submit change, public
reviewer upload, or direct Flow Node access by clients.

## Acceptance Criteria

- Exact-project Submitter can create/use only own task session; all other actor,
  cross-project/task, revoked, expired, and hidden-resource cases are tested.
- Server limits are effective minimum of platform and locked project policy.
- Seal derives trusted path/media/archive/size facts and immutable sorted
  `artifact_set_hash`; every entry has a server-derived semantic identity,
  exact duplicates are rejected, total ordering has no ties, and sealed
  sessions cannot change.
- Admission binds actor/task/session/artifact set/policy/checker hashes and
  expiry plus the canonical hash of the exact task ID, artifact-set hash,
  summary, contributor attestation, and upload-session ID. It can be created
  only from a sealed artifact set; changing any input invalidates it.
  `/api/v1/tasks/{task_id}/submission-precheck` remains explicitly
  non-submission.
- If seal locks first, a racing upload returns 409 and creates zero new
  content/replica rows; if upload transaction B locks first, seal includes that
  one ready item exactly once.
- Seal/expiry and later consume/expiry share database-time CAS semantics: one
  terminal state wins, the loser returns 409, and it creates zero side effects.
- Cancellation/sweeper produces one terminal transition and at most one
  metadata-only release; content already bound to a resource has zero release
  operations.

## Verification

```bash
cd backend && .venv/bin/ruff check app tests scripts
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q tests/test_artifacts.py tests/test_tasks.py tests/test_auth.py
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
git diff --check
```

Reviewers: all required tracks.

Human focus: exact authority, upload limits, sealing truth, races, and no early
submission authority. Stop after this PR.
