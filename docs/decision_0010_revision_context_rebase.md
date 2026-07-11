# ADR 0010: Revision Context Rebase Is Controlled By Policy

## Status

Accepted

## Context

Project guidance can change while a task is already in progress or under review.

If rule changes live only in Slack, chat, or memory, contributors can be punished for missing an out-of-band update and reviewers can apply inconsistent standards. If guide changes silently mutate prior submissions, Workstream loses auditability.

Workstream needs both fairness and correctness:

- a submitted attempt must remain tied to the exact guide and policy versions it used
- a revised attempt may need the latest active guide and policy context before the contributor resumes
- the contributor and reviewer must be able to see what changed

## Decision

Submitted attempts are immutable. Each submission remains evaluated against the locked project guide, checker policy, review policy, revision policy, and payment policy versions stamped on that submission.

When a task enters `NEEDS_REVISION`, Workstream runs a revision context preparation step before the contributor resumes. That step compares the submission's locked guide and policy context with the current active project guide and policy context.

Revision policy controls whether the next attempt:

- keeps the prior locked context
- rebases to the current active guide and policy context
- is blocked for project-manager repair when the task setup is incomplete or unsafe

Every revision context preparation must record its outcome. When the next attempt keeps the prior context, Workstream records that no rebase occurred and why. When the next attempt is rebased, Workstream records:

- task id
- prior submission id and version
- prior locked guide and policy versions
- next locked guide and policy versions
- rebase reason
- guide or policy change summary shown to the contributor
- actor or system process that prepared the revision context
- audit event id

The contributor must see the old context, the new context, and the change summary before submitting the revised attempt when a rebase occurs. The reviewer packet must also show that the revised attempt used a different guide or policy context.

Out-of-band guidance has no acceptance force until it is encoded in one of:

- project guide
- checker policy
- review policy
- revision policy
- payment policy
- task template
- checker implementation governed by the checker policy

Acceptance-affecting checker implementation changes must be tied to visible guide, policy, or checker-policy context. When those changes affect a rebased revision attempt, the contributor-visible change summary must describe the new requirement without exposing private detection details.

## Consequences

Positive:

- contributors are not expected to monitor chat to discover rule changes
- reviewers can see which standards governed each attempt
- guide and policy updates can improve future revisions without mutating prior submissions
- repeated lessons become durable guide, checker, review, revision, payment, or template changes

Tradeoff:

- revision preparation needs an explicit audit record
- revision replay must show context changes, not only finding closure
- services must keep submitted-attempt immutability separate from next-attempt preparation
