# First User Flows

The first user flows prove that Workstream can run real work from intake to acceptance. These flows come before any advanced routing or settlement.

## Flow 1: Project Manager Creates A Project

1. A system-scoped Project Manager creates the project.
2. Project owner provides open-ended guide material and business terms.
3. An authorized covered Project Manager adds the guide.
4. Workstream enqueues the Celery project setup pipeline for the immutable guide-source snapshot.
5. The pipeline runs `ProjectGuideSufficiencyAgent`.
6. Blocking sufficiency gaps stop the setup pipeline and create clarification requests for the project owner.
7. An authorized covered Project Manager acknowledges non-blocking sufficiency warnings.
8. The pipeline runs `SubmissionArtifactPolicyDerivationAgent` only after sufficiency is not blocked.
9. An authorized covered Project Manager reviews and approves the derived submission artifact policy.
10. Workstream persists the effective project submission artifact policy hash.
11. Workstream compiles, persists, and locks the project `PreSubmitCheckerPolicy`.
12. Workstream derives and compiles the project post-submit checker policy.
13. An authorized covered Project Manager approves the current compiled
    post-submit checker policy.
14. If correction is requested instead, Workstream supersedes and retains the
    unapproved compiled output, preserves its policy hash/body plus bounded
    actor/reason/time and redacted derivation metadata, passes bounded correction
    feedback to post-submit derivation, and requeues setup continuation. An
    unchanged replacement fails closed, and activation remains blocked.
15. An authorized covered Project Manager enables review policy.
16. An authorized covered Project Manager enables revision policy.
17. The owning Finance Authority publishes the active
    ContributionPolicyVersion with explicit submitter and reviewer
    compensated/unpaid rules.
18. Project becomes active.

Acceptance:

- Project cannot become active without guide, immutable guide source snapshot,
  passed or acknowledged guide sufficiency report for that immutable guide
  source snapshot, submission artifact policy, effective project submission
  artifact policy hash, project pre-submit checker bundle hash, an approved
  current compiled project post-submit checker policy with matching guide,
  source snapshot, effective project policy, and pre-submit checker provenance,
  review policy, revision policy, and an independently published active
  `ContributionPolicyVersion` containing exactly one explicit
  compensated/unpaid rule for each of `accepted_submission` and
  `completed_review`.
- Guide-policy activation and contribution-policy publication are independently
  governed. Project activation requires both to be complete; later
  `TaskAssignment` and `ReviewLease` creation freeze the applicable published
  version rather than treating award eligibility as guide or checker context.
- Normal setup starts from guide/source capture. Project Managers do not
  manually trigger sufficiency or derivation in the happy path.
- Submission artifact policy is Workstream-derived and approved by an
  authorized covered Project Manager; project owners do not author or approve
  the machine policy schema directly.
- This flow is the agent-derived setup path. A manual sufficiency report follows
  the explicit manual policy path; agent derivation requires an agent-created
  sufficiency report for the same snapshot or a fresh guide-source snapshot.
- Submission artifact, checker, review, and revision policies are visible on the
  project page; contribution policy/version is an independently governed
  project record.

## Flow 2: Project Manager Creates A Task

1. A covered Project Manager selects the active project.
2. The Project Manager creates a task with title, description, source reference, acceptance criteria, rejection criteria, deadline, and difficulty.
3. Workstream validates the task source and reviewability fields, then confirms the task fits the active project guide and policy bundle.
4. Task enters `SCREENING`.
5. Screening locks the guide source snapshot id/hash, effective project
   submission artifact policy hash, project pre-submit checker bundle hash, and
   approved provenance-matched project post-submit checker policy reference,
   then confirms the task contract, review policy, revision policy, and
   reviewability.
6. Task enters `READY`.

Acceptance:

