# ADR 0003: Project Guides Are First-Class Objects

## Status

Accepted

## Context

Different projects use different language and acceptance rules, but they share the same lifecycle.

If project rules live only in chat or loose markdown, operators and reviewers will repeat avoidable mistakes.

## Decision

Every active Workstream project must have a versioned project guide attached to its configuration.

The guide drives:

- task requirements
- checker policy
- review policy
- revision policy
- payment policy
- common rejection reasons

## Consequences

Positive:

- rules become inspectable
- checkers can be mapped to guide requirements
- reviewers have a consistent source of truth
- project templates become reusable

Tradeoff:

- project setup takes more discipline
- guide changes need versioning

