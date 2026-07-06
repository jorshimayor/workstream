# Internal Review Evidence: WS-POL-001-11

## Chunk

WS-POL-001-11

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: ef2cd187c4a1b4fc2b3cbb7d4d8d563ff9e50bb0

Reviewed at: 2026-07-06T16:07:41Z

Reviewer run IDs: senior-engineering-review-019f37c9-f47a-7fa2-ac9b-639db0d4943a, qa-test-review-019f3804-d7c9-7f40-9a55-abb3ab0ea152, security-auth-review-019f37ca-2035-7e93-b63d-e53c632ee23a, product-ops-review-019f37ca-2da9-7670-a0a1-9bb351b0ecf1, architecture-review-019f382c-b040-7ac3-a7f6-f26b17fbe533, docs-review-019f3805-095b-7490-b410-3b28688bc979, reuse-dedup-review-019f3805-369e-7050-ba48-b1aca7c8208c, test-delta-review-019f3805-5f52-73b1-9aba-6254ce075cd9

After the reviewed SHA, only evidence and status files changed.

## Reviewed Change

Scope:

- Implements local `ActorIdentity` and shared `ActorProfile` persistence for verified Flow actors.
- Keeps `get_current_actor` as the pure Flow-token boundary and adds `get_registered_actor` for explicit registry side effects.
- Migrates legacy `worker_profiles` and `reviewer_profiles` into `actor_identities` and `actor_profiles`, then removes the old stores.
- Makes worker profile activation write `ActorProfile(profile_type="worker", status="active")` through the actor module.
- Makes task claim require both a verified `worker` token role and an active worker profile.
- Preserves active/disabled profile metadata during token observation refreshes.
- Keeps persisted profiles as workflow eligibility/audit records, never route permission authority.
- Rewires demo/scripts/examples from `/api/v1/demo/worker-profile` to `POST /api/v1/workers/me/profile`.
- Aligns docs with Flow issuer plus subject as the canonical identity anchor and Workstream actor id as a local durable reference.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Fixed profile freshness updates, redundant identity upserts, and documented v0.1 audit ledger coupling. |
| QA/test | PASS | None | Confirmed migration/backfill/removal, registered auth boundary, profile eligibility, overposting protection, and demo/script rewiring. |
| security/auth | PASS AFTER FIXES | None | Confirmed token roles remain route authority; scoped docs stayed inside the chunk after reverting out-of-scope roadmap edits. |
| product/ops | PASS | None | Confirmed actor/profile workflow semantics after stale loop evidence was treated as pending final evidence work. |
| architecture | PASS WITH LOW RISKS | None | Confirmed Flow auth boundary, actor/profile non-auth semantics, worker claim gate, and documented v0.1 audit ledger coupling. |
| CI integrity | N/A - with approved reason | N/A | No CI workflow, package script, dependency, lint, typecheck, or coverage configuration changed. |
| docs | PASS WITH LOW RISKS | None | Confirmed docs align after adding `workstream_relationship_profiles` schema, audit schema, demo cleanup, and issuer-plus-subject wording. |
| reuse/dedup | PASS | None | Confirmed `ActorService` is profile authority, audit writes reuse `TaskRepository.add_audit_event`, and old profile authority paths are removed. |
| test delta | PASS | None | Confirmed persisted overposting assertions, downgrade restore assertions, metadata negative assertions, and active/disabled metadata preservation coverage. |

## Valid Findings Addressed

- Fixed active/disabled profile observation so token-role observation refreshes do not overwrite explicit workflow provenance metadata.
- Added regression coverage proving active and disabled worker profile metadata stays `worker_profile_api` after observation.
- Reused `TaskRepository.add_audit_event` for actor profile audit writes instead of adding a parallel audit persistence path.
- Removed the redundant task-service worker-profile facade; the route calls `ActorService.activate_worker_profile` directly.
- Added persisted-value overposting assertions for `POST /api/v1/workers/me/profile` and task claim so spoofed identity fields cannot write malicious registry rows.
- Added migration downgrade assertions proving legacy worker/reviewer rows are restored with actor id, subject, issuer, display/email, status, and skill tags.
- Added metadata negative assertions so old `worker_profiles`/`reviewer_profiles` metadata exports cannot silently return.
- Removed stale `/api/v1/demo/worker-profile` usage from backend scripts, Terminal Benchmark example, README, and the Week 1 demo UI.
- Removed stale `WORKSTREAM_ENABLE_DEMO_ROUTES=true` guidance where the Week 1 demo no longer needs demo routes.
- Documented exact `workstream_relationship_profiles` trusted claim schema and its non-authorizing behavior.
- Updated audit-event docs to match actual `actor_roles`, `from_status`, `to_status`, `is_dev_auth`, and `event_payload` fields.
- Aligned Flow Identity wording so docs consistently name Flow issuer plus subject as the canonical identity anchor.

## Commands Run

```bash
cd backend && .venv/bin/python -m ruff check app/api/deps/auth.py app/api/routes/auth.py app/modules/actors app/modules/tasks/models.py app/modules/tasks/repository.py app/modules/tasks/router.py app/modules/tasks/schemas.py app/modules/tasks/service.py tests/test_actors.py tests/test_alembic.py tests/test_auth.py tests/test_tasks.py
cd backend && .venv/bin/docstr-coverage app/api app/modules/actors app/modules/tasks --config .docstr.yaml
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
cd backend && .venv/bin/python -m pytest tests/test_alembic.py tests/test_actors.py tests/test_auth.py -q
cd backend && .venv/bin/python -m pytest tests/test_tasks.py -q
cd demos/week1_api_demo_ui && npm run build
rg -n 'worker_profile_setup=demo_bootstrap|demo worker profile|Activates demo worker profile|WORKSTREAM_ENABLE_DEMO_ROUTES|/api/v1/demo/worker-profile|WorkerProfile|ReviewerProfile' backend/scripts examples/terminal_benchmark backend/app/api/routes/demo.py backend/app/modules README.md demos/week1_api_demo_ui/src/App.tsx docs/spec_chunk_2_auth_actor_boundary.md docs/architecture_data_model.md docs/operations_roles_permissions.md
```

Results:

- Ruff: passed.
- Docstring coverage: 100.0%.
- Stale wording scan: passed.
- Markdown link check: passed for 9 changed Markdown files.
- Diff whitespace check: passed.
- Migration/actor/auth tests: 35 passed in 518.35s.
- Task tests: 69 passed in 1184.65s.
- Week 1 demo UI build: passed.
- Stale demo/profile scan: no matches.
- Local XLSX export: not present.

## Remaining Risks

- Actor profile audit writes use the existing task-owned audit ledger helper in v0.1. This keeps one audit source of truth for now, but a future shared audit module should extract the code boundary before actor/reputation work grows.
- Existing routes outside the chunk may continue using pure `get_current_actor` until deliberately migrated. This chunk only adds registration side effects to `/auth/me`, worker profile setup, and task claim paths touched here.
- The next Terminal Benchmark live API drill still needs to run through real HTTP calls against this implementation after PR review.
