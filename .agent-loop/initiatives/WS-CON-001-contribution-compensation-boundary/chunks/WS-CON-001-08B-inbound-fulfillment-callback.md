# Chunk Contract: WS-CON-001-08B - Inbound Fulfillment Callback

## Goal and risk

Accept immutable reports from the exact service actor bound to the frozen
adapter binding, behind an unregistered route. L1 external-auth/payment risk.

## Allowed files

```text
backend/app/modules/compensation/{schemas,repository,service,ports,callback}.py
backend/app/api/internal_compensation.py
backend/app/composition/compensation.py
backend/tests/{test_compensation,test_authorization,test_api_contract_e2e}.py
docs/operations_payment_reputation.md only callback operations
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-08B.json
```

## Not allowed

```text
production router registration or human authority
AUTH catalogue/grant/kernel/service-assignment edits
outbound adapter/dispatcher, provider secret/ref, dependency/CI weakening
REV-owned lifecycle-control persistence/phase policy or implementation
optional/no-op/fallback callback fence or REV edits to CON callback policy
```

## Acceptance criteria

- [ ] AUTH callback PermissionId/ActionId/parity/exact assignment is merged;
  human AdminRoleGrant/ProjectRoleGrant never satisfies it.
- [ ] Locks revalidate actor/link/assignment/route/award/project/instrument/
  binding/state; durable rate control is per actor+binding.
- [ ] After signature verification and AUTH/idempotency locking, callback
  handling requires a narrow CON-owned `FulfillmentCallbackFence`, captures the
  allowed lifecycle phase before any compensation-domain row, and holds the
  shared transaction fence through idempotent receipt commit. Missing injection
  fails closed; there is no optional/no-op/fallback production fence.
- [ ] The callback fence allows authenticated callbacks through
  `delivery_draining` and denies them after `disabled`. Deterministic CON test
  doubles prove allow/deny semantics; REV-12A owns integrated callback-versus-
  disable independent-session tests in both lock orderings, and REV-13 repeats
  the behavior in the joint live drill.
- [ ] CON owns callback verification, receipt/idempotency policy, and the
  callback-fence consumer port. REV-12A may inject its durable implementation
  only through explicit composition and may not edit CON callback policy.
- [ ] Suspended accepts valid already-issued work; retired accepts only exact
  previously accepted receipt replay; actor/link revocation always denies.
- [ ] Callback-before-ack suppresses delivery; replay is idempotent; changed
  receipt conflicts; callback-vs-delivery/retire races cover both orders.
- [ ] Callback-before-ack derives `acknowledged_by_adapter`; a late dispatcher
  acknowledgement is idempotent and cannot regress fulfillment or delivery.
- [ ] Behavior tests prove failed then fulfilled is allowed, fulfilled then
  failed/changed-fulfilled is denied, and partial fulfillment is rejected.
- [ ] Production OpenAPI remains unchanged and secrets/refs are never stored.

## Verification and reviewers

Execute CON-08B in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/privacy, product/ops,
architecture, docs, reuse/dedup and test-delta are required. Stop before public
registration.
