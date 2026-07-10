# Internal Review Evidence: WS-POL-002-02

## Chunk

WS-POL-002-02

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: fa7afaf4bda1db88ec6b50d7933643ba18e527fe

Reviewed at: 2026-07-10T11:45:18Z

Reviewer run ids: senior-engineering-019f4bd3-ebd5-7c22-a648-03017f876c01, qa-test-019f4bb9-6b99-74e0-aba8-d69c05a312a9, security-auth-019f4bc9-c8fe-7de1-be80-ebdf868a3e1d, product-ops-019f4bb9-83e5-7ce2-bed6-0de05726334e, architecture-019f4bb9-903b-7a92-8b2f-461bc2b6f9b4, docs-019f4bd3-f4cc-7620-8eed-7416b4fa64fc, reuse-dedup-019f4bc9-ab0a-7382-b4be-becf86d441e1, test-delta-019f4bd4-06fc-7802-a16d-cf2641034b67, ci-integrity-019f4bd3-fe3a-71d2-8398-adb2de70eff1

## Reviewed Change

Branch: `codex/ws-pol-002-02-post-submit-derivation`

Scope:

- Adds a constrained `PostSubmitCheckerPolicyDerivationAgent` contract to the project agent interface.
- Extends the OpenAI Agents SDK adapter to derive post-submit checker policy specs during setup only.
- Extends the existing project setup queue/worker path so post-submit derivation runs after submission artifact policy approval and pre-submit checker compilation.
- Adds post-submit setup-run states and output fields for derivation, compile, blocked, failed, and stale continuation handling.
- Persists compiled project `PostSubmitCheckerPolicy` rows bound to guide id, source snapshot id/hash, effective policy id/hash, and pre-submit checker id/bundle hash.
- Blocks activation until the post-submit policy is setup-approved with setup-role provenance.
- Treats guide/source excerpts as untrusted data, rejects unsupported/unknown checkers, and returns bounded redacted setup summaries.
- Hardens stale continuation handling across worker start, in-flight derivation, enqueue bookkeeping, terminal status updates, and duplicate worker retries.
- Repairs stale test/e2e fixtures so guide request bodies no longer carry the
  removed manual `post_submit_checker_policy` field.
- Documents the temporary CI activation bridge as a test-only
  generated-policy approval plus setup-ledger marker until `WS-POL-002-03`
  adds the server-owned approval API.
- Normalizes post-submit worker terminal results so compiled and idempotent
  paths both return `status`, `idempotent`, and
  `post_submit_checker_policy_id`.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Exact-SHA review confirmed `fa7afaf` final delta is wording-only and no new operational risk was added; low future crash-window hardening remains non-blocking. |
| QA/test | PASS WITH LOW RISKS | None | Confirmed stale manual guide-body payloads are removed, activation/setup coverage remains in place, and the CI bridge is bounded until `WS-POL-002-03`. |
| security/auth | PASS | None | Confirmed the prior worker-result auditability finding is resolved and no auth, tenant-boundary, PII, secrets, prompt-injection, or activation-bypass issue remains. |
| product/ops | PASS WITH LOW RISKS | None | Confirmed setup defects stay operator-visible, activation rejects compiled-only policies, and approval/correction API remains the next chunk boundary. |
| architecture | PASS WITH LOW RISKS | None | Confirmed project-scoped setup-time derivation, deterministic runtime boundary, no per-task checker generation, and no product shortcut from the CI bridge. |
| docs | PASS WITH LOW RISKS | None | Exact-SHA review confirmed CI bridge wording is clear, stale helper names are gone, and public docs need no further update. |
| reuse/dedup | PASS WITH LOW RISKS | None | Accepted low temporary duplication in test/e2e bridge fixture construction; remove or centralize it when `WS-POL-002-03` replaces the bridge. |
| test delta | PASS | None | Exact-SHA review confirmed no skipped/xfail tests, no weakened assertions, final delta is wording-only, and generated-output/manual-payload rejection coverage replaces legacy expectations. |
| ci integrity | PASS AFTER FIXES | None | Exact-SHA review found no CI/test weakening; its only blocker was stale evidence, fixed by this evidence refresh. |

## Valid Findings Addressed

- QA found stale post-commit enqueue success/failure bookkeeping could mutate a newer setup run. Added `update_project_setup_run_task_id`, routed enqueue failure through continuation-aware status updates, and added stale enqueue regression coverage.
- Senior engineering found duplicate/retried workers could regress an already compiled setup run to blocked/failed. `update_project_setup_run_status` now returns the existing compiled state for matching duplicate failure updates, and the worker treats that as idempotent success.
- Earlier QA found a stale in-flight derivation could insert a policy before terminal stale validation. `run_post_submit_checker_policy_derivation_agent` now validates the setup-run continuation payload under lock before inserting, and the stale in-flight regression proves no stale policy row remains.
- Security and architecture required setup-role approval provenance for activation. The model, migration, service guard, and tests now require setup-role approval metadata before activation accepts the generated post-submit policy.
- Docs/product review found stale wording around setup approval and manual checker attachment. README, operating manual, and the guide update docstring were corrected.
- Product/ops and docs found compiled-only activation ambiguity. Activation now rejects compiled-only policies until a setup approval path records approval provenance.
- Unsupported and unknown checker paths are fail-closed, operator-visible, and covered by tests.
- Test/e2e fixtures were aligned with the removed guide-body
  `post_submit_checker_policy` field. Manual guide-body usage now exists only
  in explicit rejection tests.
- The CI activation bridge was renamed and documented as a temporary
  test-only policy approval plus setup-ledger marker until the
  server-owned approval API lands in `WS-POL-002-03`.
- Security's low worker-result auditability finding was fixed by normalizing
  post-submit worker terminal results across compiled and idempotent paths.
- Docs and CI integrity findings about stale evidence are addressed by
  rebinding this evidence file and the trust bundle to `fa7afaf`.

## Commands Run

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

Results:

- Focused stale/setup suite: 13 passed, 214 deselected.
- Full project and agent-runtime suite: 229 passed in 2037.08s.
- Alembic suite: 6 passed in 54.19s.
- Task suite: 86 passed in 944.91s.
- Checker suite: 75 passed in 303.48s.
- Full backend suite after stale fixture repair: 442 passed in 4100.54s.
- Exact-head post-submit setup focused suite: 4 passed in 126.24s.
- Exact-head old-checker compiler regression: 2 passed in 15.34s.
- API contract real API drill passed after the CI bridge scope repair.
- Ruff: passed.
- Py compile: passed.
- Docstring coverage: 100.0%.
- Stale wording scan: passed.
- Markdown link check: passed for 14 changed Markdown files.
- Agent gates: 26 passed.
- Loop memory state check: passed.
- Diff whitespace check: passed.

## Remaining Risks

- Senior engineering accepted a low fail-closed crash window between compiled post-submit policy commit and setup-run status update. A later hardening chunk can make the first compiled policy win by provenance during retry recovery.
- Reuse/dedup accepted a low future extraction opportunity for repeated effective/pre-submit provenance checks.
- Reuse/dedup accepted a low test-maintenance risk around duplicated default-checker literal expectations.
- Reuse/dedup and test-delta accepted a low temporary CI activation bridge risk:
  it directly writes approved generated post-submit policy/setup-ledger rows
  only after API-created prerequisites and real compiler output. `WS-POL-002-03`
  must replace this bridge with the server-owned approval API.
- External review and GitHub Actions must rerun after this evidence refresh is pushed.
