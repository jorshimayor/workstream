# Architecture Review

Review scope: markdown docs only.

## Findings

### High: Missing explicit event log as system source of truth

The domain model has task history implied, but no first-class event log. Workstream is an audit-heavy product, so state changes, checker runs, review decisions, overrides, payment transitions, and reputation updates need a durable event record.

Suggested change: add `TaskEvent` or `AuditEvent` to the domain model and architecture.

### High: Roles and permissions are not defined enough for v0.1

The flows mention admin, operator, worker, and reviewer, but there is no clear permission matrix. This can create unsafe overrides, self-review, or accidental payment changes.

Suggested change: add a v0.1 roles and permissions table.

### Medium: Guide and policy versioning should be tied to submissions

The docs say guides are versioned, but submissions and checker runs need to record the guide/policy version used at time of submission. Otherwise later guide edits can make old reviews ambiguous.

Suggested change: add guide version and policy version fields to submissions, checker runs, and reviews.

### Medium: Artifact storage needs immutability rule

The docs say submission is immutable after check starts, but artifact mutation rules should be explicit.

Suggested change: require artifacts to be content-addressed or hash-locked once a submission is locked.

