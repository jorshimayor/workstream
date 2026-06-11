# Independent Review Protocol

Workstream planning and major system changes receive multiple review perspectives before being treated as ready.

Implementation and specification chunks must run internal reviewer agents before PR review. The PR must include a changed `docs/internal_reviews/*.md` evidence file, and CI runs `scripts/check_internal_review_evidence.py` to block missing or incomplete evidence.

## Review Roles

### Senior Engineering Reviewer

Focus:

- architecture consistency
- code boundaries
- naming clarity
- lifecycle and data-model invariants
- implementation risk

### QA/Test Reviewer

Focus:

- test coverage
- real API and persistence behavior
- stale wording scans
- regression risk
- CI coverage

### Security/Auth Reviewer

Focus:

- auth boundary
- redaction and visibility
- sensitive metadata exposure
- audit integrity
- permission risks

### Product/Ops Reviewer

Focus:

- daily project manager workflow
- worker and reviewer workflow
- checker policy
- revision replay
- payment/reputation consistency
- auditability

### Risk Reviewer

Focus:

- privacy
- copied data risk
- payment disputes
- reviewer abuse
- fake evidence
- low-quality generated artifacts
- scope creep

## Required Output

Each review produces concise findings:

```text
severity:
file:
finding:
suggested_change:
```

Severity:

- `critical`: must fix before using the plan
- `high`: fix before implementation
- `medium`: fix during iteration
- `low`: note or polish

## Rule

No implementation or specification chunk is marked ready, pushed for PR review, or reported complete until required reviewer tracks have run, valid findings are fixed or documented, and every reviewer-agent session is closed.

## Task Readiness Gate

Before a task moves from `SCREENING` to `READY`, run the same review pattern at task scale:

- product/ops pass: task is worth doing and payment policy is clear
- guide pass: task follows the active project guide
- checker pass: required automated checks exist for the task type
- reviewer pass: acceptance criteria are reviewable
- adversarial pass: identify how the task could be gamed, faked, or disputed

The release decision is recorded as a status snapshot, not only discussed in chat.
