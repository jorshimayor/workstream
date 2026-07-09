# Chunk Contract: WS-POL-002-02 - Post-Submit Derivation Agent And Resumable Setup Integration

## Parent Initiative

`WS-POL-002` - Post-Submit Checker Foundation

## Problem Being Solved

Post-submit policy must be derived from project guide/source context instead of
being invented manually in guide request bodies. The derivation must run
asynchronously inside the project setup pipeline and stop cleanly when the
guide implies unsupported checker requirements.

## Goal

Add `PostSubmitCheckerPolicyDerivationAgent` and integrate it into the
resumable setup continuation that runs after v0.1 setup-authorized
admin/project_manager approval creates the effective submission artifact policy
and compiled project pre-submit checker bundle.

## Target Behavior

- Initial source-capture setup still stops at `policy_draft_ready`.
- Setup-authorized admin/project_manager approval of the submission artifact
  policy creates the effective policy and compiled pre-submit bundle, then
  enqueues or resumes post-submit derivation.
- Post-submit derivation runs only after effective submission artifact policy
  and pre-submit checker bundle are available.
- Agent input includes guide source snapshot, sufficiency summary, effective
  policy summary, pre-submit checker summary, and registered post-submit
  checker catalog.
- Agent output is a constrained spec, not executable runtime code.
- Unsupported required checks are recorded as setup blockers.
- Successful derivation passes through the trusted compiler.
- Setup run status makes post-submit derivation/compile state visible.
- Hostile guide/source instructions that attempt to weaken Workstream defaults,
  roles, routing, authorization, or review decisions are ignored or rejected.
- Persisted derivation summaries are bounded and redacted; raw source text,
  local paths, secrets, signed refs, and exact source hashes are not returned in
  setup APIs by default.

## Allowed Files

```text
backend/app/adapters/project_agents/**
backend/app/workers/project_setup.py
backend/app/modules/projects/setup_queue.py
backend/app/modules/projects/service.py
backend/app/modules/projects/schemas.py
backend/app/modules/projects/models.py
backend/app/modules/projects/repository.py
backend/app/modules/checkers/compiler.py
backend/tests/test_projects.py
backend/tests/test_agent_runtime.py
backend/tests/test_alembic.py
docs/architecture_checker_framework.md
docs/architecture_data_model.md
docs/operations_project_operating_manual.md
.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not Allowed

```text
backend/app/modules/tasks/**
backend/app/modules/checkers/service.py
frontend or demo UI work
payment/reputation/blockchain settlement
per-task checker generation
runtime agent-based submission judgment
```

## Acceptance Criteria

- The setup continuation invokes post-submit derivation only after v0.1
  setup-authorized admin/project_manager approval creates the effective
  submission artifact policy and compiled project pre-submit checker bundle.
- Blocked guide sufficiency prevents post-submit derivation.
- Unsupported required checker gaps block setup and are visible to operators.
- Successful derivation creates a compiled project `PostSubmitCheckerPolicy`.
- Agent prompt/instructions explicitly forbid arbitrary checker code and
  per-task checker generation.
- Tests include malicious guide/source excerpts and prove source text is treated
  as data, not authority.
- Returned spec reasons must be tied to bounded source evidence references.
- API-visible setup summaries redact secrets, local paths, replayable refs, and
  exact source hashes.
- Tests cover success, unsupported checker gap, and setup ordering.
- Tests prove the setup trigger boundary: no post-submit derivation before
  submission artifact policy approval/pre-submit compile, and exactly one
  post-submit setup continuation after that point.
- Implementation extends the existing project setup queue/worker boundary in
  `setup_queue.py` and `project_setup.py`; it must not create a disconnected
  post-submit-only queue or parallel pipeline.

## Verification Commands

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
(cd backend && .venv/bin/pytest tests/test_projects.py tests/test_agent_runtime.py -q)
(cd backend && .venv/bin/pytest tests/test_alembic.py -q)
git diff --check
```

## Required Reviewers

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- reuse/dedup
- test delta
- CI integrity

## Human Review Focus

- Confirm the agent derives setup policy only.
- Confirm unsupported checker requirements fail closed.
- Confirm no runtime submission judgment is delegated to an agent.
