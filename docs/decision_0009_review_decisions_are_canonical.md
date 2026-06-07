# ADR 0009: Review Decisions Are Canonical

## Status

Accepted

## Context

Workstream review results drive task state, revision loops, contribution records, payment records, and reputation signals.

If projects invent their own review outcome labels, downstream lifecycle rules become ambiguous.

## Decision

The only canonical stored review decision values are:

- accept
- needs_revision
- reject

Display labels may render these as "Accept", "Needs revision", and "Reject", but persisted records, audit events, API payloads, and analytics must use the canonical stored values.

`Escalated` is not a review decision value.

Disputes, second review, suspected fraud, payment holds, or admin overrides may create separate workflow records and audit events, but they do not replace the reviewer decision contract.

## Consequences

Positive:

- task state transitions remain simple
- review analytics can compare decisions across projects
- revision policy has one clear entry point
- payment and reputation logic can depend on a stable decision set

Tradeoff:

- special handling must be modeled as workflow, audit, dispute, or override records instead of extra review decisions
