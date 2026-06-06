# Submission Packet Template

## Task

`<task id>`

## Worker

`<worker id>`

## Submission Version

`v1`

## Summary

Briefly describe what was completed.

## Output

List files, links, packages, or deliverables.

## Provenance

- package hash:
- artifact hash manifest:
- generated at:

Workstream derives the locked project guide version, checker policy version, review policy version, revision policy version, and payment policy version from the task and server-side project policy records. The worker does not provide those versions in the submission packet.

## Artifact Hash Manifest

| Artifact | Hash | Size | Notes |
| --- | --- | ---: | --- |
| `<path-or-uri>` | `<sha256-or-reference>` | `<bytes>` | `<notes>` |

## Evidence

| Evidence ID | Type | Hash Or Reference | Bound Artifact Hash | Checker Run ID | Proves Which Artifact Or Claim |
| --- | --- | --- | --- | --- | --- |
| `<evidence id>` | `<type>` | `<hash-or-reference>` | `<artifact hash>` | `<checker run id>` | `<claim>` |

When relevant, include the command, environment, dataset/version, or generation settings that produced the evidence.

## Checker Notes

Any known checker considerations.

## Revision Replay

Only required for resubmissions.

| Prior Finding | Fix Summary | Evidence | Status |
| --- | --- | --- | --- |
| `<finding>` | `<fix>` | `<evidence>` | `closed` |

## Worker Attestation

I confirm this submission is original, complete, follows the locked project guide, and does not include prohibited confidential material, private source data, credentials, or copied platform artifacts.

I also confirm that any agent-assisted or tool-assisted work was reviewed by me before submission and that I am accountable for the submitted packet.
