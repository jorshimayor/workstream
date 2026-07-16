# Chunk Contract: WS-CON-001-10A - Contribution And Award Product Reads

## Goal and risk

Implement authorized self/project contribution and award reads behind
unregistered routes. L1 auth/privacy/product risk.

## Allowed files

```text
backend/app/modules/contributions/{schemas,repository,service}.py
backend/app/modules/compensation/{schemas,repository,service}.py
backend/app/api/internal_contributions.py
backend/app/api/internal_compensation.py
backend/app/composition/{contributions,compensation}.py
backend/tests/{test_contributions,test_compensation,test_authorization,test_api_contract_e2e}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-10A.json
```

## Not allowed

```text
operations mutation/rebuild/reconciliation, AUTH edit
provider/evidence bytes/ref, balance/ledger, production registration
dependency, test, coverage or CI weakening
```

## Acceptance criteria

- [ ] The post-CON-09B AUTH contribution-read activation is merged. AUTH has
  registered the exact planned award self/project actions, typed contexts and
  applicable actor-self/AdminRoleGrant definitions. CON composes canonical
  facts; stable pre-filter pagination and cross-project concealment are
  enforced. A later AUTH gate activates award reads before CON-10B.
- [ ] D11's human-approved award-detail role set is frozen in the active
  contract before this chunk. CON implements only its disclosure projection;
  Project Manager behavior follows that decision rather than the unadopted
  candidate or broad PermissionId by inference. Reviewer remains self-only
  absent a later approved assigned-review action.
- [ ] Reads validate the allowed decision's complete resource-context digest,
  matched AdminRoleGrant ID and covered project against canonical award facts.
  CON uses role-agnostic allowed/denied seams; the later AUTH activation gate
  proves the chosen role set, mixed grants, revocation and scope denials.
- [ ] Contribution, money, points, delivery acknowledgement and fulfillment
  remain distinct; no provider/balance/ledger data appears.
- [ ] Query races never mutate truth; all matrix cases run; OpenAPI stays hidden.

## Verification and reviewers

Execute CON-10A in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/privacy, product/ops,
architecture, docs, reuse/dedup and test-delta are required. Stop before public
registration.
