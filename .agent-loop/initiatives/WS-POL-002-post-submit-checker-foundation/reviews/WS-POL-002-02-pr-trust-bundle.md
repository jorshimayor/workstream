# PR Trust Bundle: WS-POL-002-02

## Chunk

`WS-POL-002-02` - Post-Submit Derivation Agent And Resumable Setup Integration

## Reviewed Revision

Reviewed code SHA: `0318beccd0ffd086b8ed403dd8e74dabe1fd8d6b`

Reviewed at: `2026-07-11T08:33:06Z`

Internal review evidence:

- `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-02-internal-review-evidence.md`

## Goal

Add setup-time post-submit checker derivation and compilation, then connect locked submissions to the deterministic automatic pre-review gate without manager-owned normal finalization, runtime agent judgment, or per-task checker generation.

## Human-Approved Intent

Post-submit checks follow the same separation as pre-submit:

```text
Project guide/source material
-> setup-time derivation agent
-> trusted Workstream compiler
-> project PostSubmitCheckerPolicy
-> tasks lock references
-> contributor submits packet
-> Workstream reruns pre-submit authoritatively
-> Workstream locks the submission
-> Celery executes deterministic post-submit checkers
```

The agent derives constrained setup policy. Workstream compiles and owns deterministic checker policy. The agent never judges worker submissions at runtime.

## What Changed

- Added `PostSubmitCheckerPolicyDerivationAgent` interface and OpenAI Agents SDK adapter support.
- Extended the project setup continuation after submission artifact policy approval and pre-submit checker compilation.
- Added migration/model/repository/service support for generated post-submit policy provenance and setup approval state.
- Added generated post-submit policy binding to guide id/version, source snapshot id/hash, effective policy id/hash, and pre-submit checker id/bundle hash.
- Enforced activation rejection for compiled-only or non-setup-approved post-submit policies.
- Connected normal contributor submission creation to automatic gate handoff:
  - authoritative server-side pre-submit rerun against the exact payload
  - immutable submission lock and `submission_finalized` audit
  - queued automatic pre-review gate through Celery
  - system-owned gate actor with verified requester provenance
- Kept `/api/v1/submissions/{submission_id}/finalize` as repair-only for locked latest submissions.
- Added repair paths for enqueue failure, execution failure, unknown checker, stale running claims, and non-repairable failed claims.
- Added CAS fencing so dispatch-failed audit is written only if the queued automatic gate was actually marked failed.
- Added shared requester-provenance and Celery task-setting helpers to prevent drift between task enqueue, checker validation, and worker queues.
- Updated docs to clarify task-vs-submission status ownership and automatic gate repair behavior.

## Design Chosen

The existing project setup queue/worker remains the setup boundary. The existing checker service/repository boundary owns deterministic runtime gate behavior.

Normal submission flow:

```text
assigned contributor creates submission
-> TaskService authoritatively reruns pre-submit
-> TaskService persists immutable submission version
-> TaskService writes submission_created + submission_finalized audit
-> TaskService creates/gets queued automatic CheckerRun
-> Celery run_pre_review_gate executes CheckerService.run_queued_pre_review_gate
-> CheckerService validates persisted requester provenance before gate audit/status mutation
-> task moves toward evaluation_pending/review_pending/needs_revision based on deterministic checker result
```

Repair flow:

```text
operator/project manager calls /finalize for locked latest submission
-> existing automatic gate claim is reused/requeued when repairable
-> duplicate checker runs are not created
-> non-repairable failed claims return 409 instead of false success
```

## Alternatives Rejected

- Runtime agent judgment: rejected. Runtime executes deterministic checkers only.
- Per-task checker derivation: rejected. Policy is project-scoped.
- Manager-owned normal finalization: rejected. Contributor submission creation owns the normal lock and handoff.
- Manual post-submit policy in guide payloads: rejected. Generated setup output owns this path.
- Separate post-submit-only queue: rejected. Existing project setup queue is the setup boundary.
- Arbitrary generated checker code: rejected for v0.1.

## Scope Control

This PR includes both setup-time post-submit derivation and the narrow runtime handoff needed to remove manager action from the submission happy path. It does not add frontend/demo work, payment/reputation/blockchain settlement, reviewer decision records, per-task checker generation, or runtime agent-based submission judgment.

Helper files added by review:

- `backend/app/modules/checkers/pre_review_gate.py`: shared automatic-gate requester provenance contract.
- `backend/app/workers/task_settings.py`: shared Celery task settings sync without importing the Celery app at queue-module import time.

## Acceptance Criteria Proof

