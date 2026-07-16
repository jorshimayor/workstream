# Intent: WS-REV-001 Review And Revision Lifecycle

## Human goal

Implement the complete Workstream v0.1 human review and revision lifecycle from
durable checker admission through immutable review decisions, revision replay,
terminal reject, recovery, artifact-backed judgment, contribution integration,
and HTTP-visible proof.

## Why this matters

The current backend proves intake through `review_pending`, but it does not yet
provide an authorized human judgment layer. Workstream cannot certify completed
work until it can route review-ready submissions, prevent self-review and lease
hoarding, preserve every review attempt and finding, replay prior feedback on a
revision, and distinguish product judgment from checker or infrastructure
outcomes.

## Success state

- An admitted submission creates exactly one review queue entry.
- A current, explicitly granted reviewer sees only their active lease or one
  next offered item and can claim at most one review globally.
- Claims, releases, preference changes, decisions, overrides, and recovery use
  current centralized authorization and canonical resource scope.
- Every human identity in task/submission/review lineage is the canonical
  active `ActorProfile.id`; service/system actors remain explicitly typed and
  cannot occupy contributor or reviewer identity.
- Reviewers see full bounded Submission/Review history, but artifact content is
  restricted to the canonical current review packet anchored to the exact
  Submission covered by their active lease.
- `accept`, `needs_revision`, and `reject` are immutable, idempotent, atomic
  decisions with the specified task and assignment effects.
- Revisions respond to every unresolved blocking finding, preserve both
  predecessor chains, prepare the latest approved Project Guide context when it
  changed, and return to the prior reviewer before falling back to open FIFO.
- Artifact outage or integrity failure blocks judgment without creating an
  adverse contributor outcome.
- Every committed review joins the `WS-CON-001` contribution and compensation
  transaction before any public review lifecycle route is enabled.
- Guide rebase never rebases compensation: TaskAssignment freezes submitter
  terms and each ReviewLease independently freezes reviewer terms.
- Timers, revocation recovery, reconciliation, projection, audit,
  observability, and privacy-safe live drills prove normal and failure paths.

## Boundaries

- Preserve the proven project guide, task, submission, and checker spine through
  `review_pending`.
- Extend the existing versioned `Submission`; do not create a duplicate
  `SubmissionVersion` business identity.
- Maintain one Project Guide context through the task pipeline. TaskAssignment
  binds to the WorkstreamTask that owns the initial context lock rather than
  duplicating guide fields; reviewers consume the context stamped on the leased
  Submission and do not maintain a separate review guide.
- Consume `WS-AUTH-001` through its authorization kernel and decisions; do not
  query grant tables or reconstruct permissions in review code.
- Consume typed, Workstream-owned artifact capabilities over the canonical
  `ArtifactStore`; do not import provider adapters into review services.
- Keep PostgreSQL canonical for review truth. Storage projection is derived,
  asynchronous, and retryable.
- Keep review code free of contribution, compensation, fulfillment, and
  reputation policy. `WS-CON-001` owns the transaction participant.
- Keep frontend delivery separate until backend contracts and lifecycle guards
  are stable and proven.

## Non-goals

- Self-review, reviewer bidding, multiple concurrent review leases, automated
  reviewer grants, reputation scoring, adjudication, or reject reassignment.
- Flow Node or R2 provider implementation in v0.1.
- Workstream-owned authentication, login, sessions, or credentials.
- A second artifact store or review-authoritative search index.
- Payment-provider execution, points balances, or settlement.
- A frontend implementation inside the backend-first WS-REV chunks.

## Human decisions confirmed

1. Approved provider direction: LocalStorage for development, MinIO for local/CI
   conformance, AWS S3 for production; Flow Node remains deferred.
2. ADR 0010 is retained with the clarified one-Project-Guide task pipeline,
   same-version keep, rebase to any different currently active version including
   backward rebase, Task Context visibility, and no reviewer-side guide.
3. D6's recommendation is approved: limit/deadline blocks further submission while
   leaving `needs_revision` active, with only the covered Project Manager's
   explicit reason-bound revision-obligation closure and never a fabricated
   human `reject` Review.
4. The revised reviewer `current` endpoint controls over
   the older WS-IMP full-backlog reviewer response.
5. Production enables the coherent lifecycle route set only after the
   repaired and reviewed `WS-CON-001` plan, exact lineage/digest contract,
   atomic participant, lease freeze, recovery, reconciliation, projection
   operations, and WS-CON-11 joint-readiness manifest exist.

Items 3-5 and the proposed chunk sequence were approved by the human on
2026-07-15 for planning publication. This approval does not activate a successor
implementation chunk before the planning PR merges and its separately declared
start gate is satisfied.

## Proof strategy

Use PostgreSQL constraint and concurrency tests, focused module coverage at or
above 90 percent, repository-wide coverage at or above the current 78 percent
floor, API contract tests, LocalStorage and MinIO artifact conformance, timer
and reconciliation tests, and privacy-safe HTTP-visible drills covering
revision, takeover, reject, expiry, revocation, evidence attachment, outage,
and recovery.
