# Internal Review Evidence: WS-POL-001-14

## Chunk

WS-POL-001-14

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 592d4b02fec1b0b8921061ad6f93f90fc84ca83b

Reviewed at: 2026-07-08T10:16:02Z

Reviewer run IDs: senior-engineering-final-019f4040-38db-7c02-ada8-ec277d640635, qa-test-final-019f4033-07a1-72c1-a172-9cebee7ab9de, security-auth-final-019f4049-451a-75c2-8a90-1e80e12bfa55, product-ops-final-019f4021-0291-73d2-8052-69c10a6346e9, architecture-final-019f4021-172e-7671-b16c-c09a66343d87, docs-final-019f4021-22fa-7003-bf1f-4f80affcb7d9, reuse-dedup-final-019f4064-43a3-7e90-9569-a8f341310bfa, test-delta-final-019f4049-51ed-78a1-8d3a-7ffa22dba883

After the reviewed SHA, only evidence files changed.

## Reviewed Change

Scope:

- Replaced the public submission handoff route with `POST /api/v1/submissions/{submission_id}/finalize`.
- Kept internal persistence on `locked_at` while projecting public `finalized_at`.
- Added shared scoped operator authorization for task creators and admins.
- Finalization now validates the full task locked context before running post-submit checkers.
- Automatic pre-review checker runs are audited under `workstream-system:pre-review-gate`.
- Checker-run and task audit API responses include requester provenance only for scoped operators.
- Existing checker-run list/get and task audit endpoints are covered by the API contract drill.
- Terminal Benchmark example proof now uses HTTP-visible lifecycle responses for setup, pre-submit blocking, finalization, checker runs, audit events, and revision v1/v2 flow.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Confirmed the finalize boundary, endpoint naming, and proof strategy; low notes were documentation/proof clarity and were addressed. |
| QA/test | PASS | None | Confirmed success, idempotency, unauthorized roles, non-latest rejection, invalid locked context, checker-run reads, audit reads, and live API proof coverage. |
| security/auth | PASS | None | Confirmed wrong project managers and multi-role workers do not receive operator-shaped checker, audit, submission, task, or locked-context data. |
| product/ops | PASS AFTER FIXES | None | Confirmed user-facing finalization wording, system actor audit provenance, and Terminal Benchmark drill semantics after stale wording cleanup. |
| architecture | PASS | None | Confirmed no task-owned checker model was introduced and finalization uses locked project policy context. |
| docs | PASS AFTER FIXES | None | Confirmed active docs now use finalization and HTTP-visible proof wording. |
| reuse/dedup | PASS WITH LOW RISKS | None | Confirmed the shared task authorization helper removes duplicated scoped operator logic; low helper-naming feedback was addressed. |
| test delta | PASS | None | Confirmed tests strengthened coverage without skips, weakened assertions, or monkeypatch-only proof. |

## Valid Findings Addressed

- Replaced public lock-route and lock-event wording with finalization wording in code, tests, scripts, examples, and active docs.
- Added `can_admin_or_task_creator_manage()` and used it for task visibility, locked context, checker-run detail/list, audit events, and manual checker trigger authorization.
- Prevented a worker who also carries `project_manager` but did not create the task from receiving operator-shaped data for an assigned task.
- Mapped automatic post-submit checker audit to `workstream-system:pre-review-gate` and preserved requester actor provenance for authorized operator reads.
- Made finalization reject unfinished tasks, unsubmitted submissions, non-latest versions, unauthorized actors, and missing/malformed task locked context.
- Changed public response projection from `locked_at` to `finalized_at`.
- Removed overclaiming helper names and active stale wording around database proof.
- Updated API contract and Terminal Benchmark drills to use `/finalize`, `finalized_at`, checker-run APIs, audit APIs, and HTTP-visible lifecycle proof.

## Commands Run

```bash
cd backend && .venv/bin/pytest tests/test_tasks.py tests/test_checkers.py
cd backend && .venv/bin/ruff check app/modules/tasks app/modules/checkers tests/test_tasks.py tests/test_checkers.py scripts/api_contract_e2e.py scripts/week2_api_e2e.py ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/api_contract_e2e.py
bash -lc 'set -a; source /home/abiorh/flow/jarvis-live-agent-proof/.env; set +a; export WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test; export WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL=${WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL:-gpt-4.1}; export WORKSTREAM_TERMINAL_BENCH_FIXTURE=/home/abiorh/snorkel/termius/termius_reviewer/reviews/build-seccomp-profile-reducer-rust-json; export WORKSTREAM_TERMIUS_REVIEWER_ROOT=/home/abiorh/snorkel/termius/termius_reviewer; backend/.venv/bin/python examples/terminal_benchmark/terminal_benchmark_api_e2e.py'
python3 scripts/check_markdown_links.py
git diff --check
```

Active stale wording scan:

```bash
rg -n -P "<old public submission handoff, lock-event, database-proof, and helper-name patterns>" backend/app backend/scripts backend/tests examples/terminal_benchmark docs .agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation
```

Results:

- Task/checker suite: 132 passed in 1044.49s.
- Ruff: passed.
- API contract real API E2E: passed and exercised `/finalize`, checker-run reads, audit-event reads, and scoped access.
- Terminal Benchmark real API E2E: passed using the real OpenAI Agents SDK adapter and fixture `build-seccomp-profile-reducer-rust-json`.
- Terminal Benchmark scenario summary: `complete_packet=review_pending`, `missing_static_guard=pre_submit_blocked_no_submission`, `low_quality_v1=needs_revision`, `fixed_low_quality_v2=review_pending`, `worker_profile_setup=canonical_worker_profile_api`.
- Markdown link check: passed for 24 changed Markdown files.
- Diff whitespace check: passed.
- Active stale wording scan: passed with no matches.

## Remaining Risks

- Post-submit checker policy derivation remains future work; this chunk only proves current project post-submit checker execution and visibility after finalization.
- Full reviewer packet visibility remains a follow-up before broader review lifecycle expansion.
- Historical evidence files still describe earlier lock/no-database-inspection decisions; active product docs and current chunk contracts now use finalization and HTTP-visible proof wording.
