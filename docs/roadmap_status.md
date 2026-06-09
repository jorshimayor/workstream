# Workstream Roadmap Status

Current phase: Week 1 backend foundation complete; preparing checker framework.

## Completed

- Root README.
- Product principles and product brief.
- First user flows.
- 30-day master plan.
- Day-by-day execution plan.
- Implementation backlog.
- Pilot plan.
- System architecture.
- Data model.
- Lifecycle state machine.
- Checker framework.
- Operator workflow.
- Queue policy.
- Reviewer workflow.
- Revision replay.
- Roles and permissions.
- Payment and reputation.
- Workspace and packet convention.
- Risk register.
- Templates for guides, tasks, submissions, reviews, checkers, revision replay, and prior feedback.
- Decision records.
- Independent review passes.
- Review closure record.
- June 3 architecture proposal preserved and reconciled.
- Architecture lockdown note.
- Week 1 backend chunk plan.
- Chunk 1 backend scaffold.
- Chunk 2 external Flow auth actor boundary.
- Chunk 3 project guide foundation with checker, review, revision, and payment policy context.
- Chunk 4 task queue, worker/reviewer profiles, assignment, claim, start, and task audit events.
- Chunk 5 submission packet foundation with evidence items, versioning, server-stamped locked context, and submission locking.
- Week 1 backend dry run through `Project -> Guide -> Task -> Screening -> Ready -> Claim -> Start -> Submit -> Lock submission`.
- Week 2 checker framework scope specification.
- Chunk 6 checker contract and records specification.

## Review Tracks Closed

- Product strategy.
- Architecture.
- Systems architecture.
- Operations and review workflow.
- Process-pattern baseline.
- Adversarial quality.

## Pending Before Week 2

- Create the first pilot project guide from the template.
- Create the first 5 pilot task records.
- Confirm who owns product, engineering, review, operations, and payment reconciliation during the first build cycle.
- Confirm the first v0.1 project guide uses the locked guide fields, task contract fields, evidence IDs, and contribution record flow.
- Build checker run records and `check_submission_packet` in Week 2.
- Keep Week 2 backend/checker-framework only: expose checker results through APIs and dry-run/demo output, not product frontend pages.

## Week 1 Dry Run

Run from the backend directory against local Postgres:

```bash
WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream .venv/bin/python scripts/week1_dry_run.py
```

The script runs migrations forward and exercises:

`Project -> Guide -> Task -> Screening -> Ready -> Claim -> Start -> Submit -> Lock submission`

## Operating Rule

No roadmap item is considered closed until it is represented in one of:

- product spec
- architecture spec
- operation workflow
- template
- checker rule
- decision record
- review closure
