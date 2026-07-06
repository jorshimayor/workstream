# PR Trust Bundle: WS-POL-001-11

## Chunk

`WS-POL-001-11` - Actor Identity And Profile Registry

## Goal

Implement Workstream's local actor identity and shared actor profile registry for verified Flow actors without turning Workstream into the auth provider or letting persisted profiles become route permissions.

## Human-Approved Intent

The user asked for one shared actor/profile model instead of separate worker, reviewer, admin, project-manager, and project-owner implementations. The verified Flow token remains the authority for route access. Workstream stores local actor/profile rows for workflow eligibility, audit, display, future routing, and later reputation linkage.

Chunk contract:

- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/chunks/WS-POL-001-11-actor-identity-profile-registry.md`

## What Changed

- Added `actor_identities` and `actor_profiles` with async SQLAlchemy models, repository, schemas, service, and Alembic migration.
- Backfilled legacy `worker_profiles` and `reviewer_profiles` into the shared actor registry and removed the old profile tables as profile authority.
- Kept `get_current_actor` pure and added `get_registered_actor` for explicit registry side effects.
- Updated `/auth/me`, `/workers/me/profile`, and task claim paths to register actor identity/profile metadata where needed.
- Made worker claim require current verified `worker` token role plus active `ActorProfile(profile_type="worker")`.
- Preserved active/disabled profile provenance during token observation refreshes.
- Retired stale demo worker-profile bootstrap paths and rewired scripts/examples/UI to `POST /api/v1/workers/me/profile`.
- Documented Flow issuer plus subject as the canonical identity anchor; Workstream actor id is a local durable reference.
- Documented trusted `workstream_relationship_profiles` claim shape for scoped project-owner metadata.

## Why It Changed

The live Terminal Benchmark drill proved worker profile setup must be real. Doing only a worker-specific profile path would create the same problem again for reviewers, project managers, admins, project owners, audit, and later reputation. This chunk creates the shared actor/profile base before the next live API drill.

## Design Chosen

- `ActorIdentity` stores local durable identity rows for verified Flow actors.
- `ActorProfile` stores profile type, status, skill tags, scope, and non-authoritative metadata.
- `observed` records token-observed metadata for audit/display only.
- `active` is explicit workflow eligibility and still requires the matching current token role.
- `disabled` blocks workflow eligibility and is preserved by observation refresh.
- Route authorization still reads current `ActorContext.roles`, not database profile rows.
- Actor profile audit events use the existing Workstream `audit_events` ledger through `TaskRepository.add_audit_event`.

## Alternatives Rejected

- Separate profile tables per role: rejected because it duplicates profile authority.
- Persisted profiles as route permissions: rejected because Flow token claims are the route authorization source.
- Automatic worker/reviewer eligibility from token observation: rejected because eligibility must come from explicit profile workflows.
- Keeping old worker/reviewer compatibility stores: rejected because v0.1 is still under construction and should not preserve stale authority.
- A new audit table/module in this chunk: deferred because the current accepted boundary is one v0.1 audit ledger, with extraction documented for future actor/reputation expansion.

## Scope Control

Implemented only actor identity/profile registry, migration/backfill/removal, touched-route registration, worker profile activation, worker claim eligibility, tests, demo/script cleanup required by the migration, and documentation alignment.

No Workstream-owned login/signup/session/password behavior was added. No post-submit, review, revision, payment, reputation, blockchain, object storage, agent runtime, or frontend product implementation was added.

## Product Behavior

- Product review decisions remain only `accept`, `needs_revision`, and `reject`.
- Worker profile setup is now the canonical authenticated worker endpoint, not a demo bootstrap route.
- Task claim remains worker-only and now also requires active worker profile eligibility.
- Stored profile rows do not grant access without the matching current verified token role.

## Acceptance Criteria Proof

- Migration creates actor registry tables and uniqueness constraints.
- Migration backfills worker/reviewer rows and removes old profile tables.
- Downgrade restores legacy rows with identity/profile data.
- SQLAlchemy metadata imports new actor models and has negative assertions for old profile exports.
- `/auth/me` registers identity/profile metadata without Workstream auth sessions.
- Repeated requests refresh identity/profile freshness without duplicate rows.
- Observed profiles are created for token roles but do not satisfy eligibility.
- Active/disabled profile statuses and metadata are preserved during observation.
- Worker profile activation requires worker token role and explicit API call.
- Claim requires worker token role plus active worker profile.
- Persisted active profiles without matching token roles cannot authorize worker/operator routes.
- Overposting tests prove spoofed identity fields do not alter persisted registry rows.
- Demo/scripts/examples no longer use `/api/v1/demo/worker-profile`.

## Tests/Checks Run

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

Result summary:

- Ruff: passed.
- Docstring coverage: 100.0%.
- Stale wording scan: passed.
- Markdown link check: passed for 9 changed Markdown files.
- Diff whitespace check: passed.
- Migration/actor/auth tests: 35 passed in 518.35s.
- Task tests: 69 passed in 1184.65s.
- Week 1 demo UI build: passed.
- Stale demo/profile scan: no matches.

## Test Delta

- Tests added: `backend/tests/test_actors.py`.
- Tests expanded: Alembic backfill/downgrade/uniqueness, auth registration, task metadata, token-role authorization, overposting, active-profile eligibility, and stale route removal.
- Tests removed/skipped: none.

## CI Integrity

- Coverage threshold unchanged.
- Lint/typecheck configuration unchanged.
- No workflow weakening.
- No package script weakening.
- No dependency changes.

## Reviewer Results

Internal review evidence:

- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-11-internal-review-evidence.md`

