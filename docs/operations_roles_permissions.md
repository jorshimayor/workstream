# Roles And Permissions

## Purpose

Workstream needs explicit permissions from the first version because review, payment, and override actions carry real operational risk.

## Roles

Roles come from trusted Flow token claims, local Workstream role mappings, or an explicitly documented combination of both. The backend resolves those into a current actor context before protected workflow actions run.

| Role | Purpose |
| --- | --- |
| Admin | Controls project setup, policies, overrides, and user access. |
| Project Manager | Creates project guides, task batches, checker policies, and review policies. |
| Worker | Claims tasks, submits packets, and handles revisions. |
| Reviewer | Reviews checker-passed submissions and records decisions. |
| Finance | Updates payout status and payment references. |
| Auditor | Reads records and audit logs without modifying work. |

## Permission Matrix

| Action | Admin | Project Manager | Worker | Reviewer | Finance | Auditor |
| --- | --- | --- | --- | --- | --- | --- |
| Create project | yes | no | no | no | no | no |
| Edit project guide | yes | yes | no | no | no | no |
| Create task | yes | yes | no | no | no | no |
| Claim task | yes | yes | yes | no | no | no |
| Submit task | yes | no | own task only | no | no | no |
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
- Admin overrides must create an audit event with reason and evidence.

## First-Version Enforcement

The first version enforces permissions in application service or policy code, not directly inside routers. The database records actor IDs, external subject, issuer, role/claim context, and auth source for important events so later role enforcement can be audited.

Development auth, if enabled, must be impossible to use in production and must be visible in audit context.
