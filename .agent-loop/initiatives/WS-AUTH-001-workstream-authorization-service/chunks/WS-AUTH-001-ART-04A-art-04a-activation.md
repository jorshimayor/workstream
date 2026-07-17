# Chunk Contract: WS-AUTH-001-ART-04A — ART 04A Upload Action Activation

## Status

Proposed and inactive until every prerequisite has merged and the user gives a
separate explicit start.

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Integrate the exact AUTH evaluator contract and activate only `artifact.upload_session.create`, `artifact.upload_session.read`, `artifact.upload_item.write`, `artifact.upload_session.seal`, `artifact.upload_session.cancel`, and `artifact.upload_session.expire` after
the owning feature has merged complete hidden behavior.

## Risk class

L1 / P1.

## Prerequisites

merged `WS-ART-001-04A` hidden manifest, AUTH-09E scheduler admission, exact submitter/assignment authority from AUTH-10/AUTH-13, and `WS-AUTH-001-ART-CUSTODY`.

## Allowed files

```text
backend/app/modules/authorization/**
backend/app/modules/actors/**
backend/app/modules/audit/**
backend/app/api/deps/authorization.py
backend/tests/test_authorization.py
backend/tests/test_auth.py
backend/tests/test_actors.py
docs/spec_authorization_service.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/merge-intents/WS-AUTH-001-ART-04A.json
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

Owning feature files and focused feature tests may be added only by a reviewed
preimplementation amendment that cites the immutable merged feature manifest;
AUTH must not import or duplicate a feature repository.

## Not allowed

```text
new PermissionId, unrelated ActionId, dynamic action, or permission union
feature persistence, lifecycle transition, adapter I/O, route, or job behavior
client-supplied authority facts or AUTH-owned feature resource loading
activation before hidden behavior and real-kernel unavailable proof merge
availability changes outside the exact action list
feature-owned availability writes or alternate authorization path
```

## Acceptance criteria

- The immutable merged feature manifest names the exact action list, canonical
  resource types/facts, composers, guards, candidates, surfaces, transaction
  owner, and revalidation behavior.
- Before this chunk, every listed action returns `action_unavailable` through
  the real kernel while hidden behavior is testable only through feature-owned
  fakes.
- AUTH integrates only the exact typed evaluators and changes only the listed
  actions from planned to active.
- ActionId-to-PermissionId mappings, unrelated owner rows, service-matrix rows,
  and all unrelated availability remain unchanged.
- Allow, wrong-grant, cross-project, inactive actor/link, stale authority,
  rollback, idempotency, concealment, and transaction-time revalidation tests
  pass as applicable.
- Contributor upload actions and scheduler expiry are distinct principal paths with independent guards and denial proof.
- Focused changed subsystems remain at least 90 percent covered and the global
  coverage floor does not regress.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q tests/test_authorization.py tests/test_auth.py tests/test_actors.py --cov=app.modules.authorization --cov-report=term-missing --cov-fail-under=90)
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
git diff --check
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture,
CI integrity, docs, reuse/dedup, and test delta.

## Human review focus

Review immutable feature evidence, exact evaluator ownership, exact availability
delta, wrong-principal denial, and one-transaction rollback.

## Stop conditions

Stop if feature behavior or facts are incomplete, if AUTH must invent or own
feature persistence, if a fixed service is not exactly registered/provisioned,
or if any unrelated action would change.
