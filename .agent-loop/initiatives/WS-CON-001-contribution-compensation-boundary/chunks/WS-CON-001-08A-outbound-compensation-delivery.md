# Chunk Contract: WS-CON-001-08A - Outbound Compensation Delivery Handler

## Goal and risk

Consume versioned `CompensationFulfillmentRequested` through one typed ADR-0014
adapter and record acknowledgement. L1 payment/integration/worker risk.

## Allowed files

```text
backend/app/interfaces/compensation.py
backend/app/adapters/compensation/__init__.py
backend/app/adapters/compensation/deterministic.py
backend/app/modules/compensation/ports.py
backend/app/modules/compensation/{schemas,repository,service,delivery_handler}.py
backend/app/modules/outbox/handlers.py only explicit handler registration
backend/app/workers/compensation.py
backend/app/workers/celery_app.py only include registration
backend/app/composition/compensation.py only explicit ExternalServiceAdapterFactory registration
backend/tests/{test_compensation,test_outbox,test_external_service_adapters}.py
docs/operations_payment_reputation.md only delivery operations
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-08A.json
```

## Not allowed

```text
inbound router/callback, AUTH catalogue/grant/kernel edit
production provider-specific SDK, payment attempt/balance/ledger/settlement
dispatcher/async bridge/session/idempotency duplication, dependency/CI weakening
joint lifecycle-control persistence/phase policy or REV-owned implementation
optional/no-op/fallback dispatch fence or REV edits to CON product files
```

## Acceptance criteria

- [ ] The post-CON-02B AUTH checkpoint has integrated and activated the real
  `outbox.dispatch` evaluator for the fixed dispatcher, including exact active
  actor/link/action-assignment revalidation and end-to-end proof through the
  merged prepared-dispatch seam. Real-kernel dispatch succeeds only for that
  service identity; every human, stale assignment and mismatched event fails
  closed. This chunk does not edit AUTH or activate a public route.
- [ ] Reuse shared dispatcher/hashing/idempotency/worker/session/task-settings;
  preserve event/payload/binding/idempotency identity.
- [ ] Execute only as a handler of a currently claimed `outbox.dispatch`
  command assigned to the fixed shared-outbox dispatcher. CON defines no
  feature-local delivery-dispatch action, and human retry/reconciliation
  authority cannot execute the side effect.
- [ ] Lock/revalidate frozen binding/award/delivery; active permits delivery,
  suspended/retired blocks it, terminal callback status suppresses it.
- [ ] The shared dispatcher supplies an already-claimed immutable event and
  exact claim generation only after its claim transaction releases every
  database lock/session. In a new transaction, the handler acquires the injected
  lifecycle fence, revalidates the generation through the outbox-owned
  `OutboxClaimValidationPort` without locking/mutating OutboxEvent, then locks
  CON rows and persists durable `in_flight` delivery state.
- [ ] The handler commits and releases its transaction and advisory fence before
  adapter I/O. It finalizes CON delivery state in a new fenced transaction and
  returns a typed success/retry/terminal outcome; only the dispatcher mutates
  outbox claim/retry/finalization state.
- [ ] Timeout/crash/duplicate/out-of-order/ack retry never fabricates
  fulfillment; binding-vs-dispatch races cover both orders.
- [ ] Instrumentation proves no provider I/O executes while a database
  transaction, lifecycle advisory fence, or OutboxEvent row lock is held. Crash
  recovery uses the durable claim/in-flight generation and never guesses
  provider outcome.
- [ ] The delivery handler requires a narrow CON-owned
  `FulfillmentDispatchFence` consumer port after the dispatcher's committed
  claim handoff and before claim validation/CON row locks or any adapter call.
  Construction or handler registration without an injected fence fails closed;
  there is no optional/no-op/fallback production fence.
- [ ] CON owns the handler and port. REV-12A may inject its durable joint
  lifecycle-control implementation only through explicit composition; it may
  not edit `compensation/delivery_handler.py` or CON outbox handler policy.
- [ ] On a denied/lost release-control race, the handler performs no adapter I/O
  or award/delivery identity mutation and returns the exact typed retry outcome;
  the dispatcher alone returns its claimed event to retryable state.
  Deterministic CON test doubles prove required-port construction failure plus
  allow/deny behavior. REV-12A owns integrated independent-session proof of both
  shared/exclusive advisory-lock orderings after consuming the merged CON-11
  hook manifest; REV-13 repeats the behavior in the joint live drill.
- [ ] Deterministic adapter conforms to the typed capability and registers only
  through the shared `ExternalServiceAdapterFactory[CompensationDeliveryAdapter]`
  in explicit FastAPI/Celery composition; no fallback constructor, service
  locator, runtime discovery, compatibility alias, or second factory path.
- [ ] Reconciliation preserves exact original identities; no duplicate worker
  bridge, registry, canonicalizer, or idempotency implementation.

## Verification and reviewers

Execute CON-08A in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/auth, product/ops, architecture,
docs, reuse/dedup, test-delta and CI integrity are required. Stop before callback.
