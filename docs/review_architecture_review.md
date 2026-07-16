# Architecture Review

Review scope: markdown docs only.

## Findings

### High: Missing explicit event log as system source of truth

The domain model has task history implied, but no first-class event log.
Workstream is an audit-heavy product, so state changes, checker runs, review
decisions, overrides, compensation fulfillment transitions, and reputation
updates need a durable event record.

Suggested change: add `TaskEvent` or `AuditEvent` to the domain model and architecture.

### High: Roles and permissions are not defined enough for v0.1

The flows mention Access Administrator, Operator, Project Manager, Submitter, and Reviewer, but there is no clear permission matrix. This can create unsafe overrides, self-review, or accidental compensation changes.

Suggested change: add a v0.1 roles and permissions table.

### Medium: Guide and policy versioning should be tied to system records

The docs say guides are versioned, but tasks, submissions, checker runs, reviews, and payments need to record the guide/policy version used by the locked task contract. Otherwise later guide edits can make old reviews ambiguous.

Suggested change: add server-stamped locked guide and policy version fields to task-owned system records. Submitters should submit against the task id without restating those versions.

### Medium: Artifact storage needs immutability rule

The docs say submission is immutable after check starts, but artifact mutation rules should be explicit.

Suggested change: require artifacts to be content-addressed or hash-locked once a submission is locked.
