# Discovery: WS-REV-001 Review And Revision Lifecycle

## Sources reviewed

- Revised Markdown source:
  `docs/reference_specs/WS-REV-001-review-lifecycle-specification.md`
- Revised 52-page PDF:
  `docs/reference_specs/WS-REV-001-review-lifecycle-specification.pdf`
- `WS-AUTH-001`, `WS-CON-001`, `WS-IMP-001`, architecture lockdown, ADRs,
  operations docs, current initiative plans, migrations, backend modules, and
  tests
- Merged WS-XINT-001 PR #139 at trusted main `5d353b6`, including its
  AUTH/REV, AUTH role/service, ART/REV, and REV/CON handoffs

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
   `needs_revision`. Canonical active docs use `accepted`, `rejected`, and
   `cancelled`; the archival REV source's `closed/review_rejected` wording is
   stale and must not introduce an undocumented `closed` status.
5. `TaskAssignment` supports one active assignment per task but has no blocked
   fields or completed-review effects.
6. `ReviewPolicy` and `RevisionPolicy` exist, but review preference, review
   lease, self-review, reject, and finding-evidence settings do not.
7. The current revision path creates a new `Submission` directly from
   `needs_revision`; it does not create structured finding responses or run the
   ADR 0010 context-preparation record.

## Authorization boundary

- The original discovery base was `f599551`, which merged AUTH-06. The
  2026-07-17 reconciliation rebased REV onto trusted main
  `5d353b6d3f8a36b9b9ffdc1959487a150ac25fd1`, which merges WS-XINT-001 PR #139
  and includes AUTH-08, ART-02A2, ADR 0015, and the four lifecycle handoffs.
- Authority audit and mutation idempotency foundations exist.
- The request-scoped deny-by-default kernel exists. Actor self-read/self-update
  and seven AUTH-08 administrative actions are active. Project grants, actor
  state/service actor administration, product cutovers, and conformance proof
  remain later WS-AUTH chunks.
- Product services still consume legacy `ActorContext`, role helpers, and
  `LegacyWorkflowEligibility`.
- Review/task/contribution lineage must store canonical human
  `ActorProfile.id`, not external subject, email, legacy typed-profile ID, or
  role labels. Review authority requires the independent exact-project
  `reviewer` grant; `submitter` and `adjudicator` grants do not substitute.
- Protected review jobs require AUTH-09E fixed-service admission through an
  exact active identity link/profile, immutable service identity, and static
  action row. A generic system-principal or fabricated human is not allowed.
- `review.queue.override` is present in the merged 74-PermissionId catalogue;
  its owning review actions remain planned/inactive. Artifact recovery already uses
  the registered `artifact.verification_job.retry` action and ART-owned
  `ArtifactOperatorRecoveryPort`; WS-REV must not add another recovery
  permission or implementation.

AUTH-07A/07B catalogue input is superseded as the live snapshot by merged
AUTH-08 PR #131 at trusted-main
`aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`, final branch head
`0832358a0262805f553d05b50b0d778e6e6ad995`. AUTH-08 retains exactly 57 closed
ActionIds, activates seven administrative actions alongside the two actor-self
actions, and leaves 48 planned. Canonical `submission.create` plus the original
19 review-owned actions all remain planned/inactive. AUTH-13/14
also establish the final `TaskAssignment.contributor_id` and
`Submission.contributor_id` names and authority-loss replacement-assignee
  behavior. The four later revision-obligation-close, repair, legacy-close, and
  joint-lifecycle-control ActionIds remain proposed AUTH-owned additions before
  their owning hidden-behavior chunks. The merged 57-action count is a historical
  AUTH-08 snapshot, not a future fixed total. WS-XINT-001 also proposes the
  separate ART service action `artifact.review_evidence.binding.create`; each
  later AUTH registration/activation contract must derive exact before/after
  counts from current trusted main and account for its delta independently.
  REV builds hidden behavior and typed facts; AUTH alone changes availability.

AUTH-08 resolves the three consumption blockers found during the AUTH-07B
dependency review: successful dependency teardown now rolls back any open
request-session transaction; evidence-write SQL errors become typed
`AuthorizationEvidenceUnavailable` failures mapped to retryable `503`; and
successful existing-actor GET/PATCH requests advance
`ActorProfile.last_seen_at` and `ActorIdentityLink.last_verified_at` in the
route-owned transaction. Its internal evidence records 275 focused behavior
tests, 90.17 percent branch-aware focused coverage, and 17 isolated Alembic
tests. Final PR checks passed Backend, Agent Gates, and CodeRabbit. REV runtime
chunks must preserve these merged invariants and still wait for the later AUTH
  definition-of-done gate owned by each consumer, AUTH-09E for protected service
  callers, and the matching AUTH activation checkpoint. Reads consume
  request-scoped `AuthorizationService.require`; mutations consume the future
  authority-first prepared protocol and exactly one final evaluation without
  importing grant persistence into the review module.

