# Internal Review Evidence: WS-POL-001-11

## Chunk

WS-POL-001-11

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: b769b70c07d22f7a802f6d4219201e7bbd2a3ab0

Reviewed working diff digest before evidence files:
86a15c53c7e407b902094212a5c08143e9c91cf154544e38ddbfc5e9f123983d

Reviewed at: 2026-07-06T11:57:16Z

Reviewer run IDs: senior-engineering-review-019f3741-9fa2-72a2-93b2-58d9e043fd57, qa-test-review-019f3741-ac4e-7f83-b0c7-3acb174e0058, security-auth-review-019f3747-7bf3-7b63-b093-cf8ba17d1183, product-ops-review-019f3747-82e8-7f13-95c9-e8339f8f08e6, architecture-review-019f3741-befb-77a2-bd85-0c43766b2219, docs-review-019f3741-cdda-72c3-8cf6-4dc2a78260c1, reuse-dedup-review-019f3741-de89-7742-b300-74f54eb1558a, test-delta-review-019f3741-efdd-72e2-9b07-d8dfe2836a79

After the reviewed SHA, only evidence and status files changed.

## Reviewed Change

Scope:

- Defines the `WS-POL-001-11` actor identity and profile registry contract.
- Keeps Flow token verification as the route authorization source.
- Separates pure `get_current_actor` from the actor-registration boundary.
- Defines shared `ActorIdentity` and `ActorProfile` semantics for worker,
  reviewer, admin, project manager, and project owner records.
- Requires old worker/reviewer profile stores to be migrated into the shared
  actor profile model with no wrapper, shadow table, or dual-write authority.
- Clarifies profile statuses: `observed`, `active`, and `disabled`.
- Requires worker claim to remain worker-only and require both a verified
  worker token role and active worker profile.
- Adds implementation scope for stale demo/script helper cleanup so the next
  Terminal Benchmark drill uses `POST /api/v1/workers/me/profile`.

No backend implementation code changed in this PR.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Confirmed final commit scope is implementable and contract file is tracked. |
| QA/test | PASS | None | Confirmed seeded migration backfill tests, stale helper scan, full task tests, and negative auth/profile tests are required. |
| security/auth | PASS | None | Confirmed persisted profiles do not grant route access, token roles remain authority, and spoofing/dev-auth requirements are present. |
| product/ops | PASS | None | Confirmed worker/reviewer/operator semantics, project-owner metadata boundary, and Terminal Benchmark drill route are clear. |
| architecture | PASS | None | Confirmed actor registration boundary, old profile authority removal, and scoped demo/script cleanup are feasible. |
| CI integrity | N/A - with approved reason | N/A | No CI workflow, package script, dependency, lint, typecheck, or coverage configuration changed. |
| docs | PASS | None | Confirmed contract, chunk map, data model, system architecture, glossary, roles, and task spec are aligned. |
| reuse/dedup | PASS | None | Confirmed one actor module/profile authority and no wrapper/shadow/dual-write profile path in the contract. |
| test delta | PASS | None | Confirmed no tests were changed and the implementation contract requires the right regression coverage. |

## Valid Findings Addressed

- Committed the new chunk contract so the PR cannot omit the active contract.
- Clarified `project_owner` as scoped source/contact metadata, not a
  route-authorizing Workstream role.
- Changed task claim permissions to worker-only and documented that
  admin/project-manager intervention must use a separate audited override path.
- Added `is_dev_auth` to the `ActorIdentity` data model.
- Defined `observed`, `active`, and `disabled` profile statuses.
- Required observation refreshes to preserve existing `active` and `disabled`
  status unless an explicit audited profile workflow changes status.
- Narrowed actor-registration side effects to routes updated in the chunk;
  routes outside the chunk may continue using pure `get_current_actor`.
- Fixed system architecture wording so local actor/profile records are not
  permission authority and registration dependency is separate from pure auth.
- Required seeded migration tests proving old worker/reviewer rows backfill
  into `ActorIdentity` and `ActorProfile`, including profile type, status,
  skill tags, scope, and old table removal.
- Added stale helper scope for `backend/scripts/week1_api_e2e.py`,
  `backend/scripts/week2_api_e2e.py`, and
  `examples/terminal_benchmark/terminal_benchmark_api_e2e.py`.
- Added a stale helper scan for old `WorkerProfile`/`ReviewerProfile` imports
  and `/api/v1/demo/worker-profile` calls.
- Added `FAIL` to the contract's allowed reviewer results and stated that
  Critical/High findings require `FAIL` until fixed.
- Added a forward note to the older Chunk 4 spec that `WS-POL-001-11`
  supersedes separate worker/reviewer profile storage.

## Commands Run

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check HEAD~1..HEAD
git diff --check
```

Results:

- Stale wording scan: passed.
- Markdown link check: passed for 11 changed Markdown files.
- Diff whitespace checks: passed.
- Local XLSX export: not present.

## Remaining Risks

- This PR is contract/process/docs only. The next implementation PR still needs
  to prove the migration, actor service, profile route behavior, stale helper
  removal, and live API drill with real API calls.
- Existing protected routers are not all migrated to actor registration in this
  chunk. That is intentional; only routes touched in the implementation chunk
  get the registration side effect.
