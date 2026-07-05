# Internal Review Evidence: WS-POL-001-06

## Chunk

WS-POL-001-06

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: bab2fe8680407dd457016e9023970d7b5fcce95f

Reviewed at: 2026-07-05T12:14:01Z

Reviewer run IDs: 019f31e1-520e-7fb1-905c-ae156be67b38, 019f31e4-536c-7860-b036-488bbe55b4d7, 019f31e4-6eaa-7522-ba73-2fc7b4617082, 019f31e4-9085-7021-802e-46f73d784d7a, 019f31e4-b8bb-79b2-9617-1be43d6380ad, 019f31e4-eb29-7b83-9355-43452e50c8cb, 019f31e5-1700-7e21-89eb-8c06c7edee7d, 019f31f2-0cd9-7600-92cc-93a8fbd7eb04, 019f31f2-5cba-7c21-8b8b-894d2d59cab3, 019f31f2-833e-7c22-86ac-20a3e69c0a88, 019f31f2-aa70-7ed1-9aaf-dcb98134dea2, 019f31f2-dc12-7cf0-b8d8-c60497503f52, 019f31f3-0e03-7260-baae-7ef65184ee48, 019f3227-764f-7c53-818a-513ac2d4d12b, 019f3227-9311-7c00-975a-6484b4c6af1b, 019f3227-c029-7680-a0c1-14de4705ebf1, 019f322c-5b3c-7e00-9a46-6190c253f298, 019f322f-73d7-7291-80f2-6443c334dd5e

## Reviewed Change

Branch: `codex/ws-pol-001-06-terminal-benchmark-drill`

Scope:

- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/**`
- `README.md`
- `backend/alembic/versions/0010_remove_legacy_project_guide_fields.py`
- `backend/app/adapters/project_agents/local_fixture.py`
- `backend/app/modules/projects/models.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/modules/tasks/service.py`
- `backend/tests/test_alembic.py`
- `backend/tests/test_checkers.py`
- `backend/tests/test_projects.py`
- `backend/tests/test_tasks.py`
- `docs/architecture_data_model.md`
- `docs/architecture_lockdown.md`
- `docs/architecture_system_architecture.md`
- `docs/operations_operator_workflow.md`
- `docs/operations_project_operating_manual.md`
- `docs/operations_queue_policy.md`
- `docs/operations_reviewer_workflow.md`
- `docs/product_first_user_flows.md`
- `docs/roadmap_implementation_backlog.md`
- `docs/spec_chunk_3_project_guide_foundation.md`
- `docs/spec_chunk_4_task_queue_assignment.md`
- `docs/template_project_guide.md`
- `docs/template_task.md`
- `examples/terminal_benchmark/**`

The chunk now does two things in one approved scope: keeps the Terminal
Benchmark fixture drill as example proof material, and removes stale
construction-state product contracts before continuing pre-submit checker work.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Initial blockers were untracked migration and stale evidence. Scope and migration are now included; evidence is refreshed in this artifact. |
| qa/test | PASS | None | Confirmed request hard gates, migration cleanup, locked policy context, and Terminal Benchmark example forcing the OpenAI Agents SDK path. |
| security/auth | PASS | None | Confirmed request-body fail-closed behavior, activation provenance, fail-closed snapshot migration, no normal-path secret/path leakage, and bounded SDK runtime settings. |
| product/ops | PASS | None | Confirmed `PaymentPolicy` owns payment terms and task-visible payout values are locked/stamped snapshots, not project/task create inputs. |
| architecture | PASS | None | Confirmed scope drift is resolved and Terminal Benchmark remains outside product runtime. |
| docs | PASS | None | Confirmed current-contract docs align on shell project creation, human-facing guides, task-owned contract fields, and OpenAI Agents SDK drill requirements. |
| reuse/dedup | PASS | None | Confirmed repeated legacy field lists are migration/test proof scaffolding, not parallel runtime contracts. |
| test delta | PASS WITH LOW RISKS | None | Confirmed tests were added/updated without weakening assertions; low risk noted around example checker-row assertions covered elsewhere. |

## Valid Findings Addressed

- Tracked and tested `0010_remove_legacy_project_guide_fields.py`.
- Removed project-owned payment fields from the current project model/API.
- Kept `base_amount`, `currency`, and payout terms under `PaymentPolicy`.
- Removed legacy structured guide request/response/model fields, including
  `evidence_policy`, guide-side required fields, guide rubrics, and guide
  checklist aliases.
- Preserved `ProjectGuide.approved_by` and `effective_at` as server-written
  activation provenance and restored them to read responses.
- Kept `approved_by` and `effective_at` forbidden in create/update request bodies.
- Made the cleanup migration fail closed when old `guide_source_snapshots`
  exist, so stale snapshot provenance cannot survive the destructive cleanup.
- Stopped task screening from reading guide-side `required_task_fields`.
- Reworded active docs so task screening uses task-owned contract fields and
  locked policy context.
- Reworded operator, reviewer, architecture, roadmap, project-guide, and task
  docs so payment terms are policy-owned and task payout values are locked
  snapshots.
- Removed Terminal Benchmark-specific branching from the local fixture adapter.
- Updated the Terminal Benchmark example to require the OpenAI Agents SDK
  adapter and real Termius project guide, reviewer program, task TOML, and
  review packet material.
- Updated `WS-POL-001-06` chunk scope and master chunk map to include the
  intentional docs and migration cleanup.

## Verification

Passed locally:

```bash
git diff --check
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
cd backend && uv run ruff check app tests ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
cd backend && uv run pytest tests/test_alembic.py -q
cd backend && uv run pytest tests/test_checkers.py -q
cd backend && uv run pytest tests/test_tasks.py -q
cd backend && uv run pytest tests/test_projects.py -q
```

Results:

- `tests/test_alembic.py`: 6 passed
- `tests/test_checkers.py`: 47 passed
- `tests/test_tasks.py`: 60 passed
- `tests/test_projects.py`: 188 passed

Focused suites also passed during the repair loop:

- project payment-field rejection and legacy guide-field rejection
- guide activation provenance readback
- guide cleanup migration and stale snapshot fail-closed guard

## External Review Status

External GitHub Actions and CodeRabbit must rerun after this evidence/status
commit is pushed. This internal evidence does not replace external review.
