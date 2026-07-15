# Discovery: WS-CON-001 Contribution Record And Compensation Boundary

Discovery was read-only for application code. No contribution or compensation
runtime implementation was performed.

## Current behavior

- `backend/app/api/router.py` exposes the current backend only under
  `/api/v1` (plus the unversioned health compatibility route).
- `backend/app/modules/tasks/models.py::Submission` is already the immutable,
  version-numbered submission record. There is no separate `SubmissionVersion`
  table and WS-CON must not create one.
- `TaskService.claim_task` creates `TaskAssignment` but freezes no compensation
  policy. The parallel WS-REV plan will create `ReviewLease`; no review models
  exist on current `main`.
- `WorkstreamTask` and `Submission` lock guide-bound `PaymentPolicy` versions.
  The task also copies `base_amount`, `currency`, and `payout_type`. No runtime
  `ContributionRecord`, `PaymentRecord`, `CompensationPolicy`, award, receipt,
  fulfillment, or reputation model exists.
- Durable checker execution advances a locked Submission through the automatic
  gate to `review_pending`. The review/revision lifecycle is planned in the
  sibling `workstream-rev-001` worktree and remains unimplemented.
- Current task/project services still contain explicitly temporary legacy role
  checks. WS-AUTH owns their cutover; WS-CON must not reproduce or repair them.
- The shared `AuditEvent` ledger and caller-owned `AsyncSession` are the
  transaction foundation. There is no shared transactional-outbox module yet.
- Current artifact runtime is the pre-v2 foundation. Accepted ADR 0013 and
  `docs/spec_artifact_storage_service.md` define the target: only
  `ArtifactStorageOrchestrator` receives `ArtifactStore`; product modules use
  narrow typed capability ports.
- Trusted `main` now includes ADR 0014's generic typed
  `ExternalServiceAdapterFactory[TAdapter]` foundation. It does not supply a
  contribution-evidence capability or compensation provider adapter; those
  remain separately gated, explicit composition-root registrations.

## Reconciled working source and supplied generation-2 PDF

The working tree contains an editable reconciled Markdown transcription derived
from the supplied generation-2 PDF, plus that immutable PDF companion:

| File | SHA-256 | Observation |
|---|---|---|
| `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.md` | `cddbe20f4fadf5307f68519347bdd9520ef49b23fb0b92cad24c31fc9b34c640` | Editable reconciled working transcription derived from the revised PDF; not canonically adopted |
| `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification(2).pdf` | `ce65e208076769f0bafb09779d60ab6f5fc0c596514d4e8f4cc03690c6e6d457` | Revised archival companion; text extracts successfully; not a reproducible Markdown build contract |

The original tracked PDF is currently deleted in the user's working tree but
remains the immutable first archival generation at SHA-256
`34c4337f27e42a5b0ed5e153fe8ccd492ecede202c2764506a930d109aef66c1`.
`docs/reference_specs/README.md` and `SHA256SUMS` require that original to remain
unchanged. The revised candidate should therefore be retained as a second
generation rather than replacing the first.

## Reconciliation findings

| Finding | Evidence | Required correction in active contract |
|---|---|---|
| Wrong public prefix | Candidate section 18 uses `/v1`; router and ADR 0012 use `/api/v1`. | Use `/api/v1` only; no alias. |
| ActionId/PermissionId conflation | Candidate calls granular `compensation.policy.*` values permissions and says broad IDs were removed. Merged AUTH-07A preserves 74 approved PermissionIds and separately registers 50 planned ActionIds. | Publish an exact proposed ActionId -> PermissionId handoff. Never call an ActionId a permission or a merely planned identifier active. |
| Wrong Review action | Candidate uses `review.decision.record`; merged AUTH-07A and WS-REV use planned ActionId `review.decision` mapped to PermissionId `review.decision`. | Consume `review.decision` only after its AUTH/REV activation gate. |
| Invented WS-AUTH source | Candidate names `WS-AUTH-001-A`, which is not a canonical repository artifact. | Cite merged `docs/spec_authorization_service.md`, ADR 0012, and the closed catalogue. |
| Invented artifact permissions | Candidate uses `artifact.recovery.request`, `artifact.recovery.execute`, and `artifact.retrieve`. AUTH explicitly rejected the first; none is a registered PermissionId. | Use `artifact.verification_job.retry` through `ArtifactOperatorRecoveryPort`; require ART-owned typed storage/read capabilities and approved action mappings. |
| Wrong artifact port | Candidate injects `ArtifactStorePort` with store/projection/retain/retrieve methods. ADR 0013's target `ArtifactStore` has only provider-byte behavior and cannot enter product services. | WS-CON consumes narrow ART capability ports. Only ART orchestration receives the raw store. |
| Wrong providers | Candidate requires Local Storage/Flow Node parity. ADR 0013 locks LocalStorage for dev/focused tests, MinIO for local/CI S3 proof, AWS S3 for v0.1 production, and defers Flow Node/R2. | Test LocalStorage and MinIO; AWS deployment proof gates production; Flow Node remains future. |
| Wrong retention/search claims | Candidate assumes retain/pin and semantic indexing APIs that ADR 0013 deliberately excludes from v0.1 `ArtifactStore`. | Use ART's immutable completed-byte retention policy and typed lifecycle records; omit semantic indexing/search from WS-CON v0.1. |
| Duplicate submission model language | Candidate defines `SubmissionVersion` as if separate. | Treat existing `Submission` as the versioned identity and use `submission_id` in repository schemas. |
| Payment model collision | Active docs/model use guide-bound `PaymentPolicy`, a future mutable `PaymentRecord`, adjustments, and voidable contributions; candidate introduces immutable policies/awards/receipts and prohibits adjustments/voiding. | D2 approves `CompensationPolicyVersion` as the sole authority and complete PaymentPolicy removal; CON-01 records the ADR, 05A/05B perform the cutover, and only the legacy-row rule remains open. |
| Outbox assumed but absent | Candidate requires atomic outbox effects; repository has no shared outbox. WS-REV also blocks on it. | Land a shared caller-transaction outbox foundation before review-chain and contribution integration. |
| Direct system-action invention | Candidate adds `contribution.materialize`, `compensation.award.materialize`, and `outbox.dispatch` as if already registered permissions. | Derived contribution/award creation is a required participant of authorized `review.decision`. Shared outbox owns the proposed service-only dispatch action; CON adds no feature-local bypass action. |

