# Plan: WS-REV-001 Review And Revision Lifecycle

## Approach

Build the lifecycle as one review-owned backend module integrated with existing
tasks, submissions, checkers, audit, authorization, artifact, worker, and API
composition boundaries. Land persistence before behavior, keep every public
mutation hidden until its invariants and cross-domain participants exist, and
use PostgreSQL constraints as final race guards.

## Dependency gates

### Authorization gate

Runtime work starts only after the WS-AUTH definition of done is merged and
proven. Merged AUTH-07B fixes the public kernel shape but is not yet safe for
REV consumption. Before any runtime chunk, AUTH must also prove that:

- the reusable authorization dependency never commits a feature-owned open
  transaction during generic successful teardown; every read or mutation owner
  commits its own business-plus-decision unit explicitly;
- SQL failures while staging authorization evidence map centrally to the stable
  retryable service-unavailable response and leave no business mutation or
  partial decision evidence; and
- AUTH documents and restores its canonical `ActorProfile.last_seen_at` and
  `ActorIdentityLink.last_verified_at` semantics for successful existing-actor
  GET/PATCH access, with API regression proof. REV does not prescribe AUTH's
  sequencing or lifecycle-denial timestamp policy.

After those gates, WS-REV consumes:

- canonical actors: every human lifecycle FK stores the active canonical
  `ActorProfile.id`; external issuer/subject, email, legacy profile row IDs,
  token roles, and contributor profile labels never substitute for actor
  identity. Internal jobs use their registered service `ActorProfile.id` or the
  exact AUTH-defined system-principal form for the action, never a fabricated
  human actor;
- project contributor grants;
- 24 planned action dependencies: merged AUTH-07B retains canonical
  `submission.create` plus the original 19 review-owned actions; four additive
  AUTH-owned registrations remain required by revision closure/recovery and
  joint release control;
- `review.revision_context.repair` maps to existing PermissionId
  `project.task.manage`, a covered Project Manager candidate, and an exact typed
  task/assignment/prior-Submission/episode/head resource with transaction
  revalidation;
- `review.revision_context.legacy_close` maps to existing PermissionId
  `operations.reconcile.run`, an Operator AdminRoleGrant candidate, and an exact
  typed unresolved reconciliation-finding/project/task/no-Review/no-root
  resource with transaction revalidation;
- `review.revision_obligation.close` maps to existing PermissionId
  `project.task.manage`, a covered Project Manager candidate, and the exact
  task/assignment/needs-revision Review/current preparation head/observed
  limit-or-deadline resource with transaction revalidation;
- `review.lifecycle.activation.manage` maps to existing PermissionId
  `operations.reconcile.run`, an Operator AdminRoleGrant candidate, and the
  exact singleton control/current phase/target phase/manifest digest resource
  with transaction revalidation;
- registered permissions, with `review.queue.override` as the only additive
  PermissionId;
- canonical resource contexts and project mismatch handling;
- a request-scoped, transaction-aware
  `AuthorizationService.require(action_id, resource_context)` whose service is
  bound to the current AuthorizationContext and caller-owned AsyncSession,
  returns/stages one bounded decision, never commits, and never accepts a raw
  PermissionId, candidate grant, or guard from feature code;
- immutable authorization decisions and audit links;
- revocation invalidation used to recover active review leases.

REV owns its typed ResourceContext composers and lifecycle guards. It imports
the public AUTH service and `ActionId` types only; it never imports AUTH
repositories/models, queries grants, or reconstructs permission unions.
The four additive ActionIds and their closed mappings are registered by WS-AUTH,
not by review code. The three revision closure/repair actions must merge before
chunk 11; lifecycle activation must merge before 12A. They add no PermissionId.
AUTH-08 is not merged, so its runtime and exact evidence remain an unresolved
gate. Its amended contract projects 57 actions after merge: 9 active and 48
planned. The AUTH-owned REV addition must then migrate all four actions across
typed catalogue, owner table, and PostgreSQL action-to-permission audit parity
in lockstep from 57 to exactly 61, producing 9 active and 52 planned. Direct-SQL, allowed
and denied audit, missing/extra parity, upgrade, and unsafe-downgrade tests are a
hard gate; adding enum values alone is insufficient.

The currently merged pre-AUTH-08 split remains 50 actions: 2 active actor-self
actions and 48 planned actions. Neither the projected AUTH-08 additions nor the
four REV additions are treated as merged. Every one of the 24 REV action
dependencies remains inactive until its owning REV chunk activates it, and the
AUTH definition-of-done gate is unchanged.

