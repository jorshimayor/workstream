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

The checker, review, revision, and payment policies are guide-version policies. They must be tied to the project guide version they govern, not only to the project.

Project guide activation requires the guide plus its required policy context before work can lock against it:

- checker policy
- review policy
- revision policy
- payment policy

Revision policy is not optional. It defines the revision loop contract, including revision limits, revision deadlines, allowed resubmission states, and automatic rejection behavior after the limit.

Guide and policy changes do not silently mutate submitted attempts. A submitted attempt stays tied to the guide and policy versions stamped on that submission. When a task enters `NEEDS_REVISION`, revision policy controls whether the next attempt keeps the prior context or rebases to the latest active guide and policy context.

Rules that affect acceptance must be encoded in the project guide, checker policy, review policy, revision policy, payment policy, task template, or checker implementation. Chat messages and informal notices are not enforceable rules until they are moved into those contracts.

## Consequences

Positive:

- rules become inspectable
- checkers can be mapped to guide requirements
- reviewers have a consistent source of truth
- revision loops have explicit limits and deadlines
- project templates become reusable

Tradeoff:

- project setup takes more discipline
- guide changes need versioning
- policies must be versioned and validated with the guide
