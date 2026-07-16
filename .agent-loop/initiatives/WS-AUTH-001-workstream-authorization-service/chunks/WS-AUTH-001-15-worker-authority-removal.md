# Chunk Contract: WS-AUTH-001-15 - Remaining System Worker Cutover And Obsolete Authority Removal

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Verify the project-setup worker cutover completed in chunk 12, move the
remaining pre-review and queued workers to explicit system permissions,
revalidate actor-attributed queued mutations, remove obsolete token-role
runtime helpers/contexts, and add a deterministic stale-authority scanner.

## Why this chunk exists

Human/API cutover is incomplete while any remaining internal job fabricates
human roles or runtime code can still consume token roles. This chunk must not
re-open project setup behavior owned by chunk 12.

## Approved plan reference

- INTENT: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/INTENT.md`
- PLAN: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/PLAN.md`
- CHUNK_MAP: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/CHUNK_MAP.md`

## Risk class

L1

## SLA

P1

## Allowed files

```text
backend/app/workers/**
backend/app/modules/authorization/**
backend/app/modules/actors/**
backend/app/modules/projects/service.py
backend/app/modules/tasks/service.py
backend/app/modules/tasks/router.py
backend/app/modules/tasks/schemas.py
backend/app/modules/checkers/service.py
backend/app/core/permissions.py
backend/app/schemas/auth.py
backend/app/api/deps/auth.py
backend/scripts/api_contract_e2e.py
backend/tests/test_projects.py
backend/tests/test_tasks.py
backend/tests/test_checkers.py
backend/tests/test_auth.py
scripts/check_stale_authorization.py
scripts/test_agent_gates.py
.github/workflows/agent-gates.yml
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
new product lifecycle behavior
human roles on system principals
authorization allowlist broad enough to hide new token-role consumption
review/contribution/compensation implementation
```

## Acceptance criteria

- Internal jobs use fixed system principals and registered system permissions.
- Artifact service actions are activated only by dedicated AUTH activation
  custodians after the owning WS-ART chunks merge hidden resource facts, guards,
  surfaces, behavior, and tests. This chunk does not attach artifact permissions
  or create a second activation path.
- Every remaining asynchronous command declares one primary registered action,
  canonical feature-owned target, and fixed service principal. Serialized human
  identity is provenance only and never executable command authority.
- Generated command-manifest delta tests prove every protected asynchronous
  surface migrated here has exactly one active `ActionId` declaration.
- Project setup is verification/removal-only here; its behavioral cutover
  remains owned by chunk 12.
- Serialized requester context is evidence only; actor-attributed commits reload
  current actor/grant state.
- Token roles and `require_any_role()` are not product authorization inputs and
  obsolete runtime paths are removed.
- The scanner proves the `LegacyWorkflowEligibilityCompatibility` adapter,
  allowlist, and typed-profile workflow eligibility consumers removed in chunk
  14 remain absent.
- The stale scanner and route tests prove the legacy worker-profile endpoint,
  activation service/schema, token-role observation fields, and actor-service
  authority checks are absent from runtime code.
- Deterministic AST/allowlist scanner fails on new product consumption of token
  roles, role-bearing contexts, or obsolete permission helper calls.
- Scanner has regression tests and runs in CI.
- Scanner regression includes a known-bad fixture for each forbidden authority
  pattern and proves the gate fails rather than silently allowlisting it.
- Full backend suite and API contract drill pass.

## Verification commands

```bash
python3 scripts/check_stale_authorization.py
python3 scripts/test_agent_gates.py
(cd backend && .venv/bin/python -m ruff check app tests scripts)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_authorization.py tests/test_auth.py tests/test_tasks.py \
  tests/test_checkers.py --cov=app.modules.authorization \
  --cov-report=term-missing --cov-fail-under=90)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python scripts/api_contract_e2e.py)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
```

## Required reviewers

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

## Human review focus

Review system-principal boundaries, queued revocation behavior, scanner
precision, CI integrity, and complete removal of old authority.

## Stop conditions

Stop if a system job requires human authority or scanner success requires a
blanket ignore of product code.
