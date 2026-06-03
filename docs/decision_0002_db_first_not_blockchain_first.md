# ADR 0002: Use Database Ledger Before Blockchain Settlement

## Status

Accepted

## Context

Workstream will later integrate agent identity, escrow, micropayments, and on-chain reputation. Those are settlement and interoperability layers.

The first risk is not settlement. The first risk is whether the evaluation and contribution loop works.

## Decision

Use a normal database-backed payment and reputation ledger for the first version.

Blockchain settlement comes later as an adapter behind the payment ledger.

## Consequences

Positive:

- simpler 30-day build
- easier manual reconciliation
- faster pilot
- avoids premature protocol coupling

Tradeoff:

- no trustless external settlement in v0.1
- future adapter design must be preserved
