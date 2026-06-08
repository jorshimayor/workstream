# Workstream v0.1 Backend Component View

This is the C4-style component view for the FastAPI modular monolith.

The backend stays one deployable service while keeping module boundaries strict. Routers handle HTTP, services own workflow rules, repositories own database access, schemas own API contracts, and adapters own external boundaries.

```mermaid
flowchart TB
  client["React UI / API Client"]

  subgraph API["FastAPI Backend"]
    apiRouter["API Router<br/>/api/v1"]
    authDep["Current Actor Dependency<br/>Flow token -> ActorContext"]

    subgraph Modules["Domain Modules"]
      projects["Projects Module<br/>projects, guides, checker/review/revision/payment policies"]
      tasks["Tasks Module<br/>task queue, assignment, claim, status transitions"]
      submissions["Submission Module<br/>submission packets, evidence, artifact manifests"]
      checks["Checker Module<br/>checker runs, results, blocking severities"]
      reviews["Review + Revision Module<br/>accept, needs_revision, reject, findings, revision replay"]
      contribution["Contribution Module<br/>accepted-work certification"]
      payment["Payment Module<br/>payment status and references"]
      reputation["Reputation Module<br/>worker/reviewer outcome events"]
      audit["Audit Module<br/>append-only lifecycle events"]
    end

    subgraph Shared["Shared Backend Boundaries"]
      schemas["Pydantic Schemas<br/>request/response contracts"]
      services["Services<br/>workflow and policy rules"]
      repos["Repositories<br/>SQLAlchemy async queries"]
      lifecycle["Lifecycle Guards<br/>allowed state transitions"]
      permissions["Permission Policies<br/>role and object-level access"]
      storagePort["Storage Port<br/>object-storage abstraction"]
      authPort["Auth Verifier Interface"]
    end

    flowAdapter["Flow Auth Adapter"]
    storageAdapter["Local Storage Adapter<br/>R2/S3-compatible contract"]
  end

  db[("Postgres")]
  files["File Store"]
  flowAuth["External Flow Auth"]

  client --> apiRouter
  apiRouter --> authDep
  authDep --> authPort
  authPort --> flowAdapter
  flowAdapter --> flowAuth

  apiRouter --> projects
  apiRouter --> tasks
  apiRouter --> submissions
  apiRouter --> checks
  apiRouter --> reviews
  apiRouter --> contribution
  apiRouter --> payment
  apiRouter --> reputation

  projects --> services
  tasks --> services
  submissions --> services
  checks --> services
  reviews --> services
  contribution --> services
  payment --> services
  reputation --> services

  services --> schemas
  services --> lifecycle
  services --> permissions
  services --> repos
  services --> storagePort
  services --> audit

  repos --> db
  audit --> repos
  storagePort --> storageAdapter
  storageAdapter --> files

  classDef current fill:#e7f5ff,stroke:#1c7ed6,color:#0b2942
  classDef shared fill:#edf2ff,stroke:#5c7cfa,color:#17224d
  classDef record fill:#e6fcf5,stroke:#0ca678,color:#063b2c
  classDef external fill:#f1f3f5,stroke:#868e96,color:#212529

  class apiRouter,authDep,projects,tasks,submissions,checks,reviews,contribution,payment,reputation,audit,flowAdapter,storageAdapter current
  class schemas,services,repos,lifecycle,permissions,storagePort,authPort shared
  class db,files record
  class client,flowAuth external
```

## Component Contract

| Boundary | Rule |
| --- | --- |
| Routers | HTTP only: parse request, resolve actor/session, call services, map domain errors. |
| Services | Business rules: status transitions, policy locks, authorization decisions, audit intent. |
| Repositories | SQLAlchemy 2.x async persistence only; no HTTP or auth decisions. |
| Schemas | Pydantic input/output contracts and API validation. |
| Auth adapter | Verifies external Flow tokens and returns `ActorContext`. |
| Storage port | Hides local filesystem, R2, S3, or compatible object storage behind stable object references. |
| Audit module | Writes append-only evidence for state changes and sensitive workflow events. |

## Current Module Priority

The first 30 days move through the loop in this order:

```text
Projects and guides
-> tasks and assignment
-> submission packets and evidence
-> checker runs
-> review and revision
-> contribution record
-> payment status
-> reputation event
```
