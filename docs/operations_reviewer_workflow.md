# Reviewer Workflow

## Reviewer Job

The reviewer decides whether a submission satisfies the task and project guide.

The reviewer does not spend time diagnosing basic packaging or schema failures. The checker framework handles that before review.

The reviewer is accountable for judgment, not task execution. A good review is specific enough that a contributor can either fix the issue or clearly dispute it.

## Review Inputs

Every review page shows:

- project guide version
- task description
- acceptance criteria
- submission summary
- evidence items
- checker results
- prior review findings if resubmission
- revision replay if resubmission

## Decisions

Allowed decisions:

- accept
- needs_revision
- reject

Decision rules:

- `accept` means the submission satisfies the project guide. The same
  transaction creates internal FinalAcceptance, then creates the submitter
  `accepted_submission` contribution only from that fact. Its frozen
  contribution award rule independently decides whether that contribution
  creates an award.
- `needs_revision` means the work is fixable and the reviewer can name concrete required changes.
- `reject` means the work is not reasonably salvageable or violates policy.

## Finding Format

Every finding includes:

- severity
- area
- issue
- required fix
- evidence reference

Severity:

- high: blocks acceptance
- medium: fixed unless project policy says otherwise
- low: note or cleanup

Finding areas are project-specific but normalized enough for reporting.

Common areas:

- task_spec
- output_quality
- evidence
- checker_failure
- originality
- package
- revision_replay
- guide_compliance

## Accept

Use accept only when:

- task requirements are satisfied
- acceptance criteria are met
- evidence is sufficient
- no unresolved critical- or high-severity checker failure exists
- prior revision findings are closed if applicable

Accept must create:

- review decision record
- one immutable internal FinalAcceptance linked to the exact Review, existing
  versioned Submission, task, submitter, recording reviewer, and locked
  ReviewPolicy
- acceptance audit event
- reviewer `completed_review` contribution record
- submitter `accepted_submission` contribution record sourced from
  FinalAcceptance, not directly from Review.decision
- any awards required by the separately frozen reviewer and submitter
  contribution policies
- reputation event

The reviewer cites the strongest evidence supporting acceptance, not only "looks good."

## Needs Revision

Use needs_revision when:

- issues are fixable
- the submission is not acceptable yet
- reviewer can describe concrete required fixes

Do not write vague feedback. Every issue must tell the contributor what is wrong and what must change.

Needs revision feedback must not introduce preference-only work. If the guide does not require it and acceptance is not blocked by it, keep it as a low-severity note.

Each high or medium finding must have:

- exact issue
- why it blocks acceptance
- required fix
- evidence reference or file/section reference

Recording `needs_revision` sets the Task to `needs_revision`, keeps the same
TaskAssignment `active`, and creates no FinalAcceptance or submitter
contribution. The reviewer `completed_review` still commits atomically.

## Reject

Use reject when:

- the work is fundamentally wrong
- the submission is non-original or violates policy
- the task cannot be salvaged by reasonable revision
- the contributor submitted prohibited material

Use reject carefully. If the work can be reasonably corrected through one revision cycle, use `needs_revision`.

Recording `reject` sets the Task to canonical `rejected` with the bounded human
reason and blocks only the same-task TaskAssignment with its source Review. It
changes no actor grant or unrelated task and creates no FinalAcceptance or
submitter contribution. `closed/review_rejected` is not a canonical state.

Every valid recorded `needs_revision` or `reject` decision still creates the
reviewer's `completed_review` contribution and evaluates the ReviewLease-frozen
reviewer contribution policy. Neither decision creates a submitter contribution
or submitter award.

## Reviewer Quality

Track:

- review count
- decision distribution
- non-mutating quality-audit findings
- unclear feedback reports
- average turnaround
- quality-audit agreement

Reviewer reputation matters because low-quality review damages the whole system.

Reviewer quality events are generated when:

- feedback is marked unclear
- a non-mutating quality audit finds unsupported acceptance/rejection reasoning
- reviewer misses unresolved prior findings

These quality signals never reopen or replace Review, FinalAcceptance, task, or
ContributionRecord truth. V0.1 has no adjudication decision or queue.

## Reviewer Checklist

Before accepting:

- task guide was followed
- acceptance criteria are satisfied
- evidence supports the claim
- checker results are acceptable
- no prior findings are open
- FinalAcceptance can be created exactly once for this task, source Review, and
  existing versioned Submission
- reviewer and submitter contribution lineage can be created atomically
- both frozen contribution policies can be evaluated; explicit unpaid results
  are valid and create no award

Before needs revision:

- each issue has a required fix
- severity is accurate
- feedback is actionable
- no unrelated refactor or preference is demanded

Before rejection:

- rejection reason is grounded in the guide
- evidence is cited
- task is not merely fixable

## Non-Mutating Quality Sampling

During the first 30 days, audit at least:

- 25 percent of accepted submissions
- 25 percent of rejected submissions
- any submission matching the configured high-value criterion in
  `ReviewPolicy`

Sampling checks whether the reviewer followed the guide and cited evidence. It
does not create a Review, adjudication result, reopen path, replacement
FinalAcceptance, or lifecycle mutation.
