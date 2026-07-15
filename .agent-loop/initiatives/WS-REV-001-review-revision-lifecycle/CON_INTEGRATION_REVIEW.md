# WS-CON Integration Review For WS-REV-001

## Scope And State

Reconciled review of `/home/abiorh/flow/workstream-con-001` on 2026-07-15,
pinned to rebased committed planning head `c965f9b`. WS-REV edited no sibling
file. Content-level security/auth, product/QA, and architecture/docs review was
recorded on predecessor planning commit `42cf11f`; exact-head publication review
remains pending. The sibling's later uncommitted fence-handoff edits were also
read and align with the dispatch boundary below, but do not yet specify the
callback fence and are not a merged dependency. This review does not activate
`WS-CON-001-01`.

## Ownership Boundary

WS-REV owns queue, ReviewLease schema, Review and revision state, exact
Submission-to-TaskAssignment lineage, decision orchestration, final transaction
commit, and the sole joint production activation in REV-13.

WS-CON owns compensation policy/version/binding, immutable contribution and
award records, delivery/receipt/status, the database-local decision
participant, contribution-evidence projection, product/operations reads, and
its exact hidden-readiness manifest. ART owns artifact admission, provider I/O,
verification, bindings, receipts, retention, and recovery. AUTH owns canonical
actors, permissions/actions, grants, service assignments, and decisions.

REV-12A owns one shared hidden `JointLifecycleReleaseControl` and typed mutation
fence. CON-08A/08B/11 must leave exact mandatory fence hooks in fulfillment
dispatch and authenticated callback handling and name both in the readiness
manifest; CON does not create a competing shutdown state machine.
CON-10B/11 also owns a same-session
`FulfillmentLifecycleDrainObservationPort` over its fulfillment state and the
shared-outbox capability; REV consumes only that typed port and never imports a
CON or outbox repository.

## Adapter And Participant Chain

`ContributionRecord` does not consume an external provider adapter. During the
authorized review decision, REV calls the typed
`ContributionCompensationDecisionParticipant` with the caller-owned
`AsyncSession`, exact immutable Review/ReviewLease/Submission/TaskAssignment
facts, AuthorizationDecision reference, and request/correlation IDs. The
participant validates and flushes ContributionRecord, award, projection, audit,
and outbox rows and never commits or performs network I/O.

After commit, two separate adapters/capabilities may be consumed:

- the contribution-evidence worker consumes the ART-owned typed contribution
  evidence write capability. It must not import raw `ArtifactStore` or a Local,
  MinIO, or S3 adapter;
- the fulfillment handler consumes
  `CompensationDeliveryAdapter`, constructed only by the shared ADR-0014
  `ExternalServiceAdapterFactory[CompensationDeliveryAdapter]` at the explicit
  composition root. The planned deterministic adapter is conformance-only; no
  production payment provider, balance, ledger, or settlement lives here.

The generic outbox dispatcher invokes those post-commit handlers under its
fixed AUTH service actor and `outbox.dispatch` authority. Human retry or
reconciliation permission cannot execute adapter side effects.

## Exact Lineage Contract

Both reviewer and accept-only submitter records derive from immutable rows:

- Submission version identity is the existing `Submission` row plus its
  explicit version, not a second SubmissionVersion entity;
- `source_task_assignment_id = Submission.task_assignment_id`;
- reviewer actor is `Review.reviewer_id`; submitter actor is the final AUTH-14
  `Submission.contributor_id`; both it and AUTH-13
  `TaskAssignment.contributor_id` are canonical human `ActorProfile.id` values;
- reviewer lease is `Review.review_lease_id`; submitter lease is null;
- reviewer compensation comes from the exact ReviewLease freeze; submitter
  compensation comes from the exact TaskAssignment freeze;
- project/task come from the database-constrained chain; and
- `source_submission_artifact_digest` comes from one ART/CON/REV-adopted,
  immutable verified Submission packet digest.

The current unconstrained caller-supplied `Submission.package_hash` cannot be
silently renamed into that last field. CON-01/03C, ART's capability owner, and
REV-10 must close the field name, representation, derivation, and database
binding before implementation.

## Required Interleaving

```text
REV-02 exact Submission/TaskAssignment lineage
  -> CON-05A/05B PaymentPolicy consumer/schema removal

CON-03B compensation policy persistence
  -> REV-03 ReviewLease FK

CON-02A outbox persistence + CON-02C lifecycle audit
  -> REV-04 immutable review chain

CON-06 lease freeze capability
  -> REV-06 claim integration

REV-09B stable review/revision chain + CON-03C exact lineage schema
  -> CON-07 decision participant
  -> REV-10 atomic integration

CON-11 exact readiness manifest + REV-12
  -> REV-12A hidden joint release-control/fence integration
  -> REV-13 sole joint activation and live drill
```

CON-02B dispatcher activation additionally waits for AUTH's fixed dispatcher
actor/action assignment. CON-09A waits for the ART-owned contribution-evidence
capability.

## Reconciliation Result And Remaining Joint Gates

Present in rebased CON planning commit `c965f9b`:

- executable 05A semantic removal and 05B physical removal contracts replace
  the stale advisory/single-05 direction;
- source provenance, working-Markdown hash, and internal review evidence are
  truthful;
- the existing versioned `Submission` identity and `submission_id` are used;
- shared-outbox `outbox.dispatch` and bound
  `compensation.fulfillment.report` are explicit service-only AUTH dependencies;
- ART typed capabilities, verification-job retry, provider roles, and ADR-0014
  adapter composition are aligned; and
- REV-13 joint contribution/compensation activation scope is represented in
  both plans.

Still blocking the owning runtime chunks:

1. CON-01/03C, REV-09A/09B/10, and the ART capability owner must freeze one
   immutable reviewed-submission packet digest field, representation,
   derivation, and database binding. No caller `package_hash` substitution is
   allowed.
2. Contribution evidence must derive guide/policy facts from the exact context
   stamped on the reviewed Submission after forward or backward rebase, not a
   later current Project/Task context.
3. Immutable outbox/contribution/award/delivery migrations must refuse unsafe
   downgrade once canonical rows exist; generic upgrade/downgrade test wording
   is not sufficient.
4. Before each dependent chunk starts, reread the relevant contract from its
   merged trusted-main SHA. Planning commit `c965f9b` is evidence, not a runtime
   dependency by worktree path.
5. CON-05A must add merged REV-02 exact Submission/TaskAssignment lineage as an
   explicit gate before publication or activation. REV records the ordering,
   The required gate appears only in the sibling's later uncommitted planning
   delta, so `c965f9b` does not yet enforce it in its own chunk contract.
6. CON-08A/08B/11 must adopt shared lifecycle-fence hooks and prove dispatch
   loses cleanly to admission fencing before adapter I/O while authenticated
   callbacks hold the shared transaction fence, remain available through
   delivery drain, and cannot race disablement.
7. CON-10B/11 must expose and manifest the same-session typed
   `FulfillmentLifecycleDrainObservationPort` with pending/claimed/retryable
   event, in-flight dispatch, and nonterminal delivery/callback counts. It is
   read-only, never commits/calls a provider, and uses the shared-outbox port
   rather than exposing CON/outbox persistence to REV.

## Revision And Compensation Rule

The currently active Project Guide is authoritative for the next attempt even
when that is a backward rebase. That rebase changes task-execution context only.
It never mutates TaskAssignment submitter compensation or an existing
ReviewLease reviewer compensation freeze. A later ReviewLease independently
freezes the reviewer terms current for that new lease.
