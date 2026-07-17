# WS-CON Integration Review For WS-REV-001

## Authority And State

Reconciled on 2026-07-17 against merged WS-XINT-001 PR #139 at trusted main
`5d353b6d3f8a36b9b9ffdc1959487a150ac25fd1`, especially
`REV_CON_HANDOFF.md`. Sibling WS-CON worktree content remains discovery evidence
until its owning contracts merge; it cannot override the merged handoff or act
as a runtime dependency.

## Ownership Boundary

REV owns queue, ReviewLease, ReviewPacketManifest, ReviewEvidenceArtifact,
Review/finding/revision state, decision orchestration, task effects, the caller
transaction, and joint product-surface release. CON owns ContributionPolicy,
immutable ContributionPolicyVersion and rules, ContributionRecord, awards,
fulfillment, shared-outbox transitions, CON audit/projections, and every
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
-> REV locks idempotency, lifecycle fence, queue, lease, task, assignment,
   versioned Submission, Review predecessor, findings and stabilized facts
-> REV recomposes final typed review-decision context
-> AUTH evaluates once and stages decision evidence
-> REV stages Review/findings/resolutions, consumes lease/queue, applies task effects
-> REV calls the CON flush-only participant
-> CON creates reviewer completed_review ContributionRecord
-> on accept only, CON creates submitter accepted_submission ContributionRecord
-> CON evaluates each frozen ContributionPolicyVersion rule
-> explicit unpaid creates no award; payable creates immutable money and/or
   project_points CompensationAward rows
-> CON stages audit and shared-outbox rows
-> route commits once
```

CON receives the originating AuthorizationDecision reference and locked facts.
It never evaluates `review.decision`, imports REV/AUTH persistence, commits, or
performs network/provider I/O. CON failure rolls back the complete Review
decision. There is no no-op participant or post-commit repair for canonical
contribution creation.

No canonical Review-committing service may land before the CON participant.
REV-08 therefore freezes schemas, pure validation, task-effect inputs, and the
participant request only. After stable REV-09B lineage exists, CON may implement
the participant; REV-10 creates the first hidden canonical decision transaction.

## Exact Lineage Contract

The repository's existing `Submission` row is the version identity; no separate
SubmissionVersion table is added. Both contributions receive:

- `Review.id`, the exact reviewed `Submission.id` and version, project, and task;
- `Submission.task_assignment_id` and canonical actor IDs from the constrained
  lineage;
- the reviewer record's exact `ReviewLease.id` and frozen reviewer
  `ContributionPolicyVersion`;
- the submitter record's null lease and exact TaskAssignment-frozen submitter
  `ContributionPolicyVersion`;
- the server-derived stabilized `Submission.artifact_hash`, copied to
  `ContributionRecord.artifact_hash`; and
- the originating AuthorizationDecision, request, and correlation references.

The XINT `SubmissionVersion.artifact_hash` wording means the field on the
existing versioned Submission row. It does not authorize a duplicate entity.
Current caller-supplied `Submission.package_hash` is not silently renamed or
trusted; the ART submission/checker cutover must add the exact verified field and
database binding before REV-10. CON does not call ART to load or rederive it.

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
  -> REV-04 immutable review chain

CON ReviewLease freeze capability + AUTH prepared mutation protocol
  -> REV-06 claim integration

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

- Every valid Review creates one reviewer contribution; only `accept` also
  creates one submitter contribution.
- Frozen ContributionPolicyVersion rules, not guide context or an adapter,
  decide unpaid/payable eligibility.
- Core creation makes no ART call and uses no external adapter.
- Money and project-points adapters fulfill already-created awards; they never
  decide eligibility.
- Shared outbox claim ownership remains with the dispatcher.
- REV owns no CON public route, policy, award, fulfillment, or projection state.
- All runtime gates must be reread from their exact merged trusted-main SHAs.
