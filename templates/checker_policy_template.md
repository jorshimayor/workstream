# Checker Policy Template

## Project

`<project name>`

## Policy Version

`v1`

## Blocking Rule

High-severity failed checks block human review.

Medium and low severities are visible to reviewers unless this policy overrides them.

## Required Checkers

| Checker | Severity | Blocks Review | Purpose |
| --- | --- | --- | --- |
| `check_project_guide_attached` | high | yes | Task must use a versioned project guide. |
| `check_task_schema` | high | yes | Task must include required project fields. |
| `check_acceptance_criteria_present` | high | yes | Task must include reviewable acceptance criteria. |
| `check_ready_gate` | high | yes | Task must pass screening before release. |
| `check_payment_policy_present` | high | yes | Task must have base amount and currency. |
| `check_submission_packet` | high | yes | Submission must include required packet fields. |
| `check_evidence_present` | high | yes | Submission must include audit evidence. |
| `check_evidence_integrity` | high | yes | Evidence and checker runs must bind to submitted artifacts. |
| `check_prior_revision_closed` | high | yes | Resubmission must map prior findings to fixes. |
| `check_forbidden_files` | high | yes | Submission must not include prohibited files or data. |
| `check_confidentiality_attestation` | high | yes | Worker must attest no prohibited confidential material is present. |
| `check_low_quality_generated_artifacts` | medium | no | Flags project-banned generated or boilerplate patterns. |
| `check_preflight_evidence` | high | yes | Submission must include preflight evidence before review. |

## Checker Registry Fields

Each checker definition specifies:

- checker id
- phase
- version
- default severity
- default blocking behavior
- worker-visible message policy

## Project-Specific Checkers

| Checker | Severity | Blocks Review | Purpose |
| --- | --- | --- | --- |
| `<checker name>` | `<low/medium/high>` | `<yes/no>` | `<why it exists>` |

## Worker-Visible Messages

Workers may see:

- checker name
- status
- severity
- safe failure message
- suggested fix

Workers must not see:

- hidden evaluator logic
- private reviewer notes
- confidential source metadata

## Admin Override

Allowed only with:

- actor
- timestamp
- checker name
- reason
- evidence

## Review Cadence

Review this checker policy weekly during the pilot.