### Artifact gate

Artifact-sensitive work starts only after the required WS-ART contracts are
merged and proven. WS-REV consumes:

- immutable binding/content identity and project/task ownership resolution;
- typed, authorized complete retrieval and metadata reads;
- fresh availability/integrity observation with classified failures;
- generic intake for finding and finding-response evidence;
- retention and recovery operations;
- deterministic projection storage;
- LocalStorage and MinIO conformance with AWS S3 as production provider.

### Contribution gate

WS-CON remains a planning-only dependency. Rebased committed planning head
`c965f9b` contains the reconciled plan and ADR-0014 foundation; its content-level
review lineage originates at `42cf11f`, but exact-head publication review is
pending and none of its runtime interfaces are merged. The sibling's later
uncommitted fence-handoff edits are discovery evidence only. Neither worktree
state is an executable dependency.

The cross-initiative sequence is explicit:

- `WS-REV-001-02` first establishes immutable
  `Submission.task_assignment_id` attribution and guide activation sequence;
- WS-CON's approved `05A/05B` replacement chunks then freeze submitter
  compensation on `TaskAssignment` and remove legacy `PaymentPolicy` fields and
  consumers before `WS-REV-001-09A`;
- merged WS-CON compensation-policy persistence precedes `WS-REV-001-03`, so
  ReviewLease FKs target a real owner;
- merged shared outbox persistence and caller-transaction lifecycle audit
  participants precede `WS-REV-001-04`;
- the WS-CON ReviewLease freeze capability precedes `WS-REV-001-06`;
- the exact atomic contribution/award participant precedes
  `WS-REV-001-10`; and
- the exact WS-CON readiness manifest, mandatory fulfillment dispatch/callback
  fence hooks, and same-session fulfillment/outbox drain-observation port
  precede hidden joint release-control integration in `WS-REV-001-12A`; and
- the merged 12A controller and fences precede the sole joint activation in
  `WS-REV-001-13`.

Compensation context is independent of guide/review execution context. A
forward or backward Project Guide rebase never changes the submitter's frozen
TaskAssignment compensation version. Each newly created ReviewLease freezes its
own current reviewer compensation version. Review services do not implement
policy, awards, fulfillment, evidence projection, or provider delivery.

Before WS-CON contribution persistence or REV-10 integration, ART, CON, and REV
must freeze one exact immutable Submission packet-digest contract: canonical
field name, strict representation and derivation, binding, and database
validation. A caller-supplied unconstrained `Submission.package_hash` cannot be
treated as contribution evidence merely by renaming it.

### Transactional outbox gate

The shared PostgreSQL transactional-outbox contract, ownership, and lock-order
position must be frozen before immutable review-chain persistence starts. The
preferred implementation is the merged shared foundation used by WS-CON. If it
does not exist at activation, WS-REV-001-04 is blocked until a separately
approved foundation chunk lands; WS-REV must not improvise a private competing
outbox.

### Shared audit gate

WS-REV appends to the existing shared `AuditEvent` ledger through its
caller-transaction-aware audit participant, preserving request/correlation and
AuthorizationDecision links. If bounded lifecycle event inputs are not merged,
an audit-owner foundation chunk lands before chunk 04. A `ReviewAuditEvent`
table, review-private audit repository, or commit-owning audit writer is
prohibited.

## Data model alignment

### Existing records extended

- `Submission` remains the versioned submission record and receives structured
  finding-response relationships where needed. PostgreSQL enforces immutable
  rows, same-task immediate predecessor lineage, version N-1 linkage, and the
  canonical submitter Actor mapping. It also stores the exact immutable
  TaskAssignment that produced it, constrained to the same task and contributor, so
  history and WS-CON never infer attribution from a later active assignment.
  Its submitter and assignment contributor are canonical human
  `ActorProfile.id` values. The adopted ART/CON digest contract supplies the
  immutable reviewed-packet digest; no contribution participant trusts an
  unverified caller string.
- `WorkstreamTask` receives accepted/closed state support and terminal reason.
- `TaskAssignment` receives completed/blocked compatibility fields and a reject
  Review reference.
- `ReviewPolicy` receives locked preference, lease, capacity, self-review,
  reject, and finding-evidence settings.
- Existing locked non-compensation task/submission policy references remain the
  immutable execution-context anchor.

### New review-owned records

