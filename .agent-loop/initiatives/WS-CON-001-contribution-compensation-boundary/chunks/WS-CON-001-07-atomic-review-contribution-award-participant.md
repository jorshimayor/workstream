# Chunk Contract: WS-CON-001-07 - Atomic Review Contribution And Award Participant

## Parent initiative

`WS-CON-001` - Contribution Record And Compensation Boundary

## Goal

Implement the mandatory database-local participant that creates reviewer and
accept-only submitter contributions, deterministic awards, pending evidence
projections, audit, and outbox events in the caller-owned Review transaction.

## Why this chunk exists

Contribution recognition must never lag behind or disagree with a committed
human Review, and no external system can participate in that atomic commit.

## Approved plan reference

- `../INTENT.md`
- `../PLAN.md`
- `../CHUNK_MAP.md`

## Risk class

L1 payment/canonical judgment/cross-domain transaction; SLA P1.

## Allowed files

```text
backend/app/modules/contributions/schemas.py
backend/app/modules/contributions/repository.py
backend/app/modules/contributions/service.py
backend/app/modules/compensation/repository.py
backend/app/modules/compensation/service.py
backend/app/modules/compensation/ports.py
backend/tests/test_contributions.py
backend/tests/test_compensation.py
backend/tests/test_authorization.py only decision-causation evidence proof
backend/tests/test_outbox.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-07.json
```

## Not allowed

```text
Review decision/transition policy in contribution code
review service, model, route, or composition wiring
public route registration
ContributionRecordRequested compatibility event
AUTH catalogue/grants/kernel edits or new materialize permissions
external adapter, broker, or artifact provider calls
mutable/delete/void/adjust contribution/award path
reputation scoring
```

## Acceptance criteria

- [ ] Every committed Review creates exactly one reviewer
  `completed_review`; `accept` additionally creates one submitter
  `accepted_submission`; needs_revision/reject create none for submitter.
- [ ] Existing Submission/assignment/lease/Review/project/contributor chains and
  immutable artifact digest are exact and DB-validated.
- [ ] Reviewer awards use lease-frozen version and are decision-neutral;
  submitter awards use assignment-frozen version; explicit unpaid creates none.
- [ ] Participant uses caller AsyncSession, flushes, never commits, and retains
  originating `review.decision` AuthorizationDecision as causation.
- [ ] Participant accepts only a typed allowed `review.decision` whose actor,
  action, Review/lease/Submission/project resource, request, and correlation
  facts match the locked caller transaction; denied, stale, unrelated, or
  mismatched evidence is rejected. REV-10 owns final transaction-time authority
  revalidation and mandatory injection.
- [ ] Each contribution creates one pending evidence projection and one stable
  projection request event in the same transaction.
- [ ] Versioned `ContributionRecorded`, `CompensationAwardCreated`,
  `CompensationFulfillmentRequested`, and
  `ContributionEvidenceProjectionRequested` use the shared outbox with
  deterministic IDs/digests and no sensitive/provider data. These exact tokens
  are feature-owned; the generic outbox never aliases them.
- [ ] Direct participant fault injection proves its contribution/award/audit/
  outbox writes roll back with the caller transaction. REV-10 owns cross-domain
  Review/task/lease rollback and hidden-composition proof.
- [ ] Exact replay returns one logical set; changed/concurrent replay conflicts
  cleanly; no optional/no-op production participant exists.
- [ ] Claims/releases/expiry/revocation/admin closure/artifact failure create no
  contribution or award.
- [ ] No production composition or OpenAPI changes; new/changed modules >=90
  percent and global floor >=78 percent.

## Verification commands

Execute the exact CON-07 expansion in `../RUNTIME_VERIFICATION.md`; the same run
proves each changed subsystem at least 90 percent.

## Required reviewers

Baseline plus architecture, security/auth, product/ops, docs, reuse/dedup, and
test-delta.

## Human review focus

Creation matrix, exact frozen sources, no current-policy lookup, atomic rollback,
decision causation, replay/concurrency, and the explicit REV-10 integration
handoff.

## Stop conditions

Stop if REV decision/revision schemas are not stable, shared audit/outbox cannot
join caller transaction, or any external call is required before commit.
