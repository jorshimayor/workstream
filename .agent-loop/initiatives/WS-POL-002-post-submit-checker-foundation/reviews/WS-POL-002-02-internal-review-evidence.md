# Internal Review Evidence: WS-POL-002-02

## Chunk

WS-POL-002-02 - Post-Submit Derivation Agent And Resumable Setup Integration

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 0318beccd0ffd086b8ed403dd8e74dabe1fd8d6b

Reviewed at: 2026-07-11T08:33:06Z

Reviewer run ids: senior-engineering-019f5048-10d7-79d0-a873-3d603aa2bb06, qa-test-019f5048-27cc-72a0-87d9-c6fab250556d, security-auth-019f5048-43e3-7812-9e6b-6be88845025c, product-ops-019f5048-674d-7d30-8268-a20c75be2509, architecture-019f5048-8d20-74a1-b9bd-570e511c2408, docs-019f504c-f575-7331-af00-fecfda936138, reuse-dedup-019f502c-50cd-7e42-9e8f-ac5fd297b152, test-delta-019f502c-7f1f-7aa2-8fad-50a2b5ea619b, ci-integrity-019f502c-96e6-70d2-ba38-bcd26705dbfe

## Reviewed Change

Branch: `codex/ws-pol-002-02-post-submit-derivation`

Scope:

- Adds setup-time `PostSubmitCheckerPolicyDerivationAgent` contract and OpenAI Agents SDK adapter output parsing.
- Extends the existing project setup queue/worker continuation after submission artifact policy approval and pre-submit checker compilation.
- Persists generated project `PostSubmitCheckerPolicy` rows with guide/source/effective-policy/pre-submit provenance and setup approval metadata.
- Blocks guide activation until generated post-submit policies are setup-approved.
- Adds automatic contributor submission handoff: authoritative pre-submit rerun, packet lock, `submission_finalized` audit, queued automatic pre-review gate, and repair-only `/finalize`.
- Adds Celery pre-review gate dispatch through `run_pre_review_gate`, system-actor audit attribution, requester provenance preservation, and failure/repair paths.
- Adds shared automatic-gate requester provenance helpers and shared Celery task-setting sync helpers.
- Adds atomic checker-run repository primitives for queued/running/failed automatic gate claims.
- Updates task/checker/project tests and real API scripts to use generated post-submit policy setup output instead of manual guide-body post-submit policy fields.
- Updates docs and loop artifacts to align the project-scoped post-submit policy, automatic gate, repair matrix, and submission-vs-task status ownership.

## Reviewer Results

These are Codex engineering-loop reviewer verdicts, not Workstream product
review decisions. Product review decisions remain `accept`, `needs_revision`,
and `reject`; internal reviewer agents report `PASS`, `PASS WITH LOW RISKS`,
`PASS AFTER FIXES`, or `FAIL` so process evidence stays separate from product
lifecycle records.

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Final code review found no senior-engineering code fixes after CAS fence; stale evidence was fixed by this refresh. |
| QA/test | PASS AFTER FIXES | None | Confirmed focused CAS-fence, eager repair, tampered provenance, missing audit, stale queued gate, and queue settings tests pass; stale evidence was fixed by this refresh. |
| security/auth | PASS | None | Confirmed requester provenance validation, system actor fencing, `/finalize` authorization/object scope, and no private-path leakage. |
| product/ops | PASS WITH LOW RISKS | None | Accepted brief `submitted` + queued-gate visibility window before worker claim; repair matrix wording was updated. |
| architecture | PASS | None | Confirmed helper files are explicitly allowed and narrow; lifecycle remains in service/repository boundaries; no per-task checker derivation. |
| docs | PASS | None | Confirmed final repair-matrix wording aligns with code and stale wording/link checks pass. |
| reuse/dedup | PASS AFTER FIXES | None | Required shared provenance and Celery settings helpers; implemented and covered. |
| test delta | PASS AFTER FIXES | None | Required eager repair proof and task-level audit query; implemented and covered. |
| CI integrity | PASS | None | Found no workflow/package/test-runner weakening or evidence-gate bypass. |

## Valid Findings Addressed

