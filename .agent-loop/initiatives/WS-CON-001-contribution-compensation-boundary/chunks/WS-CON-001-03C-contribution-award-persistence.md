# Chunk Contract: WS-CON-001-03C - Contribution And Award Persistence

## Goal and risk

Persist immutable contribution/award truth against exact merged Review,
ReviewLease, TaskAssignment, and Submission targets. L1 history/economic risk.

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
service, route, background executor, receipt, artifact, reputation or legacy accepted-work settlement row behavior
mutable/void/delete/adjust path, dependency or CI weakening
```

## Acceptance criteria

- [ ] Existing Submission is the version identity. Project/task/submission/
  Review/lease/assignment/contributor and stabilized artifact_hash lineage are
  same-chain and non-null as applicable.
- [ ] Reviewer rows are completed_review and bind source Review + ReviewLease +
  reviewer + reviewer-frozen policy. Submitter rows are accepted_submission,
  bind accepted source Review + TaskAssignment + submitter + submitter-frozen
  policy, and are impossible for needs_revision/reject.
- [ ] Exact database uniqueness on `(source_review_id, contribution_type)`
  prevents duplicate contribution type for one source Review while allowing
  distinct reviewer contributions for distinct revision Reviews. Contributor
  identity is a validated lineage field, never part of this uniqueness key.
- [ ] Each award references the exact ContributionRecord, its frozen
  ContributionPolicyVersion, matching rule/definition, same project/contributor/
  contribution type, and same-project/instrument adapter binding.
- [ ] Unique `(contribution_record_id, instrument_type)` enforces at most one
  money and one project_points award; quantity is exact and positive.
- [ ] Database enforces immutability/at-most-one but does not require a
  contribution child during staged Review persistence before CON-07 flushes.
- [ ] At-least-one per valid Review is deferred to CON-07 + REV-10 + preflight.
- [ ] No mutable/void/delete/adjust path or legacy accepted-work settlement row/reputation schema.

## Verification and reviewers

Execute CON-03C in `../RUNTIME_VERIFICATION.md`; changed subsystems are at least
90 percent. Senior engineering, QA/test, security/auth, product/ops,
architecture, docs, reuse/dedup and test-delta are required. Stop if exact
REV-03/REV-04 targets are not merged.
