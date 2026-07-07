# Internal Review Evidence: WS-POL-001-11

## Chunk

WS-POL-001-11

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: ce57958666bb28c9112b6513ec16f504c5fd1571

Reviewed at: 2026-07-07T03:45:00Z

Reviewer run IDs: senior-engineering-review-019f3aa7-a13d-7052-85dc-635cbfa7dadb, qa-test-review-019f3aa7-a9a4-7e80-9fb5-8b9961b0c913, security-auth-review-019f3aa7-b1b3-73f2-959e-9eaae25fabd3, product-ops-review-019f3aa7-bce6-77b1-9053-09926c54b4c9

After the reviewed SHA, only evidence and status files changed.

## Reviewed Change

Scope:

- Implements local `ActorIdentity` and shared `ActorProfile` persistence for verified Flow actors.
- Keeps `get_current_actor` as the pure Flow-token boundary and adds `get_registered_actor` for explicit registry side effects.
- Creates new `actor_identities` and `actor_profiles` tables, then drops obsolete `worker_profiles` and `reviewer_profiles` without compatibility backfill.
- Makes worker profile activation write `ActorProfile(profile_type="worker", status="active")` through the actor module.
- Makes task claim require both a verified `worker` token role and an active worker profile.
- Preserves active/disabled profile metadata during token observation refreshes.
- Keeps persisted profiles as workflow eligibility/audit records, never route permission authority.
- Rewires demo/scripts/examples from `/api/v1/demo/worker-profile` to `POST /api/v1/workers/me/profile`.
- Aligns docs with Flow issuer plus subject as the canonical identity anchor and Workstream actor id as a local durable reference.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Required stale evidence wording to be fixed so the PR no longer claims compatibility backfill or deleted demo UI proof. |
| QA/test | PASS WITH LOW RISKS | None | Required stale trust-bundle proof wording to be fixed; no code/test blockers found. |
| security/auth | PASS | None | Confirmed no valid security/auth findings on the final code SHA. |
| product/ops | PASS AFTER FIXES | None | Required stale backfill wording to be fixed so operator expectations match destructive removal/no compatibility backfill. |
| architecture | PASS WITH LOW RISKS | None | Confirmed Flow auth boundary, actor/profile non-auth semantics, worker claim gate, and documented v0.1 audit ledger coupling. |
| CI integrity | PASS | None | Confirmed the post-PR lint fix only adds the missing `uuid4` import and does not weaken CI, lint, tests, typecheck, coverage, workflows, or package scripts. |
| docs | PASS WITH LOW RISKS | None | Confirmed docs align after adding `workstream_relationship_profiles` schema, audit schema, demo cleanup, and issuer-plus-subject wording. |
| reuse/dedup | PASS | None | Confirmed `ActorService` is profile authority, audit writes reuse `TaskRepository.add_audit_event`, and old profile authority paths are removed. |
| test delta | PASS | None | Confirmed persisted overposting assertions, downgrade restore assertions, metadata negative assertions, and active/disabled metadata preservation coverage. |

## Valid Findings Addressed

- Fixed active/disabled profile observation so token-role observation refreshes do not overwrite explicit workflow provenance metadata.
- Added regression coverage proving active and disabled worker profile metadata stays `worker_profile_api` after observation.
- Reused `TaskRepository.add_audit_event` for actor profile audit writes instead of adding a parallel audit persistence path.
- Removed the redundant task-service worker-profile facade; the route calls `ActorService.activate_worker_profile` directly.
- Added persisted-value overposting assertions for `POST /api/v1/workers/me/profile` and task claim so spoofed identity fields cannot write malicious registry rows.
- Added migration assertions proving new actor registry tables exist and obsolete worker/reviewer profile tables are removed rather than kept as compatibility stores.
- Added metadata negative assertions so old `worker_profiles`/`reviewer_profiles` metadata exports cannot silently return.
- Removed stale `/api/v1/demo/worker-profile` usage from backend scripts, Terminal Benchmark example, and README.
- Removed the obsolete Week 1 demo UI package and workflow instead of preserving a stale compatibility surface.
- Documented exact `workstream_relationship_profiles` trusted claim schema and its non-authorizing behavior.
- Updated audit-event docs to match actual `actor_roles`, `from_status`, `to_status`, `is_dev_auth`, and `event_payload` fields.
- Aligned Flow Identity wording so docs consistently name Flow issuer plus subject as the canonical identity anchor.
- Fixed stale evidence after final internal review so the trust bundle no longer claims compatibility backfill or deleted demo UI proof.

## Commands Run

```bash
cd backend && .venv/bin/python -m ruff check app/modules/actors/service.py app/modules/projects/service.py tests/test_actors.py tests/test_tasks.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check origin/main...HEAD
python3 scripts/test_agent_gates.py
cd backend && .venv/bin/python -m pytest tests/test_alembic.py tests/test_actors.py tests/test_auth.py -q
cd backend && .venv/bin/python -m pytest tests/test_tasks.py::test_future_roles_cannot_view_unassigned_task_or_submissions -q
cd backend && .venv/bin/python -m pytest tests/test_projects.py::test_source_snapshot_rejects_unsafe_refs -q
```

Results:

- Ruff: passed.
- Stale wording scan: passed.
- Markdown link check: passed for 24 changed Markdown files.
- Diff whitespace check: passed.
- Agent gate tests: 26 passed.
- Migration/actor/auth tests: 41 passed in 385.17s.
- Task eligibility regression: 3 passed in 139.46s.
- Project source-ref regression: 1 passed in 79.77s.
- Local XLSX export: not present.

## Remaining Risks

- Actor profile audit writes use the existing task-owned audit ledger helper in v0.1. This keeps one audit source of truth for now, but a future shared audit module should extract the code boundary before actor/reputation work grows.
- Existing routes outside the chunk may continue using pure `get_current_actor` until deliberately migrated. This chunk only adds registration side effects to `/auth/me`, worker profile setup, and task claim paths touched here.
- The next Terminal Benchmark live API drill still needs to run through real HTTP calls against this implementation after PR review.