- Reuse/dedup found duplicated requester-provenance contracts between task enqueue and checker validation. Added `backend/app/modules/checkers/pre_review_gate.py` and wired both services through it.
- Reuse/dedup found duplicated mutable Celery task-setting sync. Added `backend/app/workers/task_settings.py` and reused it from project setup and pre-review gate queues without importing the Celery app at module import time.
- QA found requester provenance could be audited before being validated against `submission_finalized`. The queued gate now validates persisted requester provenance before `pre_review_gate_started` or `evaluation_pending` mutation.
- Test-delta found eager dispatch failure was recorded but not repaired in tests. The test now restores the worker path, calls `/finalize`, and asserts the same run completes.
- Senior engineering found dispatch-failed audit could be written even when the checker-run enqueue-failure CAS missed. The task path now writes dispatch-failed audit only when `mark_pre_review_gate_enqueue_failed()` returns true, with a regression test.
- Product/ops found stale docs implying submission status owns review/revision lifecycle. Docs now state submission status stays `submitted`; task status owns evaluation/review/revision/acceptance/rejection lifecycle.
- Product/ops and docs found repair-matrix wording gaps for queued redispatch, stale running replacement, `pre_review_gate_execution_failed`, and non-repairable 409. Specs now match implemented behavior.
- Architecture found helper files and `docs/architecture_system_architecture.md` were missing from the active chunk contract. The contract now explicitly allows those files for narrow lifecycle/provenance/helper alignment.
- CodeRabbit external findings from earlier passes were handled in `WS-POL-002-02-external-review-response.md`; valid findings were fixed and stale findings documented.

## Commands Run

```bash
cd backend && .venv/bin/pytest tests/test_tasks.py::test_finalize_repairs_locked_submission_with_missing_pre_review_gate tests/test_tasks.py::test_failed_pre_review_gate_repair_is_idempotent_while_queued tests/test_tasks.py::test_enqueue_failure_without_current_claim_skips_dispatch_failed_audit tests/test_tasks.py::test_eager_pre_review_gate_failure_after_submission_is_repairable tests/test_tasks.py::test_unknown_checker_gate_failure_is_repairable tests/test_tasks.py::test_nonrepairable_failed_gate_does_not_return_success tests/test_tasks.py::test_queued_gate_policy_error_is_failed_and_repairable tests/test_tasks.py::test_queued_gate_rejects_tampered_requester_provenance tests/test_tasks.py::test_queued_gate_fails_closed_when_lock_audit_is_missing tests/test_tasks.py::test_stale_queued_pre_review_gate_skips_before_task_status_check -q
cd backend && .venv/bin/pytest tests/test_projects.py::test_project_setup_queue_syncs_all_setup_task_settings -q
cd backend && .venv/bin/ruff check app/modules/checkers/pre_review_gate.py app/modules/checkers/service.py app/modules/checkers/gate_queue.py app/modules/projects/setup_queue.py app/modules/tasks/service.py app/workers/celery_app.py app/workers/task_settings.py tests/test_tasks.py tests/test_projects.py
cd backend && .venv/bin/python -m py_compile app/modules/checkers/pre_review_gate.py app/modules/checkers/service.py app/modules/checkers/gate_queue.py app/modules/projects/setup_queue.py app/modules/tasks/service.py app/workers/celery_app.py app/workers/task_settings.py tests/test_tasks.py tests/test_projects.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
rg -n "snorkel|termius|/home/abiorh/snorkel|terminal_benchmark_reviewer|build-seccomp-profile-reducer" . -S --glob '!backend/.venv/**' --glob '!**/.git/**'
git diff --check main...HEAD
```

Results:

- Focused automatic gate repair/provenance suite: 10 passed in 126.57s.
- Shared queue settings regression: 1 passed in 3.83s.
- Ruff: passed.
- Py compile: passed.
- Stale wording scan: passed.
- Markdown link check: passed for 24 changed Markdown files.
- Private-path/Snorkel leakage scan: no matches.
- Diff whitespace check: passed.

Earlier full-suite proof retained from this PR before final CAS-fence commits:

- Full backend suite after stale fixture repair: 442 passed in 4100.54s.
- Project and agent-runtime suite: 229 passed in 2037.08s.
- Task suite: 86 passed in 944.91s.
- Checker suite: 75 passed in 303.48s.
- Alembic suite: 6 passed in 67.47s.
- API contract real API drill passed after the CI bridge scope repair.
- Docstring coverage: 100.0%.
- Agent gates: 26 passed.
- Loop memory state check: passed.

## Remaining Risks

- Product/ops accepted a low visibility window where task status remains `submitted` with a queued current automatic gate until the Celery worker claims it and moves the task to `evaluation_pending`.
- A temporary CI/API-drill activation bridge remains until `WS-POL-002-03` replaces direct generated post-submit policy approval/setup-ledger marking with the server-owned approval API.
- External GitHub Actions and CodeRabbit must rerun after this evidence refresh is pushed.
