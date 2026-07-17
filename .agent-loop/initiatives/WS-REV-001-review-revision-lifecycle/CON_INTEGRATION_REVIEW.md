# WS-CON Integration Review For WS-REV-001

## Authority And State

Reconciled on 2026-07-17 against merged WS-XINT-001 PR #139 at trusted main
`5d353b6d3f8a36b9b9ffdc1959487a150ac25fd1`, especially
`REV_CON_HANDOFF.md`, plus the later explicit human amendment establishing
`FinalAcceptance` and REV-owned audit/outbox staging. Sibling WS-CON worktree
content remains discovery evidence until its owning contracts merge; it cannot
act as a runtime dependency.

## Ownership Boundary

REV owns queue, ReviewLease, ReviewPacketManifest, ReviewEvidenceArtifact,
Review/finding/revision state, FinalAcceptance, decision orchestration, task
effects, shared audit/outbox staging, the caller transaction, and joint
product-surface release. CON owns ContributionPolicy,
immutable ContributionPolicyVersion and rules, ContributionRecord, awards,
fulfillment, CON audit/projections, and every
separately exposed CON surface. AUTH owns review authorization and action
activation. ART owns bytes, bindings, verification, recovery, and typed artifact
capabilities.

REV-12A owns one shared hidden `JointLifecycleReleaseControl` and typed mutation
fence. CON supplies mandatory fulfillment dispatch/callback fence hooks and one
same-session drain-observation port; REV never imports CON or outbox repositories.
The shared dispatcher owns claim/retry/dead-letter state. A CON handler receives
an already-claimed command and may stage its delivery attempt, but never claims
or transitions the outbox event itself.

## Atomic Decision Contract

```text
AUTH prepares review.decision and locks reviewer authority
-> REV locks idempotency, queue, lease, task, assignment,
   versioned Submission, Review predecessor, findings and stabilized facts
-> REV recomposes final typed review-decision context
-> AUTH evaluates once and stages decision evidence
-> REV appends immutable Review/findings/resolutions and consumes lease/queue
-> when decision=accept, REV appends immutable FinalAcceptance linked to Review
-> REV applies the decision-specific task and assignment effects
-> REV calls the CON flush-only participant
-> CON creates reviewer completed_review ContributionRecord
-> CON evaluates the ReviewLease-frozen reviewer ContributionPolicyVersion rule
-> when FinalAcceptance is present, CON creates submitter accepted_submission
   from it and evaluates the TaskAssignment-frozen submitter rule
-> explicit unpaid creates no award; payable creates immutable money and/or
   project_points CompensationAward rows
-> CON flushes contribution/award rows and returns typed audit/outbox inputs
-> REV stages shared audit/outbox rows
-> route commits once
```

This is the hidden pre-12A order and has no public or background-command entry
point. REV-12A inserts the mandatory lifecycle fence between idempotency and
queue before REV-13 releases the decision surface; the remaining order and CON
participant contract do not change.

CON receives the originating AuthorizationDecision reference and locked facts,
including FinalAcceptance for accept and null otherwise. It never infers
submitter acceptance from `Review.decision`, evaluates that action, imports
REV/AUTH persistence, commits, or performs network/provider I/O. CON or later
REV failure rolls back the complete Review decision. There is no no-op
participant or post-commit repair for canonical contribution creation.

No canonical Review-committing service may land before the CON participant.
REV-08 therefore freezes schemas, pure validation, task-effect inputs, and the
participant request only. After stable REV-09B lineage exists, CON may implement
the participant; REV-10 creates the first hidden canonical decision transaction.

## Exact Lineage Contract

The repository's existing `Submission` row is the version identity; no separate
SubmissionVersion table is added. FinalAcceptance is a REV-owned immutable
internal fact with:

- canonical `submission_id`, implementing the handoff's conceptual
  `submission_version_id`;
- exact project, task, source Review, accepted submitter, acceptance time, and
  recording reviewer lineage;
