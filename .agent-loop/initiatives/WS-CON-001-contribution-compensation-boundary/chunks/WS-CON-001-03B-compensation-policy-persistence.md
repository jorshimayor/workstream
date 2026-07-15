# Chunk Contract: WS-CON-001-03B - Compensation Policy Persistence

## Goal and risk

Persist draft/published/retired policy versions and Project active selector
without commands. L1 payment/data risk.

## Allowed files

```text
backend/app/modules/compensation/{models,schemas,repository}.py
backend/app/modules/projects/models.py only active compensation selector
backend/app/db/models.py
backend/alembic/versions/<next>_compensation_policy_versions.py
backend/tests/{test_compensation,test_projects,test_alembic}.py
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-03B.json
```

## Not allowed

```text
service, route, claim, award, adapter, AUTH or ART behavior
PaymentPolicy fallback or historical-row rewrite
public API, worker, dependency or CI weakening
```

## Acceptance criteria

- [ ] Exact decimals/currency/points, explicit unpaid, contribution matching,
  binding IDs, provenance and immutable publication lifecycle are constrained;
  at most one money plus one points award exists per rule.
- [ ] Active selector references one same-project published version; published
  content is immutable; missing policy has no fallback.
- [ ] Legacy classification follows D2/CON-05 and rewrites no history.
- [ ] Upgrade/downgrade and selector/version races use isolated PostgreSQL.

## Verification and reviewers

Execute CON-03B in `../RUNTIME_VERIFICATION.md`; changed subsystems are at least
90 percent. Senior engineering, QA/test, security/auth, product/ops,
architecture, docs, reuse/dedup and test-delta are required. Stop after schema.
