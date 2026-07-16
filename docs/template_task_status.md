# Task Status Template

## Task

`<task id>`

## Project

`<project id>`

## Current State

`DRAFT | SCREENING | READY | CLAIMED | IN_PROGRESS | SUBMITTED | EVALUATION_PENDING | REVIEW_PENDING | NEEDS_REVISION | ACCEPTED | REJECTED | CANCELLED`

## Locked Guide Version

`<guide version>`

## Source

- source type: `manual | markdown_import | csv_import`
- source reference:
- source payload hash:
- import batch id:

## Owner

- task creator:
- contributor:
- reviewer:
- queue owner:

## Latest Decision

- decision:
- actor:
- timestamp:
- reason:
- linked evidence:

## Screening Rejection

Use only when a draft/imported task fails before `READY`.

- gate: `project_activation | task_screening | submission_quality`
- reason code:
- fix required:
- source task id:
- retry id:
- notification status:

External-origin webhook drop delivery is a future adapter concern. In v0.1 this section records internal screening/import rejection.

## Contribution Records

- reviewer contribution record id:
- reviewer contribution type: `completed_review`
- review id and review lease id:
- submitter contribution record id, only on `accept`:
- submitter contribution type, only on `accept`: `accepted_submission`
- compensation award ids, when the frozen rules are payable:

## Open Items

| Item | Owner | Severity | Due | Status |
| --- | --- | --- | --- | --- |
| `<item>` | `<owner>` | `high` | `<date>` | `open` |

## History

| Time | State | Actor | Reason |
| --- | --- | --- | --- |
| `<time>` | `<state>` | `<actor>` | `<reason>` |
