# Roles And Permissions

This supporting note points to the canonical operator matrix in
`docs/operations_roles_permissions.md`, ADR 0012, and
`docs/spec_authorization_service.md`.

## Canonical Roles

Administrative grants:

- Access Administrator
- Operator
- Project Manager
- Finance Authority
- Audit Authority

Exact-project contributor grants:

- Submitter
- Reviewer
- Both

The external Flow token identifies a subject and supplies verified coarse
scope; it does not assign these roles. Workstream stores grants locally and
evaluates them against canonical resources and lifecycle guards.

Contributor is the umbrella human product term. Exact-project Submitter,
Reviewer, or Both grants determine candidate authority. Celery, checker, setup,
and background workers are internal services, not human product roles. Administrative grants
alone never authorize submission or review.

## Independence

- No actor administratively grants or revokes their own authority.
- A submitter cannot be the sole reviewer for their own work.
- Review decisions remain `accept`, `needs_revision`, or `reject` and require an
  eligible exact-project reviewer grant plus review lifecycle guards.
- Finance Authority cannot change review decisions or contribution records.
- Audit Authority cannot mutate product state.

## Recovery

Normal project repair uses covered Project Manager permission
`project.task.manage`. Operator recovery is limited to the registered
permissions `operations.task.start_override`,
`operations.submission_gate.repair`, `operations.checker.retry`, and the
WS-REV-owned `review.lease.force_release`.

Recovery requires exact resource scope, a reason, matched grant/permission, and
append-only evidence. It does not erase prior evidence or bypass immutable
submission, review, contribution, or compensation rules.
