# Internal Review Evidence: WS-POL-002-02

## Chunk

WS-POL-002-02

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 26efde405a13add052607eb4e093706d856f4746

Reviewed at: 2026-07-10T12:35:46Z

Reviewer run ids: senior-engineering-019f4bf9-a0e8-73b1-be5d-f8f182fd1eed, qa-test-019f4bf9-ac36-79e1-9e86-5e244ac12b63, security-auth-019f4bf9-b1c8-7e92-8dd8-c0168b0312ba, product-ops-019f4c02-907d-70e3-98a5-21c4312feceb, architecture-019f4bf9-c1c8-7ef3-bb25-b723d566d08d, docs-019f4c02-9963-7ec1-80b6-994b206fc021, reuse-dedup-019f4bf1-195a-7ce3-bd4e-3a23b466c0a6, test-delta-019f4c02-a13e-7370-9b45-f353e5482a5b, ci-integrity-019f4bf9-cb2f-7bb0-993f-96815963973e

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
- Addresses CodeRabbit external-review cleanup by using Alembic naming
  conventions for composite FK create/drop calls and deduplicating mutable
  Celery setup task configuration.
- Adds focused regression coverage that both project setup Celery task entry
  points receive the same mutable broker/result/eager configuration.
- Records CodeRabbit findings in a separate external-review response artifact
  instead of mixing external review into internal review evidence.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Found no maintainability issue in the final code delta; stale evidence was the only blocker and is fixed by this refresh. |
| QA/test | PASS AFTER FIXES | None | Confirmed Alembic, queue config, worker-result, lint, wording, link, agent-gate, and loop-memory proof; stale evidence was the only blocker. |
| security/auth | PASS AFTER FIXES | None | Found no auth bypass, tenant leak, PII/secrets issue, prompt-injection exposure, or product-token misuse; stale evidence was the only blocker. |
| product/ops | PASS WITH LOW RISKS | None | Confirmed setup remains operator-visible and engineering verdicts remain separate from Workstream product decisions; external-response wording fix is included in this refresh. |
| architecture | PASS AFTER FIXES | None | Confirmed setup-time derivation and project-scoped policy boundaries; stale evidence was the only blocker. |
| docs | PASS AFTER FIXES | None | Confirmed external review is separate from internal evidence and loop/status wording is correct after the wording fix committed with this refresh. |
| reuse/dedup | PASS WITH LOW RISKS | None | Confirmed setup queue config dedup is appropriate; low future provenance-validation extraction remains accepted. |
| test delta | PASS WITH LOW RISKS | None | Confirmed no skipped/weakened assertions and the new queue config regression covers effective shared config; low structural-enumeration caveat accepted. |
| ci integrity | PASS AFTER FIXES | None | Found no CI/test-runner weakening; stale evidence was the only blocker and is fixed by this refresh. |

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
- CodeRabbit external-review findings were separated into
  `WS-POL-002-02-external-review-response.md`. Valid findings were fixed;
  stale or invalid findings were documented there.
- CodeRabbit's valid migration naming finding was fixed by wrapping composite
  checker-policy FK names and matching downgrade drops with `op.f()`.
- CodeRabbit's valid Celery config duplication finding was fixed by applying
  mutable setup task configuration through one shared loop.
- Test-delta's queue-config proof gap was fixed by adding
  `test_project_setup_queue_syncs_all_setup_task_settings`.
- Product/docs wording findings about the external-response human checkpoint
  were fixed in the external-review response.
- Reviewer findings about stale evidence are addressed by rebinding this
  evidence file and the trust bundle to `26efde4`.

## Commands Run

```bash
cd backend && .venv/bin/pytest tests/test_projects.py -q -k "post_submit_continuation or corrected_submission_artifact_policy or stale_in_flight_post_submit or status_update_rejects_stale_continuation or enqueue_bookkeeping_rejects_stale or compiled_post_submit_setup_run_does_not_regress or activation_rejects_compiled_post_submit or approved_by_non_setup_role or unsupported_checker_gap or unknown_checker_blocks or setup_summary_redacts"
cd backend && .venv/bin/pytest tests/test_projects.py tests/test_agent_runtime.py -q
cd backend && .venv/bin/pytest tests/test_alembic.py -q
cd backend && .venv/bin/pytest tests/test_tasks.py -q
cd backend && .venv/bin/pytest tests/test_checkers.py -q
cd backend && .venv/bin/pytest -q
cd backend && .venv/bin/pytest tests/test_projects.py::test_policy_approval_resumes_post_submit_setup_continuation tests/test_projects.py::test_post_submit_continuation_is_idempotent_after_compile tests/test_projects.py::test_post_submit_continuation_running_worker_redelivery_resumes_setup tests/test_projects.py::test_activation_rejects_compiled_post_submit_checker_policy_before_approval -q
cd backend && .venv/bin/pytest tests/test_projects.py::test_project_setup_queue_syncs_all_setup_task_settings tests/test_projects.py::test_post_submit_continuation_is_idempotent_after_compile tests/test_projects.py::test_post_submit_continuation_running_worker_redelivery_resumes_setup -q
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
- Final-head queue/worker focused suite: 3 passed in 35.97s.
- Final-head setup queue config regression: 1 passed in 2.62s.
- Final-head Alembic suite: 6 passed in 67.47s.
- Exact-head old-checker compiler regression: 2 passed in 15.34s.
- API contract real API drill passed after the CI bridge scope repair.
- Ruff: passed.
- Py compile: passed.
- Docstring coverage: 100.0%.
- Stale wording scan: passed.
- Markdown link check: passed for 15 changed Markdown files.
- Agent gates: 26 passed.
- Loop memory state check: passed.
- Diff whitespace check: passed.

## Remaining Risks

- Senior engineering accepted a low fail-closed crash window between compiled post-submit policy commit and setup-run status update. A later hardening chunk can make the first compiled policy win by provenance during retry recovery.
- Reuse/dedup accepted a low future extraction opportunity for repeated effective/pre-submit provenance checks.
- Reuse/dedup accepted a low test-maintenance risk around duplicated default-checker literal expectations.
- Test-delta accepted a low structural caveat that the setup queue config
  regression proves effective shared Celery config behavior, not an isolated
  fake-task enumeration.
- Reuse/dedup and test-delta accepted a low temporary CI activation bridge risk:
  it directly writes approved generated post-submit policy/setup-ledger rows
  only after API-created prerequisites and real compiler output. `WS-POL-002-03`
  must replace this bridge with the server-owned approval API.
- External review and GitHub Actions must rerun after this evidence refresh is pushed.
