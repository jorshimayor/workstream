# ADR 0009: Review Decisions Are Canonical

## Status

Accepted

## Context

Workstream review results drive task state, revision loops, contribution records, payment records, and reputation signals.

If projects invent their own review outcome labels, downstream lifecycle rules become ambiguous.

Automated checker results also influence workflow routing before human review. That routing is not the same thing as a human review decision.

## Decision

The only canonical stored review decision values are:

- accept
- needs_revision
- reject

Display labels may render these as "Accept", "Needs revision", and "Reject", but persisted records, audit events, API payloads, and analytics must use the canonical stored values.

`Escalated` is not a review decision value.

Disputes, second review, suspected fraud, payment holds, or admin overrides may create separate workflow records and audit events, but they do not replace the reviewer decision contract.

Checker routing recommendations use a separate contract. A checker can recommend that a submission is ready for review, needs worker revision, needs checker retry handling, or needs project setup correction. A checker cannot accept or reject work.

Canonical checker routing recommendation values are:

- not_evaluated
- allow_review
- needs_revision
- checker_retry
- project_setup_required

`allow_review` must not be stored as `accept`. It only means the automated checker found no blocking issue and the packet may proceed to human review. Only a human review decision can store `accept`.

`project_setup_required` must not be stored as `needs_revision`. It means the task/project contract is incomplete and a project manager must fix setup before worker-facing revision or human review can continue.

`needs_revision` can appear in both contracts, but the source must be explicit:

- checker-caused revision: `outcome_source = auto_checker`, `review_decision_id = null`
- human reviewer revision: `outcome_source = human_review`, `review_decision_id = <review decision id>`

## Consequences

Positive:

- task state transitions remain simple
- review analytics can compare decisions across projects
- revision policy has one clear entry point
- payment and reputation logic can depend on a stable decision set
- automated checker routing cannot accidentally masquerade as human acceptance or rejection

Tradeoff:

- special handling must be modeled as workflow, audit, dispute, or override records instead of extra review decisions
- code and docs must name checker routing fields clearly so reviewers do not confuse them with review decision fields
