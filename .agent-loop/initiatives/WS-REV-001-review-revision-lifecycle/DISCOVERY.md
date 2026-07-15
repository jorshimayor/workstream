# Discovery: WS-REV-001 Review And Revision Lifecycle

## Sources reviewed

- Revised Markdown source:
  `docs/reference_specs/WS-REV-001-review-lifecycle-specification.md`
- Revised 52-page PDF:
  `docs/reference_specs/WS-REV-001-review-lifecycle-specification.pdf`
- `WS-AUTH-001`, `WS-CON-001`, `WS-IMP-001`, architecture lockdown, ADRs,
  operations docs, current initiative plans, migrations, backend modules, and
  tests

The current revised Markdown contains 2,396 lines and 12,570 words. Its SHA-256 is
`fffadc271c267801250b044edc570e515a250eff48afdc64f9c1f8753e6ab058`.
The revised PDF SHA-256 is
`8c053bc752a7b0c64e04b3eda1873bb5dbc02bbdfef84bd17d07cbbf01bce2fd`.
The Markdown has 149 headings. PDF text extraction covers the base lifecycle,
evidence, projection, and error contract but does not contain Markdown section
4.6's closed action/permission table. The current Markdown is therefore newer
than its 52-page PDF companion; neither is treated as a generated twin. Both are
the authoritative supplied pair. The temporary `(2)` filenames were a local
duplicate-name accident; their contents were restored to the canonical paths,
and the duplicate paths were removed. Chunk 01 records the one-sided section
before producing the reconciled active contract.

## Current proven behavior

1. Project guide setup, policy derivation and approval, task policy locking,
   task assignment, versioned submissions, submission finalization, durable
   post-submit checker execution, and transition to `review_pending` exist.
2. `backend/app/modules/tasks/models.py::Submission` is already the immutable
   versioned submission identity. It has `version`, `supersedes_submission_id`,
   task ownership, locked policy fields, evidence, finalization time, and a
   unique `(task_id, version)` constraint.
3. `backend/app/modules/checkers/service.py::_apply_pre_review_gate_result`
   moves an allowed checker result to `review_pending`; it creates no review
   queue entry.
4. `backend/app/modules/tasks/lifecycle.py` has statuses through
   `needs_revision`, but no `accepted` or terminal `closed` transition and no
   task `closed_reason`.
5. `TaskAssignment` supports one active assignment per task but has no blocked
   fields or completed-review effects.
6. `ReviewPolicy` and `RevisionPolicy` exist, but review preference, review
   lease, self-review, reject, and finding-evidence settings do not.
7. The current revision path creates a new `Submission` directly from
   `needs_revision`; it does not create structured finding responses or run the
   ADR 0010 context-preparation record.

## Authorization boundary

- The original discovery base was `f599551`, which merged AUTH-06. Local pull
  merge `e59e2bb` now contains trusted main `90eca12`, including merged AUTH-07B
  and ADR-0014's shared external-adapter foundation.
- Authority audit and mutation idempotency foundations exist.
- The request-scoped deny-by-default kernel exists and only actor self-read and
  self-update are active. Admin/project grants, actor state/service actor
  administration, product cutovers, and conformance proof remain later WS-AUTH
  chunks.
- Product services still consume legacy `ActorContext`, role helpers, and
  `LegacyWorkflowEligibility`.
- Review/task/contribution lineage must store canonical human
  `ActorProfile.id`, not external subject, email, legacy typed-profile ID, or
  role labels. Internal jobs remain explicitly typed service/system actors.
- `review.queue.override` is present in the merged 74-PermissionId catalogue;
  its owning review actions remain planned/inactive. Artifact recovery already uses
  the registered `artifact.verification_job.retry` action and ART-owned
  `ArtifactOperatorRecoveryPort`; WS-REV must not add another recovery
  permission or implementation.

AUTH-07A catalogue input at `3ab25cf3b1e99336c635a318101375bb4bebdf91`
is superseded as the live snapshot by merged AUTH-07B `90eca12f6398f2ef168e634244d912765572c3e5`.
AUTH-07B retains exactly 50 closed ActionIds, activates only two actor-self
actions, and leaves 48 planned. Canonical `submission.create` plus the original
19 review-owned actions all remain planned/inactive. AUTH-13/14
also establish the final `TaskAssignment.contributor_id` and
`Submission.contributor_id` names and authority-loss replacement-assignee
behavior. The four later revision-obligation-close, repair, legacy-close, and
joint-lifecycle-activation ActionIds remain explicit AUTH-owned additions before
their owning chunks. AUTH-08 is not merged: its amended contract projects a
57-action baseline with 9 active and 48 planned. After that exact merge, REV's
four additions must expand typed catalogue/owner and PostgreSQL audit parity
from 57 to exactly 61, with 9 active and 52 planned. Enum-only registration is
not runtime authority, and all 24 REV dependencies remain inactive until their
owning REV chunks activate them.

The merged kernel has three consumption blockers found during the REV dependency
review: successful dependency teardown commits any open request-session
transaction; evidence-write SQL errors can escape as raw 500 responses; and
existing actor self requests no longer advance `ActorProfile.last_seen_at` and
`ActorIdentityLink.last_verified_at`. Review implementation must therefore wait
for WS-AUTH definition of done plus AUTH-owned repair proof, then consume
`AuthorizationService.require(action_id, resource_context)`, canonical resource
contexts, decision links, revocation invalidation, and provisioned system actors
without importing grant persistence into the review module.

