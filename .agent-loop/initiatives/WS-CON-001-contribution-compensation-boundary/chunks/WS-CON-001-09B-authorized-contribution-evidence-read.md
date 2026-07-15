# Chunk Contract: WS-CON-001-09B - Authorized Contribution Evidence Read

## Goal and risk

Expose safe self/project evidence reads behind unregistered routes through ART's
typed read capability. L1 auth/privacy risk.

## Allowed files

```text
backend/app/modules/contributions/{schemas,repository,service}.py
backend/app/api/internal_contributions.py
backend/app/composition/contributions.py
backend/tests/{test_contributions,test_authorization,test_api_contract_e2e}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-09B.json
```

## Not allowed

```text
write projection, raw ArtifactStore/provider ref, AUTH/ART implementation edit
production router registration or broad artifact disclosure
dependency, test, coverage or CI weakening
```

## Acceptance criteria

- [ ] AUTH has registered the exact planned contribution self/project read
  actions, typed contexts and applicable actor-self/AdminRoleGrant definitions.
  CON composes canonical facts; pre-filter pagination and cross-project
  concealment are required. The real kernel remains fail-closed while planned;
  a later AUTH gate owns evaluator integration and availability before CON-10A.
- [ ] Matrix proves self, Project Manager, Finance, Operator/Audit views and
  Reviewer project-wide denial/self-only behavior without private/provider data.
- [ ] ART result matches immutable projection identity; evidence failure never
  changes ContributionRecord truth.
- [ ] All role/project denial cases map to CONFORMANCE_MATRIX; OpenAPI is hidden.

## Verification and reviewers

Execute CON-09B in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/privacy, product/ops,
architecture, docs, reuse/dedup and test-delta are required. Stop before public
registration.
