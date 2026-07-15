# Chunk Contract: WS-CON-001-10B - Operations, Reconciliation, And Rebuild

## Goal and risk

Implement bounded status/audit reads, reconciliation and projection rebuild
without repairing immutable truth. L1 operations/auth/data risk.

## Allowed files

```text
backend/app/modules/contributions/{schemas,repository,service}.py
backend/app/modules/compensation/{schemas,repository,service,ports}.py
backend/app/modules/audit/{schemas,repository,service}.py only bounded WS-CON query/export capability
backend/app/api/internal_operations.py
backend/app/composition/{contributions,compensation}.py
backend/tests/{test_contributions,test_compensation,test_authorization,test_outbox,test_audit}.py
docs/operations_payment_reputation.md only WS-CON operations
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-10B.json
```

## Not allowed

```text
production router registration, canonical award/receipt repair, AUTH edit
provider settlement/attempt/balance/ledger or second dispatcher
dependency, test, coverage or CI weakening
```

## Acceptance criteria

- [ ] Ops/audit actions follow handoff and revalidate after locks.
- [ ] Finance project and reason-bound Operator reconciliation use distinct
  guards; Project Manager/contributor denials are explicit.
- [ ] Reconcile preserves original identities; rebuild changes projection only;
  bounded range/reason/audit/idempotency is durable.
- [ ] Audit read/export purpose/scope/redaction/max range is proved without
  provider or sensitive failure leakage; OpenAPI remains hidden.
- [ ] Dependency-aware binding retirement now activates: it locks policy,
  assignment, lease, award, delivery and receipt dependencies, denies any
  active/unfinished/unfulfilled reference, races all dependency changes in both
  orders, and afterward permits only exact accepted-receipt replay.
- [ ] A same-session read-only `FulfillmentLifecycleDrainObservationPort`
  reports pending/claimed/retryable fulfillment outbox events, durable
  in-flight dispatch, and nonterminal delivery/callback obligations using the
  shared-outbox capability rather than importing its repository. It never
  commits, repairs state, calls a provider, or widens Operator authority.
- [ ] Observation is transactionally stable, bounded and fail-closed; tests
  cover concurrent claim/retry/callback/finalization and prove no false zero
  while work can still perform remote I/O or accept a terminal receipt.

## Verification and reviewers

Execute CON-10B in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/auth, product/ops, architecture,
docs, reuse/dedup and test-delta are required. Stop before public registration.
