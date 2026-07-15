# Chunk Contract: WS-CON-001-04A - Hidden Adapter-Binding Service

## Goal and risk

Implement authorized binding create/read/suspend/resume commands behind
unregistered composition. Retirement stays planned until dependency rows exist.
L1 payment/auth risk.

## Allowed files

```text
backend/app/modules/compensation/{schemas,repository,service}.py
backend/app/composition/compensation.py
backend/tests/{test_compensation,test_authorization,test_api_contract_e2e}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-04A.json
```

## Not allowed

```text
production router registration, policy commands, delivery or callback
AUTH catalogue/grant/kernel/service-actor edits
concrete adapter, provider secret/ref, dependency or CI weakening
```

## Acceptance criteria

- [ ] Proposed actions follow AUTHORIZATION_HANDOFF after AUTH registration.
- [ ] Create validates canonical active service ActorProfile, exact AUTH-owned
  action assignment and non-secret route identity.
- [ ] Mutations follow PLAN locks and transaction-revalidate authority; own-state
  concurrent suspend/resume is deterministic.
- [ ] Retire remains registered/planned but non-executable; any attempt fails
  closed with stable not-active behavior. CON-10B activates dependency-aware
  retirement after assignment/lease/award/delivery rows exist.
- [ ] Claims/delivery/callback races remain owned by 05/06/08A/08B/REV-13.
- [ ] Production OpenAPI remains unchanged.

## Verification and reviewers

Execute CON-04A in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/auth, product/ops, architecture,
docs, reuse/dedup and test-delta are required. Stop after hidden behavior.
