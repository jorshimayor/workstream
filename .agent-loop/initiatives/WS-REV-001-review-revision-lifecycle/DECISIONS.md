# Decisions: WS-REV-001 Review And Revision Lifecycle

## Decisions

### D1 - Existing Submission Is SubmissionVersion

`backend/app/modules/tasks/models.py::Submission` is the canonical versioned
submission identity. WS-REV extends its relationships and constraints and may
use `SubmissionVersion` as domain language, but it does not create a competing
table or duplicate version chain.

### D2 - Production Artifact Provider Follows Repository Lockdown

LocalStorage is development/test only. MinIO proves the S3-compatible protocol
in local/CI. AWS S3 is the only v0.1 production provider. Flow Node and R2 remain
deferred. The revised WS-REV source and dependent reference material must be
corrected before canonical adoption.

**Human confirmed 2026-07-15.**

### D3 - Authorization And Storage Are Consumed, Not Reimplemented

Review code consumes the merged centralized authorization kernel and typed
artifact capabilities. Test fakes may model these ports. Production no-op
authorization, direct grant reads, raw provider paths, concrete provider
imports, compatibility aliases, fallback constructors, and dual factory paths
are prohibited.

### D4 - Review Offer Is Server Selected

The reviewer current-work endpoint returns exactly one of active lease, next
offered review in a selected project, or none. It never returns full preferred
or open backlogs. Administrative inspection is a separate permission and API.

**Human confirmed 2026-07-15.**

### D5 - Controlled Revision Rebase Remains Required

ADR 0010 remains active. A human `needs_revision` decision creates the need for
revision preparation, not an implicit mutation of the prior submission.
There is one Project Guide context shared by task execution and human review;
WS-REV does not create a separate reviewer guide or reviewer-side rebase.

The task pipeline owns context resolution. TaskAssignment stores only `task_id`
and does not duplicate or reference a guide/context lock. Every immutable Submission version
stamps the exact Project Guide and policy context used for that attempt. After
`needs_revision`, preparation compares the prior Submission's locked guide with
the current approved Project Guide:

- same version: keep the existing context;
- any different current activated version, whether its activation sequence is
  greater or lower: prepare the next attempt against that authoritative version
  and record the transition direction;
- missing, incomplete, or unsafe current setup: block for Project Manager
  repair.

The Task Context API returns the prepared next-attempt context to the assigned
submitter before resubmission. Submission N+1 then stamps that context. The
prior task-attempt record and every prior Submission remain immutable. A
reviewer evaluates Submission N using the exact context stamped on Submission
N and performs no independent rebase. Both actors see the version transition
and change summary in history.

Preparation freezes the exact Project Guide/source snapshot and policy IDs,
versions, and hashes. Task Context reads that frozen preparation, not a moving
live guide pointer, and Submission N+1 must stamp it exactly. A later Project
Guide activation does not silently change an already returned revision context.
If the prepared context is revoked, corrupt, or otherwise invalid before
submission, creation fails with an explicit re-preparation requirement.

`RevisionContextPreparation` is an immutable task-owned record. Each revision
episode is rooted in the exact `needs_revision` Review for the prior Submission.
It contains that episode/Review identity, the complete next-attempt context,
context digest, outcome, change summary, prior Submission, target Submission
version, the reviewed Submission's immutable TaskAssignment, the currently
authorized target TaskAssignment, preparation sequence, preparing actor/process,
and audit link. Initial
`needs_revision` creates exactly one root before contributor access; manager
repair uses the dedicated authorized `review.revision_context.repair` command
to append a successor rather than editing it. Database constraints enforce
one root per episode, one child per preparation, same task/reviewed-assignment/
prior-Submission/episode across an edge, and a sequence increment of exactly one.
The target assignment normally remains the reviewed assignment. After AUTH-13
closes it for authority loss and a covered manager creates a replacement on the
durable `needs_revision` obligation, the same caller transaction appends one
successor bound to that replacement assignment and recomputes the current guide
classification. No edit or branch occurs, and the prior contributor loses
submission authority. Submission N+1 binds to that successor's target
TaskAssignment.
Thus the chain cannot branch and its only head is the row with no successor.
Task Context first selects that head and then validates it; blocked, revoked,
corrupt, or invalid head state never falls back to a predecessor. Initial work
comes from the task lock, revision work from the validated head, and submitted
history from each Submission lock. The revision submission acknowledges the
head ID/digest and commits Submission N+1 plus responses against it.

