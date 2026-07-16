# Review Packet Template

## Task

`<task id>`

## Submission

`<submission id>`

## Reviewer

`<reviewer id>`

## Routing And Independence

- assigned reason:
- conflict-of-interest attestation:
- contributor-reviewer pair risk:
- second review required:
- second review trigger:

## Decision

`accept | needs_revision | reject`

## Summary

Short decision summary.

## Evidence Cited For Acceptance

Required when decision is `accept`.

| Evidence ID | Artifact Hash | Claim Supported |
| --- | --- | --- |
| `<evidence id>` | `<artifact hash>` | `<claim>` |

## Findings

| Severity | Area | Issue | Required Fix | Evidence |
| --- | --- | --- | --- | --- |
| high | `<area>` | `<issue>` | `<fix>` | `<evidence>` |

## Checker Result Assessment

State whether checker output supports the decision.

## Prior Revision Closure

For resubmissions, list whether prior findings are closed.

## Revision Context

Required when reviewing a resubmission.

| Field | Value |
| --- | --- |
| context rebased | yes or no |
| prior guide version | `<guide version>` |
| next guide version | `<guide version>` |
| prior policy versions | `<checker/review/revision/payment policy versions>` |
| next policy versions | `<checker/review/revision/payment policy versions>` |
| change summary shown to contributor | `<summary>` |
| revision context audit event | `<audit event id>` |

## Payment Eligibility

State both determinations independently:

- reviewer `completed_review`: evaluate the ReviewLease-frozen compensation
  policy for every valid recorded decision; an explicit unpaid rule creates no
  award;
- submitter `accepted_submission`: evaluate the TaskAssignment-frozen
  compensation policy only for `accept`; `needs_revision` and `reject` create no
  submitter contribution or award.

## Contribution Records

Reviewer record, required for every valid recorded human Review:

- contribution record id:
- contribution type: `completed_review`
- review id:
- review lease id:
- reviewer actor id:
- submission id and version:
- artifact hash:

Submitter record, additionally required only when decision is `accept`:

- contribution record id:
- contribution type: `accepted_submission`
- accepted submission id and version:
- accepting review id:
- submitter actor id:
- task assignment id:
- artifact hash:

## Reviewer Confidence

`low | medium | high`