- Post-submit derivation runs only after submission artifact policy approval and pre-submit compile.
- Unsupported or unknown checker gaps fail closed and block setup.
- Generated post-submit policies bind to source/effective/pre-submit provenance.
- Guide activation rejects compiled-only post-submit policies until setup-approved.
- Contributor submission creation locks the packet and queues the automatic gate without manager action.
- Queue payload requester provenance is sanitized and validated against persisted `submission_finalized` audit before gate audit/status mutation.
- Dispatch/eager failures after accepted submission are recorded as repairable automatic gate failures.
- CAS misses cannot write false dispatch-failed audit trails.
- `/finalize` is repair-only, idempotent, and does not create duplicate checker runs.
- Worker-facing state remains simple; internal checker route tokens are not product review decisions.

## Tests/Checks Run

```bash
cd backend && .venv/bin/pytest tests/test_tasks.py::test_finalize_repairs_locked_submission_with_missing_pre_review_gate tests/test_tasks.py::test_failed_pre_review_gate_repair_is_idempotent_while_queued tests/test_tasks.py::test_enqueue_failure_without_current_claim_skips_dispatch_failed_audit tests/test_tasks.py::test_eager_pre_review_gate_failure_after_submission_is_repairable tests/test_tasks.py::test_unknown_checker_gate_failure_is_repairable tests/test_tasks.py::test_nonrepairable_failed_gate_does_not_return_success tests/test_tasks.py::test_queued_gate_policy_error_is_failed_and_repairable tests/test_tasks.py::test_queued_gate_rejects_tampered_requester_provenance tests/test_tasks.py::test_queued_gate_fails_closed_when_lock_audit_is_missing tests/test_tasks.py::test_stale_queued_pre_review_gate_skips_before_task_status_check -q
cd backend && .venv/bin/pytest tests/test_projects.py::test_project_setup_queue_syncs_all_setup_task_settings -q
cd backend && .venv/bin/ruff check app/modules/checkers/pre_review_gate.py app/modules/checkers/service.py app/modules/checkers/gate_queue.py app/modules/projects/setup_queue.py app/modules/tasks/service.py app/workers/celery_app.py app/workers/task_settings.py tests/test_tasks.py tests/test_projects.py
cd backend && .venv/bin/python -m py_compile app/modules/checkers/pre_review_gate.py app/modules/checkers/service.py app/modules/checkers/gate_queue.py app/modules/projects/setup_queue.py app/modules/tasks/service.py app/workers/celery_app.py app/workers/task_settings.py tests/test_tasks.py tests/test_projects.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check main...HEAD
```

Result summary:

- Focused automatic gate repair/provenance suite: 10 passed.
- Shared queue settings regression: 1 passed.
- Ruff: passed.
- Py compile: passed.
- Stale wording scan: passed.
- Markdown link check: passed for 24 changed Markdown files.
- Private-path/Snorkel leakage scan: no matches.
- Diff whitespace check: passed.

Earlier PR proof retained:

- Full backend suite after stale fixture repair: 442 passed.
- Project and agent-runtime suite: 229 passed.
- Task suite: 86 passed.
- Checker suite: 75 passed.
- Alembic suite: 6 passed.
- API contract real API drill passed.
- Docstring coverage: 100.0%.
- Agent gates: 26 passed.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | No final code issue after CAS fence; stale evidence fixed by this bundle. |
| QA/test | PASS AFTER FIXES | None | Focused acceptance tests pass; stale evidence fixed by this bundle. |
| security/auth | PASS | None | Provenance, system actor, `/finalize` auth/object scope, and leakage checks pass. |
| product/ops | PASS WITH LOW RISKS | None | Accepted brief queued-gate visibility window before worker claim; docs updated for repair matrix. |
| architecture | PASS | None | Helper files are contract-allowed and boundary-appropriate. |
| docs | PASS | None | Final repair wording aligns with code. |
| reuse/dedup | PASS AFTER FIXES | None | Shared helper extraction addressed required findings. |
| test delta | PASS AFTER FIXES | None | Eager repair and task-level audit proof added. |
| CI integrity | PASS | None | No CI or runner weakening found. |

## External Review

External review response:

- `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-02-external-review-response.md`

GitHub Actions and CodeRabbit must rerun on the pushed final head before human merge review.

## Remaining Risks

- Product/ops accepted a low visibility window where task status remains `submitted` with a queued current automatic gate until the Celery worker claims it and moves the task to `evaluation_pending`.
- Temporary API/CI bridge remains until `WS-POL-002-03` replaces direct generated post-submit policy approval/setup-ledger marking with the server-owned approval API.

## Human Review Focus

- Confirm setup-time agent derivation remains separate from runtime deterministic checker execution.
- Confirm contributor submission creation, not manager action, owns the normal submission lock/handoff.
- Confirm `/finalize` is repair-only.
- Confirm tasks do not generate their own checker policies.

## Human Merge Ownership

Only the user can approve and merge this PR. Codex must not merge it without explicit user approval for this specific PR.
