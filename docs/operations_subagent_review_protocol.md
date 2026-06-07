# Independent Review Protocol

Workstream planning and major system changes receive multiple review perspectives before being treated as ready.

This repository may not have actual autonomous subagents wired in yet, but the review roles are simulated consistently until tooling exists.

## Review Roles

### Product Strategy Reviewer

Focus:

- product clarity
- 30-day scope
- MVP risk
- first-user flow
- operator value
- whether the plan is too broad

### Architecture Reviewer

Focus:

- system boundaries
- state model
- data model
- extensibility
- failure modes
- whether future adapters can be added without rewriting the core

### Operations Reviewer

Focus:

- daily operator workflow
- reviewer workflow
- checker policy
- revision replay
- payment/reputation consistency
- auditability

### Risk Reviewer

Focus:

- privacy
- copied data risk
- payment disputes
- reviewer abuse
- fake evidence
- low-quality generated artifacts
- scope creep

## Required Output

Each review produces concise findings:

```text
severity:
file:
finding:
suggested_change:
```

Severity:

- `critical`: must fix before using the plan
- `high`: fix before implementation
- `medium`: fix during iteration
- `low`: note or polish

## Rule

No major plan is marked ready without at least product, architecture, and operations review passes.

## Task Readiness Gate

Before a task moves from `SCREENING` to `READY`, run the same review pattern at task scale:

- product/ops pass: task is worth doing and payment policy is clear
- guide pass: task follows the active project guide
- checker pass: required automated checks exist for the task type
- reviewer pass: acceptance criteria are reviewable
- adversarial pass: identify how the task could be gamed, faked, or disputed

The release decision is recorded as a status snapshot, not only discussed in chat.