- `ReviewQueueEntry`
- `ReviewLease`
- `Review`
- `ReviewFinding`
- `SubmissionFindingResponse`
- `FindingResolution`
- evidence relation rows for review findings and finding responses
- review-owned `ReviewDecisionRequest` idempotency aggregate bound to actor,
  operation, lease, submission, and canonical payload (the existing
  AUTH-owned authority idempotency record is not reused)
- `ReviewAdministrativeCommandRequest`, a separate bounded administrative
  idempotency aggregate for repair/closure resources and payloads; it does not
  widen or overload lease/submission-bound `ReviewDecisionRequest`
- `ReviewReconciliationFinding` with immutable canonical defect/evidence facts,
  a set-once resolution pointer, and one-to-one immutable
  `ReviewReconciliationResolution` for domain inconsistency evidence
- one canonical shared outbox event for review snapshot projection; delivery
  attempts/status remain owned by the shared outbox and immutable artifact
  receipts remain owned by ART, with no review-private delivery table

All mutable-state compatibility, predecessor, uniqueness, and partial-active
invariants are enforced in PostgreSQL as well as in services.

`ReviewLease.reviewer_id`, `Review.reviewer_id`, preferred-reviewer references,
and every human administrative actor reference use canonical `ActorProfile.id`
with database-enforced human actor kind and status checks at mutation time.
Schema chunks use a composite immutable actor-kind key plus local
`actor_kind='human'` check, or an equivalently reviewed deferred constraint
trigger; a plain actor-profile FK is insufficient. Audit attribution additionally
preserves the AUTH-defined actor-reference kind so service/system work is not
misrepresented as a human reviewer.

## Application flow

```text
durable checker allow_review
  -> verify required retained binding facts
  -> create at most one open/preferred ReviewQueueEntry for an admitted version
     with task review_pending and the exact admitting CheckerRun ID
  -> server selects current lease or one next offer
  -> artifact availability preflight
  -> transaction-aware authorization and atomic ReviewLease claim
  -> authorized Review Context shows the bounded immutable chain but retrieves
     artifact content only for the currently leased Submission version
  -> finding evidence is ingested and verified before decision
  -> decision transaction follows the canonical lock order across current
     authority, idempotency, task, assignment, submission, queue, lease,
     immutable predecessors, binding facts, and WS-CON rows
  -> Review/findings/resolutions + task effects + WS-CON effects + audit +
     projection request commit together
  -> projection and notifications execute from the canonical shared outbox
     event after commit
```

## Application dependency direction

`reviews` owns review orchestration. Task-owned `TaskReviewEffectsParticipant`
and `TaskSubmissionParticipant` operations accept the caller's `AsyncSession`,
flush without commit, and reuse `TaskRepository`, the existing `Submission`,
version allocation, locked-policy checks, lifecycle guards, audit ordering, and
post-commit dispatch contract. The public task adapter owns commit and dispatch;
review code never imports `TaskRepository` or clones task rules.

Checker owns a typed review-context reader. CheckerService accepts a typed
review-admission participant implemented by reviews; the durable
`_apply_pre_review_gate_result` transaction invokes it directly and never polls
or recomputes `allow_review`. One explicit `app.composition.review_lifecycle`
constructor assembly supplies these ports to checker routers, task services,
checker workers, and review routers. It is not a service locator and has no
fallback constructor. Models may hold database relationships without creating
repository/service import cycles. Import-boundary tests enforce the direction.

AUTH, ART, CON, shared audit, and shared outbox are likewise injected ports.

## Joint release control

Public lifecycle activation and shutdown use one hidden PostgreSQL-canonical
`JointLifecycleReleaseControl`, not shell-script or process-local state. Chunk
12A persists compare-and-set phase history, exposes a typed mandatory mutation
fence, and installs that fence through explicit composition across review
mutations, every task submission, review-queue admission, authority-loss
replacement, and the exact CON-owned fulfillment dispatch and callback hooks.
It adds no public production route.

The fence uses matching PostgreSQL advisory locks so a phase transition waits
for admitted mutation transactions and then applies the persisted command-class
matrix. A dedicated `revision_cutover_fenced` phase keeps initial submission and
checker admission open while blocking legacy revision/replacement writers;
shutdown phases separately fence all new admission, drain review commands and
leases, drain fulfillment dispatch, preserve authenticated callbacks, and then
disable. `disabled(N) -> pre_activation(N+1)` is the only reactivation edge and
requires a newly reviewed manifest. Every edge and observation is a fresh
Operator-authorized lifecycle command; lease draining reuses fresh
`review.lease.force_release` commands rather than widening lifecycle authority.
No worker replays human authority or advances phase. Timeout leaves phase
unchanged for forward retry and no edge attempts schema downgrade. Chunk 13 alone registers the Operator surface,
performs the ordered cutover, and proves crash resume and coherent reactivation.

