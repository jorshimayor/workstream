# ADR 0007: Execution Is Async-First

## Status

Accepted

## Context

Workstream will run checks, submissions, reviews, revision loops, payment reconciliation, notifications, and audit writes.

Some of these operations are quick request/response work. Others are long-running jobs that must not block API requests.

## Decision

Workstream is async-first.

FastAPI route handlers, service calls, database access, storage access, checker orchestration, and audit writes use async boundaries where I/O is involved.

Long-running checker and background work must not block request/response paths.

FastAPI background tasks are acceptable only for simple early v0.1 local jobs. Celery or an equivalent durable worker is required when work needs retries, scheduling, progress tracking, isolation, distributed execution, or operational durability.

## Consequences

Positive:

- API responsiveness does not depend on checker duration
- checker runs can produce durable running/completed state
- the system has a clear upgrade path from simple background work to durable workers
- synchronous-first shortcuts are rejected by architecture, not debated per chunk

Tradeoff:

- services must be designed around async database and I/O APIs from the start
- durable job infrastructure is introduced only when the workflow needs it
