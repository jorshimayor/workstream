# Roles And Permissions

This is a supporting note. The canonical permission matrix lives in `docs/operations_roles_permissions.md`.

`Operator` is a product persona, not a separate permission role. Operator work is performed by project managers, workers, reviewers, admins, or finance users depending on the action.

## v0.1 Roles

### Admin

Can:

- create projects
- edit project guides
- configure checker policies
- configure review policies
- configure revision policies
- configure payment policies
- override task status with audit reason
- assign reviewers
- mark payments as submitted or paid
- approve project guide versions
- suspend workers, reviewers, or projects during fraud or confidentiality review

### Worker

Can:

- claim or assign tasks if project policy allows
- create submissions
- attach evidence
- respond to needs-revision findings
- add rebuttal notes

Cannot:

- review own submission
- mark task accepted
- mark payment paid
- edit submitted artifacts in place
- change task acceptance criteria after claiming the task

### Reviewer

Can:

- review submissions assigned to them
- create structured findings
- accept, needs revision, or reject
- close or reopen revision findings

Cannot:

- review own submission as sole reviewer
- edit submitted artifacts
- change payment status
- review a submission from a worker they directly manage unless project policy allows disclosed review
- accept a task with unresolved high-severity checker failures unless an admin override exists

### Finance

Can:

- view accepted tasks
- reconcile pending payouts
- mark payout submitted
- mark paid with payment reference

Cannot:

- accept tasks unless also assigned reviewer by policy
- change accepted amount without a payment adjustment record

## Independence Rule

A user cannot be the submitter and sole reviewer for the same task.

Project policy may require:

- one reviewer
- two reviewers
- admin review for high-value tasks
- escalation review for disputed findings

High-value tasks, disputed tasks, and suspected fraud/confidentiality tasks require independent second review before acceptance or payment.

## Override Rule

Admin overrides require:

- actor
- reason
- old value
- new value
- timestamp
- linked evidence or incident id

Overrides must be visible in task history.

Overrides do not change authorship, erase prior failed checks, or remove payment dispute history.

## Collusion And Abuse Controls

The platform flags:

- repeated accept decisions between the same worker and reviewer pair
- reviewers whose accept decisions are frequently overturned
- workers whose evidence hashes or text patterns repeat across unrelated tasks
- fast accept decisions with no evidence cited
- payment edits after acceptance without adjustment records