Existing Submission-to-WorkstreamTask equality FKs cannot represent a rebase.
They are replaced in chunk 09A with direct project/guide/policy/context
integrity constraints and a Submission-to-preparation binding. The original
WorkstreamTask locks and all earlier Submissions remain unchanged.

Guide ordering never compares version strings. Chunk 02 adds a per-project,
monotonic immutable `activation_sequence`. Existing active/superseded guides are
backfilled deterministically from effective time, creation time, and ID under
migration validation; drafts remain null until first activation. Active or
superseded state requires a non-null sequence, draft state requires null, and a
sequence is allocated exactly once while locking the project. Task, preparation,
and Submission contexts stamp guide ID, version, and activation sequence. Equal
identity/sequence keeps. Any different currently active guide identity/sequence
rebases, including an intentional backward rebase to an older activation
sequence. A mismatched identity/sequence pair or incomplete/unsafe context blocks
for manager repair.

**Human confirmed 2026-07-15:** one Project Guide, same-version keep,
any-different-active-version rebase including backward rebase, Task Context
visibility, and no reviewer-side rebase. The currently active Project Guide is
the authority for the next task attempt.

Normal blocked/revoked/invalid preparation is recoverable only by a reason-bound,
idempotent covered Project Manager repair command that acknowledges the current
head and appends one validated successor after project setup correction. It
cannot create a root or rewrite a prior preparation. A legacy `needs_revision`
task with no originating Review/root cannot be repaired this way; an Operator
may close it through the separately authorized, evidence-linked legacy closure
with terminal reason `legacy_revision_context_unrecoverable`. That closure
releases the assignment and creates no Review or WS-CON record.

### D6 - No Synthetic Human Reject

Checker outcomes, revision limits, deadlines, artifact failures, withdrawals,
and administrative closure do not create a `Review(decision=reject)`. A reject
Review exists only when an authorized reviewer commits that decision under an
active lease.

**Human-approved behavior:** a reached limit/deadline blocks further revision
preparation and `submission.create` with a stable policy error but leaves the
task `needs_revision` and assignment active. It never closes automatically. A
covered Project Manager may use the dedicated, idempotent, reason-bound
`review.revision_obligation.close` command in chunk 11; that closes the task with `revision_limit_reached` or
`revision_deadline_expired`, atomically sets `TaskAssignment.status=released`
and `released_at=database_now`, clears the task's active-assignee projection,
closes any queue entry as `admin_cancelled`, leaves the project grant unchanged,
prevents reclaim because the task is closed, and creates no Review,
contribution, award/payment instruction, or reputation
effect.

**Human confirmed 2026-07-15.**

The normal D6 command maps to existing `project.task.manage` and is not an
Operator reconciliation shortcut. Operator-only `review.queue.close` and
`review.revision_context.legacy_close` remain distinct recovery commands and
cannot close a healthy Review-rooted obligation merely because a limit or
deadline exists.

### D7 - Artifact Preflight Does Not Hold Review Locks Across Remote Calls

Review evidence availability is preflighted outside the queue-row transaction.
The claim transaction then stabilizes and revalidates canonical binding facts
and the preflight identity before creating a lease. A subsequent provider
outage is handled as an outage during an active lease and cannot create an
adverse review outcome.

### D8 - Public Decision Activation Waits For WS-CON

The internal review decision kernel may be implemented and tested behind an
unexposed composition boundary. Production routing for the decision endpoint
remains disabled until lease compensation-policy freeze and the WS-CON atomic
transaction participant are installed. No production no-op participant exists.

### D9 - Canonical Review Projection Is Post-Commit

The Review transaction appends one canonical shared-outbox projection event in
the same PostgreSQL commit. Shared-outbox delivery state and immutable ART
receipts are the only delivery records; WS-REV creates no parallel request or
status table. A worker stores the immutable projection after commit. Projection
failure changes only shared delivery state and never a Review.

