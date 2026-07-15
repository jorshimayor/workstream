# Chunk Contract: WS-CON-001-11 - Hidden Release Readiness And Dependency Manifest

## Goal and risk

Prove the complete WS-CON subsystem is coherent while still hidden, emit an
exact dependency/action/schema/test/fence manifest, hand hidden joint
release-control composition to WS-REV-12A, and hand sole production activation
to WS-REV-13. L1 release/auth/payment risk.

## Allowed files

```text
backend/app/composition/contributions.py
backend/app/composition/compensation.py
backend/app/composition/outbox.py
backend/tests/test_api_contract_e2e.py
backend/tests/test_authorization.py
backend/tests/test_contributions.py
backend/tests/test_compensation.py
backend/tests/test_outbox.py
docs/spec_contribution_compensation.md
docs/internal_reviews/WS-CON-001-hidden-release-readiness.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-11.json
```

## Not allowed

```text
production router registration or /v1 alias
review service/composition ownership
REV-owned lifecycle-control persistence, phase policy, or fence implementation
AUTH/ART catalogue, kernel, grant, provider, or storage edits
active public API/operations claims before REV-13 activation
archival reference edits
```

## Acceptance criteria

- [ ] Startup/preflight fails closed unless exact migrations, AUTH action
  definitions/owners/PermissionId mappings/availability/typed
  contexts/evaluators/matched authorities/prepared protocol/service
  dependencies and assignments, ART capabilities, outbox dispatcher, REV-10
  integration and provider readiness are present. An active action without its
  executable evaluator or feature behavior fails startup.
- [ ] Hidden integration proves `/api/v1` target paths are absent from production
  OpenAPI before release and no partial direct construction path exists.
- [ ] `CONFORMANCE_MATRIX.md` has collected node IDs/evidence for every adopted
  invariant; isolated full-suite metadata proves repository >=78 percent and
  every changed subsystem >=90 percent from the same run.
- [ ] Dependency manifest names exact merged SHAs/schema symbols/action mappings,
  migration heads, stable Celery task IDs, handler registry entries and live
  preconditions consumed by REV-13.
- [ ] Manifest names the exact CON-owned `FulfillmentDispatchFence` and
  `FulfillmentCallbackFence` port symbols, handler constructor/injection seams,
  registry bindings, `OutboxClaimValidationPort`, committed claim handoff,
  phase/command mappings, denied retry/callback transitions, and proof that
  production construction fails closed without the REV-12A implementation.
  REV-12A consumes both seams through composition and does not edit CON product
  files.
- [ ] Manifest names the exact same-session
  `FulfillmentLifecycleDrainObservationPort`, shared-outbox observation
  capability, pending/claimed/retryable/in-flight/nonterminal count semantics,
  and zero-obligation proof consumed by REV-12A. Lifecycle control receives no
  CON or outbox repository.
- [ ] CON-01 inventory covers every active README-linked source/generated
  companion with stale mutable PaymentRecord, accept-only/voidable contribution,
  automatic reputation, PaymentPolicy execution or `/v1` wording. REV-13 owns
  the atomic active-doc/API/live-drill update; archival/history remains untouched.
- [ ] Joint drill script/evidence contract covers every conformance family but
  is not represented as executed until REV-13's sole activation PR.

## Verification commands

Execute the exact CON-11 expansion in `../RUNTIME_VERIFICATION.md`, then:

```bash
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
git diff --check
```

## Review and stop

All internal reviewer tracks, including CI integrity and test-delta, are
required. Stop after the reviewed hidden-readiness manifest. Do not register a
route, implement lifecycle-control policy, perform the production drill, edit
WS-REV, or start REV-12A/13. Only the human may direct the WS-REV owner to
consume this gate.
