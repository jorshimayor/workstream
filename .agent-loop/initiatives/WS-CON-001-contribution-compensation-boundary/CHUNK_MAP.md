# Chunk Map: WS-CON-001 Contribution Record And Compensation Boundary

## Rule

One chunk maps to one reviewable PR. No runtime chunk starts until its exact
AUTH, ART, REV, outbox, migration, and human gates are satisfied on current
trusted `main`. Every runtime chunk uses the fresh isolated PostgreSQL runner
and same-invocation coverage evidence defined in `PLAN.md`. D12 must resolve
one exact activation owner/custodian for every action before any AUTH
registration checkpoint starts; feature ownership never supplies a second
availability writer.

## Chunks

| Chunk | Title | Risk | Gate | Status |
|---|---|---:|---|---|
| `WS-CON-001-PLAN` | Contribution And Compensation Planning | L0 | None | Reviewed; D11/D12 human gates |
| `WS-CON-001-01` | Canonical Contract Adoption And Architecture Decision | L0/L1 | Plan/human decisions approved | Proposed |
| `WS-CON-001-02A` | Shared Transactional Outbox Persistence | L1 | 01; event ownership approved | Proposed |
| `WS-CON-001-02B` | Shared Outbox Dispatcher And Recovery | L1 | 02A; worker/operations contract; AUTH planned `outbox.dispatch` registration/context/fixed actor/assignment/prepared protocol merged; dispatcher remains disabled pending later AUTH activation | Proposed |
| `WS-CON-001-02C` | Shared Lifecycle Audit Participant | L1 | 02B; existing AuditEvent contract refreshed | Proposed |
| `WS-CON-001-03A` | Compensation Adapter-Binding Persistence | L1 | 02C; migration head refreshed | Proposed |
| `WS-CON-001-03B` | Compensation Policy Persistence | L1 | 03A; legacy-data rule | Proposed |
| `WS-CON-001-03C` | Contribution And Award Persistence | L1 | 03B; merged REV-03 and REV-04 exact FK targets | Proposed |
| `WS-CON-001-03D` | Delivery, Receipt, And Status Persistence | L1 | 03C | Proposed |
| `WS-CON-001-04A` | Hidden Adapter-Binding Service | L1 | 03A; AUTH planned binding registrations/typed contracts/grants/prepared protocol plus planned callback action/new permission and active callback actor/link/exact assignment merged; callback remains unavailable | Proposed |
| `WS-CON-001-04B` | Hidden Compensation-Policy Service | L1 | 03B,04A; post-04A AUTH binding activation merged; AUTH planned policy registrations/typed contracts/grants/prepared protocol merged | Proposed |
| `WS-CON-001-05A` | PaymentPolicy Semantic Consumer Cutover And Task Freeze | L1 | 04B; merged REV-02 exact `Submission.task_assignment_id` lineage; D2 approved; legacy rule; AUTH `task.claim` registration/evaluator/prepared protocol/activation | Proposed |
| `WS-CON-001-05B` | PaymentPolicy Physical Schema Removal | L1 | 05A; zero-consumer scan; removal migration approval | Proposed |
| `WS-CON-001-06` | Review-Lease Freeze Capability | L1 | REV-03 schema; 05B; AUTH planned `review.claim` typed/prepared contract; exact caller facts stable | Proposed |
| `WS-CON-001-07` | Atomic Contribution/Award Decision Participant | L1 | 03C-D; REV-09B; shared audit/outbox; AUTH planned `review.decision` typed/prepared contract | Proposed |
| `WS-CON-001-08A` | Outbound Compensation Delivery Handler | L1 | 07; 02B; post-02B AUTH `outbox.dispatch` evaluator/activation and exact service-assignment proof merged; ADR 0014 adapter foundation; joint lifecycle-fence port contract | Proposed |
| `WS-CON-001-08R` | Bound-Service Callback Rate Control | L1 | 08A; shared API-control contract | Proposed |
| `WS-CON-001-08B` | Inbound Fulfillment Callback | L1 | 08R; callback identity/action registration already merged before 04A; AUTH typed callback context and prepared protocol merged; joint callback-fence port contract | Proposed |
| `WS-CON-001-09A` | Contribution Evidence Projection Write | L1 | 07; D12 exact AUTH custody for all eleven ART-02D actions; AUTH-09 internal executor registration/identities/assignments -> merged ART 02A2 -> 02A3 -> 02B1 -> 02C1 -> 02C2 -> 02C3 -> hidden 02D behavior -> AUTH Operator/internal evaluator activation; named `WS-ART-001-CON-EVIDENCE` write port; AUTH planned evidence action/context/prepared protocol and exact assignment on existing `workstream.artifact.binding` | Proposed |
| `WS-CON-001-09B` | Authorized Contribution Evidence Read | L1 | 09A; merged named `WS-ART-001-CON-EVIDENCE` read port; disclosure schema; AUTH planned contribution-read registrations/typed contexts | Proposed |
| `WS-CON-001-10A` | Contribution And Award Product Reads | L1 | 08B,09B; post-09B AUTH contribution-read activation; D11 award/audit role outcome approved; AUTH planned award-read registrations/typed contexts/exact chosen role contract | Proposed |
| `WS-CON-001-10B` | Operations, Reconciliation, Rebuild, And Fulfillment Drain Observation | L1 | 10A; post-10A AUTH award-read activation; full D11 outcome approved and any chosen AUTH role-matrix amendment merged; AUTH planned binding-retire/ops/audit registrations/typed contexts/exact chosen role contract/prepared protocol; shared-outbox observation capability | Proposed |
| `WS-CON-001-11` | Hidden Release Readiness And Dependency Manifest | L1 | 10B; REV-10 integration; exact AUTH evaluator/action/service manifest, ART/outbox readiness, required CON-owned dispatch/callback fence hooks and drain port | Proposed |

