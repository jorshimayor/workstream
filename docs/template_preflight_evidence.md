# Preflight Evidence Template

## Task

`<task id>`

## Submission

`<submission id / version>`

## Locked Project Guide Version

`<guide version>`

## Locked Checker Policy Version

`<checker policy version>`

These values come from Workstream's task context and checker run records. They are not worker-provided submission fields.

## Preflight Summary

State what was checked before review.

## Checks Run

| Check | Result | Checker Run ID | Evidence ID | Evidence |
| --- | --- | --- | --- | --- |
| `<checker>` | `<pass/warn/fail>` | `<checker run id>` | `<evidence id>` | `<log/hash/reference>` |

## Package Evidence

- package path or URI:
- package hash:
- artifact count:
- required files present:
- artifact hash manifest:
- evidence ids bound to artifact hashes:

## Review Readiness

Confirm:

- task guide is attached
- acceptance criteria exist
- output package exists
- evidence exists
- evidence ids exist
- blocking checker failures are closed or overridden
- revision replay exists when required

## Known Warnings

List non-blocking warnings reviewers see.