## Artifact boundary

- `ArtifactContent`, immutable `ArtifactBinding`, `ArtifactReplica`, operation
  receipts, upload staging, a provider-neutral `ArtifactStore`, and a
  LocalStorage adapter exist.
- Current ArtifactStore v1 operations cover store, recover committed store,
  open, stat, verify, retain, release, and receipt lookup. They are discovery
  state only: WS-XINT-001 requires ART v2 as the sole future provider boundary,
  and REV must not consume the v1 provider contract.
- Merged ART-02A2 PR #129 at trusted main
  `9a04434e2f23c5dec8939dadb943bba4d85110c0`, final head
  `32aab89262a3944f305e9e5dc4c65a2d31e2e144`, adds an inactive
  `PreparedArtifact`/`CommittedArtifactSource` boundary, bounded private
  `ArtifactScratchManager`, deterministic cleanup mechanics, and shared bounded
  file locking. Active ArtifactStore v1, provider selection, schema, routes, and
  lifecycle behavior remain unchanged.
- ART scratch is bounded private ephemeral processing state, not artifact
  storage or a product reference. REV never imports ART preparation/scratch
  types, persists their paths or ledger identities, or creates a second scratch
  manager. Future ART-owned intake capabilities may use that foundation behind
  their port.
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
- WS-XINT-001 assigns immutable bytes, commitments, bindings, verification,
  recovery, and candidates to ART while REV owns `ReviewPacketManifest`,
  `ReviewEvidenceArtifact`, packet membership, and lifecycle semantics. Exact
  packet read uses `review.context.read`, never generic `artifact.retrieve` or
  Operator-only `artifact.binding.read`.
- Evidence finalization requires the separate service action
  `artifact.review_evidence.binding.create`, mapped to
  `artifact.binding.create`, restricted to `workstream.artifact.binding`, backed
  by a separately approved ART review-evidence capability, and activated only by
  AUTH after its hidden behavior merges.

## Contribution boundary

- No contribution policy, award, fulfillment outbox, or callback
  models are implemented in this snapshot.
- Revised WS-REV requires one reviewer contribution for every Review and a
  submitter contribution only on `accept`.
- WS-CON requires the reviewer `ContributionPolicyVersion` to be frozen on the
  `ReviewLease` and its flush-only transaction participant to commit or roll
  back with the Review, task/assignment effects, awards, audit, and outbox.
- Review core may be built behind an unexposed composition boundary, but the
  public decision endpoint cannot be enabled with a no-op contribution path.
- Core contribution creation receives locked Review/Submission/assignment/
  policy facts from REV, copies the stabilized versioned Submission
  `artifact_hash` into `ContributionRecord.artifact_hash`, and performs no ART
  call, provider I/O, or mandatory contribution-evidence artifact write.

## WS-XINT-001 reconciliation findings

1. Current `ActionOwner.REV_*` values are stale activation-custody encodings,
   not feature ownership. AUTH must transfer every approved review action to an
   exact AUTH activation custodian.
2. Delivery order is AUTH registration, hidden dependency and REV behavior,
   AUTH evaluator integration/activation, then REV joint product release.
3. Reviewer authority is one exact active independent `reviewer` grant;
   reviewer revocation changes only review-owned state.
4. Preference expiry, lease expiry, review reconciliation, artifact-reference
   reconciliation, and projection rebuild need distinct fixed service identities
   and exact AUTH-09E static rows.
5. Review evidence uses ART candidate/finalize and its exact binding service
   action. Final decisions use stabilized binding facts without provider I/O.
6. Contribution creation is a caller-owned single transaction using a CON
   flush-only participant, frozen `ContributionPolicyVersion` rows, and no core
   ART dependency or mandatory evidence projection.

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
- Exact later merged ART v2, S3, admission, verification/publication, read,
  binding, intake, retention, recovery, service-scope, checker, and projection
  interfaces. ART-02A2 does not provide those product capabilities.
- Exact WS-CON policy-freeze and transaction-participant interfaces.
- Whether a shared outbox foundation lands before the first review consumer.
- Production timer schedule and operational alert thresholds.
- The user decision for revision limits/deadlines without synthetic reject.
