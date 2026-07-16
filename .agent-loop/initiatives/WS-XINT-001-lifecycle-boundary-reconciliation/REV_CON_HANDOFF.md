# REV/AUTH <-> CON Handoff

## Boundary

REV owns the Review decision and review/task effects. CON owns
ContributionRecord, compensation freezes, awards, delivery, shared outbox
transitions, and CON audit/projections. AUTH owns authorization for review and
all separately exposed CON actions.

Core ContributionRecord creation performs no synchronous ART capability call,
provider I/O, contribution-evidence artifact write, or ART authorization action.
It copies the already-stabilized `SubmissionVersion.artifact_hash` supplied by
REV into the existing `ContributionRecord.artifact_hash` lineage field. CON does
not load or rederive that value from ART.

## Preconditions

- reviewer and submitter use canonical human ActorProfile IDs;
- TaskAssignment freezes submitter compensation policy;
- ReviewLease freezes reviewer compensation policy;
- Submission has immutable assignment/version lineage and a stabilized verified
  packet digest;
- `review.decision` registration, prepared evaluator, and grant path are ready;
- the CON decision participant and shared transactional outbox are merged but
  hidden.

## Atomic decision transaction

```text
AUTH prepares review.decision and locks reviewer authority
-> REV locks idempotency, lifecycle fence, queue, lease, task, assignment,
   Submission, Review predecessor and stabilized binding facts
-> REV recomposes final review-decision context
-> AUTH evaluates once and stages decision evidence
-> REV creates Review/findings/resolutions, consumes lease/queue and applies task effects
-> REV calls the CON flush-only participant
-> CON creates one reviewer completed_review ContributionRecord
-> on accept only, CON creates one submitter accepted_submission ContributionRecord
-> CON creates applicable award, audit and shared-outbox rows
-> route commits once
```

`needs_revision` and `reject` still create the reviewer contribution because a
valid Review was completed. They do not create a submitter contribution. A CON
failure rolls back the complete Review decision; there is no no-op participant
or post-commit repair for canonical contribution creation.

CON receives the originating AuthorizationDecision reference and canonical
locked facts. It never evaluates `review.decision`, reads REV or AUTH
repositories, commits, or performs network/provider I/O.

## Independent CON authorization

CON requires separate AUTH actions only for its independently invoked surfaces:
contribution/award reads, compensation policy and adapter-binding management,
fulfillment callback, outbox dispatch, reconciliation, projections, and audit.
Derived contribution/award inserts inside `review.decision` do not invent
`contribution.materialize` or `compensation.award.materialize` actions.

## Optional post-commit evidence projection

A deterministic contribution-evidence document may be added later as an
asynchronous projection. It is not a gate inside the Review/ContributionRecord
transaction. If adopted, it uses a separately reviewed ART capability and AUTH
action, records projection status independently, and cannot change Review,
ContributionRecord, award, or payment truth when storage is unavailable.

## REV owner response

REV must define the exact participant request, lock order, source facts, and
single transaction owner, then remove any no-op contribution fallback.

## CON owner response

CON must keep the participant flush-only, remove mandatory ART evidence from
core contribution gates, preserve the canonical `artifact_hash` lineage, and
own all outbox, award, fulfillment, and projection transitions.

## AUTH owner response

AUTH must activate `review.decision` only after the complete REV+CON hidden
composition exists and independently activate each public/service CON action
after its own behavior merges.

This handoff changes no runtime and starts no downstream chunk.
