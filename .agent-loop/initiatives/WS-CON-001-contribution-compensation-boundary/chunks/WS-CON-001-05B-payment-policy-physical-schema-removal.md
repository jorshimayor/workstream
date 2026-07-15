# Chunk Contract: WS-CON-001-05B - PaymentPolicy Physical Schema Removal

## Goal and risk

Delete the now-unreachable PaymentPolicy model, table, columns, constraints,
and compatibility code after 05A proves there are zero semantic consumers. L1
migration and historical-data risk.

## Allowed files

```text
backend/app/modules/projects/{models,schemas,repository,service}.py only dead PaymentPolicy removal
backend/app/modules/tasks/{models,schemas,repository,service}.py only dead references
backend/app/modules/checkers/{models,schemas,repository,service,runner}.py only dead references
backend/app/db/models.py
backend/alembic/versions/<next>_remove_payment_policy.py
backend/tests/{test_projects,test_tasks,test_checkers,test_alembic,test_api_contract_e2e}.py
docs/{architecture_data_model,operations_payment_reputation,spec_contribution_compensation}.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-05B.json
```

## Not allowed

```text
new compensation behavior, policy conversion or inferred backfill
ReviewLease/Review/contribution/award behavior
AUTH, ART, provider, frontend, dependency or CI changes
```

## Acceptance criteria

- [ ] Exact zero-consumer scan from 05A still passes on current trusted main.
- [ ] Approved legacy classification drains, resets, or deterministically
  migrates every row; ambiguous economic meaning fails migration and never
  guesses a CompensationPolicyVersion.
- [ ] PaymentPolicy model/table/columns/FKs/indexes and API/OpenAPI references
  are absent after upgrade; active compensation/frozen references remain valid.
- [ ] Downgrade is explicitly data-loss aware, requires intake disabled, and
  never recreates PaymentPolicy as executable authority.
- [ ] PostgreSQL upgrade/downgrade and fresh-install schema tests pass; changed
  code remains at least 90 percent and repository coverage at least 78 percent.

## Verification and reviewers

Execute CON-05B in `../RUNTIME_VERIFICATION.md`. Senior engineering, QA/test,
security/auth, product/ops, architecture, docs, reuse/dedup, test-delta and CI
integrity are required. Stop before CON-06.