## Revision flow

```text
needs_revision Review
  -> task remains assigned and enters needs_revision
  -> compare prior locked Project Guide with the current approved Project Guide
  -> same keeps; any different active guide rebases; inconsistent/unsafe blocks
  -> contributor sees prior findings and context delta
  -> same submission.create action creates next existing Submission version
  -> one SubmissionFindingResponse per unresolved blocking finding
  -> response evidence uses verified ArtifactBinding IDs
  -> existing finalization/checker spine runs
  -> allow_review creates queue entry preferred to prior reviewer
  -> preference expiry/decline/invalidation opens entry without resetting age
  -> later Review records one FindingResolution per required prior finding
```

If the current preparation becomes blocked, revoked, corrupt, or invalid after
project correction, the covered Project Manager invokes the authorized
idempotent repair command with reason and current head ID/digest. The command
locks and revalidates current authority, project context, task/assignment, prior
Submission, episode, and head, then appends exactly one successor. Concurrent
repair or submission resolves to one successor/replay or a stable stale-head
conflict. It never fabricates an episode root.

Legacy `needs_revision` rows without an originating Review/root remain readable
but cannot advance. Reconciliation reports them; an Operator-only,
evidence-linked closure releases the assignment and closes any queue with stable
terminal reason `legacy_revision_context_unrecoverable`, producing audit/outbox
evidence but no Review, contribution, award, payment, or reputation effect.

The task pipeline owns the only guide binding. TaskAssignment stores only
`task_id`; it carries no duplicate guide/context field. Each Submission stamps
its resolved context immutably. During `needs_revision`, the Task Context API resolves
the prepared next-attempt context so the submitter sees the new approved guide
before resubmission. The reviewer never rebases: it consumes the guide and
task-execution policy context stamped on the single Submission covered by its
active lease.
Preparation freezes exact guide/source-snapshot and task-execution policy IDs,
versions, and hashes; Task Context and Submission N+1 must use that same record.
It never freezes or rebases compensation policy. Later guide
activation does not silently drift it, while invalidation requires explicit
re-preparation.

Activation sequence records chronology but does not overrule the active guide.
When the current active guide differs, preparation records `rebased` plus
`forward` or `backward` transition direction and freezes that active guide's
complete context. A lower sequence is therefore a deliberate backward rebase,
not a manager-repair condition.

The immutable `RevisionContextPreparation` stores the complete next-attempt
context and digest. Each episode is rooted in the exact `needs_revision` Review;
manager repair appends a non-branching successor with an incremented preparation
sequence. One root per episode, one child per preparation, and same-lineage edge
constraints leave one head. Task Context selects that head before validation and
reads without mutation; an invalid or blocked head never falls back. Revision
submission acknowledges the head ID/digest. Chunk 09A replaces the current
Submission-to-task and CheckerRun-to-task context-equality FKs with direct
project/context integrity and exact Submission/preparation/checker-run bindings,
preserving original task locks and prior Submission rows.

Normal revision returns to the same assigned contributor. AUTH-13 authority-loss
reconciliation is the exceptional transfer path: it closes the old assignment
without changing history and leaves a durable unassigned obligation. A covered
manager's replacement assignment transaction invokes the review-owned
preparation-transfer participant, which appends one successor bound to the new
target TaskAssignment and the then-authoritative Project Guide context. The
episode keeps the reviewed Submission and its original assignment as immutable
source lineage; Submission N+1 and submitter compensation use the replacement
target assignment. Partial transfer rolls back assignment and preparation
together.

History access and artifact-content access are separate. Authorized history may
show every Submission/Review version, findings, responses, resolutions,
guide-version transitions, and bounded audit facts. ART retrieval is limited to
the canonical current review packet anchored to the leased Submission:
submission, the queue's exact admitting checker-run, current finding-response evidence, and
required locked-context bindings. No prior-version packet bytes are disclosed
merely because they appear in the chain.

Historical packet projection is limited to binding ID, relation purpose/kind,
media type, verification/availability state, and required/optional class. It
contains no digest, provider locator/key/CID, signed capability, replica/receipt
detail, service scope, content excerpt, or credential.

