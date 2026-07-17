# Queue Policy

## Purpose

The queue is the operational truth of Workstream. It tells the team what
exists, what is blocked, what needs human action, and what creates contribution
or compensation-award exposure.

Queue lanes must be derived from task status, not manually maintained in separate lists.

## Lanes

### Draft

Tasks being prepared.

Owner:

- project manager
- task creator

Exit requirement:

- project guide attached
- acceptance criteria present
- required output defined

### Screening

Tasks that look ready but need independent release review before contributors can claim them.

Owner:

- project manager
- reviewer lead
- quality lead

Exit requirement:

- project guide version locked
- immutable guide source snapshot id/hash locked
- acceptance criteria are concrete
- effective project submission artifact policy hash locked
- project `PreSubmitCheckerPolicy` compiled bundle hash locked
- approved generated project `PostSubmitCheckerPolicy` is locked with matching
  guide, source snapshot, effective project policy, and pre-submit checker
  provenance
- review policy is attached
- revision policy is attached
- no open critical- or high-severity readiness finding

Policy:

- screening is where weak task guides and low-quality task specs fail
- contributors do not see tasks that have not passed screening

### Ready

Tasks that can be claimed or assigned.

Owner:

- project manager

Exit requirement:

- assigned or claimed by contributor

### Active

Tasks in `CLAIMED` or `IN_PROGRESS`.

Owner:

- contributor
- operator

Operational risk:

- stale active tasks block throughput

Policy:

- each active task must have a deadline or next check-in
- stale tasks get an owner action before deadline breach

### Submitted

Tasks with a new submission packet.

Owner:

- checker system

Exit requirement:

- checker run created

### Auto Checking

Checker run is active.

Owner:

- checker system
- Operator when infrastructure recovery is required

Policy:

- checker failure because of platform/tooling stays in checker retry handling;
  Operator retry uses `operations.checker.retry`, while covered Project Manager
  repair uses `project.task.manage`, and neither moves work directly to review
- retry and repair actions record matched grant/permission, reason, attempt, and
  immutable audit history

### Pre Review Gate

Optional reviewer-simulation or adversarial readiness audit after automated checks and before normal human review.

Owner:

- reviewer lead
- quality lead
- assigned simulation reviewer

Policy:

- use this for high-value tasks, new project types, disputed checker outcomes, or projects still being calibrated
- the gate records findings or explicitly clears the packet for normal review
- unresolved blocking issues go to `NEEDS_REVISION` when contributor-fixable or
  remain blocked from review until the owning covered repair/retry action
  succeeds

### Review Pending

Submission passed blocking checks and is ready for human review.

Owner:

- reviewer

Policy:

- reviewers only see this lane for normal work
- any critical- or high-severity checker failure in this lane is a system bug;
  no administrative grant can override it into review readiness

### Needs Revision

Contributor-facing lane for fixable issues from automated checks, pre-review gates, or human review.

Policy:

- before the contributor resumes, Workstream prepares revision context against the active guide and policy records
- revision policy decides whether the next attempt keeps the prior locked context or rebases to the current active context
- a rebase must show the contributor the prior version, next version, and change summary
- out-of-band guidance is not enforceable until it is encoded into guide, policy, task template, or checker contracts

Owner:

- contributor
- operator

Policy:

- every task in this lane must have at least one structured finding
- resubmission must include revision replay

### Accepted

Work satisfies the project guide and acceptance criteria.

Owner:

- project operations
- finance/reconciliation only for payable contribution awards

Policy:

- the accepting Review creates reviewer `completed_review`, REV-owned
  FinalAcceptance, and FinalAcceptance-sourced submitter `accepted_submission`
  contribution records atomically
- each frozen contribution policy is evaluated independently; only payable
  contributions create awards and fulfillment follow-up
- accepted task is not confused with fulfilled compensation

### Rejected

Work is not acceptable and will not continue in the normal revision loop.

Owner:

- project manager
- reviewer lead if disputed

Policy:

- rejection requires evidence and guide-grounded reason
- the Task enters canonical `rejected`; only its same-task TaskAssignment is
  blocked and bound to the reject Review
- no FinalAcceptance or submitter contribution is created; no actor grant or
  unrelated task changes

### Compensation Fulfillment Follow-Up

Compensation follow-up is not a task queue lane. It is derived from payable
`CompensationAward` records and their fulfillment projections, whether the
source contribution is `completed_review` or `accepted_submission`.

Track:

