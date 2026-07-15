# Joint Release Handoff: WS-CON-001 To WS-REV-001-13

## Incorporation status

The inspected sibling working delta atop `3e09e99` has incorporated
contribution/compensation router registration, the WS-CON-11 preflight
manifest, the complete joint live matrix, PaymentPolicy removal dependencies,
the active generated/document companions, and a new REV-12A hidden
release-control chunk. The delta also corrects REV-12A to consume the CON-owned
dispatch and callback fences plus fulfillment-drain observation through
composition instead of editing CON product files or importing CON/outbox
repositories. Its required content-review tracks pass, but the snapshot remains
uncommitted and lacks commit-bound freshness evidence as recorded in
`SOURCE_MANIFEST.md`; it is working discovery evidence, not a dependency.
The current REV-12A draft still says the CON handler claims the shared-outbox
event; before review/merge it must instead accept the dispatcher's already-
claimed command and return a typed outcome, leaving every outbox transition to
CON-02B's shared dispatcher.
WS-CON does not edit the parallel worktree. The WS-REV owner must commit the
exact content-reviewed delta, run commit-bound freshness review, and merge
before CON-11, REV-12A, or REV-13 can activate. Until the later implementation
gates land, both initiatives remain hidden.

## Required REV-13 allowed-file additions

```text
backend/app/api/router.py for one joint review/contribution/compensation registration
backend/app/modules/reviews/router.py
backend/app/modules/contributions/router.py
backend/app/modules/compensation/router.py
backend/tests/test_api_contract_e2e.py
backend/tests/test_authorization.py
backend/tests/test_reviews.py
backend/tests/test_contributions.py
backend/tests/test_compensation.py
README.md
docs/product_brief.md
docs/product_principles.md
docs/principles.md
docs/architecture_data_model.md
docs/operations_payment_reputation.md
docs/operations_operator_workflow.md
docs/operations_project_operating_manual.md
docs/template_project_guide.md
docs/template_task.md
docs/architecture_brief/workstream_architecture_brief.md
docs/architecture_brief/workstream_architecture_brief.pdf
docs/architecture_brief/task_lifecycle_sequence.puml
docs/architecture_brief/images/task_lifecycle_sequence.png
docs/architecture_brief/images/future_identity_payment_reputation.png
docs/architecture_brief/images/workstream_v01_container.png
docs/diagrams/task_lifecycle_sequence.md
docs/diagrams/workstream_v01_container.md
docs/diagrams/workstream_v01_container.puml
docs/diagrams/rendered/workstream_v01_container.svg
docs/diagrams/future_identity_payment_reputation.md
docs/diagrams/future_identity_payment_reputation.puml
docs/diagrams/rendered/future_identity_payment_reputation.svg
```

This is a seed list, not a closed substitute for discovery. REV-13 must replace
it with CON-01's exact generated active-document/companion inventory and may add
or remove paths only from that evidence. It must include every active/template/
operations/generated file containing an affected claim. Archival inputs,
historical reviews, and generated loop memory remain excluded.

## Required joint activation criteria

- Register review, contribution, compensation policy/binding, contribution/
  award/evidence reads, fulfillment callback, and bounded operations routers in
  the same PR under `/api/v1`; no `/v1` alias and no partial prior surface.
- Consume CON-11's exact merged-SHA/migration/action/service-assignment/ART/
  outbox/worker/handler/fence manifest and fail startup/preflight on any
  mismatch.
- Use REV-12A only for hidden persisted joint lifecycle control and explicit
  composition. Consume the required CON-owned `FulfillmentDispatchFence`,
  `FulfillmentCallbackFence`, and `FulfillmentLifecycleDrainObservationPort`;
  do not edit CON delivery/callback/outbox policy or import CON/outbox
  repositories from REV.
- Preserve CON-02B as sole outbox claim/retry/finalization owner. REV-12A may
  fence the CON handler and observe drain state, but neither REV nor the handler
  claims or directly transitions the shared OutboxEvent.
- Prove the complete `CONFORMANCE_MATRIX.md` plus REV matrix with collected node
  IDs and retained live evidence, including policy/binding setup, task/review
  freezes, accept/needs_revision/reject, second revision review, money+points,
  explicit unpaid, delivery/callback ordering, suspended/retired binding,
  evidence privacy/rebuild, Finance-versus-Operator operations, denials, atomic
  rollback, storage/adapter outage, replay and reconciliation.
- Update all active sources/generated companions in the same release so no
  mutable PaymentRecord, accept-only/voidable contribution, automatic
  reputation, executable PaymentPolicy or stale prefix claim remains.
- Preserve the one-sheet roadmap rule if the roadmap is touched; do not change
  archival reference bytes.

## Ownership

WS-REV-001-12A owns only the hidden joint release-control foundation and typed
composition; WS-REV-001-13 remains the sole production activation/live-drill
PR. This file does not authorize WS-CON to edit the sibling plan or start REV
work. The incorporated sibling contract must be preserved through rebase,
receive any required delta review, and merge before an implementation chunk may
consume it.
