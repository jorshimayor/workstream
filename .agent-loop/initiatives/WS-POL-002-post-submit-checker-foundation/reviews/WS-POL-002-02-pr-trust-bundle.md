# PR Trust Bundle: WS-POL-002-02

## Chunk

`WS-POL-002-02` - Post-Submit Derivation Agent And Resumable Setup Integration

## Goal

Add setup-time post-submit checker derivation and compilation after
submission artifact policy approval and pre-submit checker compilation, without
introducing runtime agent judgment or per-task checker generation.

## Human-Approved Intent

Post-submit checkers must follow the same shape as pre-submit:

```text
Project guide/source material
-> setup-time derivation agent
-> trusted Workstream compiler
-> project PostSubmitCheckerPolicy
-> tasks later lock references
-> finalized submissions execute deterministic checkers
```

The agent derives a constrained specification during setup. Workstream compiles
and owns the deterministic checker policy. The agent never judges worker
submissions at runtime.

## What Changed

- Added post-submit derivation models to the project-agent interface.
- Extended the OpenAI Agents SDK adapter with a post-submit derivation prompt and structured output parsing.
- Extended project setup continuation after submission artifact policy approval and pre-submit compile.
- Added post-submit setup-run statuses and persisted output metadata.
- Added migration `0014_post_submit_setup` for post-submit setup provenance.
- Added generated post-submit policy provenance fields:
  - guide id/version
  - source snapshot id/hash
  - effective project policy id/hash
  - pre-submit checker policy id/bundle hash
  - lifecycle and setup approval provenance
- Enforced activation rejection for compiled-only or non-setup-approved post-submit policies.
- Added stale continuation guards for enqueue bookkeeping, worker start, in-flight derivation, terminal state updates, and duplicate worker retries.
- Updated docs to describe the setup continuation and the next approval chunk boundary.
- Removed stale manual `post_submit_checker_policy` request-body usage from
  test/e2e setup paths and kept it only in explicit rejection tests.
- Added a clearly named temporary CI activation bridge for generated
  post-submit policy approval plus setup-ledger marking until `WS-POL-002-03`
  provides the server-owned approval API.
- Normalized post-submit worker terminal results so compiled and idempotent
  paths both include `status`, `idempotent`, and
  `post_submit_checker_policy_id`.

## Design Chosen

The existing project setup queue and worker were extended. No disconnected
post-submit-only queue was added.

The setup pipeline now continues like this:

```text
policy_draft_ready
-> setup-authorized submission artifact policy approval
-> effective project submission artifact policy
-> compiled project pre-submit checker policy
-> enqueue post-submit setup continuation
-> PostSubmitCheckerPolicyDerivationAgent
-> trusted post-submit compiler
-> compiled project PostSubmitCheckerPolicy pending setup approval
```

The post-submit policy remains project-scoped. Tasks will later lock the
project policy reference; they do not derive or compile their own checker
bundle.

## Alternatives Rejected

- Runtime agent judgment: rejected. Runtime executes deterministic checkers only.
- Per-task checker derivation: rejected. Policy is project-scoped.
- Manual post-submit policy in guide payloads: rejected. Generated setup output owns this path.
- Separate post-submit-only queue: rejected. The current project setup queue is the correct boundary.
- Arbitrary generated checker code: rejected for v0.1.

## Scope Control

No task runtime module changes, frontend/demo work, payment, reputation,
blockchain, marketplace, or settlement work were included.

The route change is docstring-only to remove stale OpenAPI wording that implied
manual post-submit policy updates.

## Product Behavior

Setup-authorized admins/project managers can approve the submission artifact
policy. That approval creates the effective project policy and compiled
pre-submit checker bundle, then resumes setup into post-submit derivation.

Unsupported post-submit checker requirements block setup with bounded
operator-visible details. Workers and reviewers do not receive internal setup
defects as product review decisions.

Guide activation still requires setup approval of the compiled post-submit
policy. This chunk creates the compiled generated output; `WS-POL-002-03`
implements the server-owned visibility and approval surface.

## Acceptance Criteria Proof

- Derivation runs only after submission artifact policy approval and pre-submit compile.
- Blocked sufficiency prevents post-submit derivation.
- Unsupported required checker gaps block setup.
- Unknown checkers fail closed.
- Successful derivation creates compiled project `PostSubmitCheckerPolicy`.
- Activation rejects compiled-only post-submit policies.
- Provenance binds guide, source snapshot, effective policy, and pre-submit checker policy.
- Hostile source is treated as data and cannot override Workstream defaults.
- API-visible setup summaries are bounded and redacted.
- Stale workers cannot insert stale policy rows.
- Stale enqueue success/failure bookkeeping cannot mutate a newer setup run.
- Duplicate worker failures cannot regress an already compiled setup run.

## Tests/Checks Run

