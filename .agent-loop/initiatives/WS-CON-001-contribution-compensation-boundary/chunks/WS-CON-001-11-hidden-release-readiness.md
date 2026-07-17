# Chunk Contract: WS-CON-001-11 - Hidden Release Readiness And Dependency Manifest

## Goal and risk

Prove the core WS-CON subsystem coherent while hidden and publish an exact
merged-SHA/schema/action/service/handler/fence/drain/test manifest for the
reviewed REV release owner. L1 release/auth/economic risk.

## Allowed files

```text
backend/app/composition/{contributions,compensation,outbox}.py
backend/tests/{test_api_contract_e2e,test_authorization,test_contributions,test_compensation,test_outbox}.py
docs/spec_contribution_compensation.md
docs/internal_reviews/WS-CON-001-hidden-release-readiness.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-11.json
```

## Not allowed

```text
production route registration or noncanonical prefix alias
REV lifecycle-control persistence/policy; AUTH/ART implementation
optional evidence projection/read or ART readiness gate
archival input edits
```

## Acceptance criteria

- [ ] Startup parity covers closed ActionId/PermissionId/ActionOwner, typed
  contexts/evaluators, ServiceIdentity/static rows, and active-feature behavior.
  Active-without-evaluator/behavior or extra/missing matrix membership fails.
- [ ] Missing provisioned service ActorProfile/link rows do not fail app startup
  or Access Administrator provisioning. Protected runtime calls deny and
  release readiness stays false until exact rows exist.
- [ ] AUTH manifest binds trusted baseline, complete REV custody transfer,
  proposed core CON mappings plus separately approved executor actions, D11
  role sets, exact grants/static rows, AUTH-09E admission, prepared protocol,
  decision digests/matched authority, and activation evidence.
- [ ] No partial ART/REV transfer is restated. Complete mappings are referenced
  from merged WS-XINT handoffs. ART and optional CON-09A/09B are absent from
  core prerequisites.
- [ ] Hidden integration proves production OpenAPI routes remain absent and no
  direct construction path bypasses AUTH, fixed-service admission, outbox
  handler isolation, or mandatory REV/CON participant composition.
- [ ] Manifest names exact migrations, schemas, event/task IDs, registry rows,
  service identities/actions/static rows, handler execution boundaries, and
  retained test metadata. Dispatcher cannot execute protected handlers.
- [ ] Manifest names CON-owned FulfillmentDispatchFence,
  FulfillmentCallbackFence, FulfillmentLifecycleDrainObservationPort,
  OutboxClaimValidationPort, injection seams, phase mappings, denial states,
  and fail-closed construction without REV release-control implementation.
- [ ] Core conformance matrix has executable evidence; same-run repository
  coverage is at least 78 and changed subsystems at least 90.
- [ ] Joint drill contract covers all core families. Accept proves Task
  `accepted`, Assignment `completed`, one FinalAcceptance and one submitter
  contribution. Needs_revision proves Task `needs_revision`, Assignment still
  `active`, and neither acceptance fact nor submitter contribution. Reject
  proves Task `rejected` with bounded human reason, only the same-task
  Assignment blocked with its source Review, and neither acceptance fact nor
  submitter contribution. Every Review proves one reviewer contribution. It
  explicitly
  asserts zero ART calls and no adjudication model/action/state/queue/readiness
  dependency. It is not marked executed here.

## Verification

Run the initiative runtime commands plus Markdown links, stale wording,
authorization/artifact scanners, loop-memory check, internal evidence check, and
git diff check.

## Review and stop

All internal tracks including CI integrity and test-delta. Stop after hidden
manifest. Do not register routes, implement REV release control, run production
activation, or start optional evidence work.
