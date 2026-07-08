# Internal Review Evidence: WS-POL-001-14

## Chunk

WS-POL-001-14

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 8372c6e15299960cc78231603a463d238464bc35

Reviewed at: 2026-07-08T12:01:24Z

Reviewer run IDs: senior-engineering-final-019f4040-38db-7c02-ada8-ec277d640635, qa-test-final-019f4033-07a1-72c1-a172-9cebee7ab9de, security-auth-final-019f4049-451a-75c2-8a90-1e80e12bfa55, product-ops-final-019f4021-0291-73d2-8052-69c10a6346e9, architecture-final-019f4021-172e-7671-b16c-c09a66343d87, docs-final-019f4021-22fa-7003-bf1f-4f80affcb7d9, reuse-dedup-final-019f4064-43a3-7e90-9569-a8f341310bfa, test-delta-final-019f4049-51ed-78a1-8d3a-7ffa22dba883, senior-engineering-coderabbit-fix-019f4179-808b-7503-97bd-016cb2e1bbba, qa-test-coderabbit-fix-019f4179-8247-7751-9222-d678cd0f1b79, security-auth-coderabbit-fix-019f4179-8487-7153-bea8-fc093979a7da, product-ops-coderabbit-fix-019f4179-8647-77a3-830d-c5a8f2187b8a, architecture-coderabbit-fix-019f4179-883c-7330-ad49-d8ec9bca999c, docs-coderabbit-fix-019f4187-1fa8-7563-8854-c2e01c71178d, reuse-dedup-coderabbit-fix-019f417d-763c-73e1-80fa-d30e0adc1f1f, test-delta-coderabbit-fix-019f417d-850c-7362-8f44-850fd42e3b40, senior-engineering-docstring-fix-019f4198-90a8-71f2-898f-48b087443428, docs-docstring-fix-019f4198-c2b5-7c01-ae2c-161d4fe3ec64

After the reviewed SHA, only evidence and review-bundle files changed.

## Reviewed Change

Scope:

- Replaced the public submission handoff route with `POST /api/v1/submissions/{submission_id}/finalize`.
- Kept internal persistence on `locked_at` while projecting public `finalized_at`.
- Added shared scoped operator authorization for task creators and admins.
- Finalization now validates the full task locked context before running post-submit checkers.
- Finalization now uses an atomic database guard so concurrent finalize calls cannot duplicate audit or checker side effects.
- Automatic pre-review checker runs are audited under `workstream-system:pre-review-gate`.
- Checker-run and task audit API responses include requester provenance only for scoped operators.
- Existing checker-run list/get and task audit endpoints are covered by the API contract drill.
- Terminal Benchmark example proof now uses HTTP-visible lifecycle responses for setup, pre-submit blocking, finalization, checker runs, audit events, and revision v1/v2 flow.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Confirmed the finalize boundary, endpoint naming, atomic guard direction, and proof strategy. Low note: true concurrent API race coverage can be added later. |
| QA/test | PASS WITH LOW RISKS | None | Confirmed success, idempotency, unauthorized roles, non-latest rejection, invalid locked context, checker-run reads, audit reads, and live API proof coverage. Low note: atomic repository test is sequential but covers the SQL guard. |
| security/auth | PASS WITH LOW RISKS | None | Confirmed wrong project managers and multi-role workers do not receive operator-shaped checker, audit, submission, task, or locked-context data. Low audit wording note was fixed. |
| product/ops | PASS WITH LOW RISKS | None | Confirmed user-facing finalization wording, system actor audit provenance, and Terminal Benchmark drill semantics after stale wording cleanup. |
| architecture | PASS WITH LOW RISKS | None | Confirmed no task-owned checker model was introduced and finalization uses locked project policy context. Allowed-file contract was updated for the touched loop state files. |
| docs | PASS | None | Confirmed operations role wording now matches service behavior and active docs use finalization and HTTP-visible proof wording. |
| reuse/dedup | PASS WITH LOW RISKS | None | Confirmed the shared task authorization helper removes duplicated scoped operator logic; optional duplication notes were non-blocking. |
| test delta | PASS WITH LOW RISKS | None | Confirmed tests strengthened coverage without skips, weakened assertions, or monkeypatch-only proof. Low note: true concurrent public API test remains optional follow-up. |

## Valid Findings Addressed

