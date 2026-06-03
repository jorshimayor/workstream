# Final Architecture Review

Reviewer role: Systems Architecture Reviewer.

Scope: markdown planning package.

## Findings

### High: Task status and payment status must remain separate

Finding:

This is now correctly handled in the core state machine. Payment follow-up is derived from payment records, not a task queue lane.

Suggested change:

Keep `PAID` out of task lifecycle states and enforce payment transitions in the payment ledger.

Status: fixed in `architecture/lifecycle_state_machine.md`, `operations/payment_reputation.md`, and `operations/queue_policy.md`.

### High: Auditability is represented but must be implemented early

Finding:

The data model includes audit events, but the implementation must treat audit logging as P0, not later observability.

Suggested change:

Every status transition, checker override, review decision, payment transition, and guide activation writes an audit event.

Status: documented in `architecture/data_model.md` and `architecture/lifecycle_state_machine.md`.

### Medium: The v0.1 stack decision is clear

Finding:

The plan now chooses Next.js/TypeScript/Postgres for v0.1. This avoids wasting the first month debating stack.

Suggested change:

Only introduce Go services later for checker runners or high-throughput workers.

Status: addressed in `architecture/system_architecture.md`.

### Medium: Artifact immutability is correctly captured

Finding:

Submission versions, artifact hashes, and checker-run binding to exact submission versions are documented.

Suggested change:

Implement hash manifests and prevent in-place artifact mutation.

Status: documented in `architecture/data_model.md`, `architecture/lifecycle_state_machine.md`, and `architecture/checker_framework.md`.