## Artifact boundary

- `ArtifactContent`, immutable `ArtifactBinding`, `ArtifactReplica`, operation
  receipts, upload staging, a provider-neutral `ArtifactStore`, and a
  LocalStorage adapter exist.
- Current artifact operations cover store, recover committed store, open, stat,
  verify, retain, release, and receipt lookup. The current application service
  is ingest-focused; public product cutovers and review-specific typed reads do
  not exist.
- The active WS-ART plan changes the production choice to AWS S3 behind
  `S3CompatibleArtifactStore`, proves it with MinIO, removes the old
  `flow_node` configuration value, and leaves review packet/evidence integration
  to WS-REV.
- The revised WS-REV source still says production Flow Node in sections 6.10,
  25.8, and 27. That conflicts with AGENTS.md, repository engineering policy,
  architecture lockdown, and the merged WS-ART amendment.
- Review services should consume typed binding metadata, complete verified
  retrieval, finding-evidence intake, retention, and projection capabilities
  supplied through composition-root registration. Tests may use fakes; no
  production bypass or provider import is acceptable.

## Contribution boundary

- No contribution, compensation policy, award, fulfillment outbox, or callback
  models are implemented in this snapshot.
- Revised WS-REV requires one reviewer contribution for every Review and a
  submitter contribution only on `accept`.
- WS-CON requires the reviewer compensation policy to be frozen on the
  `ReviewLease` and its transaction participant to commit or roll back with the
  Review, task/assignment effects, awards, audit, and outbox.
- Review core may be built behind an unexposed composition boundary, but the
  public decision endpoint cannot be enabled with a no-op contribution path.

## Existing infrastructure

- FastAPI routes are registered below `/api/v1`; revised `/v1` examples must be
  adapted to this convention.
- Celery exists for project setup and checker gates. There is no timer schedule,
  review worker, generic transactional outbox worker, or review reconciliation
  worker yet.
- The structured API error envelope and request/correlation IDs exist.
- `AuditEvent` is shared and append-only for authority evidence; lifecycle
  audit input is still legacy-shaped and needs a bounded WS-REV event contract.
- There are 20 migrations through canonical actor profile migration `0020` at
  this snapshot. Parallel initiatives mean WS-REV contracts must allocate the
  next migration number only at activation time.
- The backend has 609 discovered test functions across 18 test modules.

## Specification and documentation conflicts

1. Revised WS-REV names Flow Node as the production artifact adapter; locked
   repository policy names AWS S3 and MinIO.
2. Revised WS-REV does not describe ADR 0010 context rebase. The omission does
   not repeal the accepted ADR.
3. WS-IMP still exposes reviewer preferred/open backlog arrays, while revised
   WS-REV exposes only active lease, one next offer, or none.
4. WS-IMP and current runtime configuration still contain Flow Node production
   wording superseded by the WS-ART amendment.
5. `operations_reviewer_workflow.md` uses high/medium/low findings, requires a
   finding on reject, and says accept directly creates payment/reputation
   records. Revised WS-REV uses blocking/advisory, makes reject findings
   optional, delegates contributions/compensation to WS-CON, and defers
   reputation.
6. `operations_revision_replay.md` and `architecture_lockdown.md` use legacy
   contributor and reviewer closure tokens that do not map directly to
   `SubmissionFindingResponse` plus `FindingResolution`.
7. The revised PDF says “Approved design baseline for implementation” while
   Markdown says “Locked for implementation handoff.” This prevents treating
   the supplied PDF as a reproducible semantic twin; the active reconciled
   Markdown contract must declare precedence explicitly.

## Baseline verification observation

- `uv run pytest -q` did not reach repository collection because an ambient
  user-level Web3 pytest plugin failed during plugin loading. Repository
  verification must use the locked dev environment and isolated runner.
- `uv run --extra dev python -m pytest -q` completed with `586 passed`, `11
  failed`, and `403 errors` in 227.35 seconds. Database-backed setup failed
  because `WORKSTREAM_TEST_DATABASE_URL` was not configured; this was an
  environment failure, not valid green baseline evidence.
- Runtime chunks therefore require `scripts/run_isolated_tests.py` with a
  disposable `WORKSTREAM_TEST_ADMIN_DATABASE_URL`, fresh coverage, and no
  ambient plugin dependence.

## Conventions to preserve

- Async SQLAlchemy repositories under the owning module.
- Service-owned domain rules and thin FastAPI routers.
- PostgreSQL database time, row locks, partial unique indexes, and expected-race
  error mapping.
- Shared structured error envelopes and request/correlation context.
- Celery jobs carry stable IDs and reload PostgreSQL state.
- New or materially changed subsystem coverage at or above 90 percent and the
  repository floor at or above 78 percent.
- One approved chunk per PR, required internal reviewer tracks, explicit human
  merge approval, one merge intent, automated post-merge memory, and stop.

## Unknowns to resolve at each activation gate

- Exact merged AUTH service, resource-context, invalidation, and system-actor
  interfaces.
- Exact merged ART read, binding, retention, recovery, service-scope, and
  projection interfaces.
- Exact WS-CON policy-freeze and transaction-participant interfaces.
- Whether a shared outbox foundation lands before the first review consumer.
- Production timer schedule and operational alert thresholds.
- The user decision for revision limits/deadlines without synthetic reject.
