# Chunk Contract: WS-CON-001-02A - Shared Transactional Outbox Persistence

## Goal and risk

Land feature-neutral PostgreSQL outbox truth and caller-transaction append only.
L1 infrastructure/audit/data risk.

## Allowed files

```text
backend/app/modules/outbox/{__init__,models,schemas,repository,service}.py
backend/app/db/models.py
backend/alembic/versions/<next>_shared_transactional_outbox.py
backend/tests/{test_outbox,test_alembic}.py
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-02A.json
```

## Not allowed

```text
Celery/dispatcher/handler/route changes
review, contribution, compensation, AUTH, ART, task or project behavior
new JSON canonicalizer, idempotency framework, dependency or CI weakening
```

## Acceptance criteria

- [ ] Immutable event identity/type/version/project/correlation/causation,
  canonical payload/digest, idempotency key and occurrence time are separate
  from mutable delivery state.
- [ ] Reuse `app.core.hashing.canonical_json_hash` and the existing
  reserve/lock/complete idempotency shape; no second canonicalizer/framework.
- [ ] Caller AsyncSession append flushes but never commits/publishes; changed
  payload under one identity conflicts; PostgreSQL proves duplicate races.
- [ ] No Celery, handler, broker, review, or compensation behavior is added.

## Verification and reviewers

Execute the exact CON-02A expansion in `../RUNTIME_VERIFICATION.md`.
Same-run outbox coverage is at least 90 percent. Baseline plus architecture,
security/auth, product/ops, docs, reuse/dedup, test-delta, and CI integrity.
Stop before dispatcher behavior.
