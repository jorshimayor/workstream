# Chunk Contract: WS-CON-001-08A - Outbound Compensation Delivery Handler

## Goal and risk

Handle committed fulfillment-request events, persist durable pre-I/O delivery
state, call the typed external adapter after commit, and return a typed outbox
outcome. L1 economic/external-service/auth risk.

## Prerequisites

- CON-07 and shared outbox merged;
- exact outbound-delivery ServiceIdentity and ActionId/static row approved and
  registered as planned by AUTH, or an explicitly approved closed
  dual-principal design;
- provisioned service ActorProfile/link, AUTH-09E admission, typed context, and
  prepared protocol; the action remains planned while this hidden behavior
  merges;
- ADR 0014 typed adapter/factory composition and lifecycle fence port.

## Allowed files

```text
backend/app/modules/compensation/{schemas,repository,service,ports}.py
backend/app/interfaces/compensation.py
backend/app/adapters/compensation/**
backend/app/modules/outbox/handlers.py only explicit handler registration
backend/app/composition/compensation.py
backend/app/workers/compensation.py
backend/app/workers/celery_app.py only delivery task registration
backend/tests/{test_compensation,test_outbox,test_authorization,test_external_service_adapters}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-08A.json
```

## Not allowed

```text
outbox claim/finalization transitions; callback behavior
generic dispatcher identity executing delivery
AUTH implementation; provider SDK/concrete adapter import in domain service
database/fence lock held during external I/O
```

## Acceptance criteria

- [ ] Handler validates committed claim generation but never locks/mutates the
  OutboxEvent. Dispatcher later applies its typed outcome.
- [ ] Delivery authority is independent from `outbox.dispatch`. Dispatcher is
  denied delivery; delivery identity is denied dispatch and every other
  handler/action; humans are denied fixed-service execution.
- [ ] Prepared authorization locks service ActorProfile/link, validates exact
  ServiceIdentity/static row/action, then CON locks award/binding/delivery rows
  and evaluates final facts once.
- [ ] Durable in-flight generation and exact event/payload/binding/idempotency
  identity commit before adapter I/O; every database transaction and lifecycle
  fence is released before the call.
- [ ] Adapter result cannot change award identity/quantity. Retry, ambiguous
  completion, acknowledgement, callback-before-ack, cancellation, and replay
  preserve monotonic delivery/receipt truth.
- [ ] Provider I/O is only through typed capability/factory at composition root.
- [ ] Coverage/concurrency/failure proof meets repository floors.
- [ ] The real kernel continues to deny the planned action. AUTH activation is
  a later checkpoint after this hidden handler and its evaluator composition
  merge.

## Review and stop

All baseline plus architecture, security, product, docs, reuse, CI integrity,
and test-delta. Stop after hidden handler; do not activate the action or
register public routes.
