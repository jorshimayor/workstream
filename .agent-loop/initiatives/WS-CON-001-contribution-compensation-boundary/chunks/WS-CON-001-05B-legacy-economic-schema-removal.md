# Chunk Contract: WS-CON-001-05B - Legacy Economic Schema Removal

## Goal and risk

Delete the now-unreachable guide-bound economic model, tables, columns,
constraints, and compatibility code after 05A proves zero semantic consumers.
L1 migration/historical-data risk.

## Allowed files

```text
backend/app/modules/projects/{models,schemas,repository,service}.py only dead schema removal
backend/app/modules/tasks/{models,schemas,repository,service}.py only dead references
backend/app/modules/checkers/{models,schemas,repository,service,runner}.py only dead references
backend/app/db/models.py
backend/alembic/versions/<next>_remove_legacy_project_economic_schema.py
backend/tests/{test_projects,test_tasks,test_checkers,test_alembic,test_api_contract_e2e}.py
docs/{architecture_data_model,operations_payment_reputation,spec_contribution_compensation}.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-05B.json
```

## Not allowed

```text
new ContributionPolicy/award behavior or inferred backfill
ReviewLease/Review/contribution/award behavior
AUTH, ART, provider, frontend, dependency or CI changes
```

## Acceptance criteria

- [ ] 05A zero-consumer proof still passes on current trusted main.
- [ ] Approved classification drains/rebuilds or explicitly maps every row;
  ambiguous meaning fails migration and never guesses a policy version.
- [ ] Dead model/tables/columns/FKs/indexes and API/OpenAPI references are absent
  after upgrade; ContributionPolicy and frozen references remain valid.
- [ ] Downgrade is data-loss aware, requires intake disabled, and never revives
  the removed schema as executable authority.
- [ ] PostgreSQL upgrade/downgrade and fresh install pass; changed code remains
  at least 90 percent and repository coverage at least 78 percent.

## Review and stop

Required tracks: senior, QA, security, product, architecture, docs, reuse, test-
delta, and CI integrity. Stop before CON-06.