## Dependency order

```text
PLAN -> 01 -> 02A -> 02B -> 02C -> 03A -> 03B -> 03C -> 03D -> 04A -> 04B -> 05A -> 05B -> 06 -> 07 -> 08A -> 08R -> 08B -> 09A -> 09B -> 10A -> 10B -> 11
```

Cross-initiative ownership and merge gates:

```text
CON-02A -> AUTH outbox registration/service assignment -> CON-02B hidden dispatcher -> AUTH outbox evaluator/activation -> CON-08A
CON-03A -> AUTH binding registration/contracts + planned callback action/permission + active callback actor/link/assignment -> CON-04A hidden binding behavior -> AUTH binding evaluator/activation
CON-04A + AUTH policy registration/contracts -> CON-04B hidden policy behavior -> AUTH policy evaluator/activation -> CON-05A
CON-03B policy persistence -> REV-03 lease persistence (REV owns lease FK)
REV-02 exact Submission.task_assignment_id lineage -> CON-05A semantic cutover/freeze -> CON-05B physical removal -> new task claims under compensation policy only
AUTH-13 ordered task.claim registration/typed-prepared contract -> task resource behavior -> evaluator/activation (or the same ordered work in a reviewed AUTH successor) -> CON-05A
CON-02C shared audit participant -> REV-04 review-chain persistence
REV-03 lease persistence + CON-05B -> CON-06 capability
AUTH review.claim registration/contracts -> CON-06 -> REV-06 hidden claim composition while planned -> AUTH review.claim evaluator/activation
REV-04 exact Review target -> CON-03C foreign keys
AUTH review.decision registration/contracts + REV-09B + CON-07 participant -> REV-10 hidden decision composition while planned -> AUTH review.decision evaluator/activation
AUTH callback identity/action registration before CON-04A + remaining typed/prepared callback contracts -> CON-08B hidden callback -> AUTH callback evaluator/activation -> CON-11
D12 AUTH custody for 8 ART-02D Operator + 3 internal actions -> AUTH-09 fixed executor registration/identities/assignments -> ART-02A2 preparation -> ART-02A3 v2 -> ART-02B1 MinIO/AWS -> ART-02C1 admission -> ART-02C2 verification/publication -> ART-02C3 recovery -> ART-02D hidden executor/Operator behavior -> AUTH Operator/internal evaluator activation -> ART-owned CON-EVIDENCE write/read ports
AUTH evidence action/typed/prepared/exact-service-assignment registration + ART capability -> CON-09A hidden handler -> AUTH evidence evaluator/activation -> CON-11
AUTH contribution-read registration/contracts -> CON-09B hidden reads -> AUTH contribution-read activation -> CON-10A
D11 award-role decision + AUTH award-read registration/contracts -> CON-10A hidden reads -> AUTH exact-role award activation -> CON-10B
D11 delivery/audit decisions + any required AUTH matrix amendment + operations registration/typed/prepared/exact-role contracts -> CON-10B hidden operations -> AUTH exact-role operations activation -> CON-11
CON-08A/B,09A/B,10A/B + REV-12 + AUTH/ART/outbox -> CON-11 hidden readiness
CON-08A/08B/10B/11 required CON-owned dispatch/callback fence ports and fulfillment-drain observation + CON-11 hidden manifest + REV-12 -> REV-12A hidden joint release-control composition -> REV-13 sole route activation and joint live drill
```

