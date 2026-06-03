# Payment And Reputation

## Payment Principle

Payment can be manual in the first version, but it must be tracked with the same discipline as automated settlement.

Accepted work must never disappear into memory or chat. Every accepted task needs a payment record.

Accepted work must create a contribution record first. The contribution record certifies accepted work under a locked guide with evidence. Payment records and reputation events attach to the contribution record.

## Payment States

```text
NONE
PENDING
PAYOUT_SUBMITTED
PAID
DISPUTED
```

Payment status is not task lifecycle status. A task can be `ACCEPTED` while payment remains `PENDING`.

## Payment Record

Fields:

- contribution record id
- task id
- worker id
- project id
- base amount
- accepted amount
- pending amount
- paid amount
- currency
- status
- payment reference
- accepted at
- paid at

## Payment Rules

Default:

- DRAFT through REVIEW_PENDING: no payment owed
- NEEDS_REVISION: no payment owed yet
- ACCEPTED: contribution record is created, then accepted amount becomes pending
- PAID: pending amount becomes paid
- REJECTED: payment policy decides

Acceptance and payment must remain separate.

`ACCEPTED` means the work met the guide. `PAID` means money moved or payout was recorded with a reference.

The dashboard must always show:

- accepted but unpaid amount
- payout submitted amount
- paid amount
- disputed amount

## Reputation Principle

Reputation is not a badge. It is an outcome ledger.

It updates from:

- contribution records
- accepted work
- needs revision
- rejection
- payment completion
- reviewer decision quality
- task difficulty
- skill area

## Worker Reputation

Track:

- accepted count
- needs revision count
- rejected count
- acceptance rate
- revision rate
- average turnaround
- skill-specific quality
- payout reliability

Suggested v0.1 worker events:

| Event | Default Delta | Notes |
| --- | ---: | --- |
| accepted | +3 | Weight by task difficulty and project trust. |
| needs_revision | -1 | Do not over-penalize if revision closes cleanly. |
| rejected | -3 | Higher penalty for policy/originality issues. |
| late_submission | -1 | Only if deadline policy was explicit. |
| revision_closed | +1 | Rewards learning and recovery. |

## Reviewer Reputation

Track:

- completed reviews
- decision distribution
- overturned decisions
- unclear feedback reports
- average turnaround
- second-review agreement

Suggested v0.1 reviewer events:

| Event | Default Delta | Notes |
| --- | ---: | --- |
| clear_review | +2 | Structured findings or clear acceptance evidence. |
| unclear_feedback | -2 | Finding lacks issue, evidence, or required fix. |
| overturned_accept | -3 | Accepted work later found non-compliant. |
| overturned_reject | -3 | Rejected work that belonged in accepted or needs-revision state. |
| missed_prior_finding | -2 | Resubmission accepted with unresolved prior issue. |

## Skill Tags

Reputation is tagged by skill so a worker can be strong in one domain and weak in another.

Examples:

- coding
- rubric-review
- data-qa
- technical-writing
- research
- security
- database
- frontend
- long-context

## Future Settlement Compatibility

The payment ledger is designed so future payment adapters can attach references:

- bank transfer reference
- stablecoin transaction hash
- Stripe transfer id
- ERC-8183 job id
- x402 payment id

The first version does not depend on these.

## Reconciliation Rules

Finance reconciles daily:

- accepted tasks without payment records
- pending payout older than agreed SLA
- payout submitted without paid confirmation
- paid records missing references
- payment amount mismatches

Any mismatch becomes an operations issue, not a silent spreadsheet correction.
