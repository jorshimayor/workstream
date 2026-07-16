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
- Trusted `main` `aa0fdcd` now includes AUTH-08. The authorization catalogue is
  74 PermissionIds/57 ActionIds with nine active and 48 planned actions. Durable
  scoped AdminRoleGrants, the five-role permission matrix, typed grant resource
  contexts, resource-context digests, matched grant/scope evidence, explicit
  route-owned commits and retryable authorization-evidence failure handling are
  merged. Service actors, ProjectRoleGrants, D10 and every WS-CON action remain
  future AUTH-owned work.

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
| ActionId/PermissionId conflation | Candidate calls granular `compensation.policy.*` values permissions and says broad IDs were removed. Merged AUTH-08 preserves 74 approved PermissionIds and separately registers 57 ActionIds: nine active self/admin actions and 48 planned actions. | Publish an exact proposed ActionId -> PermissionId handoff. Never call an ActionId a permission or a registered/planned identifier executable. |
| Registration treated as activation | AUTH-08 evaluates only its self/admin action families; all planned, unsupported, wrong-context and unimplemented actions deny. No WS-CON evaluator exists. | AUTH must own typed-context/evaluator/principal/transaction integration and active availability. CON owns product facts/guards only and cannot flip the AUTH catalogue. |
| Cross-domain mutation lock gap | Current `require()` can revalidate actor-self wholly inside AUTH, but WS-CON mutations need AUTH rows before product rows and final evaluation against locked product facts. | AUTH supplies the prepared, caller-session-bound, single-use `T` protocol in D10; no unlocked-snapshot decision or product-before-AUTH lock order. |
| Merged Operator permission gap | AUTH-08's closed `operator` definition omits existing PermissionId `compensation.delivery.reconcile`, but the reconciled candidate WS-CON matrix proposes a reason-bound Operator as well as Finance Authority to request delivery reconciliation. Only D2 is human-approved. | D11 human decision: an AUTH-owned reviewed successor adds the existing permission before CON-10B if Operator behavior is retained, otherwise CON-01 removes the candidate before registration. CON has no role-query/local fallback. |
| Cross-spec role-set conflict | AUTH-08 gives Project Manager `compensation.award.read` and broader roles `audit.read`/`audit.export`, while the unadopted WS-CON candidate proposes narrower monetary/audit sets. | D11 human choice freezes each active set. Any approved narrowing is AUTH evaluator policy with matched grant/scope proof; preserving merged candidates updates CON-01. Permission membership or candidate text alone never settles the action. |
| ActionOwner activation conflict | Canonical `ActionOwner` means the implementation chunk allowed to activate an action. Existing review actions name REV owners, while the reconciled AUTH boundary says only AUTH activates after feature composition; the 23 WS-CON actions had no exact owner mapping. | D12 human/AUTH decision plus the exact closed owner map in `AUTHORIZATION_HANDOFF.md`; never permit AUTH and a feature chunk to both change availability. |
| Missing upstream task action | PermissionId `task.claim` exists, but current ActionId has no `task.claim` member. | AUTH-13 or reviewed AUTH successor registers/evaluates/activates `task.claim` before CON-05A integrates compensation freeze. |
| Wrong Review action | Candidate uses `review.decision.record`; merged AUTH catalogue and WS-REV use registered planned ActionId `review.decision` mapped to PermissionId `review.decision`. | Consume `review.decision` only after its AUTH evaluator/availability and REV resource-composition gates. |
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
| `backend/app/modules/authorization/{catalogue,kernel,runtime,policy}.py` from merged AUTH-08 | Canonical closed registry, grant policy and executable kernel | 74 PermissionIds, 57 ActionIds, nine active self/admin actions and 48 planned; eight resource-context variants and actor-self/AdminRoleGrant matched authority. All WS-CON-specific actions and both service permissions remain absent. |
| `backend/app/api/deps/authorization.py` | Current human composition root and transaction cleanup | Human self/admin only; it rejects service subjects, maps typed evidence failure to retryable 503 and rolls back any transaction a feature route leaves open. WS-CON routes must explicitly commit their own unit and need AUTH-owned project/service composition, not a copied dependency. |
| `backend/app/modules/authorization/policy.py::ADMIN_ROLE_PERMISSIONS` | Exact merged AdminRole permission candidates | Finance has delivery reconcile; Operator does not; Project Manager has award-read. D11 decides whether each candidate WS-CON difference changes AUTH or the active CON matrix. |
| sibling `workstream-rev-001/.../` clean branch head `a13bf35` | Parallel review plan's committed AUTH-08 dependency refresh | Counts, teardown/error/timestamp repairs and source SHAs now match AUTH-08, but publication evidence deliberately remains stale pending ART. REV-06/10 still use one-step current authorization rather than the registration -> CON -> REV hidden -> AUTH activation choreography; D12 owner custody is unresolved; REV-12A still says the CON handler claims the event. Treat it as non-consumable until those CON/AUTH ownership contracts are repaired, commit-bound reviewed and merged. |
| `backend/app/modules/artifacts/*` | Current artifact metadata/orchestration foundation | Target v2 is still being delivered by WS-ART; WS-CON cannot import provider internals. |
| `backend/app/interfaces/artifacts.py` | Current v1 raw provider port | Not a WS-CON dependency; it is being clean-cut to ADR 0013 v2. |
| `docs/spec_artifact_storage_service.md` | Canonical target artifact contract | Owns narrow product capability ports, recovery, verification, quotas, and provider policy. |
| `docs/spec_authorization_service.md` | Canonical target authorization contract | Preserves broad PermissionIds; ActionIds are separate. |
| `docs/architecture_data_model.md` | Existing contribution/payment target | Conflicts with supplied candidate and needs ADR-backed reconciliation. |
| `docs/operations_payment_reputation.md` | Existing manual payment/reputation workflow | Needs coordinated update only after architecture adoption. |
| `backend/alembic/versions/*` | Current schema through merged AUTH-08 migration `0022_bootstrap_admin_grants.py` | Every runtime chunk must refresh the next migration number from trusted `main`; no WS-CON contract pre-reserves `0023`. |

