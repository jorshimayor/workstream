# Internal Review Evidence: Revision Context Rebase

## Scope

- ADR 0010 revision context rebase
- `task_setup_blocked` checker routing rename
- worker/reviewer visibility for revision context
- internal review evidence gate

## Required Tracks

### Senior Engineering

Status: passed after fixes.

Findings addressed:

- task-state wording changed from `needs_revision` to `NEEDS_REVISION`
- ADR 0010 now records every revision context preparation outcome, not only rebases
- stale project-setup wording changed to locked task setup wording

### QA/Test

Status: passed after fixes.

Findings addressed:

- `task_setup_blocked` is covered in schema, runner, service routing, and checker tests
- stale test wording changed to task setup blocked route
- PR evidence gate added through `scripts/check_internal_review_evidence.py` and backend CI

### Security/Auth

Status: passed after fixes.

Findings addressed:

- revision replay template now separates worker-visible fields from reviewer/admin fields
- acceptance-affecting checker implementation changes must be tied to visible guide, policy, or checker-policy context
- worker redaction keeps internal routing and setup details hidden

### Product/Ops

Status: passed after fixes.

Findings addressed:

- revision policy now has `context_rebase_rule` and `context_rebase_triggers`
- `task_setup_blocked` is documented as an internal checker routing recommendation, not a lifecycle state
- out-of-band guidance is not enforceable until it becomes guide, policy, template, or checker contract

## Final Gate

Valid findings addressed: yes.

Open sub-agent sessions: none.