### D10 - Frontend Follows Backend Proof

WS-REV-001 completes backend contracts, operational read models, and HTTP proof.
The React frontend begins only after these contracts and lifecycle guards are
stable, through a separately approved successor initiative.

### D11 - Coherent Public Cutover Is Atomic

Chunks 05-12A may implement and test internal services and routers, but the
production API composition exposes none of the reviewer/contributor lifecycle
mutations. Chunk 13 enables current-work, claim, release, decline, context,
decision, revision preparation/resubmission, chain reads, and authorized admin
operations together only when AUTH, ART, WS-CON, audit, outbox, recovery,
reconciliation, projection, workers, and live preflight are mandatory and
proven.

**Human confirmed 2026-07-15.**

### D12 - Shared Outbox And Lock Order Are Prerequisites

WS-REV uses the repository shared transactional outbox and the canonical
cross-domain lock order in `PLAN.md`. If either contract is unavailable at its
gate, the affected chunk stops for a separately reviewed foundation change;
review code does not create a private replacement or choose a local order.

### D13 - Historical Queue Admission Is Fail Closed

Queue schema migration does not create one entry for every historical
Submission. A later audited reconciliation admits only the latest finalized
version whose durable checker outcome is current `allow_review`, whose task is
compatibly `review_pending`, and whose required bindings are verified. Ambiguous
or legacy-incompatible rows remain unqueued for explicit operator remediation.

### D14 - Lease-Bounded Artifact Disclosure

Reviewer history and Review Context expose the authorized chain of Submission
versions, Reviews, findings, responses, resolutions, guide-version transitions,
and bounded audit facts. Artifact content is narrower: an active ReviewLease
authorizes only the exact current review packet anchored to its single
Submission version. That packet contains the Submission bindings, the durable
checker-run bindings from the exact immutable CheckerRun ID stored on its queue
admission, its finding-response evidence bindings,
and required locked-context/source-snapshot bindings. Membership is derived
from canonical relations, never caller-supplied IDs. It does not authorize
artifact bytes from a prior, later, sibling, cross-task, or cross-project
submission packet. An expired or consumed historical lease is not current read
authority.

Historical artifact projection is deliberately bounded to ArtifactBinding ID,
relation kind/purpose, media type, verification/availability state, and required
or optional classification. It excludes content bytes/excerpts, content digest,
provider URI/path/key/CID, signed capability, replica/receipt detail, service
scope, and credentials.

Chain metadata authorization is relationship-specific. It permits the exact
submitter whose immutable TaskAssignment/Submission appears in the chain, an
active reviewer leased to that chain, a prior reviewer who authored a Review in
that chain and still has a current project grant, or an explicitly authorized
Project Manager/Operator. It does not permit an arbitrary same-project reviewer.
Prior participation grants metadata history only; artifact content still
requires the current active lease for the exact Submission packet.

Reviewer finding evidence enters through typed ART intake under the active
lease and is attached to ReviewFinding by ArtifactBinding ID. Submitter response
evidence uses the same ART boundary under the assigned submitter's
`submission.create` scope. Human bearer tokens and raw provider locations never
cross into storage calls.

Evidence upload uses an ART-owned two-phase candidate/finalize capability.
Authority and scope are checked before candidate intake, then re-locked and
revalidated before a canonical ArtifactBinding/review relation is created.
Expiry, revocation, assignment loss, or preparation supersession during upload
may leave only an ART-owned unbound candidate governed by ART retention; it
creates no canonical binding/relation or lifecycle effect. Decision and
resubmission revalidate the relation again.

### D15 - Submission And Review Chains Drive Contributions

There is one immutable Review for each reviewed Submission version, with the
Review predecessor chain following the Submission predecessor chain. A separate
mutable "review version" entity is unnecessary. Both submitter and authorized
reviewer history views traverse all Submission/Review versions and bounded logs.

Every committed Review creates exactly one reviewer ContributionRecord. Only an
`accept` Review additionally creates exactly one submitter ContributionRecord
for the accepted Submission version. All records, review effects, audit, and
outbox state commit or roll back together through WS-CON.

