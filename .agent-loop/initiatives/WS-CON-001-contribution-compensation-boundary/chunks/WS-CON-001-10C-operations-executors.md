# Chunk Contract: WS-CON-001-10C - Reconciliation And Projection Executors

## Goal and risk

Execute committed bounded compensation-reconciliation and contribution-
projection-rebuild requests under independent exact fixed-service authority.
L1 background-execution/auth/economic-data risk.

## Prerequisites

- 10B durable request and drain contracts merged;
- exact ServiceIdentity/ActionId/static-row design approved for compensation
  reconciliation and contribution projection rebuild, or explicitly approved
  closed dual-principal evaluators;
- controlled service ActorProfile/link provisioning, AUTH-09E admission,
  typed context, and prepared protocol; both actions remain planned while this
  hidden behavior merges;
- shared outbox claim validation and handler registry.

## Allowed files

```text
backend/app/modules/contributions/{repository,service}.py
backend/app/modules/compensation/{repository,service}.py
backend/app/modules/outbox/handlers.py only explicit registration
backend/app/workers/{contributions,compensation}.py
backend/app/composition/{contributions,compensation}.py
backend/tests/{test_contributions,test_compensation,test_outbox,test_authorization}.py
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-10C.json
```

## Not allowed

```text
generic dispatcher identity executing feature work
human request authority reused without approved dual-principal evaluator
canonical contribution/award/receipt mutation; provider settlement
outbox claim/finalization transitions; AUTH implementation
```

## Acceptance criteria

- [ ] Dispatcher can invoke but is denied both executor actions. Each executor
  is denied dispatch, the other executor's action, delivery/callback/ART/REV
  actions, and every human action outside its exact row.
- [ ] Handler validates committed claim generation, prepares fixed-service
  authority, locks bounded request/product rows, evaluates final facts once,
  stages result/audit/projection state, and returns typed outcome.
- [ ] Compensation reconciliation compares immutable award/delivery/receipt
  truth and creates durable findings/actions allowed by the approved contract;
  it never changes award amount/eligibility or fabricates receipt truth.
- [ ] Contribution rebuild changes rebuildable projections only and never
  mutates ContributionRecord or CompensationAward.
- [ ] Retry/replay/idempotency and crash fencing preserve request identity.
  Missing service provisioning denies runtime/readiness without failing startup.
- [ ] Coverage, concurrency, and cross-service negative proof meet floors.
- [ ] The real kernel continues to deny both planned executor actions. AUTH
  activation is a later checkpoint after hidden behavior and exact evaluator
  composition merge.

## Review and stop

All baseline plus architecture, security, product, docs, reuse, CI integrity,
and test-delta. Stop before AUTH activation and CON-11.