Reviewed code SHA: `912a1bef3ce7065e9563a03a440b24efe6af3f89`

Reviewer run IDs: see `WS-POL-001-11-internal-review-evidence.md`.

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Fixed profile freshness, identity upsert churn, and documented audit ledger coupling. |
| QA/test | PASS | None | Confirmed actor registry behavior, migration, auth boundary, eligibility gates, and demo rewiring. |
| security/auth | PASS AFTER FIXES | None | Confirmed token authority and fail-closed scope after fixes. |
| product/ops | PASS | None | Confirmed actor/profile workflow semantics. |
| architecture | PASS WITH LOW RISKS | None | Confirmed auth/profile boundaries; future shared audit module noted as follow-up. |
| CI integrity | PASS | None | Confirmed the post-PR lint fix only imports `uuid4` and does not weaken CI or tests. |
| docs | PASS WITH LOW RISKS | None | Confirmed docs alignment after final issuer-plus-subject wording. |
| reuse/dedup | PASS | None | Confirmed single actor/profile authority and audit helper reuse. |
| test delta | PASS | None | Confirmed tests were strengthened and not weakened. |

## External Review

External review has not run yet. CodeRabbit and GitHub checks should run after the PR is opened.

## Remaining Risks

- Actor profile audit persistence currently imports the existing task audit repository. This keeps one v0.1 audit ledger but should be extracted to a shared audit module before actor/reputation work grows.
- Existing routes outside this chunk may continue using pure `get_current_actor` until deliberately migrated.
- The next Terminal Benchmark live API drill still needs to run against this implementation through real HTTP calls after merge.

## Follow-Up Work

- Open PR and wait for CodeRabbit/GitHub checks.
- Address external review in a separate external-review response file if needed.
- After merge, rerun the Terminal Benchmark live API drill using the canonical worker profile endpoint.

## Human Review Focus

Please inspect:

- Flow auth boundary: token role first, profile eligibility second.
- Migration/backfill/removal of old worker/reviewer profile stores.
- `ActorProfile` status semantics and preservation of explicit profile metadata.
- Overposting protections around registry writes.
- Demo/script cleanup from demo bootstrap to canonical worker profile API.

## Human Merge Ownership

Only the user can approve and merge this PR. Codex must not merge it without explicit user approval for that specific PR.
