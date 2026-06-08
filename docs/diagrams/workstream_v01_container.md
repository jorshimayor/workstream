# Workstream v0.1 Container View

This is the 30-day implementation architecture. It shows the deployable containers and internal runtime boundaries for the current build.

Future external origins, ERC-8004, ERC-8183, x402, OmniClaw, and USDC settlement are not active v0.1 dependencies. They remain later adapters behind the same records and interfaces.

```mermaid
flowchart TB
  subgraph People["People"]
    pm["Project Manager"]
    worker["Human-Agent Contributor"]
    reviewer["Reviewer"]
    operator["Operator / Admin"]
  end

  subgraph External["External Boundary"]
    flowAuth["Flow Auth<br/>Token issuer and human identity source"]
  end

  subgraph Workstream["Workstream v0.1"]
    frontend["React + Vite + TypeScript UI<br/>Internal operations dashboard"]
    api["FastAPI Backend<br/>Modular monolith API"]
    jobs["Async Job Boundary<br/>FastAPI background tasks now; durable workers later"]
    checker["Checker Runner<br/>Automated task and submission checks"]
    storageAdapter["Storage Interface<br/>Object-storage style API"]
  end

  subgraph Records["Durable Records"]
    db[("Postgres<br/>Projects, guides, tasks, submissions, checks, reviews, revisions, contribution records, payment records, reputation events, audit events")]
    fileStore["Local File Store Behind Interface<br/>R2/S3-compatible abstraction"]
  end

  pm --> frontend
  worker --> frontend
  reviewer --> frontend
  operator --> frontend

  frontend --> api
  api --> flowAuth
  api --> db
  api --> storageAdapter
  api --> jobs
  jobs --> checker
  checker --> db
  checker --> storageAdapter
  storageAdapter --> fileStore

  classDef current fill:#e7f5ff,stroke:#1c7ed6,color:#0b2942
  classDef record fill:#e6fcf5,stroke:#0ca678,color:#063b2c
  classDef external fill:#f1f3f5,stroke:#868e96,color:#212529

  class frontend,api,jobs,checker,storageAdapter current
  class db,fileStore record
  class pm,worker,reviewer,operator,flowAuth external
```

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
