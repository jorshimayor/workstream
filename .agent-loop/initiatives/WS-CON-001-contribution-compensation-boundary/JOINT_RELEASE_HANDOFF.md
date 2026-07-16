# Joint Release Handoff: WS-CON-001 To WS-REV-001-13

## Incorporation status

The inspected sibling branch now has clean committed head `a13bf35`, based
on trusted `main` including AUTH-08. Its planning contracts assign future
contribution/compensation router registration, consumption of the WS-CON-11
preflight manifest, the joint live matrix, PaymentPolicy removal dependencies,
active generated/document companions and REV-12A hidden release control. Those
runtime changes are not implemented. The planned composition consumes the
CON-owned dispatch/callback fences and fulfillment-drain observation instead of
importing CON/outbox repositories.

The AUTH-08 dependency refresh now records correct merged counts and
transaction/error/timestamp repairs, but final publication evidence remains
intentionally stale pending ART. The sibling is still not consumable: REV-06/10
predate the registration -> CON -> REV hidden -> AUTH activation choreography
and D12 owner-custody decision, and REV-12A still says the CON handler claims
the shared-outbox event. Before review/merge it must instead accept the
dispatcher's already-claimed command and return a typed outcome, leaving every
outbox transition to CON-02B. It must also adopt AUTH-08's current decision/
transaction contract and the executable-gate/prepared-authorization
requirements. WS-CON does not edit the sibling. The WS-REV owner must repair,
commit-bind, internally review and merge the exact final contract. Until later
implementation gates land, both initiatives remain hidden.

The refresh must also repair REV-06/10 authorization choreography. AUTH first
registers the planned review action and typed/prepared contract; CON supplies
its capability/participant; REV then merges hidden resource composition and
final-context integration while the real kernel still denies; AUTH alone
integrates the evaluator and activates the action before production execution.
REV must not require active review actions before building the hidden
composition that AUTH activation depends on.

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
- Every registered route explicitly commits its own complete read or mutation
  plus AuthorizationDecision and business/audit/outbox/idempotency state.
  Domain services remain flush-only. The service-authenticated fulfillment
  callback explicitly commits its decision plus receipt/idempotency state in
  the fenced transaction. Tests prove an omitted commit is rolled back by
  dependency teardown, authorization-evidence failure is one retryable 503 with
  zero partial state, callback commit failure leaves no partial receipt, and no
  route relies on dependency ordering to commit.
- Consume CON-11's exact merged-SHA/migration/action/service-assignment/ART/
  outbox/worker/handler/fence manifest plus AUTH context/evaluator/matched-
  authority/prepared-protocol/availability parity, and fail startup/preflight
  on any mismatch or active action without executable behavior.
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
  evidence privacy/rebuild, D11-approved delivery/operations role behavior,
  denials, atomic
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
