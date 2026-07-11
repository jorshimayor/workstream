# Revision Replay

## Purpose

Revision replay prevents the common failure where a task comes back, the contributor says it is fixed, and nobody can prove which reviewer issues were actually closed.

Every resubmission after `NEEDS_REVISION` must map prior findings to concrete fixes.

## Required Replay Fields

For each prior finding:

- prior finding id
- prior severity
- prior area
- required fix
- contributor fix summary
- evidence reference
- contributor claim status: `fixed`, `disputed`, or `not_applicable`

Reviewer closure status:

- `closed_fixed`
- `closed_rebutted`
- `partially_closed`
- `still_open`
- `obsolete`

## Contributor Rules

The contributor must:

- address every high and medium finding
- attach evidence for every claimed fix
- explain any disputed finding directly
- avoid bundling multiple findings into vague "fixed all" notes

## Reviewer Rules

The reviewer must:

- check each replay row
- mark closure status per finding
- only introduce new findings when they are real and guide-grounded
- avoid moving goalposts unless the new issue blocks acceptance

## Blocking Policy

A resubmission cannot move to `REVIEW_PENDING` when:

- prior high finding has no replay row
- prior medium finding has no replay row
- replay row has no fix summary
- replay row has no evidence and project policy requires evidence

Low findings can be left unresolved if the reviewer marks them as informational.

## Revision Context Preparation

Before the contributor resumes a task in `NEEDS_REVISION`, Workstream prepares the next revision context.

That preparation compares the prior submission's locked project guide and policy versions with the current active guide and policy versions. Revision policy decides whether the next attempt keeps the prior context, rebases to the latest active context, or is blocked for project-manager repair.

A rebase does not change the prior submission. It only defines the guide and policy context for the next submission attempt.

When a rebase happens, the contributor must see:

- prior guide and policy versions
- next guide and policy versions
- guide or policy change summary
- reason the next attempt was rebased

The reviewer must see the same context change in the review packet. A reviewer cannot apply out-of-band guidance unless it was encoded into the guide, policy, task template, or checker contract that governed the attempt.

## Replay Table

| Prior Finding ID | Required Fix | Contributor Fix Summary | Evidence | Contributor Status | Reviewer Closure |
| --- | --- | --- | --- | --- | --- |
| `RF-001` | `<required fix>` | `<what changed>` | `<evidence id/file/log/link>` | `fixed` | `still_open` |

## Operational Standard

Revision replay is not optional paperwork. It is the memory of the system.

If the replay is weak, the platform fails the resubmission before a reviewer spends time on it.
