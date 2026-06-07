# First User Flows

The first user flows prove that Workstream can run real work from intake to acceptance. These flows come before any advanced routing or settlement.

## Flow 1: Admin Creates A Project

1. Admin creates project.
2. Admin adds guide.
3. Admin sets base amount.
4. Admin selects required submission fields.
5. Admin enables checker policy.
6. Admin enables review policy.
7. Admin enables revision policy.
8. Admin enables payment policy.
9. Project becomes active.

Acceptance:

- Project cannot become active without guide, base amount, checker policy, review policy, revision policy, and payment policy.
- Checker, review, revision, and payment policies are visible on the project page.

## Flow 2: Operator Creates A Task

1. Operator selects active project.
2. Operator creates task with title, description, expected output, acceptance criteria, base amount, deadline, and difficulty.
3. Workstream validates task against project guide.
4. Task enters `SCREENING`.
5. Screening confirms guide version, task contract, evidence requirements, checker policy, review policy, revision policy, payment policy, and reviewability.
6. Task enters `READY`.

Acceptance:

- Missing required fields block `SCREENING`.
- Missing required fields block `READY`.
- Task shows project guide, required files, checker policy, review policy, revision policy, and payment policy.

## Flow 3: Worker Submits Work

1. Worker opens assigned task.
2. Worker attaches output files or links.
3. Worker attaches evidence.
4. Worker writes submission notes.
5. Worker submits packet.
6. Task enters `AUTO_CHECKING`.

Acceptance:

- Submission cannot be created without required evidence.
- Submission packet is immutable after checks start.

## Flow 4: Automated Checks Run

1. Checker runner loads project policy.
2. Runner executes enabled checks.
3. Results are saved with pass, warn, fail, severity, message, and evidence.
4. If high-severity failures exist, task enters `NEEDS_REVISION`.
5. If no high-severity failures exist, task enters `REVIEW_PENDING`.

Acceptance:

- High-severity failure blocks human review.
- Warnings remain visible to reviewer.
- Every checker result is timestamped.

## Flow 5: Reviewer Reviews Submission

1. Reviewer opens review queue.
2. Reviewer selects `REVIEW_PENDING` task.
3. Reviewer reads guide, task, submission, evidence, and checker results.
4. Reviewer enters structured findings.
5. Reviewer selects accept, needs_revision, or reject.

Acceptance:

- Review cannot be submitted without a decision.
- needs_revision and reject require at least one finding.
- accept requires no unresolved high-severity checker failure.

## Flow 6: Revision Replay

1. Worker opens needs-revision task.
2. Worker sees each finding as a checklist item.
3. Worker adds fix note and evidence per finding.
4. Worker resubmits.
5. Checkers rerun.
6. Reviewer closes or reopens each finding.

Acceptance:

- Prior review remains visible.
- Each required finding has a closure state.
- Revision count is tracked against the locked revision policy.
- Resubmission is blocked or rejected when the revision policy limit or deadline says so.

## Flow 7: Accepted Work Creates Contribution Record

1. Reviewer accepts task.
2. Task enters `ACCEPTED`.
3. Contribution record is created from accepted submission, accepting review, guide version, evidence refs, and artifact hashes.
4. Payment record is created or updated as `PENDING`.
5. Worker reputation updates from the contribution record.
6. Project dashboard updates.

Acceptance:

- Accepted task cannot lack contribution record.
- Accepted task cannot lack payment record.
- Payment status is separate from assignment status.