- `policy_context_ref` constrained to the immutable ReviewPolicy row matching
  the reviewed Submission context; and
- unique task, source Review, and Submission constraints.

There is no public/manual FinalAcceptance creation API or independent AUTH
action. Only the already-authorized accept decision creates it.

Both contribution shapes receive common project/task/Submission/digest lineage,
but their canonical sources are distinct:

- reviewer `completed_review` receives `Review.id` and `ReviewLease.id` directly;
- submitter `accepted_submission` receives `FinalAcceptance.id` and the exact
  `TaskAssignment.id`, with direct Review/ReviewLease source fields null;
- each receives canonical actor IDs and its exact frozen
  `ContributionPolicyVersion`;
- each receives the server-derived stabilized `Submission.artifact_hash`, copied
  to `ContributionRecord.artifact_hash`; and
- each retains originating AuthorizationDecision, request, and correlation
  references.

The XINT `SubmissionVersion.artifact_hash` wording means the field on the
existing versioned Submission row. It does not authorize a duplicate entity.
Current caller-supplied `Submission.package_hash` is not silently renamed or
trusted; the ART submission/checker cutover must add the exact verified field and
database binding before REV-10. CON does not call ART to load or rederive it.

PostgreSQL enforces one `completed_review` per Review and one
`accepted_submission` per FinalAcceptance, plus mutually exclusive reviewer and
submitter source shapes.

## Independent CON Authorization

Derived ContributionRecord and CompensationAward inserts inside
`review.decision` do not create `contribution.materialize` or
`compensation.award.materialize` actions. CON requires its own AUTH actions only
for independently invoked reads, policy/binding administration, callbacks,
outbox dispatch, reconciliation, projections, and audit. REV-13 does not edit or
register CON routers; it consumes the exact merged CON readiness manifest and
verifies that CON-owned surfaces are already composed by their owner.

## Optional Evidence Projection

A deterministic contribution-evidence document may be added later as an
asynchronous projection with its own ART capability, AUTH action, status, and
failure lifecycle. It is not created or required by the core Review transaction,
does not gate CON readiness or REV product release, and cannot change Review,
ContributionRecord, CompensationAward, fulfillment receipt, or status truth when
storage is unavailable.

## Required Interleaving

```text
REV-02 exact Submission/TaskAssignment lineage
  -> CON contribution-policy and legacy-policy cutover

CON ContributionPolicyVersion persistence
  -> REV-03 ReviewLease FK

CON shared outbox + lifecycle-audit participants
  -> REV-04 immutable Review and FinalAcceptance persistence

CON ReviewLease freeze capability + AUTH prepared mutation protocol
  -> REV-06 claim integration

REV-04 stable FinalAcceptance schema
  -> CON exact FinalAcceptance-sourced contribution schema

REV-09B stable review/revision lineage + CON exact lineage schema
  -> CON flush-only decision participant
  -> REV-10 first canonical Review-committing transaction

CON core hidden-readiness manifest + REV-12
  -> REV-12A hidden joint release control
  -> AUTH action activation after hidden behavior
  -> REV-13 joint product release
```

Optional contribution-evidence projection work is not on this critical path.

## Reconciliation Result

- Every valid Review creates one reviewer contribution. When its decision is
  `accept`, REV also creates FinalAcceptance and CON creates exactly one
  submitter contribution from that fact.
- Frozen ContributionPolicyVersion rules, not guide context or an adapter,
  decide unpaid/payable eligibility.
- Core creation makes no ART call and uses no external adapter.
- Money and project-points adapters fulfill already-created awards; they never
  decide eligibility.
- Shared outbox claim ownership remains with the dispatcher.
- REV stages shared audit/outbox rows after the CON participant and owns the
  single commit; CON returns typed staging inputs and never commits.
- REV owns no CON public route, policy, award, fulfillment, or projection state.
- All runtime gates must be reread from their exact merged trusted-main SHAs.