## Chunk boundaries

- 01 reconciles specifications/ADR and owns only the exact fail-closed scanner
  classification required by its byte-preserving archival rename; 05A
  atomically removes all PaymentPolicy semantic consumers and freezes the
  replacement policy on task claim; 05B physically drops the unreachable
  model/table/columns/constraints.
- 02A owns generic persistence/append; 02B alone owns the feature-neutral
  dispatcher, handler registry, retry/dead-letter/replay, operations, and typed
  read-only drain observation.
- 02C extends the existing shared AuditEvent repository/service with one typed
  caller-transaction lifecycle participant; it owns no review/CON semantics.
- 03A/03B split binding and policy schema; 03C/03D split canonical economic
  truth from delivery/receipt/projection schema.
- 04A/04B split hidden binding and policy services; routes remain unregistered.
- Every authorized feature family follows AUTH registration -> hidden CON
  implementation -> AUTH activation. Registration alone stays fail-closed; the
  CON chunk may prove domain behavior below an explicit test boundary but owns
  no production allow fallback. AUTH owns availability/evaluators/principal
  truth and the prepared mutation protocol. A later CON consumer and CON-11
  wait for the preceding AUTH activation gate.
- 05A owns the cross-module semantic cutover because the old locked fields span
  project, task, submission and checker contracts; 05B is schema cleanup only.
- 06 exposes only a CON-owned capability; REV-06 owns review claim wiring.
- 07 creates the database-local participant; REV-10 owns review wiring.
- 08A is an outbox feature handler and owns its narrow mandatory dispatch-fence
  consumer port; REV-12A may supply the durable implementation only through
  joint composition and may not edit the CON handler. 08R extends the shared
  closed rate-control scopes; 08B owns the separately authenticated callback
  and its narrow mandatory callback-fence consumer port.
- 09A writes evidence projections through ART; 09B owns safe reads. PR #129's
  02A2 preparation is only a prerequisite: CON passes a bounded deterministic
  byte source plus expected digest/size/media type through the named port, while
  ART alone owns scratch preparation, sealed-source lifetime, admission,
  provider I/O, verification and binding.
- 10A owns product reads; 10B owns operations/reconciliation/rebuild plus the
  read-only fulfillment-drain observation port over CON and shared-outbox state.
- 11 proves hidden readiness, including both required fence injection seams and
  the drain-observation port, and produces the exact dependency manifest. It
  registers no production routes. REV-12A owns hidden release-control
  composition; REV-13 remains the sole joint activation owner.

## Required reviewer tracks

Every chunk: senior engineering, QA/test, security/auth, product/ops,
architecture, docs, and reuse/dedup. Runtime/test chunks add test-delta. Add CI
integrity for workflow, scripts, dependency, package, test configuration, or
coverage changes.

## Stop condition

Planning ends after required plan review and human discussion. Do not start 01
or any runtime chunk automatically.
