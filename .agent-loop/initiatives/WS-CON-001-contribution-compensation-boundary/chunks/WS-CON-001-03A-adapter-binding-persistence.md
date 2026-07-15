# Chunk Contract: WS-CON-001-03A - Compensation Adapter-Binding Persistence

## Goal and risk

Persist immutable binding identity/lifecycle without adapter behavior. L1
payment/auth/data risk.

## Allowed files

```text
backend/app/modules/compensation/{__init__,models,schemas,repository}.py
backend/app/db/models.py
backend/alembic/versions/<next>_compensation_adapter_bindings.py
backend/tests/{test_compensation,test_alembic}.py
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-03A.json
```

## Not allowed

```text
AUTH actor/grant/action-assignment edits
adapter, route, worker, policy, award, receipt or delivery behavior
credentials, secrets, raw provider refs, dependency or CI weakening
```

## Acceptance criteria

- [ ] Binding stores project, instrument, typed capability, canonical
  `adapter_actor_id`, non-secret route identity, state/version and immutable
  lifecycle timestamps; credentials/provider refs are impossible.
- [ ] Composite constraints preserve project/instrument ownership and valid
  active/suspended/retired transitions.
- [ ] Schema supports the callback guard but creates no ActorProfile, grant,
  action assignment, adapter, route, or delivery behavior.
- [ ] Upgrade/downgrade and duplicate/state races use isolated PostgreSQL.

## Verification and reviewers

Execute the exact CON-03A expansion in `../RUNTIME_VERIFICATION.md`; changed
compensation code is at least 90 percent. Senior engineering, QA/test,
security/auth, product/ops, architecture, docs, reuse/dedup and test-delta are
required. Stop after schema.
