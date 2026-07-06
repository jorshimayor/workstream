# Roles And Permissions

## Purpose

Workstream needs explicit permissions from the first version because review, payment, and override actions carry real operational risk.

## Roles

The Identity Issuer owns identity, audience, scopes, delegation, and token
signing. Workstream owns product roles and exact resource authorization keyed
by the issuer plus subject. Scopes are an outer request-class gate; they are not
proof that the subject is a reviewer, worker, project owner, or admin inside
Workstream.

In the current v0.1 bootstrap, route checks still read trusted role claims from
the verified `ActorContext` where a dedicated Workstream role-assignment table
does not exist yet. Those token roles are request context and provisioning
input, not the long-term source of truth. The role-assignment API must become a
Workstream-owned authorization layer keyed to `ActorIdentity`.

Local Workstream `ActorIdentity` and `ActorProfile` records may mirror observed
roles, profile state, skill tags, scope, and eligibility metadata, but persisted
profile rows do not grant route access by themselves.

| Role | Purpose |
| --- | --- |
| Admin | Controls project setup, policies, overrides, and user access. |
| Project Manager | Creates project guides, task batches, checker policies, review policies, revision policies, and payment policies. |
| Worker | Claims tasks, submits packets, and handles revisions. |
| Reviewer | Reviews checker-passed submissions and records decisions. |
| Finance | Updates payout status and payment references. |
| Auditor | Reads records and audit logs without modifying work. |

`project_owner` is not a route-authorizing Workstream role in v0.1. A project
owner is the external or internal source of project material or business terms.
It may be recorded as scoped actor profile/contact metadata, but it does not
approve Workstream machine-readable policies unless the verified token also
carries an authorized Workstream role such as admin or project manager.
The token claim key for trusted relationship metadata is
`workstream_relationship_profiles`; v0.1 accepts only
`profile_type="project_owner"` with non-empty `scope_type` and `scope_id`, plus
optional object `profile_metadata`.

Actor profile status is a workflow condition, not route permission. An
`observed` profile only records that Workstream saw the actor through a verified
token. An `active` profile can satisfy the profile side of a workflow gate, but
the route still requires the matching role in the current verified token.

## Permission Matrix

| Action | Admin | Project Manager | Worker | Reviewer | Finance | Auditor |
| --- | --- | --- | --- | --- | --- | --- |
| Create project | yes | no | no | no | no | no |
| Edit project guide | yes | yes | no | no | no | no |
| Create task | yes | yes | no | no | no | no |
| Claim task | no | no | yes | no | no | no |
| Submit task | no | no | own task only | no | no | no |
| Run checkers | yes | yes | own submission | no | no | no |
| Review submission | yes | no | no | yes | no | no |
| Review own submission | no | no | no | no | no | no |
| Request revision | yes | no | no | yes | no | no |
| Accept submission | yes | no | no | yes | no | no |
| Reject submission | yes | no | no | yes | no | no |
| Override checker failure | yes | no | no | no | no | no |
| Mark payout submitted | yes | no | no | no | yes | no |
| Mark paid | yes | no | no | no | yes | no |
| View audit log | yes | yes | own tasks only | reviewed tasks | payment records | yes |

## Separation Rules

- A worker cannot review their own submission.
- A reviewer cannot mark payment as paid.
- Finance cannot change review decisions.
- Project managers cannot silently override checker failures.
- Admin and project-manager operational intervention must use a separate
  audited override path. It must not masquerade as worker task claiming.
- Admin overrides must create an audit event with reason and evidence.

## Role Provisioning Direction

The Workstream role/provisioning layer is product-owned. A subject can exist in
the Identity Issuer and still have no Workstream access until Workstream creates
local actor and role records for that issuer plus subject.

The first durable shape should be:

```text
WorkstreamActor
- id
- issuer
- subject
- status

WorkstreamRoleAssignment
- actor_id
- role
- scope_type
- scope_id
- status
```

Role records may be global, project-scoped, task-scoped, or review-queue scoped.
One actor can hold multiple roles at once, such as worker plus reviewer, or
admin plus worker. Permission checks must evaluate the current role assignment
for the exact resource and still enforce workflow rules such as no self-review.

## First-Version Enforcement

The first version enforces permissions in application service or policy code,
not directly inside routers. The database records actor IDs, external subject,
issuer, role/claim context, auth source, actor identity, and actor profile
context for important events so later route decisions and workflow eligibility
can be audited.

Development auth, if enabled, must be impossible to use in production and must be visible in audit context.