`review.chain.read` is relationship-scoped, not project-reviewer-wide. A current
submitter may read a chain containing a Submission bound to their exact
TaskAssignment; an active reviewer may read the chain anchored to their exact
lease; a prior participating reviewer may read metadata only when they authored
a Review in that chain and still hold the current project grant; and an
Operator/Project Manager needs the explicit inspection permission. The server
resolves these relationships from canonical rows. Arbitrary same-project,
cross-project, revoked, or caller-supplied chain IDs confer no access. Only the
active exact lease can authorize current-packet content.

Evidence intake is two phase across PostgreSQL and ART. The service first
authorizes and derives an exact scope, then ingests an idempotent ART-owned
unbound candidate. In a database transaction it re-locks and revalidates actor,
grant, lease or assignment, Submission/finding, and preparation before creating
the canonical binding/relation. Failure after upload can leave only an ART-owned
orphan candidate under ART retention/cleanup; it creates no Workstream binding,
review/submission relation, or lifecycle effect. Decision and submission
transactions validate the canonical binding and authority again. If merged ART
does not expose this candidate/finalize contract, chunk 07 stops for an ART-owned
foundation change rather than adding review-private storage state.

## Concurrency design

- Preflight remote artifact availability before acquiring review row locks.
- Inside claims and decisions, use database time and targeted `FOR UPDATE` or
  atomic conditional updates over canonical rows.
- Every mutating operation uses this cross-domain lock order: AUTH-owned current
  actor/identity/grant rows in the AUTH-defined internal order; idempotency row;
  the `JointLifecycleReleaseControl` advisory lock and persisted phase row;
  `Project`; active/candidate `ProjectGuide`; `GuideSourceSnapshot`;
  submission-artifact, effective, pre-submit-checker, post-submit-checker,
  review, and revision policy rows in that order; the active compensation
  selector, `CompensationPolicyVersion`, and referenced
  `CompensationAdapterBinding` rows; `WorkstreamTask`;
  `TaskAssignment`; `Submission`; `CheckerRun`; `RevisionContextPreparation`;
  `ReviewQueueEntry`;
  `ReviewLease`; `ReviewReconciliationFinding`; prior Review/finding rows;
  ArtifactBinding/Replica facts; then ContributionRecord, CompensationAward,
  delivery, receipt, and projection rows in the WS-CON-defined internal order.
  Multiple same-type rows are
  locked by ascending primary key. Audit and outbox rows are append-only writes
  after state locks. Operations skip absent resource classes but never reorder
  those they share.
- Partial unique indexes enforce one active lease per queue entry and reviewer.
- Stabilize verified binding/replica facts inside the decision transaction; do
  not call a remote provider while holding decision locks.
- Map expected constraint races to stable 409 or replay results.
- Timer workers use deterministic batches with `SKIP LOCKED`; user claims do
  not.
- Lazy request-time recovery shares the same transition service as sweeps.
- Retry only database-classified serialization/deadlock failures, with a
  bounded attempt count. Real-Postgres tests use independent sessions and
  barriers to run both conflicting permutations and inject rollback failures
  after each cross-domain participant.
- Project-guide publication adopts the same Project-to-policy lock prefix.
  Concurrent publication versus `needs_revision` preparation must freeze one
  complete old or new context, never a mixed context, and must not deadlock.
- Checker retry/supersession and queue admission both use the
  Submission-to-CheckerRun-to-ReviewQueueEntry portion of this order, so neither
  can validate a run and then anchor a different generation.
- Decision idempotency reuses `app.core.hashing.canonical_json_hash`, shared
  request/correlation identifiers, and the proven reserve/lock/complete
  transaction shape while retaining a review-owned operation/response matrix.
  No second JSON canonicalizer or generic idempotency framework is introduced.

## API design

Use existing `/api/v1` and structured error conventions.

- Reviewer current work: active lease, one next offer, or none.
- Administrative queue inspection: complete authorized project view.
- Claim, release, decline preference, decision, context read, and chain read are
  separate capabilities.
- Override, force release, and administrative closure require dedicated
  permissions, reasons, and audit. Artifact verification recovery consumes the
  existing `artifact.verification_job.retry` action through the ART-owned
  `ArtifactOperatorRecoveryPort`; WS-REV adds no recovery permission or
  execution path.
