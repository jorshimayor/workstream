# Chunk Contract: WS-AUTH-001-ART-CUSTODY — ART Activation Custody Transfer

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Atomically transfer all 25 current planned ART actions from historical feature
owner labels to the eight exact AUTH activation custodians in
`ACTIVATION_CUSTODY.md` without changing mappings or availability.

## Risk class

L1 / P1.

## Allowed files

```text
backend/app/modules/authorization/catalogue.py
backend/tests/test_authorization.py
backend/tests/test_auth.py
docs/spec_authorization_service.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-ART-CUSTODY.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
ActionId, PermissionId, mapping, or availability changes
database migration or audit-history rewrite
resource composer, evaluator, route, command, ART behavior, or adapter changes
service provisioning or action activation
partial transfer or retained ART activation-owner enum
```

## Acceptance criteria

- Exactly the 25 canonical rows move to the eight AUTH owner values.
- All seven ART owner enum values are removed atomically.
- The catalogue remains 57 actions, nine active, 48 planned, and 74
  permissions with identical ActionId-to-PermissionId pairs.
- Typed, PostgreSQL, audit, definition-owner, and documentation parity reject
  missing, extra, dual, or changed mappings.
- Every ART action remains unavailable through the real kernel.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q tests/test_authorization.py tests/test_auth.py --cov=app.modules.authorization --cov-report=term-missing --cov-fail-under=90)
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
git diff --check
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture,
CI integrity, docs, reuse/dedup, and test delta.

## Human review focus

Verify exact 25-row custody transfer, unchanged mappings/counts, and zero
activation.

## Stop conditions

Stop if any mapping or availability must change, or if ART runtime behavior is
required.
