# External Review Response: WS-POL-002-01

## Source

PR #87 external checks.

## Comments Addressed

### Backend CI failure

Status: addressed.

Finding:

- The Backend workflow failed in `tests/test_tasks.py` at
  `test_screening_uses_persisted_post_submit_policy_body_after_default_drift`.
  The old test expected screening to keep accepting and locking an existing
  persisted post-submit policy body after the server-owned default checker list
  drifted.

Decision:

- The old expectation was stale under `WS-POL-002-01`. The new compiler
  contract requires `policy_body.default_checkers` to exactly match the active
  server-owned `DEFAULT_DURABLE_CHECKERS` list. Future default-list changes
  require explicit compatibility, versioning, or migration work. They must not
  silently reinterpret old locked bodies.

Fix:

- Renamed the test to
  `test_screening_rejects_post_submit_policy_body_after_default_drift`.
- Updated the assertion to expect a fail-closed `422` with
  `active post-submit checker policy hash is invalid`.
- Added a negative assertion that screening does not stamp a
  `locked_post_submit_checker_policy_body` after rejection.

Verification:

```bash
cd backend && .venv/bin/pytest tests/test_tasks.py::test_screening_rejects_post_submit_policy_body_after_default_drift -q
cd backend && .venv/bin/ruff check tests/test_tasks.py
```

Results:

- Focused CI-fix test: 1 passed.
- Ruff: passed.

Internal post-fix review:

- QA/test: PASS.
- Test delta: PASS.

## Final External Check Status

- Backend: passed after the CI fix push.
- Agent Gates: passed.
- CodeRabbit: passed with no actionable comments.

## Comments Deferred

None.

## Human Decisions Needed

None before human merge review.

## Commands Rerun

```bash
cd backend && .venv/bin/pytest tests/test_tasks.py::test_screening_rejects_post_submit_policy_body_after_default_drift -q
cd backend && .venv/bin/ruff check tests/test_tasks.py
```

## Remaining Risks

- None from external review. Human merge review is still required.