## Current tests

| Test path | What it covers | Gaps relevant to WS-CON |
|---|---|---|
| `backend/tests/test_tasks.py` | Task policy locks, assignment uniqueness, immutable Submission versions, checker admission, concurrency | No compensation freeze, review effects, contribution, or award tests. |
| `backend/tests/test_projects.py` | Guide/policy activation including `PaymentPolicy` | No CompensationPolicy lifecycle or Finance Authority behavior. |
| `backend/tests/test_authorization.py` | Closed catalogue plus AUTH-08 self/admin kernel/runtime | Self/admin allow/deny, scope/grant revalidation, complete resource digests, unknown/planned/unsupported denial, evidence failure and request-local state are covered. ProjectRoleGrants, service composition, WS-CON contexts/evaluators and prepared cross-domain mutation authorization remain AUTH-owned work. |
| `backend/tests/test_audit.py` | Typed append-only authority evidence | No contribution/compensation lifecycle audit contract. |
| `backend/tests/test_artifacts.py` | Current artifact port, local adapter, content/binding/receipt foundation | Target v2, S3/MinIO, typed contribution projection capability, and evidence reads are not merged. |
| `backend/tests/test_checkers.py` | Durable checker run and `allow_review` routing | Stops before Review persistence. |
| `backend/tests/test_alembic.py` | Migration upgrade/downgrade guards | No outbox, review, or WS-CON schema. |
| `backend/tests/test_api_contract_e2e.py` | Current API contract drill | No review/contribution/compensation routes or events. |

## Dependencies/integrations

- WS-AUTH: merged actor-self/admin kernel and AdminRoleGrants plus future
  ProjectRoleGrants/service actors, exact
  WS-CON ActionId/PermissionId/ActionOwner/audit registration, typed resource
  contexts, closed evaluators, matched authorities, prepared `T` protocol,
  service-capable composition, active availability and final bypass removal.
  WS-CON does not edit those owned surfaces.
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
| Merged AdminRole matrix conflicts with candidate WS-CON human matrix | Operator cannot currently satisfy candidate delivery reconciliation; award/audit candidate sets differ in the other direction. | D11 human decision, followed by only the required AUTH matrix/evaluator amendments or CON-01 active-matrix updates; no local role policy. |
| Registered-but-inexecutable AUTH action | Planned availability or a missing evaluator causes every WS-CON command to deny; a feature-local workaround would bypass central AUTH. | Separate AUTH registration and executable activation gates; startup parity rejects active-without-evaluator and CON never edits AUTH. |
| AUTH/product lock inversion | One-step authorization after product locks reverses canonical order; authorization before product locks can evaluate stale facts. | AUTH-owned prepared handle locks authority first and evaluates once against final locked product facts. |
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
| Approve two new service-only PermissionIds, `outbox.dispatch` and `compensation.fulfillment.report`? | Human outbox recovery/reconciliation authority must not execute async side effects; no existing permission safely names the external adapter callback entitlement. | Before CON-02B for dispatch and before CON-04A for callback binding identity. |
| Approve the AUTH-owned WS-CON registration/evaluator/activation work and D10 prepared mutation protocol? | Current AUTH-08 supports nine self/admin actions but no WS-CON action; CON cannot safely or physically activate its own actions. | Before any authorized CON service chunk. |
| Approve adding existing `compensation.delivery.reconcile` to the Operator role definition? | The reconciled candidate proposes reason-bound Operator delivery reconciliation, but merged AUTH-08 does not make that role a permission candidate. Rejecting the addition removes Operator from the active WS-CON action contract. | Before AUTH registration for CON-10B. |
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