- Request JSON never supplies authoritative project relationships, provider
  paths, CIDs, URLs, or service scopes.
- No reviewer, contributor, compensation, or lifecycle-control router is
  included in production `/api/v1` composition before chunk 13. Chunks 05-12A
  prove internal service, recovery, fence, and operational contracts while
  OpenAPI tests prove those mutations remain absent.

## Dependency ownership rule

WS-REV contracts import only merged AUTH, ART, CON, audit, and outbox ports. They
do not list dependency-module wildcards as editable scope. At activation, each
chunk replaces any composition locator with an exact existing file path. A
missing typed capability becomes a separately approved dependency-owner chunk;
it is not added opportunistically to a WS-REV PR.

The pre-WS-CON task/project schema may still contain legacy `PaymentPolicy`
locks when chunk 02 lands. Those are transitional migration inputs only.
WS-CON `05A/05B` owns their consumer cutover and schema removal; WS-REV-09A and
every public/final context operate only after that removal and must not replace
them with a moving current `CompensationPolicyVersion`.

## Background processing

- Preference-expiry sweep
- Lease-expiry sweep
- Grant-revocation lease recovery
- Queue/lease/review orphan reconciliation
- Review snapshot projection
- Artifact binding/retention/projection reconciliation
- Event-driven notifications

Correctness does not depend only on scheduled delivery. Jobs reload current
PostgreSQL state and are idempotent under duplicate execution.
All review jobs reuse `run_async_task`, fresh worker engine/session disposal,
stable Celery task IDs, and `sync_task_settings`. The shared outbox dispatcher
is the sole claimant/retry/dead-letter owner; reviews registers only a typed,
deterministic projection handler and records ART receipts.

## Documentation alignment

Before runtime code, adopt the reconciled active contract while preserving all
archival inputs and update precedence material. Before final proof, align
glossary, architecture lockdown, reviewer
workflow, revision replay, first-user flows, roles/permissions, templates, and
operator docs with blocking/advisory findings, server-selected offers,
contribution boundaries, controlled rebase, and deferred reputation.

## Alternatives rejected

- **Create a new SubmissionVersion table:** duplicates the existing versioned
  Submission identity and violates WS-IMP integration rules.
- **Implement temporary local role checks:** creates an authorization bypass
  that becomes difficult to remove and violates WS-AUTH precedence.
- **Let reviewers choose from the full queue:** leaks operational data and
  enables cherry-picking against the revised contract.
- **Call storage inside the decision transaction:** risks long locks and
  ambiguous cross-system atomicity.
- **Emit only ContributionRecordRequested:** conflicts with the revised
  WS-REV/WS-CON atomic integration contract.
- **Treat revision limits or artifact errors as reject:** fabricates human
  judgment and contaminates contributor history.
- **Build frontend concurrently:** violates backend-first sequencing before
  lifecycle guards and contracts are stable.

## Verification strategy

Every chunk runs focused tests and lint. Every runtime chunk also runs a fresh
isolated real-PostgreSQL coverage invocation; a stale `.coverage` file is never
accepted as evidence. The runner requires a disposable administrative database
URL through `WORKSTREAM_TEST_ADMIN_DATABASE_URL`, creates independent databases
for concurrent workers, and fails rather than silently falling back. Artifact
chunks use provider-neutral fakes plus LocalStorage and MinIO conformance as
applicable. The common runtime evidence is:

```text
(metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78))
cd backend && coverage report --include='app/modules/reviews/*,app/workers/reviews.py' --precision=2 --fail-under=90
cd backend && ruff check app tests scripts
python3 scripts/check_internal_review_evidence.py
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
```

Each contract's focused test command is diagnostic evidence in addition to,
not instead of, this common runtime evidence. New/materially changed review
code remains at or above 90 percent and repository-wide coverage remains at or
above 78 percent on the same fresh run.

The final live proof covers first submit, needs revision, controlled
continuation, preferred return, preference expiry/takeover, accept, reject,
lease expiry, revocation during lease, evidence attachment, provider outage,
integrity failure, recovery, contribution atomicity, and projection retry.
The versioned conformance matrix maps specification sections 25.1-25.9 to the
owning chunk, executable tests, live drill cases, and retained evidence.

## Delivery rule

Only one WS-REV chunk may be active. A chunk begins from current trusted main,
refreshes dependency discovery, runs required internal review, receives external
and human approval, merges, records automated memory, and stops. Cross-initiative
gates do not authorize starting the next WS-REV chunk automatically.
