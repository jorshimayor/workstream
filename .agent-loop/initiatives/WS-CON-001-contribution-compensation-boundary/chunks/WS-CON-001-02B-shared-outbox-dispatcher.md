# Chunk Contract: WS-CON-001-02B - Shared Outbox Dispatcher And Recovery

## Goal and risk

Implement the one feature-neutral outbox dispatcher and operational recovery.
L1 worker/operations/infrastructure risk.

## Allowed files

```text
backend/app/modules/outbox/{models,schemas,repository,service,ports,dispatcher,handlers}.py
backend/app/workers/celery_app.py
backend/app/workers/outbox.py
backend/app/core/config.py only bounded dispatcher settings
backend/tests/test_outbox.py
backend/tests/test_config.py only dispatcher-setting coverage
docs/operations_outbox.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-02B.json
```

## Not allowed

```text
backend/app/workers/async_runner.py or task_settings.py rewrites
feature callback/adapter, review or compensation behavior
second dispatcher/handler registry/async bridge/session factory/idempotency framework
dependency, workflow, test or coverage weakening
```

## Acceptance criteria

- [ ] AUTH has registered planned `outbox.dispatch` with its new service-only
  PermissionId, typed context contract, fixed `workstream.outbox.dispatcher`
  ActorProfile/link, exact action assignment, and D10 prepared-mutation
  protocol. This chunk keeps dispatcher execution disabled and proves the real
  kernel denies while planned; only a later AUTH-owned evaluator/activation
  change may enable it, and no human grant can execute dispatch.
- [ ] The dispatcher prepares authority from a server-resolved preliminary
  event target before locking/claiming OutboxEvent, then evaluates the opaque
  handle exactly once against final typed event/claim/lease/generation facts
  recomposed from locked rows. It retains the one AuthorizationDecision in the
  dispatch causation/audit path, never asks AUTH to commit, and rejects missing,
  reused, mismatched, cross-session or cross-action handles.
- [ ] While the action is planned, success-path domain tests use only an
  explicit decision/fake below that prepared seam. Real-kernel and worker tests
  remain fail-closed; transaction tests cover prepare denial, stale claim,
  final-context mismatch and both AUTH-first/product-lock race orders.
- [ ] One explicit handler registry, stable Celery task IDs, fenced claim,
  attempt, retry schedule, dead-letter, replay, retention and bounded recovery
  preserve immutable event identity.
- [ ] The shared dispatcher alone mutates outbox claim, lease/generation,
  retry/dead-letter and finalization state. Feature handlers receive an already
  claimed immutable command and return a typed success/retry/terminal outcome;
  they never claim or directly transition the OutboxEvent.
- [ ] Claim reservation commits and releases its session and every row/database
  lock before handler invocation. The immutable handler command carries exact
  event/claim generation, but no live ORM row or caller session.
- [ ] A read-only same-session `OutboxClaimValidationPort` lets a handler verify
  that exact generation after acquiring its lifecycle fence and before locking
  feature rows. It never locks or mutates OutboxEvent state and exposes no
  repository; the dispatcher revalidates again when applying the typed outcome.
- [ ] Reuse `run_async_task`, current fresh-engine/session-disposal worker
  pattern, existing Celery include list and `sync_task_settings`; no second async
  bridge, session factory, handler registry, scheduler, or idempotency framework.
- [ ] Crash-before/after handler, stale completion, duplicate task, retry
  exhaustion and reason-bound replay are real-PostgreSQL tested.
- [ ] A feature-neutral same-session `OutboxDrainObservationPort` reports
  bounded counts by exact registered event type/handler and closed delivery
  states, including pending, claimed, retryable and handler-in-flight work. It
  is read-only, never commits or invokes a handler, and exposes neither the
  repository nor mutable outbox rows.
- [ ] Observation races claim, stale-claim recovery, retry, dead-letter and
  finalization in both orders without false zero. Feature modules may compose
  the port with their own canonical state but may not extend its status model or
  query outbox persistence directly.
- [ ] Handler invocation occurs after commit; no feature event semantics or
  compensation adapter is implemented here.
- [ ] The post-CON AUTH activation gate owns end-to-end central evaluator and
  service-assignment proof against this merged seam without editing dispatcher
  code. CON-08A and any worker enablement remain blocked until that gate merges.

## Verification and reviewers

Execute the exact CON-02B expansion in `../RUNTIME_VERIFICATION.md`. Same-run
changed-subsystem coverage is at
least 90 percent. All baseline tracks plus architecture, security/auth,
product/ops, docs, reuse/dedup, test-delta and CI integrity. Stop before feature
handlers.
