# Internal Review Evidence: WS-POL-001-06

## Chunk

WS-POL-001-06

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 96792961c7cb74f31150df803c533fe4c6432636

Reviewed at: 2026-07-05T13:59:55Z

Reviewer run IDs: 019f31e1-520e-7fb1-905c-ae156be67b38, 019f31e4-536c-7860-b036-488bbe55b4d7, 019f31e4-6eaa-7522-ba73-2fc7b4617082, 019f31e4-9085-7021-802e-46f73d784d7a, 019f31e4-b8bb-79b2-9617-1be43d6380ad, 019f31e4-eb29-7b83-9355-43452e50c8cb, 019f31e5-1700-7e21-89eb-8c06c7edee7d, 019f31f2-0cd9-7600-92cc-93a8fbd7eb04, 019f31f2-5cba-7c21-8b8b-894d2d59cab3, 019f31f2-833e-7c22-86ac-20a3e69c0a88, 019f31f2-aa70-7ed1-9aaf-dcb98134dea2, 019f31f2-dc12-7cf0-b8d8-c60497503f52, 019f31f3-0e03-7260-baae-7ef65184ee48, 019f3227-764f-7c53-818a-513ac2d4d12b, 019f3227-9311-7c00-975a-6484b4c6af1b, 019f3227-c029-7680-a0c1-14de4705ebf1, 019f322c-5b3c-7e00-9a46-6190c253f298, 019f322f-73d7-7291-80f2-6443c334dd5e, 019f326f-a62a-7ac1-b9de-fef3dd5c6b8e, 019f326f-bdf6-7541-b22b-abf3bfd3c722, 019f326f-df56-72d0-83e2-909c98484bbb, 019f3270-0454-7583-9efd-605556e23a00, 019f3270-357b-7723-8ea7-1b5946719040, 019f3270-6d12-7202-b946-be2f4a6a2862, 019f3271-8abd-7a10-898b-fed8f52a8908, 019f3272-5213-7cc0-b8ad-6785ebc50103, 019f3275-3888-71a1-ad0d-9942db14f476, 019f3289-8823-7be2-9da8-ea3b998b11fd, 019f3289-a9f1-76e0-890d-eb35c1834c2f, 019f3289-c61d-7c22-9139-c3dabf384926, 019f3289-e2d8-7ac0-b872-fce6f07ee527, 019f3289-ff61-7113-b468-4d5c1333838e, 019f328a-358b-7ca1-a9ce-18b8ca088969, 019f328c-0e09-7ac3-9248-42fb150882e5, 019f328d-f6b8-74d0-b5d5-3fd06a6ca715, 019f328f-3150-7fc0-94f4-bdad99b8cc00

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
- `backend/scripts/week1_api_e2e.py`
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
| senior engineering | PASS | None | Confirmed CodeRabbit fixes are minimal and preserve intended behavior. |
| qa/test | PASS WITH LOW RISKS | None | Confirmed migration guard, task validation cleanup, fixture-root bound, and docs field list; wording precision was tightened before commit. |
| security/auth | PASS WITH LOW RISKS | None | Confirmed fail-closed migration guard, bounded fixture traversal, no auth/payment weakening, and no normal-path secret/path leakage. |
| product/ops | PASS | None | Confirmed project creation, payment policy ownership, worker/reviewer status semantics, and naming remain aligned. |
| architecture | PASS | None | Confirmed project-scoped policy architecture is preserved and no compatibility alias is introduced. |
| docs | PASS WITH LOW RISKS | None | Confirmed docs are accurate; evidence/status are refreshed in this commit. |
| reuse/dedup | PASS WITH LOW RISKS | None | Confirmed no missed helper or redundant abstraction in the CodeRabbit fix set. |
| test delta | PASS WITH LOW RISKS | None | Confirmed tests were not weakened; Alembic guard test still seeds a pre-cleanup snapshot and asserts failure. |
| ci integrity | PASS AFTER FIXES | None | Found stale evidence after CodeRabbit fixes; this evidence/status update binds the new reviewed SHA. |

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
- Updated the Week 1 real API E2E script after GitHub Actions proved it still
  sent stale request bodies. The script now creates a shell project, keeps
  payment terms in `PaymentPolicy`, sends only human-facing guide content plus
  policy records for guide creation, and no longer sends task
  `required_files`/`required_evidence` as intake-policy inputs.
- Narrowly expanded the `WS-POL-001-06` contract to allow
  `backend/scripts/week1_api_e2e.py` because that script is the CI-invoked
  real API drill for the corrected request-body contract.
- Addressed CodeRabbit review feedback:
  - clarified the `0010_guide_cleanup` guard as a fail-closed check for any
    existing guide-source snapshots before the destructive guide-field cleanup;
  - added missing `ProjectGuide.status` and `ProjectGuide.updated_at` to the
    data-model field list;
  - removed unused task validation map entries left from guide-driven
    validation;
  - bounded Terminal Benchmark reviewer-root discovery to the fixture root and
    immediate parent unless the explicit reviewer-root environment variable is
    set.

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
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test uv run python scripts/week1_api_e2e.py
cd backend && .venv/bin/python -m ruff check app tests scripts ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
cd backend && .venv/bin/python -m pytest tests/test_alembic.py -q
cd backend && .venv/bin/python -m pytest tests/test_tasks.py -k 'screen or missing or required or locked_context' -q
```

Results:

- `tests/test_alembic.py`: 6 passed
- `tests/test_checkers.py`: 47 passed
- `tests/test_tasks.py`: 60 passed
- `tests/test_projects.py`: 188 passed
- `scripts/week1_api_e2e.py`: passed against local Postgres on 2026-07-05
- CodeRabbit fix validation:
  - ruff: passed
  - `tests/test_alembic.py`: 6 passed
  - targeted task screening/locked-context subset: 11 passed, 49 deselected

Focused suites also passed during the repair loop:

- project payment-field rejection and legacy guide-field rejection
- guide activation provenance readback
- guide cleanup migration and stale snapshot fail-closed guard

## External Review Status

External GitHub Actions and CodeRabbit must rerun after this evidence/status
commit is pushed. This internal evidence does not replace external review.
