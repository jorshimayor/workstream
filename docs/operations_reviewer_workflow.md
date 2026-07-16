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

- `accept` means the submission satisfies the project guide and can create payment exposure.
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
- payment_policy
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
- acceptance audit event
- reviewer `completed_review` contribution record
- submitter `accepted_submission` contribution record
- any awards required by the separately frozen reviewer and submitter
  compensation policies
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

## Reject

Use reject when:

- the work is fundamentally wrong
- the submission is non-original or violates policy
- the task cannot be salvaged by reasonable revision
- the contributor submitted prohibited material

Use reject carefully. If the work can be reasonably corrected through one revision cycle, use `needs_revision`.

Every valid recorded `needs_revision` or `reject` decision still creates the
reviewer's `completed_review` contribution and evaluates the ReviewLease-frozen
reviewer compensation policy. Neither decision creates a submitter contribution
or submitter award.

## Reviewer Quality

Track:

- review count
- decision distribution
- overturned decisions
- unclear feedback reports
- average turnaround
- agreement with second reviewer

Reviewer reputation matters because low-quality review damages the whole system.

Reviewer quality events are generated when:

- review is overturned
- feedback is marked unclear
- reviewer accepts work later found non-compliant
- reviewer rejects work that belonged in revision
- reviewer misses unresolved prior findings

## Reviewer Checklist

Before accepting:

- task guide was followed
- acceptance criteria are satisfied
- evidence supports the claim
- checker results are acceptable
- no prior findings are open
- payment record can be generated

Before needs revision:

- each issue has a required fix
- severity is accurate
- feedback is actionable
- no unrelated refactor or preference is demanded

Before rejection:

- rejection reason is grounded in the guide
- evidence is cited
- task is not merely fixable

## Second Review Sampling

During the first 30 days, sample at least:

- 25 percent of accepted submissions
- 25 percent of rejected submissions
- any submission above the configured second-review payment-policy threshold

Second review checks whether the first reviewer followed the guide, cited evidence, and made the correct decision type.
