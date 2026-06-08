# Workstream v0.1 Container View

This is the 30-day implementation architecture. It shows the deployable containers and internal runtime boundaries for the current build.

Future external origins, ERC-8004, ERC-8183, x402, OmniClaw, and USDC settlement are not active v0.1 dependencies. They remain later adapters behind the same records and interfaces.

![Workstream v0.1 Container View](rendered/workstream_v01_container.svg)

Source: [workstream_v01_container.puml](workstream_v01_container.puml)

## Container Responsibilities

| Container | Responsibility |
| --- | --- |
| React + Vite UI | Internal project, queue, task, submission, review, payment, and reputation operations surfaces. |
| FastAPI backend | API contracts, workflow rules, auth dependency, lifecycle guards, module orchestration, audit writes. |
| Postgres | Record database for workflow state, policy context, submissions, checks, reviews, revisions, contribution records, payment records, reputation events, and audit history. |
| Storage interface | Stable file/evidence boundary that can use local storage in development and R2/S3-style object storage later. |
| Async job boundary | Non-blocking checker and background execution path. FastAPI background tasks are acceptable for simple local v0.1 jobs; durable workers come when retries, scheduling, isolation, or distribution are needed. |

## v0.1 Guardrails

- Postgres is used locally, in CI, and in production-like development.
- Workstream verifies Flow auth tokens and does not manage primary authentication.
- Task rules lock to guide and policy versions so upstream changes do not silently mutate in-progress work.
- Acceptance, payment status, and reputation are separate records.
- External origins, agent identity writes, task escrow, and settlement rails remain adapter boundaries until the internal loop is proven.
