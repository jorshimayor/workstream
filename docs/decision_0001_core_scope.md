# ADR 0001: Core Scope

## Status

Accepted for 30-day build.

## Decision

Workstream will first build Flow's task evaluation and contribution infrastructure, not the marketplace, not the agent workspace, and not blockchain settlement.

## Context

Across task evaluation and contribution projects, the repeated pattern is:

```text
Project Guide
-> Task
-> Submission
-> Platform Checker
-> Human Review
-> Needs Revision / Accepted / Rejected
-> Contribution Record
-> Payment Record
-> Reputation Event
```

The same evaluation and contribution infrastructure can support many project domains if project-specific rules are configurable.

## Consequences

The first version prioritizes:

- project guides
- task queues
- submissions
- checkers
- reviews
- revisions
- evidence
- contribution records
- payment ledger
- reputation ledger

Deferred:

- source adapters
- autonomous execution runtime
- marketplace discovery
- blockchain settlement
- external client billing

This keeps the build focused on the part that determines quality and acceptance.
