# Chunk Contract: WS-CON-001-10B - Operations Requests, Reads, And Drain Observation

## Goal and risk

Implement hidden bounded status/audit reads, binding retirement, durable
reconciliation/rebuild request creation, and fulfillment drain observation.
Execution belongs to 10C. L1 operations/auth/data risk.

## Allowed files

```text
backend/app/modules/contributions/{schemas,repository,service}.py
backend/app/modules/compensation/{schemas,repository,service,ports}.py
backend/app/modules/audit/{schemas,repository,service}.py only bounded WS-CON projection
backend/app/api/internal_operations.py
backend/app/composition/{contributions,compensation}.py
backend/tests/{test_contributions,test_compensation,test_authorization,test_outbox,test_audit}.py
docs/operations_payment_reputation.md only implemented WS-CON operations
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-10B.json
```

## Not allowed

```text
async reconciliation/rebuild execution or provider I/O
outbox dispatcher/transition implementation; immutable truth repair
AUTH implementation; production router registration; CI weakening
```

## Acceptance criteria

- [ ] D11 is final. AUTH registers binding-retire, delivery-reconcile, status,
  reconcile-request, rebuild-request, and audit actions with exact candidates,
  contexts, prepared protocol, and AUTH custodians.
- [ ] Every mutation uses the exact PR #140 prepared protocol: AUTH prepares
  authority first; CON locks and recomposes final facts; AUTH consumes/evaluates
  once before request/retirement mutation; the route commits once.
- [ ] Human operations create bounded durable idempotent requests only; they do
  not execute reconciliation/rebuild under human or dispatcher authority.
- [ ] Binding retirement locks policy/assignment/lease/award/delivery/receipt
  dependencies and denies active/unfinished/unfulfilled references in both race
  orders. Exact prior receipt replay remains the only post-retirement path.
- [ ] Audit read/export enforces purpose/scope/range/redaction with no provider
  or sensitive failure leakage.
- [ ] `FulfillmentLifecycleDrainObservationPort` reports pending/claimed/
  retryable outbox work, durable in-flight delivery, and nonterminal callback
  obligations through typed outbox capability, plus the current maximum
  immutable `fulfillment_obligation_ordinal`; zero is valid only when no root
  exists. It never imports an outbox or lifecycle-control repository.
- [ ] Observation uses the caller AsyncSession, is bounded/read-only, never
  commits or calls a provider, and never returns false zero while remote I/O or
  terminal receipt remains possible. Caller-supplied timestamps, ordinals,
  generation, or event IDs cannot substitute.
- [ ] AUTH later activates after hidden behavior; 10C waits for approved
  executor identities/actions/static rows.

## Review and stop

Required tracks: senior, QA, security, product, architecture, docs, reuse, and
test-delta. Stop before executor work.
