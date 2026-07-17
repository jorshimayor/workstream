# Chunk Contract: WS-CON-001-08B - Inbound Fulfillment Callback

## Goal and risk

Accept authenticated bound-service fulfillment results and create immutable
receipts/status updates. L1 auth/economic/replay risk.

## Allowed files

```text
backend/app/modules/compensation/{schemas,repository,service,ports}.py
backend/app/api/internal_compensation.py
backend/app/composition/compensation.py
backend/tests/{test_compensation,test_authorization,test_api_controls}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-08B.json
```

## Not allowed

```text
AUTH catalogue/grant/ServiceIdentity/static-matrix implementation edits
human role fallback; dynamic service grant; provider credentials
outbox transition ownership; production route registration
```

## Acceptance criteria

- [ ] Human/AUTH approves exact callback ServiceIdentity and static
  `compensation.fulfillment.report` row (or an explicitly closed set of
  identities), provisions ActorProfile/link, admits through AUTH-09E, and keeps
  the action planned until hidden callback behavior merges.
- [ ] Prepared callback locks profile/link and validates immutable
  ServiceIdentity, matrix membership and active action as code-owned facts.
  AUTH prepares its exact bound handle; CON locks binding/award/delivery/
  receipt rows and recomposes final facts; AUTH consumes/evaluates once before
  callback mutation.
- [ ] Exact route identity, project, instrument, award, frozen binding, external
  event, quantity/status, and idempotency must match. Actor/link/binding state
  loss denies.
- [ ] Duplicate exact receipt is idempotent; changed replay conflicts; fulfilled
  receipt is immutable and at most one exists per award.
- [ ] Suspended binding accepts only valid already-issued obligations; retired
  binding accepts only exact replay of a receipt accepted before retirement.
- [ ] Callback-before-local-ack creates terminal truth and suppresses later
  delivery without regression. Both lock orders and rate limits per actor plus
  binding are covered.
- [ ] Missing provisioned callback rows deny callback/readiness but do not fail
  startup/provisioning. AUTH later activates after hidden behavior proof.

## Review and stop

All baseline plus architecture, security, product, docs, reuse, test-delta, and
CI integrity. Stop before public registration.
