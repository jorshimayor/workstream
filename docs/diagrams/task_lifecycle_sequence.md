# Task Lifecycle Sequence

This sequence shows the v0.1 operating loop from project guide to accepted contribution and payment/reputation records.

It is intentionally separate from the future identity and settlement diagram. v0.1 records payment status and reputation events internally; it does not execute on-chain settlement or write portable agent reputation.

```mermaid
sequenceDiagram
  autonumber
  actor PM as Project Manager
  actor Contributor as Human-Agent Contributor
  actor Reviewer as Reviewer
  participant UI as React UI
  participant API as FastAPI Backend
  participant Auth as Flow Auth Verifier
  participant Authorization as Workstream Authorization
  participant DB as Postgres
  participant Storage as Storage Abstraction
  participant Checks as Checker Runner

  PM->>UI: Create project, guide, and policies
  UI->>API: POST project / guide / policies
  API->>Auth: Verify Flow token
  Auth-->>API: Verified external identity
  API->>Authorization: Resolve actor profile and local grants
  Authorization->>Authorization: require(project.create/configure, candidates, resource/lifecycle guards)
  Authorization-->>API: Allowed AuthorizationContext with matched Project Manager grant
  API->>DB: Persist draft guide and checker/review/revision/payment policy context

  PM->>UI: Activate guide
  UI->>API: POST activate guide
  API->>Authorization: require(guide.activate, candidates, project/lifecycle guards)
  Authorization-->>API: Allowed with matched grant and permission
  API->>DB: Validate required policy context and mark guide active
  API->>DB: Audit project activation

  PM->>UI: Create and screen task
  UI->>API: POST task, then screen/release
  API->>Authorization: require(task.manage, candidates, project/lifecycle guards)
  Authorization-->>API: Allowed with matched grant and permission
  API->>DB: Lock active guide and policy versions onto task
  API->>DB: Move DRAFT -> SCREENING -> READY
  API->>DB: Audit transitions

  Contributor->>UI: Claim task
  UI->>API: POST claim
  API->>Auth: Verify Flow token
  Auth-->>API: Verified external identity
  API->>Authorization: Resolve actor profile and project grants
  Authorization->>Authorization: require(task.claim, candidates, assignment/resource/lifecycle guards)
  Authorization-->>API: Allowed AuthorizationContext with matched submitter/both grant
  API->>DB: Validate visibility, qualification, skill tags, and READY status
  API->>DB: Create assignment and move READY -> CLAIMED -> IN_PROGRESS

  Contributor->>UI: Submit packet
  UI->>API: POST submission packet with evidence and artifact manifest
  API->>Auth: Verify Flow token
  Auth-->>API: Verified external identity
  API->>Authorization: require(submission.create, candidates, ownership/resource/lifecycle guards)
  Authorization-->>API: Allowed with matched submitter/both grant
  API->>Storage: Store or reference artifacts through storage abstraction
  API->>DB: Create immutable submission version
  API->>DB: Lock submission version and audit submitter-owned finalization

  API->>Checks: Enqueue automated checks through Celery
  Checks->>Storage: Read referenced artifacts
  Checks->>DB: Persist checker run and results
  Checks->>DB: Keep task EVALUATION_PENDING while pre-review gate runs
  Checks->>DB: Move to REVIEW_PENDING, NEEDS_REVISION, or internal task_setup_blocked

  Reviewer->>UI: Review packet
  UI->>API: Submit review decision
  API->>Auth: Verify Flow token
  Auth-->>API: Verified external identity
  API->>Authorization: Resolve actor profile and project grants
  Authorization->>Authorization: require(review.decision, candidates, assignment/resource/lifecycle guards)
  Authorization-->>API: Allowed AuthorizationContext with matched reviewer/both grant
  API->>DB: Store decision: accept, needs_revision, or reject
  API->>DB: Create reviewer completed_review contribution and applicable award

  alt needs_revision
    API->>DB: Create revision requirements from findings
    Contributor->>UI: Submit revision replay
    UI->>API: POST revision replay and new submission version
    API->>DB: Link replay to prior findings
    API->>Checks: Run checks again
  else accept
    API->>DB: Create submitter accepted_submission contribution
    API->>DB: Create applicable submitter award/payment record
    API->>DB: Create reputation event
    API->>DB: Audit acceptance
  else reject
    API->>DB: Store rejection decision and findings
    API->>DB: Apply reviewer reputation effects; no submitter contribution
    API->>DB: Audit rejection
  end
```

## Lifecycle Invariants

- A task cannot enter `READY` without locked guide, checker, review, revision, and payment policy context.
- A contributor submission creates a new immutable submission version; locked artifacts are not edited in place.
- Review decisions are exactly `accept`, `needs_revision`, or `reject`.
- `needs_revision` starts a revision loop and must replay prior findings.
- Every valid human review creates a reviewer contribution. Accepted work
  additionally creates a submitter contribution before compensation or
  reputation records.
- Payment status is separate from task acceptance.