- payable contribution missing its award or fulfillment projection
- pending award delivery
- acknowledged by adapter
- failed fulfillment
- fulfilled with immutable receipt

## Daily Queue Review

Every operating day starts with:

1. count tasks by lane
2. clear screening tasks or send them back to draft
3. inspect stale active tasks
4. clear checker failures
5. assign review pending tasks
6. push needs revision tasks to contributors
7. reconcile payable awards with pending/failed fulfillment projections
8. record new lessons learned

## Transition Guards

| Transition | Required Records |
| --- | --- |
| `DRAFT -> SCREENING` | project id, locked guide candidate, task source/description fields, acceptance and rejection criteria |
| `SCREENING -> READY` | screening decision, guide version lock, guide source snapshot id/hash lock, acceptance criteria, effective project submission artifact policy hash lock, project `PreSubmitCheckerPolicy` compiled bundle hash lock, approved generated project `PostSubmitCheckerPolicy` with matching provenance, review policy, revision policy |
| `READY -> CLAIMED` | active published ContributionPolicyVersion whose `accepted_submission` rule is explicit; TaskAssignment freezes that version |
| `IN_PROGRESS -> SUBMITTED` | blocking pre-submit checks passed, submission packet, artifact hash manifest, evidence references, contributor attestation |
| `SUBMITTED -> EVALUATION_PENDING` | immutable submission version, locked post-submit checker policy id/version/hash/body copied from the task context |
| `EVALUATION_PENDING -> REVIEW_PENDING` | checker run for exact submission version, readiness certificate, no blocking failures |
| `EVALUATION_PENDING -> NEEDS_REVISION` | checker run id, outcome source `auto_checker`, contributor-visible checker failures with severity, message, suggested fix |
| `REVIEW_PENDING -> NEEDS_REVISION` | review decision, at least one structured finding, TaskAssignment remains `active`, reviewer `completed_review` contribution and applicable reviewer award, no FinalAcceptance or submitter contribution, revision policy still permits revision |
| `REVIEW_PENDING -> ACCEPTED` | accepted Review, one FinalAcceptance for the exact task/Review/Submission, acceptance evidence refs, reviewer `completed_review` and FinalAcceptance-sourced submitter `accepted_submission` contributions, applicable awards |
| `REVIEW_PENDING -> REJECTED` | rejected Review, bounded human reason/finding, only the same-task TaskAssignment blocked with its source Review, reviewer `completed_review` contribution and applicable reviewer award; no FinalAcceptance, submitter contribution, grant change, or unrelated task effect |
| pre-submit feedback in `NEEDS_REVISION` | prior findings visible to contributor, revision deadline active, no new submission created |
| `NEEDS_REVISION -> SUBMITTED` | replacement submission packet, revision replay covering every high and medium prior finding, revision count under policy limit |
| compensation `pending -> fulfilled` | immutable fulfillment receipt, external reference, and audit event |

## Lane Capacity

Each project defines capacity limits:

- maximum active tasks per contributor
- maximum review-pending tasks per reviewer
- maximum stale active age
- maximum pending/failed payable-award fulfillment age

Capacity limits prevent the queue from looking healthy while hidden work is stuck.

For early pilots, use conservative defaults:

- contributor active task limit: 2
- reviewer review-pending limit: 5
- review SLA: 24 hours
- compensation fulfillment reconciliation SLA: daily

## Queue Health Metrics

- tasks ready
- tasks screening
- tasks active
- submitted awaiting checks
- review pending age
- needs revision age
- unfulfilled compensation award amount
- rejected count
- fulfilled compensation total

## Failure Modes

### Review Pending Pileup

Cause:

- not enough reviewers
- reviewers lack context
- checker output too noisy

Fix:

- assign reviewer owner
- improve review packet
- split projects by reviewer skill

### Needs Revision Looping

Cause:

- vague feedback
- contributor not closing findings
- task spec unclear

Fix:

- require revision replay
- audit reviewer wording
- update project guide

### Payable Contribution Fulfillment Drift

Cause:

- contribution award creation and fulfillment are disconnected

Fix:

- frozen contribution policy evaluation creates awards only for payable
  contributions; explicit unpaid rules create none
- compensation fulfillment dashboard is reviewed daily

### Ready Lane Contains Weak Tasks

Cause:

- no ready gate
- task creator skipped project guide
- acceptance criteria are vague

Fix:

- run ready gate before `READY`
- add task creator checklist
- require reviewer simulation for first-of-kind tasks
