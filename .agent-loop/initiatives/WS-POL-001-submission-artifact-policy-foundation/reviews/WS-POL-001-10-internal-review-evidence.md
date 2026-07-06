# Internal Review Evidence: WS-POL-001-10

## Chunk

WS-POL-001-10

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed base SHA: 8a524dec9de1fabb7ae6a605d45ae8ab3778a32c

Reviewed working diff digest before evidence files:
67e2b7561d3688f6e588e5abe09317104da3bbd66ec97231f9f49b886801903b

Reviewed at: 2026-07-06T09:50:05Z

Reviewer run IDs:

- senior-engineering-review-019f369f-e0e6-7e01-b2e8-cb2f818e9edf
- qa-test-review-019f369f-e51a-7ad3-89d0-bae5f7e56261
- security-auth-review-019f369f-eb9a-73b1-afa9-9024eea0aeaf
- product-ops-review-019f369f-f004-75e2-9bb8-142aa1860201
- architecture-review-019f369f-f734-7c20-9173-264c5206406c
- reuse-dedup-review-019f36a0-010b-7b40-a19f-69853bffb72f
- docs-review-019f36a5-e8bb-7403-b892-48a8705c3f0d
- docs-rereview-019f36ab-acfb-76e0-8155-062ecc40d995
- test-delta-review-019f36a5-e313-7de0-b3c0-74462ebebb43
- test-delta-rereview-019f36ab-b42d-7893-a9f8-44972d830d94
- test-delta-final-rereview-019f36ae-1cf4-78f2-8a4b-e41e75a8ab4a

## Reviewed Change

Scope:

- Maps duplicate guide versions to a 409 conflict instead of an unhandled DB
  error.
- Allows guide creation to include immutable source-snapshot items, including
  representative task examples, so the existing automatic setup pipeline has
  full setup material.
- Exposes project pre-submit checker names and configs in the active-guide
  summary while still excluding the compiled checker bundle body.
- Adds `POST /api/v1/workers/me/profile` so workers can create or refresh their
  own active profile from verified Flow identity before claim.
- Writes durable `pre_submission_check_failed` task audit evidence when
  submission creation is blocked by pre-submit checks, while creating no
  submission version.
- Updates standing docs to distinguish no submission-created audit event from
  the new failed-attempt task audit evidence.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Requested narrower guide `IntegrityError` mapping and worker skill-tag normalization. Both addressed. |
| QA/test | PASS WITH LOW RISKS | None | Requested negative fail-closed worker profile request test. Addressed. |
| security/auth | PASS | None | Verified worker profile identity is derived from `ActorContext`, role-gated, and audit payload exposure is bounded. |
| product/ops | PASS WITH LOW RISKS | None | Requested skill-tag normalization before future routing/reputation use. Addressed. |
| architecture | PASS WITH LOW RISKS | None | Requested narrowing broad guide conflict mapping. Addressed. |
| reuse/dedup | PASS WITH LOW RISKS | None | Noted small duplication between worker/reviewer profile construction. Accepted for now; defer abstraction until another profile path exists. |
| docs | PASS AFTER FIXES | Medium findings fixed | Required docs for worker profile endpoint and failed pre-submit audit behavior. Addressed and passed rereview. |
| docs rereview | PASS | None | Confirmed scoped docs updates, loop state, and product/engineering wording. |
| test delta | PASS WITH LOW RISKS | None | Requested non-worker role gate coverage. Addressed. |
| test-delta rereview | PASS WITH LOW RISKS | None | Requested public profile refresh coverage. Addressed. |
| test-delta final rereview | PASS | None | Confirmed refresh coverage and no weakened assertions. |

## Valid Findings Addressed

- Narrowed `create_guide` duplicate-version handling so `GuideVersionConflict`
  maps only the guide insert/flush integrity failure, not later optional policy
  or source-snapshot persistence.
- Added worker profile skill-tag normalization: strip, lowercase, dedupe, reject
  blank tags, and cap each tag at 64 characters.
- Added worker profile request negative tests for unknown client identity fields,
  blank tags, overlong tags, non-worker role access, and public refresh behavior.
- Updated docs to state that failed pre-submit submission-create attempts write
  `pre_submission_check_failed` task audit evidence while creating no
  `Submission`, submission version, task transition to `submitted`, or
  submission-created audit event.
- Updated task assignment docs to document the worker-owned profile create or
  refresh endpoint and its Flow-token-derived identity boundary.
- Updated the chunk contract to allow only the specific standing docs needed by
  the docs reviewer findings.

## Commands Run

```bash
cd backend && .venv/bin/python -m ruff check app/modules/projects/schemas.py app/modules/projects/service.py app/modules/tasks/router.py app/modules/tasks/schemas.py app/modules/tasks/service.py tests/test_projects.py tests/test_tasks.py
cd backend && .venv/bin/python -m pytest tests/test_projects.py -k 'duplicate_guide_version_returns_conflict or guide_creation_accepts_source_snapshot_items_for_agent_material or guide_activation_and_active_guide_retrieval' -q
cd backend && .venv/bin/python -m pytest tests/test_tasks.py -k 'worker_can_create_profile_before_claiming_task or worker_profile_request_is_fail_closed_and_validated or worker_profile_requires_worker_role or worker_without_profile_cannot_claim_ready_task or pre_submit_failure_writes_audit_event_without_submission' -q
cd backend && .venv/bin/docstr-coverage app/modules/projects app/modules/tasks --config .docstr.yaml
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
git diff --check
cd backend && .venv/bin/python -m pytest tests/test_projects.py tests/test_tasks.py tests/test_checkers.py -q
```

Results:

- ruff: passed.
- Focused project tests: 3 passed, 196 deselected.
- Focused task tests: 5 passed, 59 deselected.
- Docstring coverage: 100.0%.
- Markdown link check: passed for 7 changed Markdown files.
- Stale wording scan: passed.
- Diff whitespace check: passed.
- Full project/task/checker suite: 310 passed in 41:18.

## Remaining Risks

- The worker and reviewer profile construction paths still have small duplicate
  actor-claim mapping logic. This is intentionally left as-is until another
  profile path appears; adding an abstraction now would not simplify the chunk.
- This chunk does not implement post-submit policy derivation or review
  lifecycle behavior. That remains out of scope.
