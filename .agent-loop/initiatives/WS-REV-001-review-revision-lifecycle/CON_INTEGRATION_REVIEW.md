# WS-CON Integration Review For WS-REV-001

## Scope And State

Reconciled review of `/home/abiorh/flow/workstream-con-001` on 2026-07-15,
pinned to CON planning commit `42cf11f`. WS-REV edited no sibling file. The
content received security/auth, product/QA, and architecture/docs delta review
before that commit; CON's exact-commit publication review remains pending. The
plan also depends on human approval and merged AUTH/ART/REV contracts; this
review does not activate `WS-CON-001-01`.

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
  -> REV-13 sole joint activation and live drill
```

CON-02B dispatcher activation additionally waits for AUTH's fixed dispatcher
actor/action assignment. CON-09A waits for the ART-owned contribution-evidence
capability.

## Reconciliation Result And Remaining Joint Gates

Closed by CON commit `42cf11f`:

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
   merged trusted-main SHA. Planning commit `42cf11f` is evidence, not a runtime
   dependency by worktree path.
5. CON-05A must add merged REV-02 exact Submission/TaskAssignment lineage as an
   explicit gate before publication or activation. REV records the ordering,
   but CON commit `42cf11f` does not yet enforce it in its own chunk contract.

## Revision And Compensation Rule

The currently active Project Guide is authoritative for the next attempt even
when that is a backward rebase. That rebase changes task-execution context only.
It never mutates TaskAssignment submitter compensation or an existing
ReviewLease reviewer compensation freeze. A later ReviewLease independently
freezes the reviewer terms current for that new lease.
