# Internal Review Evidence: WS-POL-001-09

## Chunk

WS-POL-001-09

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 4cd69b525665d5c9000734300aa313d9713c575f

Reviewed at: 2026-07-06T04:59:38Z

Reviewer run IDs: senior-engineering-review-019f35c3-7e90-74e3-8c90-11de33de686e, qa-test-review-019f359f-bc92-7060-83ee-f13ce919bc81, security-auth-review-019f35c3-9ae4-76b0-891b-17879e1ef4da, product-ops-review-019f35bd-a6c1-77b1-a93b-2188bafe6af1, architecture-review-019f35c3-b43a-75a2-a8b5-3f142a244734, docs-review-019f35c3-d889-76f1-af7d-6d13784458c8, reuse-dedup-review-019f35be-0a39-7462-9ecd-616a6ef57d2f, test-delta-review-019f35ca-554f-7211-a6a4-b7cf7c2d7560

## Reviewed Change

Branch: `codex/ws-pol-001-09-openai-agent-sdk-only`

Scope:

- Removes the production `local_fixture` project setup runtime.
- Removes `WORKSTREAM_PROJECT_AGENT_RUNTIME_ADAPTER` from active settings.
- Keeps the project-agent port but makes the factory build only the OpenAI
  Agents SDK runtime for current production code.
- Moves deterministic project-agent behavior into an explicit test-local fake.
- Updates README and Terminal Benchmark example wording so no current operator
  docs imply a deterministic runtime fallback.
- Records `WS-POL-001-09` as the active bounded corrective chunk without
  rewriting prior chunk-contract history.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Verified maintainability, single-path runtime factory, fail-closed model config, no active selector in production code, and append-only chunk-map update. |
| QA/test | PASS | None | Confirmed removed production adapter, old selector ignored/failing closed, explicit test-local fakes, README/demo safety, and focused verification. |
| security/auth | PASS | None | Confirmed no production fixture fallback, old selector ignored by settings, model config fails closed, no secret exposure, and safe local example placeholders. |
| product/ops | PASS | None | Confirmed operator docs require OpenAI SDK model/API-key settings, Week 1 demo autostart is disabled, and product/runtime separation remains clear. |
| architecture | PASS WITH LOW RISKS | None | Confirmed project-agent port stays clean, no hidden fixture runtime remains, and historical chunk history is preserved. Low local `__pycache__` residue is ignored and untracked. |
| docs | PASS | None | Confirmed README and Terminal Benchmark docs no longer expose the removed runtime selector, fallback wording, or stale fixture placeholder. |
| reuse/dedup | PASS WITH LOW RISKS | None | No production abstraction missed. Low risk: repeated test monkeypatch fake injection may become a fixture if it grows further. |
| test delta | PASS | None | Confirmed selector regressions run in `test`, missing model asserts the exact OpenAI model error, valid model returns OpenAI runtime, and no tests were skipped or weakened. |

## Valid Findings Addressed

- Initial reviewers found that the active chunk contract was missing while the
  diff changed runtime code, tests, README, examples, and loop state. Added
  `WS-POL-001-09` chunk contract, active status, and chunk-map entry.
- Reviewers found stale Terminal Benchmark wording that blurred real source
  material with the removed runtime fixture. Updated operator-facing examples
  to use `source-material` wording and removed fallback language.
- Reviewers found retrospective edits to historical `WS-POL-001-02` and
  `WS-POL-001-06` contracts, plus the historical `WS-POL-001-06` entry in
  `CHUNK_MAP.md`. Reverted those historical changes and kept the correction in
  `WS-POL-001-09`.
- Test-delta found the first selector regression would have passed under the
  old production deny path. Strengthened selector tests to run in `test`, assert
  the exact OpenAI model configuration error, and prove valid model settings
  still build `OpenAIAgentSdkProjectGuideRuntime`.
- Docs review found one stale `/path/to/terminal-benchmark-fixture` placeholder.
  Updated it to `/path/to/terminal-benchmark-source-material`.

## Commands Run

```bash
cd backend && .venv/bin/python -m ruff check app/core/config.py app/adapters/project_agents tests/test_projects.py tests/test_config.py
cd backend && .venv/bin/python -m pytest tests/test_projects.py -k 'project_agent_factory_requires_openai_agent_sdk_model or project_agent_factory_ignores_removed_runtime_selector' -q
cd backend && .venv/bin/python -m pytest tests/test_projects.py -k 'project_agent_factory_requires_openai_agent_sdk_model or project_agent_factory_ignores_removed_runtime_selector or openai_runtime_misconfiguration_is_sanitized_and_agent_route_only' -q
cd backend && .venv/bin/python -m pytest tests/test_config.py tests/test_projects.py -k 'create_guide_autostart_runs_celery_pipeline_to_draft_policy or create_guide_autostart_stops_before_derivation_when_sufficiency_blocks or project_agent_factory_requires_openai_agent_sdk_model or project_agent_factory_ignores_removed_runtime_selector or sufficiency_agent_route_is_async_idempotent_and_secret_safe or openai_runtime_misconfiguration_is_sanitized_and_agent_route_only or derivation_agent_allows_warning_report_without_acknowledgement_and_is_idempotent or agent_derived_warning_policy_requires_acknowledgement_before_approval' -q
cd backend && .venv/bin/python -m pytest tests/test_projects.py -k 'agent or autostart or source_snapshot_integrity or openai or project_setup_pipeline' -q
cd backend && .venv/bin/python -m pytest tests/test_config.py tests/test_projects.py -q
cd backend && .venv/bin/docstr-coverage app/adapters/project_agents app/core/config.py --config .docstr.yaml
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
```

Results:

- ruff: passed.
- Selector regression tests: 2 passed, 195 deselected.
- Selector/runtime route focused tests: 3 passed, 194 deselected.
- Expanded focused project-agent slice: 8 passed, 191 deselected.
- Broader project-agent/autostart slice: 31 passed, 165 deselected.
- Full `tests/test_config.py` and `tests/test_projects.py`: 198 passed.
- Docstring coverage: 100.0%.
- Stale wording scan: passed.
- Markdown link check: passed for 7 changed Markdown files.
- Diff whitespace check: passed.

## Remaining Risks

- External GitHub Actions and CodeRabbit have not run for this branch yet. They
  must be recorded separately as external review evidence after a PR is opened.
- Test-local fake injection is repeated in several tests. It is acceptable for
  this chunk, but a shared fixture can be extracted if more project-agent tests
  are added.
