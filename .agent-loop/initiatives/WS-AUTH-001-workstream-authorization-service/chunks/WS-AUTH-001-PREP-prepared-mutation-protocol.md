# Chunk Contract: WS-AUTH-001-PREP — Prepared Mutation Authorization Protocol

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Add the AUTH-first, caller-committed prepared authorization protocol required
for sensitive cross-module mutations without changing feature behavior.

## Risk class

L1 / P1.

## Prerequisites

AUTH-09E is merged so human and fixed-service authority sources are structurally
separate and can be locked through one prepared protocol.

## Allowed files

```text
backend/app/api/deps/authorization.py
backend/app/modules/authorization/**
backend/app/modules/actors/**
backend/app/modules/audit/**
backend/tests/test_authorization.py
backend/tests/test_auth.py
backend/tests/test_api_controls.py
docs/spec_authorization_service.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-PREP.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
feature repository imports or feature lifecycle mutations in AUTH
feature route, worker, resource-composer, or adapter changes
new grant type, permission, action, service identity, or activation
dependency-teardown commit of an arbitrary shared session
serializable, reusable, cross-session, or caller-constructible prepared handles
```

## Acceptance criteria

- AUTH creates an opaque, session-bound, action-bound, single-use prepared
  handle only after locking canonical current human or service authority.
- The feature locks its records and recomposes final typed facts before AUTH
  evaluates exactly once and stages decision evidence.
- The route or service command owns one commit; AUTH and feature participants
  flush only.
- Reads retain request-scoped `require()`.
- Stale, reused, wrong-action, cross-session, serialized, or authority-lost
  handles deny before feature mutation.
- Evidence SQL failure, participant failure, commit failure, timeout, and
  cancellation roll back all staged AUTH and feature state with a stable public
  error and no partial evidence.
- Lock-order, concurrency, rollback, denial-concealment, and at-least-90-percent
  focused authorization coverage are proven with real PostgreSQL behavior.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q tests/test_authorization.py tests/test_auth.py tests/test_api_controls.py --cov=app.modules.authorization --cov-report=term-missing --cov-fail-under=90)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q)
python3 scripts/check_stale_authorization_docs.py
git diff --check
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture,
CI integrity, docs, reuse/dedup, and test delta.

## Human review focus

Review lock order, handle non-reusability, caller-owned commit, and complete
rollback under failure and cancellation.

## Stop conditions

Stop if AUTH must own a feature repository, if the caller cannot own one
transaction, or if evidence can commit separately from feature state.
