# Chunk Contract: WS-AUTH-001-REV-REG — REV Lifecycle Action Registration

## Status

Blocked planning contract. It is not executable until REV publishes the exact
typed principal, resource, guard, surface, transaction, and hidden-behavior
manifest required below.

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Register four approved REV lifecycle ActionIds as planned metadata under one
exact AUTH activation custodian without implementing or activating REV behavior.

## Risk class

L1 / P1.

## Allowed files

```text
backend/app/modules/authorization/**
backend/app/modules/audit/**
backend/alembic/versions/<next_head>_*.py
backend/tests/test_authorization.py
backend/tests/test_audit.py
backend/tests/test_alembic.py
docs/spec_authorization_service.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-REV-REG.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
new PermissionId
REV repositories, routes, jobs, state, or resource composition
invented principal, facts, guards, or service identities
active availability or evaluator integration
editing historical migrations
```

## Acceptance criteria

- Register exactly the four ActionId-to-PermissionId pairs in
  `ACTIVATION_CUSTODY.md`, owned by `WS-AUTH-001-REV-LIFECYCLE` and planned.
- REV's merged manifest supplies exact typed context and activation dependencies;
  AUTH does not infer them.
- Typed and PostgreSQL audit validation add all four pairs atomically and reject
  missing, extra, changed, or active rows.
- Permission count remains 74; action count becomes 61 with nine active and 52
  planned when applied to the 57-action baseline.
- Migration uses the next trusted-main head and proves prior-head upgrade,
  downgrade safety, fresh replay, and immutable historical evidence.

## Verification commands

```bash
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic downgrade -1)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q tests/test_authorization.py tests/test_audit.py tests/test_alembic.py --cov=app.modules.authorization --cov-report=term-missing --cov-fail-under=90)
git diff --check
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture,
CI integrity, docs, reuse/dedup, and test delta.

## Human review focus

Review the exact four mappings, owning REV manifest, migration parity, and zero
availability change.

## Stop conditions

Stop until REV supplies the complete typed contract, or if any permission or
feature behavior must be invented.
