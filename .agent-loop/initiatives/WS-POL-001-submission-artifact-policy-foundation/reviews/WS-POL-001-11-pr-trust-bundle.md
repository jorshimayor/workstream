# PR Trust Bundle: WS-POL-001-11

## Chunk

`WS-POL-001-11` - Actor Identity And Profile Registry

## Goal

Implement Workstream's local actor identity and shared actor profile registry for verified Flow actors without turning Workstream into the auth provider or letting persisted profiles become route permissions.

## Human-Approved Intent

The user asked for one shared actor/profile model instead of separate worker, reviewer, admin, project-manager, and project-owner implementations. During the v0.1 bootstrap, trusted roles in the verified `ActorContext` remain the request-time route gate until Workstream-owned role assignment exists. Workstream stores local actor/profile rows for workflow eligibility, audit, display, future routing, and later reputation linkage.

Chunk contract:

- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/chunks/WS-POL-001-11-actor-identity-profile-registry.md`

## What Changed

- Added `actor_identities` and `actor_profiles` with async SQLAlchemy models, repository, schemas, service, and Alembic migration.
- Created the shared actor registry and dropped obsolete `worker_profiles` and `reviewer_profiles` without compatibility backfill.
- Kept `get_current_actor` pure and added `get_registered_actor` for explicit registry side effects.
- Updated `/auth/me`, `/workers/me/profile`, project routes, checker routes, and task paths touched by this chunk to register actor identity/profile metadata where needed.
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
- Persisted profiles as route permissions: rejected because profile rows are workflow metadata/eligibility, not product authorization.
- Automatic worker/reviewer eligibility from token observation: rejected because eligibility must come from explicit profile workflows.
- Keeping old worker/reviewer compatibility stores: rejected because v0.1 is still under construction and should not preserve stale authority.
- A new audit table/module in this chunk: deferred because the current accepted boundary is one v0.1 audit ledger, with extraction documented for future actor/reputation expansion.

## Scope Control

Implemented only actor identity/profile registry, destructive removal of obsolete profile stores, touched-route registration, worker profile activation, worker claim eligibility, tests, demo/script cleanup required by the migration, and documentation alignment.

No Workstream-owned login/signup/session/password behavior was added. No post-submit, review, revision, payment, reputation, blockchain, object storage, agent runtime, or frontend product implementation was added.

## Product Behavior

- Product review decisions remain only `accept`, `needs_revision`, and `reject`.
- Worker profile setup is now the canonical authenticated worker endpoint, not a demo bootstrap route.
- Task claim remains worker-only and now also requires active worker profile eligibility.
- Stored profile rows do not grant access without the matching current verified token role.

## Acceptance Criteria Proof

- Migration creates actor registry tables and uniqueness constraints.
- Migration creates actor registry tables and removes old worker/reviewer profile tables without compatibility backfill.
- Downgrade restores the old table shape only; obsolete experimental data is not preserved by this chunk.
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
cd backend && .venv/bin/python -m ruff check tests/test_auth.py tests/test_tasks.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check origin/main...HEAD
python3 scripts/test_agent_gates.py
python3 scripts/check_internal_review_evidence.py
cd backend && .venv/bin/python -m pytest tests/test_alembic.py tests/test_actors.py tests/test_auth.py -q
cd backend && .venv/bin/python -m pytest tests/test_auth.py::test_no_local_login_password_or_session_routes -q
cd backend && .venv/bin/python -m pytest tests/test_tasks.py::test_disabled_worker_profile_cannot_claim_ready_task tests/test_tasks.py::test_worker_without_profile_cannot_claim_ready_task -q
```

Result summary:

- Ruff: passed.
- Stale wording scan: passed.
- Markdown link check: passed for 24 changed Markdown files.
- Diff whitespace check: passed.
- Agent gate tests: 26 passed.
- Internal review evidence gate: passed after evidence update.
- Migration/actor/auth tests: 41 passed in 348.89s.
- Demo route regression: 1 passed in 14.77s.
- Task eligibility regressions: 2 passed in 84.84s.

## Test Delta

- Tests added: `backend/tests/test_actors.py`.
- Tests expanded: Alembic destructive removal/downgrade/uniqueness, auth registration, task metadata, token-role authorization, overposting, active/disabled-profile eligibility, stale route removal, and internal-review evidence gate behavior.
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

Reviewed code SHA: `a008cf81519913f1ec2f6ffe530c0598f8df087e`

Reviewer run IDs: see `WS-POL-001-11-internal-review-evidence.md`.

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Required stale evidence wording to be fixed so the PR no longer claims compatibility backfill or deleted demo UI proof. |
| QA/test | PASS AFTER FIXES | None | Added disabled-worker claim denial and deleted demo-route regression coverage. |
| security/auth | PASS | None | Confirmed no valid security/auth findings on the final code SHA. |
| product/ops | PASS AFTER FIXES | None | Required stale backfill wording to be fixed so operator expectations match destructive removal/no compatibility backfill. |
| architecture | PASS WITH LOW RISKS | None | Confirmed auth/profile boundaries; future shared audit module noted as follow-up. |
| CI integrity | PASS AFTER FIXES | None | Fixed stale reviewed-SHA evidence and kept `.agent-loop` review evidence as the canonical gate input. |
| docs | PASS AFTER FIXES | None | Added destructive migration note and marked old demo/Week 1 internal-review references as superseded. |
| reuse/dedup | PASS AFTER FIXES | None | Added full reviewer provenance and corrected route-registration scope in evidence. |
| test delta | PASS AFTER FIXES | None | Added disabled-profile claim denial, deleted demo-route assertion, and gate behavior coverage. |

## External Review

External review has not run yet. CodeRabbit and GitHub checks should run after the PR is opened.

## Remaining Risks

- Actor profile audit persistence currently imports the existing task audit repository. This keeps one v0.1 audit ledger but should be extracted to a shared audit module before actor/reputation work grows.
- Existing routes outside this chunk may continue using pure `get_current_actor` until deliberately migrated; this chunk deliberately registers actor context on `/auth/me`, worker profile setup, project routes, checker routes, and touched task routes.
- The next Terminal Benchmark live API drill still needs to run against this implementation through real HTTP calls after merge.

## Follow-Up Work

- Open PR and wait for CodeRabbit/GitHub checks.
- Address external review in a separate external-review response file if needed.
- After merge, rerun the Terminal Benchmark live API drill using the canonical worker profile endpoint.

## Human Review Focus

Please inspect:

- Flow auth boundary: token role first, profile eligibility second.
- Destructive removal of old worker/reviewer profile stores with no compatibility backfill.
- `ActorProfile` status semantics and preservation of explicit profile metadata.
- Overposting protections around registry writes.
- Demo/script cleanup from demo bootstrap to canonical worker profile API.

## Human Merge Ownership

Only the user can approve and merge this PR. Codex must not merge it without explicit user approval for that specific PR.
