# Chunk Contract: WS-CON-001-10A - Contribution And Award Product Reads

## Goal and risk

Implement hidden authorized self/project reads directly from canonical
PostgreSQL ContributionRecord and CompensationAward truth. L1 auth/privacy risk.

## Allowed files

```text
backend/app/modules/contributions/{schemas,repository,service}.py
backend/app/modules/compensation/{schemas,repository,service}.py
backend/app/api/internal_{contributions,compensation}.py
backend/app/composition/{contributions,compensation}.py
backend/tests/{test_contributions,test_compensation,test_authorization,test_api_contract_e2e}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-10A.json
```

## Not allowed

```text
ART/evidence read or provider reference
operations mutation/rebuild/reconciliation; AUTH edit
balance/ledger; production route registration; CI weakening
```

## Acceptance criteria

- [ ] AUTH registers planned contribution/award self/project actions and typed
  contexts. CON composes canonical PostgreSQL facts while real kernel denies;
  AUTH later integrates evaluators/activation.
- [ ] D11 exact award-detail candidate set is approved before implementation.
  CON contains no role logic and never infers access from broad PermissionId.
- [ ] Self reads require exact contributor/beneficiary. Project reads use exact
  eligible AdminRole, covered project, pre-filtered stable pagination, and
  cross-project concealment. Reviewer has no project-wide access by review role.
- [ ] Allowed decisions bind complete resource digest, matched grant/project,
  request, and correlation. Stale/mismatched evidence denies.
- [ ] Contribution, money, points, delivery acknowledgement, and fulfillment
  are distinct. No provider/balance/ledger/evidence artifact data appears.
- [ ] CON-09A/09B absence or failure has no effect. OpenAPI remains hidden;
  coverage stays at required floors.

## Review and stop

Required tracks: senior, QA, security, product, architecture, docs, reuse, and
test-delta. Stop before operations/public registration.
