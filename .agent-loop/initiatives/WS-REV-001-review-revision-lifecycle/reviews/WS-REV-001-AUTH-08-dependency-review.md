# Dependency Review: Merged AUTH-08

## Scope

Read-only review of AUTH-08 from prior trusted main
`90eca12f6398f2ef168e634244d912765572c3e5` through merged trusted main
`aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3` and its impact on the WS-REV
plan. AUTH implementation remains owned by WS-AUTH.

## Exact Merge Evidence

- Pull request: #131
- Merge commit: `aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`
- Final branch head: `0832358a0262805f553d05b50b0d778e6e6ad995`
- Merged at: `2026-07-16T08:14:06Z`
- Final implementation review head: `a284a718e68f08e072cb965cc5834bcc7ab45ee9`
- Final GitHub Backend: run `29481047118`, success
- PR-head GitHub Agent Gates: runs `29481047119` and `29481057005`, success
- Final-head GitHub Agent Gates: run `29482246184`, success
- CodeRabbit: success

AUTH's internal evidence records 275 focused behavior tests, 90.17 percent
branch-aware focused coverage, and 17 isolated Alembic tests. Replacement
Backend run `29479547151` passed after the retained-revision regression repair;
the final PR-head Backend run above also passed.

## Confirmed Boundary

- Authorization remains request scoped and bound to the caller-owned
  `AsyncSession`.
- Product services call only
  `AuthorizationService.require(action_id, typed_resource_context)`; they do not
  query AUTH grants, accept token roles as authority, or import AUTH persistence.
- AUTH-08 adds seven active administrative actions and no PermissionId. The
  catalogue now contains 74 PermissionIds and exactly 57 ActionIds: 9 active and
  48 planned.
- Canonical `submission.create` and the original 19 review-owned actions remain
  planned. The four later REV additions remain absent. All 24 REV dependencies
  remain inactive until their owning REV chunks activate them.
- The four additions require exact 57-to-61 typed catalogue, owner, and
  PostgreSQL action-to-permission audit parity, producing 9 active and 52
  planned. Enum-only registration is not authority.
- Administrative roles provide bounded permission candidates only. They do not
  activate planned product actions or authorize a caller without the action's
  canonical resource and guards.

## AUTH-07B Consumption Findings Resolved

### Generic Teardown

`get_authorization_service` no longer commits an arbitrary open shared-session
transaction during successful teardown. It rolls back any transaction left
open, while each protected route owns its explicit business-plus-decision
commit. `test_authorization_dependency_rolls_back_a_forgotten_route_transaction`
proves a forgotten consumer commit cannot be rescued by dependency ordering.

### Evidence Failure Mapping

The kernel converts SQL failure around its own evidence write into typed
`AuthorizationEvidenceUnavailable`. The FastAPI dependency rolls back and maps
that exception once to the stable retryable `503 service_unavailable` envelope.
Feature persistence failures remain feature-owned and are not relabeled as
authorization evidence failures.

### Canonical Verification Timestamps

Successful existing-actor GET/PATCH routes advance
`ActorProfile.last_seen_at` and `ActorIdentityLink.last_verified_at` in the
route-owned transaction after authorization. The actor repository uses
execution-time database timestamps with monotonic `GREATEST` semantics. Denial
or persistence failure rolls back both timestamps. API tests cover failed and
successful GET/PATCH behavior, repeated access, and independent-session commit
ordering.

## REV Disposition

The three findings are resolved for the merged AUTH-08 baseline. REV changes no
AUTH runtime code. Every consuming chunk treats the behavior above as a
regression invariant and must re-prove it on that chunk's trusted-main SHA.

The current merged catalogue baseline is 57 actions, not the historical 50.
REV's four additions remain a future AUTH-owned 57-to-61 migration. No REV
action becomes active through this planning refresh.

ART PR #129 remains open and conflict-blocked at
`a7432c87719e694038dae5b386b7c9b3ecf9e9b4`. The final PLAN publication review
and exact-SHA binding remain parked until ART merges and its contracts are
reconciled from trusted main.

## Snapshot Evidence

Current non-review initiative snapshot digest:
`ad176b2acf5da47194ce0ae786e6bc86ef847efa6cd9159eb1ad6b760fe6f552`.

The digest hashes sorted `sha256sum` output for initiative files excluding
`reviews/**`; it is a parked dependency-refresh snapshot, not the final PLAN
publication evidence binding.

The historical PLAN evidence remains bound to its earlier reviewed SHA and is
therefore stale after the AUTH-08/main rebase. It is not current dependency
evidence and must not authorize a push or merge.

```text
git show --check aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_loop_memory_state.py
python3 scripts/test_agent_gates.py
```

## Current Refresh Reviewer Status

The AUTH-08 dependency-refresh diff received these internal reviewer tracks:

| Tracks | Agent | Result |
|---|---|---|
| Senior engineering, architecture, reuse/dedup | `/root/auth08_senior_review` | PASS AFTER FIXES |
| QA/test, product/ops | `/root/auth08_qa_review` | PASS |
| Security/auth, docs, CI integrity | `/root/auth08_security_review` | PASS AFTER FIXES |

These results review the parked AUTH-08 dependency snapshot. They do not replace
the historical PLAN evidence or bind the final publication SHA. Final exact-SHA
publication review remains blocked by ART #129.

The focused catalogue and teardown tests passed locally. Two PostgreSQL API
regressions were inspected but not rerun because
`WORKSTREAM_TEST_DATABASE_URL` is unset; merged PR #131 Backend run
`29481047118` supplies the fresh database evidence.
