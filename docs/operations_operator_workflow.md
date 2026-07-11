# Operator Workflow

## Roles

### Project Manager

Creates projects when system-scoped and manages guides, policies, tasks, and
contributor grants only for covered projects.

### Contributor

An exact-project Submitter grant permits queue/claim/submission candidates. The
person is a Contributor in product, lifecycle, assignment, and attribution
language.

### Reviewer

Reviews checker-passed submissions and issues accept, needs_revision, or reject decisions.

### Operator

Inspects runtime state and performs only registered reasoned recovery. Operator
does not issue grants, approve policy, or record review decisions by that grant.

### Access Administrator

Manages actors, identity links, the permission catalog, and administrative
grants. This grant does not manage project work.

### Finance Authority

Tracks accepted work, pending payout, payout submitted, and paid states.

### Audit Authority

Reads authorized immutable and operational evidence without mutation.

## Daily Operating Loop

```text
1. Check task queue
2. Create or release ready tasks
3. Assign tasks
4. Review submitted packets
5. Resolve needs-revision queue
6. Update accepted and paid records
7. Review failed checks; use covered repair or registered Operator retry only
8. Update project lessons learned
```

## Task Creation Workflow

1. Select project.
2. Confirm active project guide.
3. Create task title and description.
4. Add acceptance criteria.
5. Add required output format.
6. Confirm the active payment policy amount and currency that will be locked onto the task.
7. Set skill tags.
8. Run task schema check.
9. Move to READY.

## Contributor Submission Workflow

1. Read project guide.
2. Read task requirements.
3. Complete work outside Workstream.
4. Prepare submission packet.
5. Attach evidence.
6. Submit.
7. Wait for automated checks.
8. If NEEDS_REVISION, use revision replay.

## Revision Workflow

1. Read every reviewer finding.
2. Create fix summary per finding.
3. Attach evidence per fix.
4. Resubmit packet.
5. Checker verifies prior revision closure.
6. Reviewer confirms findings are closed.

## Acceptance Workflow

1. Reviewer accepts submission.
2. Task moves to ACCEPTED.
3. Payment record moves to pending.
4. Reputation event is recorded.
5. Finance marks payout submitted or paid.

## Rejection Workflow

1. Reviewer rejects submission or task.
2. Review must include rejection reason.
3. Reputation event is recorded.
4. Payment policy determines whether any payment is owed.

## Lessons Learned

Every project maintains lessons learned:

- common failure
- root cause
- new checker needed
- guide update needed
- reviewer policy update needed
- revision policy update needed
- payment policy update needed

This is how Workstream compounds operational knowledge.

Each lesson links to an operating source:

- checker failure
- reviewer finding
- rejected task
- repeated needs-revision loop
- payment reconciliation issue
- user/operator incident

Lessons are not just notes. They become one of:

- guide update
- checker update
- reviewer workflow update
- queue policy update
- revision policy update
- payment policy update
- risk register update