## Relevant files/modules

| Path | Purpose | Notes |
|---|---|---|
| `backend/app/api/router.py` | API composition | Canonical `/api/v1`; future routes stay unregistered until coherent cutover. |
| `backend/app/modules/tasks/models.py` | Task, assignment, versioned Submission, shared audit | Must gain exact assignment compensation freeze; Submission remains canonical version identity. |
| `backend/app/modules/tasks/service.py` | Claim, submission, task lifecycle | WS-CON may integrate only through task-owned participants; auth cutover stays WS-AUTH-owned. |
| `backend/app/modules/projects/models.py` | Project and guide-bound `PaymentPolicy` | Approved for complete semantic removal in CON-05A and physical removal in CON-05B; the legacy-row rebuild/classification rule remains a human gate. |
| `backend/app/modules/projects/service.py` | Guide activation and policy locking | Must not become a second compensation-policy engine. |
| `backend/app/modules/authorization/*` | Current authority idempotency/audit foundation | WS-CON imports only the future public service/types, never repositories or grants. |
| `backend/app/modules/authorization/catalogue.py` from AUTH-07A `3ab25cf`, merged through `e9d72a1` | Canonical merged closed catalogue | 74 PermissionIds and 50 planned ActionIds; the additive permission is `review.queue.override`, not either proposed WS-CON service permission. All WS-CON ActionIds remain absent/proposed. |
| sibling `workstream-rev-001/.../` working delta atop `3e09e99` | Content-reviewed, uncommitted parallel review integration amendment | The branch has integrated trusted `main` `e9d72a1`; its delta defines hidden composition, lock order, contribution participant gates, PaymentPolicy removal dependencies, WS-CON-11 preflight, REV-12A hidden release control, and joint REV-13 activation. Required content tracks pass, but its handler-claim wording must be repaired to preserve CON-02B ownership. It cannot be consumed until the exact repaired snapshot is committed, commit-freshness reviewed, refreshed against trusted main, and merged. |
| `backend/app/modules/artifacts/*` | Current artifact metadata/orchestration foundation | Target v2 is still being delivered by WS-ART; WS-CON cannot import provider internals. |
| `backend/app/interfaces/artifacts.py` | Current v1 raw provider port | Not a WS-CON dependency; it is being clean-cut to ADR 0013 v2. |
| `docs/spec_artifact_storage_service.md` | Canonical target artifact contract | Owns narrow product capability ports, recovery, verification, quotas, and provider policy. |
| `docs/spec_authorization_service.md` | Canonical target authorization contract | Preserves broad PermissionIds; ActionIds are separate. |
| `docs/architecture_data_model.md` | Existing contribution/payment target | Conflicts with supplied candidate and needs ADR-backed reconciliation. |
| `docs/operations_payment_reputation.md` | Existing manual payment/reputation workflow | Needs coordinated update only after architecture adoption. |
| `backend/alembic/versions/*` | Current schema through merged AUTH-07A migration `0021_authorization_action_evidence.py` | Every runtime chunk must refresh the next migration number from trusted `main`; no WS-CON contract pre-reserves `0022`. |

## Current tests

