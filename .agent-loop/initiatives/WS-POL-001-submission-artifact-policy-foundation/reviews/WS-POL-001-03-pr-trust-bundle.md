# PR Trust Bundle: WS-POL-001-03

## Chunk

`WS-POL-001-03` - Task Locked Context And Submission Creation

## Goal

Move task readiness and submission creation onto the locked project guide-source
snapshot, effective project submission artifact policy, and compiled project
`PreSubmitCheckerPolicy` bundle.

## Human-Approved Intent

- Intent: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/INTENT.md`
- Plan: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/PLAN.md`
- Chunk contract: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/chunks/WS-POL-001-03-task-locked-context-submission-creation.md`

## What Changed

- Added task locked-context columns for guide source snapshot, effective project submission artifact policy, and project pre-submit checker bundle references.
- Added submission locked-context columns that copy the task's trusted context at submission creation.
- Added database constraints binding locked ids to their corresponding hashes.
- Moved task screening readiness onto the active project guide-policy bundle and compiled project pre-submit checker.
- Kept checker architecture project-scoped: tasks lock references; tasks do not derive policy or compile checker bundles.
- Made submission creation run the locked project pre-submit checker before inserting a submission row.
- Made blocking pre-submit failure return `pre_submission_checker_failed` with structured check details and create no submission, version, task transition, audit event, or durable checker run.
- Hardened checker runtime validation so hash-consistent but malformed effective policies or compiled bundles are rejected before execution.
- Added OpenAPI response documentation for the domain-level failed submission-create response.
- Updated docs/templates to match the implemented locked context and pre-submit/post-submit boundary.

## Scope Control

Allowed implementation surface:

- `backend/alembic/versions/**`
- `backend/app/modules/projects/models.py`
- `backend/app/modules/projects/repository.py`
- `backend/app/modules/tasks/**`
- `backend/app/modules/checkers/**`
- `backend/tests/test_tasks.py`
- `backend/tests/test_checkers.py`
- `backend/tests/test_projects.py`
- `docs/architecture_data_model.md`
- `docs/spec_chunk_5_submission_packet_foundation.md`
- `docs/spec_chunk_7_checker_runner_registry.md`
- `docs/template_checker_policy.md`
- `docs/template_submission_packet.md`
- `.agent-loop/LOOP_STATE.md`
- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/**`

No frontend, payment, reputation, auth-session, object-storage, post-submit policy split, or per-task checker generation was added.

## Product Behavior

When a task moves through screening, Workstream locks the active project context:

```text
GuideSourceSnapshot
EffectiveProjectSubmissionArtifactPolicy
Project PreSubmitCheckerPolicy
Post-submit checker policy version
Review policy version
Revision policy version
Payment policy version
```

At submission time, the worker sends only draft packet content. Workstream loads
the locked task context, executes the locked project `PreSubmitCheckerPolicy`,
and creates the submission only when blocking checks pass.

Pre-submit failure is not a review decision. The worker-facing API receives
`pre_submission_checker_failed` with pass/fail/warning details. Stored product
review decisions remain only `accept`, `needs_revision`, and `reject`.

## Acceptance Criteria Proof

- Locked task fields: `backend/app/modules/tasks/models.py`, `backend/app/modules/tasks/service.py`
- Locked submission fields: `backend/app/modules/tasks/models.py`, `backend/app/modules/tasks/service.py`
- Composite FK/hash binding: `backend/alembic/versions/0007_task_locked_submission_context.py`, `backend/app/modules/tasks/models.py`
- Project-scoped checker reuse: `backend/app/modules/projects/repository.py`, `backend/app/modules/tasks/service.py`, `backend/tests/test_tasks.py`
- No derivation/compilation per task: task service locks existing project context only; tests assert shared project checker behavior.
- Pre-submit before submission row: `backend/app/modules/tasks/service.py`, `backend/tests/test_tasks.py`
- No side effects on pre-submit failure: `backend/tests/test_tasks.py`
- Domain error body: `backend/app/modules/tasks/router.py`, `backend/tests/test_tasks.py`
- Runtime policy/bundle shape validation: `backend/app/modules/checkers/service.py`, `backend/app/modules/checkers/compiler.py`, `backend/tests/test_checkers.py`

## Tests And Checks Run

```bash
cd backend && .venv/bin/python -m ruff check app tests scripts
cd backend && .venv/bin/docstr-coverage --config .docstr.yaml
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
git diff --check
python3 scripts/workstream_agent_gate.py --base origin/main --head HEAD --format json
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python -m pytest tests -q
```

Result summary:

```text
Ruff app/tests/scripts passed.
Docstring coverage passed: 100.0% (527/527).
Markdown link check passed for 8 changed Markdown files.
Stale wording check passed.
git diff --check passed.
Agent gate result: REVIEW_REQUIRED because this is a large L1 migration/runtime/checker diff touching risk-sensitive files.
Full Postgres-backed backend suite passed before docs-only repair commits: 306 passed in 1680.44s.
No backend code or tests changed after the full backend suite.
```

## Reviewer Results

Reviewed code SHA: `df468066cc3c6180c12735daf5e4dd8de654bef7`

Reviewed at: `2026-07-02T17:19:29Z`

Reviewer run IDs: see `WS-POL-001-03-internal-review-evidence.md`.

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Runtime/migration flow reviewed; process evidence gap addressed by evidence artifact. |
| QA/test | PASS AFTER FIXES | None | Runtime acceptance criteria reviewed; process evidence gap addressed by evidence artifact. |
| security/auth | PASS | None | Locked context, hash binding, and auth boundaries reviewed. |
| product/ops | PASS | None | Worker-facing pre-submit semantics and project-scoped checker reuse reviewed. |
| architecture | PASS | None | Project-scoped checker architecture and boundaries reviewed. |
| docs | PASS AFTER FIXES | None | Registry and scope wording repaired. |
| reuse/dedup | PASS WITH LOW RISKS | None | Low residual around shared path/pattern helpers. |
| test delta | PASS WITH LOW RISKS | None | Low residual around revision transition and focused migration downgrade assertions. |
| CI integrity | PASS AFTER FIXES | None | Evidence gate behavior preserved; evidence artifact added. |

## External Review

PR #63 is awaiting initial GitHub Actions and CodeRabbit results.
External review responses must be tracked separately in
`WS-POL-001-03-external-review-response.md`.

## Remaining Risks

- `WS-POL-001-05` should add public lifecycle coverage for the revision path.
- A future migration-focused regression can assert exact `0007 -> 0006` downgrade behavior.
- Shared path/pattern validation helpers should be extracted before further checker-policy expansion.

## Human Review Focus

Please inspect:

- Task locked context stamping before `READY`.
- Shared project `PreSubmitCheckerPolicy` reuse across tasks.
- Submission-create no-row/no-version/no-transition guarantee on blocking pre-submit failure.
- Domain error shape for `pre_submission_checker_failed`.
- Removal of transitional `required_files` and `required_evidence` authority from submission runtime.

## Human Ownership

- [ ] I can explain what changed.
- [ ] I can explain why it changed.
- [ ] I know what could break.
- [ ] I accept the remaining risks.
- [ ] The user explicitly approved this specific PR for merge.
