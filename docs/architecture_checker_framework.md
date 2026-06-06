# Checker Framework

## Purpose

The checker framework protects reviewer time and enforces project rules before human review.

It does not replace reviewers. It blocks structurally broken work and gives reviewers reliable evidence.

## Checker Result Contract

Every checker returns:

```json
{
  "name": "check_submission_packet",
  "status": "pass",
  "severity": "high",
  "message": "Submission packet is complete.",
  "suggested_fix": null,
  "evidence": [],
  "metadata": {}
}
```

Status:

- pass
- warn
- fail

Severity:

- low
- medium
- high

## Checker Registry

Every checker is registered with a stable definition before projects reference it.

Definition fields:

- `checker_id`
- `name`
- `phase`
- `version`
- `default_severity`
- `default_blocks_review`
- `worker_visible`
- `description`

Phase:

- project_activation
- task_screening
- submission_quality
- pre_review_gate
- lifecycle_transition
- payment_reconciliation

Checker names must not drift between project guides, policy templates, implementation code, and checker results. New behavior uses a new checker version or a new checker id.

## Blocking Policy

Default:

- high fail blocks human review
- medium fail creates reviewer warning
- low fail creates informational note

Project guides can override this by declaring stricter policies.

The checker framework is conservative. It blocks objective structural failures and warns on judgment-heavy issues. Human reviewers own final quality judgment.

## Required Core Checkers

### check_task_schema

Validates task record fields required by the project guide.

### check_project_guide_attached

Ensures the task has a guide version attached.

### check_payment_policy_present

Ensures the task has base amount and currency.

### check_submission_packet

Ensures submission has summary, output reference, and package/evidence where required.

### check_evidence_present

Ensures accepted work can be audited.

### check_evidence_integrity

Ensures the submission packet records content hashes for uploaded artifacts and that checker runs use those exact hashes.

### check_acceptance_criteria_present

Ensures a task has rubric or acceptance criteria.

### check_required_files

Validates project-specific required files.

### check_forbidden_files

Blocks known forbidden files, secrets, private keys, copied internal data, or files forbidden by the project guide.

Default forbidden patterns include:

- private keys
- API tokens
- `.env`
- copied confidential client/source files
- generated low-quality helper artifacts banned by the project guide
- files not allowed in the submission packet

### check_confidentiality_attestation

Ensures the worker explicitly attests that the submission does not contain prohibited client data, private source material, credentials, or copied platform artifacts.

### check_low_quality_generated_artifacts

Flags repeated low-quality generated patterns banned by the project guide, such as generic helper files, hidden-test leakage patterns, fabricated model files, placeholder evidence, or boilerplate reports that do not prove task-specific work.

### check_prior_revision_closed

For resubmissions, ensures prior review findings are addressed in a revision replay.

### check_status_transition

Validates that requested lifecycle movement is legal.

### check_ready_gate

Ensures the task has passed the project-specific release checklist before entering `READY`.

### check_preflight_evidence

Ensures the submission has a stored preflight evidence record with checker results, package references, artifact hashes, and review-readiness confirmation.

### check_pre_review_gate

Runs project-configured reviewer simulation, adversarial pass, or readiness guard before moving a submission to human review.

This is optional by project policy, but recommended for high-value work.

## Gate Mapping

Project activation gate:

- `check_project_guide_attached`
- `check_payment_policy_present`
- project-specific guide completeness checks

Task screening gate:

- `check_task_schema`
- `check_acceptance_criteria_present`
- `check_ready_gate`
- `check_status_transition`

Submission quality gate:

- `check_submission_packet`
- `check_evidence_present`
- `check_evidence_integrity`
- `check_required_files`
- `check_forbidden_files`
- `check_confidentiality_attestation`
- `check_low_quality_generated_artifacts`
- `check_prior_revision_closed`
- `check_preflight_evidence`

Pre-review gate:

- `check_pre_review_gate`

The first two gates replace external origin qualification and task ingestion for v0.1. Origin qualification and webhook drop notifications are future adapter concerns.

## Project-Specific Checkers

Each project can register specialized checkers.

Examples:

- code task package checker
- rubric formatting checker
- document citation checker
- data annotation completeness checker
- security artifact checker
- plagiarism or originality checker
- hidden-test packaging checker
- no-confidential-source-data checker
- reviewer-simulation checker for first-of-kind or high-value tasks
- reviewer simulation gate
- prior feedback checklist checker

## Checker Run Flow

```text
Submission received
-> create CheckerRun
-> load project CheckerPolicy
-> run required checkers
-> store CheckerResult records
-> calculate blocking status
-> issue ReadinessCertificate when no blocking failures remain
-> move to REVIEW_PENDING or NEEDS_REVISION
```

The checker run must bind to one immutable submission version. If the worker uploads a replacement file, the platform creates a new submission version and reruns checks.

If a checker crashes or cannot run because of platform infrastructure, the checker run remains failed as an infrastructure failure and the task does not move to human review. The retry or admin action is recorded in audit history.

## Readiness Certificate

When all blocking checks pass, the checker service issues a readiness certificate.

The certificate records:

- submission id
- checker run id
- checker policy version derived from the locked task context
- artifact hash manifest
- blocking failure count
- warning count
- issued timestamp

This gives reviewers a clear proof that they are reviewing the same packet that passed automated checks.

## Checker Output Visibility

Workers see:

- failed checker name
- severity
- message
- suggested fix when safe

Reviewers see:

- all checker output
- evidence references
- full metadata where allowed

Admins see:

- full logs
- internal rule IDs
- override controls

## Admin Override

An admin can override a high-severity checker failure only with:

- reason
- actor
- timestamp
- affected checker
- evidence

Overrides are rare and visible in audit logs.

Overrides cannot delete checker results. They only create an auditable exception record.

## Checker Quality Metrics

Track:

- false positive rate
- false negative rate
- most common failures
- checks that reviewers repeatedly ignore
- checks that predict rejection

Checker quality is reviewed weekly during the first month. A repeated reviewer finding becomes one of:

- a new checker
- a stronger project guide rule
- a template update
- a reviewer training note
- a ProjectLesson record for operating review

## Checker Blind-Spot Review

Every week, compare accepted submissions, rejected submissions, and needs-revision findings against checker output.

Look for:

- reviewer findings that no checker predicted
- checker warnings reviewers always ignore
- high-severity checker failures that admins repeatedly override
- evidence that passed structurally but did not prove the claim
- generated or copied artifacts that evade forbidden-file rules

Each blind spot becomes a guide update, checker update, reviewer policy update, revision policy update, or payment policy update.

## First Implementation

The first checker runner can be simple:

- async-first execution
- local background worker process or FastAPI background task for simple local v0.1 jobs
- markdown/json output
- attached logs

The request path does not block on long-running checker execution. A checker run is created as `running`, then completed by background execution.

Use Celery or an equivalent durable queue when checker execution needs retries, scheduled jobs, progress reporting, worker isolation, or distributed execution.
