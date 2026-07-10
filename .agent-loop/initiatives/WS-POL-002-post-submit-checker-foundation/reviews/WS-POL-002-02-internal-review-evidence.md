# Internal Review Evidence: WS-POL-002-02

## Chunk

WS-POL-002-02

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 9179f9dced4b5b58c298cb1f93149c26d6d2b6c3

Reviewed at: 2026-07-10T05:27:44Z

Reviewer run ids: senior-engineering-019f4a79-3545-7f62-bf84-098fce8946b4, qa-test-019f4a79-3d75-7ab1-96b6-879259c185ca, security-auth-019f4a4c-2ada-7481-9462-17d28b920582, product-ops-019f4a4c-32af-7710-b929-f5ed38943c19, architecture-019f4a4c-439b-7511-9e35-a4aaaeb192fd, docs-019f4a4c-ae92-7741-aa03-25da1c94c80f, reuse-dedup-019f4a79-4970-7db2-8d26-2a29546544a8, test-delta-019f4a79-552b-7a02-bdc5-7b68afcc3ba4, ci-integrity-019f4a79-6787-7830-8eaa-7801b45f747e

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

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Confirmed duplicate/retried continuation failures no longer regress `post_submit_policy_compiled`; noted a low future hardening risk around crash recovery between compiled policy commit and setup-run status write. |
| QA/test | PASS | None | Confirmed stale enqueue bookkeeping, stale status updates, stale in-flight derivation, and duplicate worker regression tests cover the prior failures. |
| security/auth | PASS | None | Confirmed setup roles, provenance binding, redaction, prompt-injection boundaries, stale replay handling, and activation fail-closed behavior. |
| product/ops | PASS WITH LOW RISKS | None | Confirmed setup defects stay operator-visible and do not become product review decisions; stale router wording was fixed. |
| architecture | PASS WITH LOW RISKS | None | Confirmed setup-time agent boundary and project-scoped policy; stale enqueue bookkeeping was fixed; future catalog abstraction accepted as non-blocking. |
| docs | PASS WITH LOW RISKS | None | Confirmed docs align after README, operations manual, and route docstring wording fixes. |
| reuse/dedup | PASS WITH LOW RISKS | None | Low future extraction opportunity for repeated provenance checks and test default-list literals; no blocking missed abstraction. |
| test delta | PASS | None | Confirmed additive tests, no skipped/xfail tests, and no weakened coverage. |
| ci integrity | PASS | None | No workflow/config/test-runner weakening; deterministic proof matches the changed files. |

## Valid Findings Addressed

- QA found stale post-commit enqueue success/failure bookkeeping could mutate a newer setup run. Added `update_project_setup_run_task_id`, routed enqueue failure through continuation-aware status updates, and added stale enqueue regression coverage.
- Senior engineering found duplicate/retried workers could regress an already compiled setup run to blocked/failed. `update_project_setup_run_status` now returns the existing compiled state for matching duplicate failure updates, and the worker treats that as idempotent success.
- Earlier QA found a stale in-flight derivation could insert a policy before terminal stale validation. `run_post_submit_checker_policy_derivation_agent` now validates the setup-run continuation payload under lock before inserting, and the stale in-flight regression proves no stale policy row remains.
- Security and architecture required setup-role approval provenance for activation. The model, migration, service guard, and tests now require setup-role approval metadata before activation accepts the generated post-submit policy.
- Docs/product review found stale wording around setup approval and manual checker attachment. README, operating manual, and the guide update docstring were corrected.
- Product/ops and docs found compiled-only activation ambiguity. Activation now rejects compiled-only policies until a setup approval path records approval provenance.
- Unsupported and unknown checker paths are fail-closed, operator-visible, and covered by tests.

## Commands Run

```bash
cd backend && .venv/bin/pytest tests/test_projects.py -q -k "post_submit_continuation or corrected_submission_artifact_policy or stale_in_flight_post_submit or status_update_rejects_stale_continuation or enqueue_bookkeeping_rejects_stale or compiled_post_submit_setup_run_does_not_regress or activation_rejects_compiled_post_submit or approved_by_non_setup_role or unsupported_checker_gap or unknown_checker_blocks or setup_summary_redacts"
cd backend && .venv/bin/pytest tests/test_projects.py tests/test_agent_runtime.py -q
cd backend && .venv/bin/pytest tests/test_alembic.py -q
cd backend && .venv/bin/ruff check app/adapters/project_agents/openai_agent_sdk.py app/interfaces/project_agents.py app/workers/project_setup.py app/modules/projects/setup_queue.py app/modules/projects/service.py app/modules/projects/schemas.py app/modules/projects/models.py app/modules/projects/repository.py app/modules/projects/router.py tests/test_projects.py tests/test_agent_runtime.py tests/test_alembic.py
cd backend && .venv/bin/python -m py_compile app/adapters/project_agents/openai_agent_sdk.py app/interfaces/project_agents.py app/workers/project_setup.py app/modules/projects/setup_queue.py app/modules/projects/service.py app/modules/projects/schemas.py app/modules/projects/models.py app/modules/projects/repository.py app/modules/projects/router.py tests/test_projects.py tests/test_agent_runtime.py tests/test_alembic.py
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
- Ruff: passed.
- Py compile: passed.
- Docstring coverage: 100.0%.
- Stale wording scan: passed.
- Markdown link check: passed for 12 changed Markdown files.
- Agent gates: 26 passed.
- Loop memory state check: passed.
- Diff whitespace check: passed.

## Remaining Risks

- Senior engineering accepted a low fail-closed crash window between compiled post-submit policy commit and setup-run status update. A later hardening chunk can make the first compiled policy win by provenance during retry recovery.
- Reuse/dedup accepted a low future extraction opportunity for repeated effective/pre-submit provenance checks.
- Reuse/dedup accepted a low test-maintenance risk around duplicated default-checker literal expectations.
- External review and GitHub Actions are still pending for this branch after the evidence commit.
