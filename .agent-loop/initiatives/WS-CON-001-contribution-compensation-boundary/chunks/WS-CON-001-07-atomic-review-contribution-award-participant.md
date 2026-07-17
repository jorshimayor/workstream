# Chunk Contract: WS-CON-001-07 - Atomic Review Contribution And Award Participant

## Goal

Implement the mandatory flush-only participant that creates reviewer and
FinalAcceptance-sourced submitter contributions, evaluates frozen
ContributionRules, creates applicable awards, and returns typed audit/outbox
inputs in the caller-owned Review transaction. It performs no evidence
projection or ART work.

## Risk

L1 economic/canonical-judgment/cross-domain transaction; SLA P1.

## Allowed files

```text
backend/app/modules/contributions/{schemas,repository,service,ports}.py
backend/app/modules/compensation/{repository,service}.py
backend/tests/{test_contributions,test_compensation,test_authorization,test_outbox}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-07.json
```

## Not allowed

```text
Review policy/model/service/route/composition wiring or commit
public route registration; optional/no-op participant
AUTH catalogue/grant/kernel edits or materialize actions
ART capability/repository/provider call or evidence projection row/event
mutable/delete/void/adjust contribution/award path; reputation scoring
```

## Participant request

The typed request carries the caller AsyncSession and exact locked:

- Review, ReviewLease, queue/lifecycle fence, and canonical decision;
- accept-only REV-owned FinalAcceptance, otherwise null;
- versioned Submission, TaskAssignment, task, and project;
- reviewer/submitter ActorProfile IDs;
- reviewer and submitter frozen ContributionPolicyVersion IDs;
- server-derived stabilized `Submission.artifact_hash`/reviewed-packet digest
  from the merged REV/Submission lineage, never caller package data;
- originating review.decision AuthorizationDecision, request, and correlation.

## Acceptance criteria

- [ ] Every valid committed Review creates exactly one reviewer
  `completed_review`. Accept requires exactly one same-chain FinalAcceptance and
  creates one submitter `accepted_submission` from it; needs_revision/reject
  require no FinalAcceptance and create no submitter record.
- [ ] Locked participant inputs prove REV already applied the exact outcome:
  accept has Task `accepted` and Assignment `completed`; needs_revision has Task
  `needs_revision` and Assignment still `active`; reject has Task `rejected`
  with the bounded human reason and only the same-task Assignment `blocked` with
  its source Review. CON does not own or mutate those lifecycle effects.
- [ ] Repeated idempotent decision returns the same rows; a later revision
  Review creates a distinct reviewer contribution; automated outcomes create
  none.
- [ ] Reviewer uses lease-frozen policy; submitter uses assignment-frozen
  policy. Matching explicit unpaid rule creates no award; compensated rule
  creates at most one money and one project-points award copied from immutable
  definitions.
- [ ] CON copies the supplied stabilized digest exactly into
  ContributionRecord.artifact_hash. It does not load/rederive it or call ART.
- [ ] Participant validates exact FinalAcceptance/Review/Submission/assignment/
  lease/project/actor/policy lineage and an allowed review.decision whose actor, action,
  resource digest, matched reviewer grant/project, request, and correlation
  match the locked transaction.
- [ ] Participant uses caller AsyncSession, stages contribution/award rows,
  returns canonical typed audit/outbox inputs, flushes, and never commits. REV
  stages shared audit/outbox rows after the participant and before its single
  commit. CON creates no evidence projection or evidence-request event.
- [ ] CON never reads REV/AUTH repositories or evaluates review.decision. REV
  owns canonical composition and the single route commit.
- [ ] AUTH registration -> CON participant -> REV hidden composition -> AUTH
  evaluator/activation order is proven. Real kernel denies while planned.
- [ ] Fault injection at every CON write/flush and every later REV step rolls
  back Review/FinalAcceptance/task/assignment/contribution/award/audit/outbox
  together. No post-commit repair path exists.
- [ ] No FinalAcceptance create action/API exists. Static/runtime proof finds no
  adjudication policy, grant/action, queue/lease, state, decision, contribution,
  conditional branch, readiness check, or initiative dependency.
- [ ] Static/runtime spies prove zero ART capability, repository, preparation,
  provider, or evidence calls in every decision path.
- [ ] PostgreSQL uniqueness, replay, changed-fact conflict, and concurrency tests
  pass; changed code is at least 90 percent and repository floor at least 78.

## Review and stop

Required tracks: senior, QA, security, product, architecture, docs, reuse, and
test-delta. Stop after the participant. REV, not CON-07, owns integration and
production execution.
