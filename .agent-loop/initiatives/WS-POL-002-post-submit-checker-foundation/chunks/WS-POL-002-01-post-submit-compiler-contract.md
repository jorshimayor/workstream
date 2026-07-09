# Chunk Contract: WS-POL-002-01 - Post-Submit Provenance And Compiler Contract

## Parent Initiative

`WS-POL-002` - Post-Submit Checker Foundation

## Problem Being Solved

Post-submit policy currently has a canonical body and hash, but it lacks a
trusted compiler contract equivalent to pre-submit. Before adding an agent,
Workstream needs deterministic compiler rules that prevent project policy from
weakening platform defaults or referencing unsupported checkers.

## Goal

Introduce the durable post-submit policy provenance fields, setup-run output
fields, and trusted compiler contract that produce the canonical project-scoped
`PostSubmitCheckerPolicy` body from a constrained spec.

## Target Behavior

- Compiler always includes platform default durable post-submit checkers.
- Compiler rejects unknown checker names.
- Compiler rejects attempts to remove or weaken defaults.
- Compiler rejects duplicate/conflicting checker classifications.
- Compiler rejects unsupported blocking-severity downgrade attempts.
- Compiler emits the canonical policy body and hash.
- Compiler supports default-only projects by representing platform defaults as
  required durable coverage while permitting an empty project-specific addition
  set.
- `policy_body.default_checkers` must exactly equal the platform-owned
  `DEFAULT_DURABLE_CHECKERS` list.
- Policy rows bind to guide source snapshot id/hash, compiler version,
  derivation provenance, lifecycle status, and approval provenance.
- `ProjectSetupRun` can reference post-submit derivation/compile output and
  represent post-submit setup statuses without JSON-only hiding.
- Activation/runtime validation uses the compiled canonical body, not ad hoc
  request lists.

## Allowed Files

```text
backend/app/modules/projects/post_submit_policy.py
backend/app/modules/checkers/compiler.py
backend/app/modules/projects/models.py
backend/app/modules/projects/repository.py
backend/app/modules/projects/service.py
backend/app/modules/projects/schemas.py
backend/alembic/versions/**
backend/tests/test_alembic.py
backend/tests/test_checkers.py
backend/tests/test_projects.py
docs/architecture_checker_framework.md
docs/architecture_data_model.md
docs/template_checker_policy.md
.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not Allowed

```text
backend/app/adapters/project_agents/**
backend/app/modules/tasks/**
frontend or demo UI work
payment/reputation/blockchain settlement
per-task checker generation
arbitrary generated checker code execution
```

## Acceptance Criteria

- A constrained post-submit checker spec can be compiled into a canonical
  project `PostSubmitCheckerPolicy` body.
- Default durable post-submit checkers are always present in
  `execution_checkers`.
- `policy_body.default_checkers` exactly matches `DEFAULT_DURABLE_CHECKERS`; no
  missing, extra, renamed, or reordered defaults are accepted. This chunk must
  not change the `DEFAULT_DURABLE_CHECKERS` list; any future default-list change
  requires explicit human approval and security review in its own chunk.
- Default-only project policy compilation and activation are valid when all
  platform defaults remain required.
- Unknown checker names fail closed.
- Duplicate or contradictory required/warning checker classifications fail
  closed.
- Policy hash equals `sha256(canonical_json(policy_body))`.
- Compiler implementation reuses or consolidates through existing
  `post_submit_policy.py` canonical body, hash, default-list, and locked-body
  parsing helpers instead of reimplementing a second post-submit canonicalizer.
- Migration and ORM metadata persist source snapshot id/hash, compiler version,
  lifecycle status, approval actor/role/time, derivation provenance, and
  unsupported checker gaps without weakening existing policy locks.
- Migration and ORM metadata add explicit setup-run post-submit output/status
  support.
- Existing runtime tests still pass.
- Docs describe the compiler boundary and default checker list.

## Verification Commands

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
(cd backend && .venv/bin/pytest tests/test_projects.py tests/test_checkers.py -q)
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

- Confirm the compiler, not the agent, owns canonical runtime policy.
- Confirm project policy cannot weaken defaults.
- Confirm no task-specific checker generation is introduced.