```bash
cd backend && .venv/bin/pytest tests/test_projects.py -q -k "post_submit_continuation or corrected_submission_artifact_policy or stale_in_flight_post_submit or status_update_rejects_stale_continuation or enqueue_bookkeeping_rejects_stale or compiled_post_submit_setup_run_does_not_regress or activation_rejects_compiled_post_submit or approved_by_non_setup_role or unsupported_checker_gap or unknown_checker_blocks or setup_summary_redacts"
cd backend && .venv/bin/pytest tests/test_projects.py tests/test_agent_runtime.py -q
cd backend && .venv/bin/pytest tests/test_alembic.py -q
cd backend && .venv/bin/pytest tests/test_tasks.py -q
cd backend && .venv/bin/pytest tests/test_checkers.py -q
cd backend && .venv/bin/pytest -q
cd backend && .venv/bin/pytest tests/test_projects.py::test_policy_approval_resumes_post_submit_setup_continuation tests/test_projects.py::test_post_submit_continuation_is_idempotent_after_compile tests/test_projects.py::test_post_submit_continuation_running_worker_redelivery_resumes_setup tests/test_projects.py::test_activation_rejects_compiled_post_submit_checker_policy_before_approval -q
cd backend && .venv/bin/pytest tests/test_checkers.py::test_old_checker_name_blocks_post_submit_compilation_without_alias -q
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/alembic downgrade base && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/api_contract_e2e.py
cd backend && .venv/bin/ruff check app/adapters/project_agents/openai_agent_sdk.py app/interfaces/project_agents.py app/workers/project_setup.py app/modules/projects/setup_queue.py app/modules/projects/service.py app/modules/projects/schemas.py app/modules/projects/models.py app/modules/projects/repository.py app/modules/projects/router.py tests/test_projects.py tests/test_agent_runtime.py tests/test_alembic.py
cd backend && .venv/bin/ruff check app tests scripts
cd backend && .venv/bin/python -m py_compile app/adapters/project_agents/openai_agent_sdk.py app/interfaces/project_agents.py app/workers/project_setup.py app/modules/projects/setup_queue.py app/modules/projects/service.py app/modules/projects/schemas.py app/modules/projects/models.py app/modules/projects/repository.py app/modules/projects/router.py tests/test_projects.py tests/test_agent_runtime.py tests/test_alembic.py
python3 -m py_compile backend/scripts/api_contract_e2e.py backend/scripts/week2_api_e2e.py examples/terminal_benchmark/terminal_benchmark_api_e2e.py
cd backend && .venv/bin/docstr-coverage --config .docstr.yaml
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/test_agent_gates.py
python3 scripts/check_loop_memory_state.py
git diff --check
```

Result summary:

- Focused stale/setup suite: 13 passed.
- Full project and agent-runtime suite: 229 passed.
- Alembic suite: 6 passed.
- Task suite: 86 passed.
- Checker suite: 75 passed.
- Full backend suite after stale fixture repair: 442 passed.
- Exact-head post-submit setup focused suite: 4 passed.
- Exact-head old-checker compiler regression: 2 passed.
- API contract real API drill passed after the CI bridge scope repair.
- Ruff, py_compile, docstring coverage, stale wording, Markdown links, agent gates, loop memory, and diff whitespace checks passed.

## Reviewer Results

Internal review evidence:

- `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-02-internal-review-evidence.md`

Reviewed code SHA: `fa7afaf4bda1db88ec6b50d7933643ba18e527fe`

Reviewed at: `2026-07-10T11:45:18Z`

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Exact-SHA review found no new maintainability or operational findings. |
| QA/test | PASS WITH LOW RISKS | None | Setup/activation/e2e fixture repair remains covered; CI bridge risk accepted for `WS-POL-002-02`. |
| security/auth | PASS | None | Prior worker-result auditability finding resolved; no auth/security issue remains. |
| product/ops | PASS WITH LOW RISKS | None | Setup defects stay operator-visible and separate from review decisions. |
| architecture | PASS WITH LOW RISKS | None | Setup-time/project-scoped boundaries preserved; no product shortcut from CI bridge. |
| docs | PASS WITH LOW RISKS | None | Exact-SHA review confirmed bridge wording is clear and stale helper names are gone. |
| reuse/dedup | PASS WITH LOW RISKS | None | Low temporary duplication in test/e2e bridge fixture construction accepted until `WS-POL-002-03`. |
| test delta | PASS | None | Exact-SHA review found no skipped/weakened tests and final delta was wording-only. |
| CI integrity | PASS AFTER FIXES | None | No CI/test weakening; stale evidence blocker fixed by this trust/evidence refresh. |

## External Review

External review response:

- `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-02-external-review-response.md`

CodeRabbit comments are triaged there: valid findings were fixed, stale or
invalid findings were documented, and GitHub Actions plus CodeRabbit must be
checked on the PR head before human merge review.

## Remaining Risks

- A narrow fail-closed crash window remains between post-submit policy commit
  and setup-run compiled-status write. Retry/operator repair can recover; later
  hardening can make first compiled policy win by provenance.
- Provenance validation appears in a few service locations for different
  exception semantics. This is accepted for this chunk but should be extracted
  if setup policy grows further.
- The CI activation bridge is temporary. `WS-POL-002-03` must replace direct
  test/e2e policy approval plus setup-ledger marking with the server-owned
  post-submit approval API.

## Human Review Focus

- Confirm the agent derives setup policy only.
- Confirm unsupported checker requirements fail closed.
- Confirm no runtime submission judgment is delegated to an agent.
- Confirm tasks are still not generating their own checker policies.

## Human Merge Ownership

Only the user can approve and merge this PR. Codex must not merge it without
explicit user approval for that specific PR.
