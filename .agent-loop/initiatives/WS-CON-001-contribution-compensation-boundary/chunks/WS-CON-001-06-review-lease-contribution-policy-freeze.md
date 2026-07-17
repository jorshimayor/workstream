# Chunk Contract: WS-CON-001-06 - ReviewLease Contribution-Policy Freeze Participant

## Goal

Deliver the narrow CON policy lookup/freeze participant that REV invokes inside
the review-claim transaction. Reviewer award eligibility is frozen before
review work begins.

## Risk

L1 economic/review lifecycle/authorization; SLA P1.

## Allowed files

```text
backend/app/modules/contributions/{ports,service}.py
backend/tests/{test_contributions,test_authorization}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-06.json
```

## Not allowed

```text
review queue/lease policy, model, migration, service, route, or composition
AUTH catalogue/grant/kernel changes; review decision or award creation
task assignment changes; provider/artifact/adapter calls
```

## Acceptance criteria

- [ ] Port accepts caller AsyncSession and canonical locked project/claim facts,
  locks one active ContributionPolicy and published version plus referenced
  definitions/bindings, returns the exact version ID, and never commits.
- [ ] Missing/inactive/invalid policy or binding returns stable failure with no
  CON/audit/outbox partial state.
- [ ] REV-owned ReviewLease has immutable non-null
  `reviewer_contribution_policy_version_id` and REV owns its write/wiring.
- [ ] review.claim uses exact active same-project reviewer ProjectRoleGrant;
  submitter/adjudicator/admin grants do not substitute. No-self-review and REV
  lifecycle guards remain REV-owned.
- [ ] CON hidden port and REV hidden composition merge while review.claim
  remains planned; AUTH later integrates the evaluator and alone activates.
- [ ] Policy publish and binding state versus claim pass both lock orders;
  changed modules stay at least 90 percent and global floor stays 78.

## Review and stop

Required tracks: senior, QA, security, product, architecture, docs, reuse, and
test-delta. Stop if REV lease schema/caller facts or review.claim authority are
not merged. CON owns no review composition.
