# Chunk Contract: WS-CON-001-03C - Contribution And Award Persistence

## Goal and risk

Persist immutable contribution/award truth against merged REV-03/REV-04 exact
targets. L1 history/payment risk.

## Allowed files

```text
backend/app/modules/contributions/{__init__,models,schemas,repository}.py
backend/app/modules/compensation/{models,schemas,repository}.py
backend/app/db/models.py
backend/alembic/versions/<next>_contribution_award_truth.py
backend/tests/{test_contributions,test_compensation,test_alembic}.py
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-03C.json
```

## Not allowed

```text
review model/service/composition edits
service, route, worker, receipt, artifact, reputation or PaymentRecord behavior
mutable/void/delete/adjust path, dependency or CI weakening
```

## Acceptance criteria

- [ ] Existing Submission is the version identity; exact project/review/lease/
  assignment/contributor lineage and immutable digests are constrained.
- [ ] DB enforces immutability/at-most-one but does not require a contribution
  child for staged Review writes.
- [ ] At-least-one per valid Review is deferred to CON-07 + REV-10 + preflight.
- [ ] No mutable/void/delete/adjust path or PaymentRecord/reputation schema.

## Verification and reviewers

Execute CON-03C in `../RUNTIME_VERIFICATION.md`; changed subsystems are at least
90 percent. Senior engineering, QA/test, security/auth, product/ops,
architecture, docs, reuse/dedup and test-delta are required. Stop if exact
REV-03/REV-04 targets are not merged.