| Test path | What it covers | Gaps relevant to WS-CON |
|---|---|---|
| `backend/tests/test_tasks.py` | Task policy locks, assignment uniqueness, immutable Submission versions, checker admission, concurrency | No compensation freeze, review effects, contribution, or award tests. |
| `backend/tests/test_projects.py` | Guide/policy activation including `PaymentPolicy` | No CompensationPolicy lifecycle or Finance Authority behavior. |
| `backend/tests/test_authorization.py` | Authority foundations plus merged closed catalogue/audit parity | The deny-by-default kernel, grants, service actors, and feature action activation remain later AUTH-owned work. |
| `backend/tests/test_audit.py` | Typed append-only authority evidence | No contribution/compensation lifecycle audit contract. |
| `backend/tests/test_artifacts.py` | Current artifact port, local adapter, content/binding/receipt foundation | Target v2, S3/MinIO, typed contribution projection capability, and evidence reads are not merged. |
| `backend/tests/test_checkers.py` | Durable checker run and `allow_review` routing | Stops before Review persistence. |
| `backend/tests/test_alembic.py` | Migration upgrade/downgrade guards | No outbox, review, or WS-CON schema. |
| `backend/tests/test_api_contract_e2e.py` | Current API contract drill | No review/contribution/compensation routes or events. |

## Dependencies/integrations

- WS-AUTH: executable kernel, grants, service actors, exact WS-CON ActionId
  registrations/mappings, immutable `AuthorizationDecision`, and final bypass
  removal. WS-CON does not edit those owned surfaces.
- WS-REV: `Review`, `ReviewLease`, findings/resolutions, decision idempotency,
  task effects, hidden composition, and final public review cutover.
- WS-ART: v2 store, LocalStorage/MinIO conformance, AWS proof, narrow system-
  generated projection/read/bind capabilities, verification recovery, and
  artifact action activation.
- Shared outbox: caller-transaction append, stable event identity, post-commit
  publication, at-least-once dispatch, delivery attempts, dead-letter, replay,
  and idempotent consumer contract.
- PostgreSQL: exact decimals, composite project ownership, uniqueness, row
  locking, immutable history, and atomic cross-domain commit.
- Celery/Redis: post-commit dispatch/projection/reconciliation execution only;
  correctness must remain PostgreSQL-backed.
- External compensation adapters: typed ADR 0014 capability, deterministic test
  adapter for proof, no provider-specific runtime integration in WS-CON.

## Risks discovered

| Risk | Why it matters | Suggested handling |
|---|---|---|
| Dual payment truth | `PaymentPolicy`/future `PaymentRecord` and new compensation versions/awards can disagree. | ADR-backed sole execution authority and clean documentation/schema cutover. |
| Permission replacement | Treating ActionIds as replacement permissions would break merged audit/grants. | Exact mapping table; AUTH-owned additive registration; typed manifest tests. |
| Circular REV/CON dependency | Leases need policy FKs; claims need freeze; decisions need contribution participant. | Explicit interleaving gates in chunk map. |
| Cross-domain deadlock/partial commit | Review, authority, tasks, artifacts, CON, audit, and outbox share one transaction. | One canonical lock order, caller-owned session, fault injection, real Postgres concurrency tests. |
| Economic overreach | Payment-provider or points-ledger logic could leak into Workstream. | Typed outbound instruction/receipt boundary and architecture import tests. |
| Artifact bypass | Direct store injection could bypass quotas, verification, binding, and audit. | ART-owned typed capability only; static import/composition tests. |
| Premature public surface | Partial routes would create authorization or lifecycle gaps. | Hidden internal composition until final coherent activation. |
| Legacy/pre-production rows | Existing PaymentPolicy/tasks/assignments cannot be safely guessed into new frozen terms. | Human-approved rebuild/classification/backfill rule before migration. |
| Event/schema drift | The candidate names many events without a shared outbox registry. | Freeze envelope/ownership in the outbox chunk before persistence consumers. |
| Scope size | The candidate is a multi-initiative system, not one PR. | PR-sized L1 chunks with hard stop after each merge. |

## Unknowns/questions for human

| Question | Why it matters | Needed before chunk? |
|---|---|---|
| Preserve both candidate generations and reconcile into active spec? | Maintains archival provenance and follows repository precedent. | Before 01. |
| May pre-production payment/task rows be rebuilt, or must they be classified/backfilled? | Determines migration safety and atomic claim cutover. | Before 05. |
| Approve two new service-only PermissionIds, `outbox.dispatch` and `compensation.fulfillment.report`? | Human outbox recovery/reconciliation authority must not execute async side effects; no existing permission safely names the external adapter callback entitlement. | Before shared-outbox prerequisite/08A. |
| Does the ART initiative add the contribution evidence capability, or should it be a separate ART-owned prerequisite chunk? | WS-CON cannot own raw storage orchestration. | Before 10. |

## Existing conventions to preserve

- One caller-owned async SQLAlchemy session and explicit commit boundary.
- Router -> service -> repository separation with stable structured errors.
- `/api/v1`, no short-prefix alias.
- Existing `Submission` is the versioned submission identity.
- Canonical review decisions only: `accept`, `needs_revision`, `reject`.
- ActionId and PermissionId are distinct closed types.
- Authorization resource facts come from canonical rows, never request JSON.
- Provider-neutral external adapters follow ADR 0014 with explicit composition.
- Only ART orchestration receives raw `ArtifactStore`.
- AWS S3 production, MinIO local/CI protocol proof, LocalStorage focused
  development/tests; Flow Node and R2 deferred.
- New/materially changed backend subsystems stay at or above 90 percent while
  repository coverage stays at or above 78 percent.
