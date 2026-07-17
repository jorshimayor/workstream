# Chunk Contract: WS-AUTH-001-ART-REV-EVIDENCE-REG — Review Evidence Binding Action Registration

## Status

Blocked planning contract. It is not executable until ART and REV publish the
exact dual-authority command boundary and hidden binding behavior.

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Register `artifact.review_evidence.binding.create` as planned and extend only
the existing artifact binding service's static row.

## Risk class

L1 / P1.

## Allowed files

```text
backend/app/modules/actors/service_identities.py
backend/app/modules/authorization/**
backend/app/modules/audit/**
backend/alembic/versions/<next_head>_*.py
backend/tests/test_actors.py
backend/tests/test_authorization.py
backend/tests/test_audit.py
backend/tests/test_alembic.py
docs/spec_authorization_service.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-ART-REV-EVIDENCE-REG.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
new PermissionId or service identity
database service-action assignment row
ART or REV binding/evidence behavior
human authority substitution with service authority
active availability or evaluator integration
editing historical migrations
```

## Acceptance criteria

- Register exactly `artifact.review_evidence.binding.create` mapped to existing
  `artifact.binding.create`, owned by `WS-AUTH-001-ART-REV-EVIDENCE`, planned.
- Add only that action to `workstream.artifact.binding`; the seven identities
  remain unchanged and matrix membership grows from 11 to 12.
- ART/REV's merged contract defines the in-process/service command boundary,
  admitted service context, two decisions/evidence records, lock order, and one
  transaction owner before this contract becomes executable.
- Typed and PostgreSQL audit parity plus service-matrix parity fail closed.
- Permission count remains 74; action count becomes 62 with nine active and 53
  planned when applied after REV registration.

## Verification commands

```bash
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic downgrade -1)
(cd backend && WORKSTREAM_DATABASE_URL=<isolated-test-db> .venv/bin/alembic upgrade head)
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q tests/test_actors.py tests/test_authorization.py tests/test_audit.py tests/test_alembic.py --cov=app.modules.authorization --cov-report=term-missing --cov-fail-under=90)
git diff --check
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture,
CI integrity, docs, reuse/dedup, and test delta.

## Human review focus

Review exact mapping, one-row matrix extension, dual-authority transaction
contract, and zero feature activation.

## Stop conditions

Stop until ART and REV publish the complete atomic boundary, or if a new service
identity, grant table, or authority substitution is required.