- Missing required fields block `SCREENING`.
- Missing required fields block `READY`.
- Task shows project guide, required artifacts, generated project pre-submit
  checker policy summary, permission-appropriate post-submit checker policy
  summary, review policy, and revision policy. After claim, the contributor sees
  the Assignment-frozen submitter compensation terms.

## Flow 3: Contributor Submits Work

1. Contributor opens assigned task.
2. Contributor attaches output files or links.
3. Contributor attaches evidence.
4. Contributor writes submission notes.
5. Workstream executes the task's locked project `PreSubmitCheckerPolicy`.
6. Preflight failures return `PreSubmitCheckResponse`; blocked submission-create attempts return `pre_submission_checker_failed` with structured pass/fail/warning details and create no submission.
7. When blocking pre-submit checks pass, Contributor submits packet.
8. Task enters `SUBMITTED`.

Acceptance:

- Submission cannot be created when blocking pre-submit checks fail.
- Blocking pre-submit failures are not review decisions and never return `accept`, `needs_revision`, or `reject`.
- Submission cannot be created without required artifacts, evidence references, hashes, and contributor attestation defined by the locked project pre-submit checker policy.
- Submission packet is immutable after checks start.

## Flow 4: Automated Checks Run

1. Checker runner validates the submission-stamped locked `PostSubmitCheckerPolicy` id/version/hash/body.
2. Runner executes enabled checks from that locked policy body.
3. Results are saved with `passed`, `warning`, or `failed`, plus severity, message, and evidence.
4. If contributor-fixable blocking failures exist, task enters `NEEDS_REVISION`.
5. If setup or provenance defects exist, the task stays in the internal operations queue.
6. If no blocking failures exist, task enters `REVIEW_PENDING`.

Acceptance:

- Critical- or high-severity failure blocks human review.
- Warnings remain visible to reviewer.
- Every checker result is timestamped.

## Flow 5: Reviewer Reviews Submission

1. Reviewer opens review queue.
2. Reviewer selects `REVIEW_PENDING` task.
3. Reviewer reads guide, task, submission, evidence, and checker results.
4. Reviewer enters structured findings.
5. Reviewer selects accept, needs_revision, or reject.
6. Workstream atomically creates the reviewer `completed_review` contribution;
   `accept` additionally creates the submitter `accepted_submission`
   contribution.

Acceptance:

- Review cannot be submitted without a decision.
- needs_revision and reject require at least one finding.
- accept requires no unresolved critical- or high-severity checker failure.
- Every valid human decision has exactly one reviewer contribution.
- Only accept has a submitter contribution.

## Flow 6: Revision Replay

1. Contributor opens needs-revision task.
2. Workstream prepares revision context from the revision policy.
3. Contributor sees prior guide/policy version, next guide/policy version, and any change summary when the task was rebased.
4. Contributor sees each finding as a checklist item.
5. Contributor adds fix note and evidence per finding.
6. Contributor resubmits.
7. Checkers rerun.
8. Reviewer closes or reopens each finding.

Acceptance:

- Prior review remains visible.
- Context changes are visible before the contributor revises.
- Each required finding has a closure state.
- Revision count is tracked against the locked revision policy.
- Resubmission is blocked or rejected when the revision policy limit or deadline says so.

## Flow 7: Accepted Work Creates Submitter Contribution

1. Reviewer accepts task.
2. Task enters `ACCEPTED`.
3. The reviewer `completed_review` contribution already created with the Review
   remains immutable.
4. A submitter `accepted_submission` contribution is created from the accepted
   submission, accepting review, frozen policy lineage, and artifact hash.
5. The frozen reviewer and submitter contribution policies independently create
   applicable awards; explicit unpaid rules create none.
6. Reputation and project projections update from the contribution records.

Acceptance:

- Accepted task cannot lack its submitter contribution record.
- Every accepted Review cannot lack its reviewer contribution record.
- A payable contribution cannot lack its immutable CompensationAward and
  fulfillment projection; an explicit unpaid policy creates no award.
- Compensation fulfillment status is separate from assignment status.