The WS-CON input is derived exclusively from immutable lineage. The reviewer
record uses `Review.id`, `Review.review_lease_id`, the reviewed Submission row
and version, the Submission's immutable TaskAssignment binding,
`Review.reviewer_id`, the adopted immutable verified Submission packet digest
mapped to WS-CON `source_submission_artifact_digest`, and the ReviewLease's
frozen reviewer compensation policy version. The submitter record uses the same accepting Review and reviewed
Submission, null review lease, that Submission's TaskAssignment,
the canonical `Submission.contributor_id`, the same immutable Submission
packet digest, and the
TaskAssignment's frozen submitter compensation policy version. Project and task
come from the same constrained chain. Actor, assignment, lease, Review, and
Submission cross-links are database- and transaction-validated; no current task
projection or current project compensation policy may substitute for them.

ART, CON, and REV must adopt the exact underlying Submission digest field,
representation, derivation, and database binding before CON-03C or REV-10. The
current unconstrained caller-supplied `Submission.package_hash` is not accepted
as canonical evidence without that adoption.

### D16 - Canonical Actor IDs Are Product Lineage

Every human identity persisted by review/revision is the canonical active
`ActorProfile.id`: Submission contributor, TaskAssignment contributor,
ReviewQueueEntry preference, ReviewLease reviewer, Review reviewer, finding
author, and human administrative actor. External issuer/subject, email, legacy
typed-profile row IDs, token roles, and profile labels are evidence or
compatibility data, never actor IDs or authority.

Internal timer, reconciliation, projection, and dispatch work uses the exact
AUTH-registered service ActorProfile or system-principal representation required
by its ActionId. It cannot occupy a human reviewer/submitter FK or receive a
fabricated human grant. Authorization and audit retain the canonical actor
reference kind so UUID-shaped service identities are not inferred to be human.

### D17 - Compensation Freeze Is Independent Of Revision Context

Legacy `PaymentPolicy` is removed by WS-CON-05A/05B. It is not retained in the
final Project Guide, Submission, CheckerRun, Task Context, or
RevisionContextPreparation contract, and it is not replaced by the current
CompensationPolicyVersion.

Submitter compensation freezes once on the exact TaskAssignment; reviewer
compensation freezes separately on each ReviewLease. Forward or backward guide
rebase changes neither an existing assignment freeze nor an existing lease
freeze. A later lease may independently freeze the then-current reviewer terms.

### D18 - Authority-Loss Replacement Preserves Source And Changes Target

Normal `needs_revision` returns to the same contributor. The AUTH-13/14 final
contract nevertheless preserves a durable unassigned revision obligation when
that contributor loses authority and permits a covered manager to assign a
replacement. WS-REV adopts that dependency rather than stranding the task.

The episode permanently retains the reviewed Submission and its original
TaskAssignment as source lineage. Replacement assignment appends one immutable
preparation successor whose target assignment is the replacement and whose
guide context is freshly classified against the currently active Project Guide.
Submission N+1 binds to that target assignment, and WS-CON submitter attribution
and compensation derive from it. The old contributor cannot submit; no prior
Submission, assignment, Review, finding, or preparation is rewritten.

### D19 - Joint Release Control Is A Hidden Persisted Foundation

Safe activation/shutdown is product infrastructure, not proof-script state.
Chunk 12A owns one PostgreSQL-canonical `JointLifecycleReleaseControl`, the
Operator-only `review.lifecycle.activation.manage` action, advisory-lock-based
mutation fencing, typed internal fence ports, bounded drain observations, and
crash-resumable phase history. Every canonical phase change is a fresh
Operator-authorized adjacent transition; no worker replays the initiating human
or advances phase. It lands with no production lifecycle route.

Review, every task submission, review-queue admission, authority-loss
replacement, and compensation dispatch consume the same mandatory fence through
explicit composition. CON retains fulfillment/callback semantics and exposes
mandatory dispatch and callback hooks; it does not
create a second shutdown controller. REV-13 registers and exercises the merged
foundation, performs the ordered writer fence/migration/process cutover, and
prohibits downgrade after protected rows exist.