- Replaced public lock-route and lock-event wording with finalization wording in code, tests, scripts, examples, and active docs.
- Added `can_admin_or_task_creator_manage()` and used it for task visibility, locked context, checker-run detail/list, audit events, and manual checker trigger authorization.
- Prevented a worker who also carries `project_manager` but did not create the task from receiving operator-shaped data for an assigned task.
- Added an atomic `finalize_submission_if_unlocked()` repository guard so repeat or concurrent finalize calls cannot duplicate checker-run and audit side effects.
- Added a docstring bridge explaining why the finalize-facing repository method still writes the internal `locked_at` persistence column.
- Made repeat finalization return the already-finalized submission response without scheduling another pre-review gate.
- Mapped automatic post-submit checker audit to `workstream-system:pre-review-gate` and preserved requester actor provenance for authorized operator reads.
- Made finalization reject unfinished tasks, unsubmitted submissions, non-latest versions, unauthorized actors, and missing/malformed task locked context.
- Changed public response projection from `locked_at` to `finalized_at`.
- Split the operations matrix into separate precheck and finalization rows, and documented multi-role precheck behavior against the actual service gate.
- Removed overclaiming helper names and active stale wording around database proof.
- Updated API contract and Terminal Benchmark drills to use `/finalize`, `finalized_at`, checker-run APIs, audit APIs, and HTTP-visible lifecycle proof.

## Commands Run

```bash
cd backend && .venv/bin/ruff check app/modules/tasks/repository.py app/modules/tasks/service.py tests/test_tasks.py
cd backend && .venv/bin/pytest tests/test_tasks.py::test_finalize_submission_requires_operator_and_latest_version tests/test_tasks.py::test_submission_finalize_guard_is_atomic -q
cd backend && .venv/bin/pytest tests/test_tasks.py tests/test_checkers.py
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/api_contract_e2e.py
bash -lc 'set -a; source /home/abiorh/flow/jarvis-live-agent-proof/.env; set +a; export WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test; export WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL=${WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL:-gpt-4.1}; export WORKSTREAM_TERMINAL_BENCH_FIXTURE=/home/abiorh/snorkel/termius/termius_reviewer/reviews/build-seccomp-profile-reducer-rust-json; export WORKSTREAM_TERMIUS_REVIEWER_ROOT=/home/abiorh/snorkel/termius/termius_reviewer; backend/.venv/bin/python examples/terminal_benchmark/terminal_benchmark_api_e2e.py'
python3 scripts/check_markdown_links.py
git diff --check
```

Active stale wording scan:

```bash
rg -n -P "<old public submission handoff, lock-event, database-proof, and helper-name patterns>" .agent-loop/LOOP_STATE.md .agent-loop/REVIEW_LOG.md .agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/chunks/WS-POL-001-14-submission-finalize-no-db-drill.md backend/app/modules/tasks backend/app/modules/checkers backend/tests/test_tasks.py backend/tests/test_checkers.py backend/scripts/api_contract_e2e.py examples/terminal_benchmark docs/current_system_data_flow.html docs/operations_roles_permissions.md docs/spec_chunk_5_submission_packet_foundation.md docs/spec_chunk_6_checker_contract_records.md docs/spec_chunk_7_checker_runner_registry.md docs/roadmap_day_by_day_execution_plan.md docs/roadmap_status.md docs/roadmap_week1_backend_plan.md README.md
```

Results:

- Focused Ruff: passed.
- Focused finalize guard tests: 2 passed.
- Final CodeRabbit docstring-nitpick Ruff: passed for `backend/app/modules/tasks/repository.py`.
- Task/checker suite: 133 passed in 1666.46s.
- API contract real API E2E: passed and exercised `/finalize`, checker-run reads, audit-event reads, and scoped access.
- Terminal Benchmark real API E2E: passed using the real OpenAI Agents SDK adapter and fixture `build-seccomp-profile-reducer-rust-json`.
- Terminal Benchmark scenario summary: `complete_packet=review_pending`, `missing_static_guard=pre_submit_blocked_no_submission`, `low_quality_v1=needs_revision`, `fixed_low_quality_v2=review_pending`, `worker_profile_setup=canonical_worker_profile_api`.
- Markdown link check: passed for 27 changed Markdown files.
- Diff whitespace check: passed.
- Active stale wording scan: passed with no matches.

## External Review Separation

CodeRabbit and GitHub checks are external review. They are tracked separately in:

- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-14-external-review-response.md`

## Remaining Risks

- Post-submit checker policy derivation remains future work; this chunk only proves current project post-submit checker execution and visibility after finalization.
- Full reviewer packet visibility remains a follow-up before broader review lifecycle expansion.
- True concurrent public API race coverage can be added later; the current fix uses an atomic conditional SQL update and covers the guard at the repository boundary plus repeat-finalize side effects at the API boundary.
