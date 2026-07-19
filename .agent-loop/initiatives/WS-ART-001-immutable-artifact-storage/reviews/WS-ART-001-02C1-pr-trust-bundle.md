# PR Trust Bundle: WS-ART-001-02C1

## Chunk

`WS-ART-001-02C1` - Admission And Put-Attempt Foundation

Merge intent: `.agent-loop/merge-intents/WS-ART-001-02C1.json`

## Goal

Create the durable admission and prepared-attempt transaction required before
any artifact provider write, while keeping execution and product cutover
inactive.

## What Changed

- Added server-derived task, producer, project, and deployment byte limits.
- Added unique provisional/completed/released content charges with exact replay
  deduplication and concurrent oversubscription protection.
- Added closed guide, contributor, and checker-output admission commands.
- Added one atomic namespace-claim, capacity-reservation, audit, and prepared
  `ArtifactPutAttempt` transaction.
- Added exact human and service identity revalidation, canonical relationship
  checks, guide-source row locking, and replay charge-set validation.
- Added migration and real PostgreSQL concurrency, rollback, and downgrade
  proofs.

## Scope Control

This chunk adds no provider write, provider observation, verification,
publication, Celery execution, recovery attempt, Operator/public route, product
cutover, task claim, reviewer lease, R2 path, or Flow Node path.

## Acceptance Proof

- [x] Callers cannot supply or weaken admission scopes.
- [x] Same content is charged once per applicable scope.
- [x] Concurrent reservations cannot double-charge or oversubscribe.
- [x] Reservation failure leaves no attempt, charge, audit success, or provider call.
- [x] One committed prepared attempt is required before later provider work.
- [x] Guide facts, human authority, service identity, and producer relationships are revalidated transactionally.
- [x] Provider execution fields remain inactive and no product route exposes admission.
- [x] Exactly one schema-v2 merge intent names only `02C2`, which still requires an explicit start.

## Tests And Checks

```text
369 focused tests PASS
Scoped changed-subsystem coverage 94.32%
Ruff PASS
Stale artifact contract scan PASS
88 agent-gate tests PASS
Markdown links PASS
git diff --check PASS
```

GitHub Backend CI remains authoritative for the isolated full suite and 78
percent repository coverage floor.

## Internal Review

Reviewed code SHA: `b4d54469b1590cf43fd9f496c64b6172577c0eec`

All nine required reviewer tracks passed with no unresolved findings. Every
reviewer session is closed. Run IDs and repaired findings are recorded in the
internal review evidence.

## External Review

External checks are separate from internal agent review and have not yet run on
this candidate.

| Source | Status | Notes |
|---|---:|---|
| GitHub Actions | Pending | Must prove Agent Gates, Backend, and every required repository check on the published branch. |
| CodeRabbit | Pending | Review comments, resolutions, and reruns will be recorded in a separate external-review response file. |
| Human review | Pending | Only the user may approve merge. |

## Remaining Risks

- Admission is not yet connected to provider execution or product submission
  routes; those remain later, separately approved chunks.
- Native AWS remains unavailable until its release-bound live proof.

## Human Review Focus

- Can a caller omit a scope, bypass a limit, or substitute producer context?
- Does every successful admission create exactly one durable prepared attempt
  before any provider side effect?
- Do rollback and exact replay preserve byte accounting and audit integrity?
- Are provider execution, verification, recovery, and product routes still absent?

## Human Merge Ownership

- [ ] I can explain what changed and why.
- [ ] I know what could break.
- [ ] I accept the remaining risks.
- [ ] GitHub CI and external review pass.
- [ ] The user explicitly approved this PR for merge.
