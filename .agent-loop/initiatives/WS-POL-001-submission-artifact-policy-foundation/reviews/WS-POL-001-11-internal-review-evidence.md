# Internal Review Evidence: WS-POL-001-11

## Chunk

WS-POL-001-11

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: a008cf81519913f1ec2f6ffe530c0598f8df087e

Reviewed at: 2026-07-07T04:12:04Z

Reviewer run IDs: senior-engineering-review-019f3aa7-a13d-7052-85dc-635cbfa7dadb, qa-test-review-019f3aa7-a9a4-7e80-9fb5-8b9961b0c913, qa-test-rerun-019f3ac2-c5d7-7e90-947f-85309bd89808, security-auth-review-019f3aa7-b1b3-73f2-959e-9eaae25fabd3, product-ops-review-019f3aa7-bce6-77b1-9053-09926c54b4c9, architecture-review-019f3ab2-f368-7f03-bff7-29999e5a076f, ci-integrity-review-019f3ab2-f9fd-7263-82a3-d6fdf9d3967b, ci-integrity-rerun-019f3ac2-d856-7c80-9bcf-63f5c5b71c2d, docs-review-019f3ab3-0752-7391-adac-3a72c9af37ba, docs-rerun-019f3ac2-ce8e-7c12-9bbe-c3ffc54d1166, reuse-dedup-review-019f3ab3-12ad-7c92-86e7-eee531d82a6a, reuse-dedup-rerun-019f3ac2-e587-7d33-a978-57734c17d681, test-delta-review-019f3ab3-2436-7b82-9e17-7dd083ef1afa, test-delta-rerun-019f3ac2-fb49-7530-968f-50cd1b79041b

After the reviewed SHA, only evidence and status files changed.

## Reviewed Change

Scope:

- Implements local `ActorIdentity` and shared `ActorProfile` persistence for verified Flow actors.
- Keeps `get_current_actor` as the pure Flow-token boundary and adds `get_registered_actor` for explicit registry side effects.
- Creates new `actor_identities` and `actor_profiles` tables, then drops obsolete `worker_profiles` and `reviewer_profiles` without compatibility backfill.
- Makes worker profile activation write `ActorProfile(profile_type="worker", status="active")` through the actor module.
- Applies registration side effects to `/auth/me`, worker profile setup, project routes, checker routes, and task routes touched by this chunk.
- Makes task claim require both a verified `worker` token role and an active worker profile.
- Preserves active/disabled profile metadata during token observation refreshes.
- Keeps persisted profiles as workflow eligibility/audit records, never route permission authority.
- Rewires demo/scripts/examples from `/api/v1/demo/worker-profile` to `POST /api/v1/workers/me/profile`.
- Aligns docs with Flow issuer plus subject as the canonical identity anchor and Workstream actor id as a local durable reference.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Required stale evidence wording to be fixed so the PR no longer claims compatibility backfill or deleted demo UI proof. |
| QA/test | PASS AFTER FIXES | None | Added disabled-worker claim denial and deleted demo-route regression coverage. |
| security/auth | PASS | None | Confirmed no valid security/auth findings on the final code SHA. |
| product/ops | PASS AFTER FIXES | None | Required stale backfill wording to be fixed so operator expectations match destructive removal/no compatibility backfill. |
| architecture | PASS WITH LOW RISKS | None | Confirmed Flow auth boundary, actor/profile non-auth semantics, worker claim gate, and documented v0.1 audit ledger coupling. |
| CI integrity | PASS AFTER FIXES | None | Fixed stale reviewed-SHA evidence and made `.agent-loop` review evidence the canonical gate input; historical `docs/internal_reviews` notes are docs. |
| docs | PASS AFTER FIXES | None | Added destructive migration note and marked old demo/Week 1 internal-review references as superseded. |
| reuse/dedup | PASS AFTER FIXES | None | Added full reviewer provenance and corrected route-registration scope in evidence. |
| test delta | PASS AFTER FIXES | None | Added disabled-profile claim denial, deleted demo-route assertion, and gate behavior coverage. |

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
- Added a disabled-worker-profile claim regression proving disabled profiles cannot satisfy worker eligibility.
- Added a route-regression assertion proving `/api/v1/demo/worker-profile` is no longer mounted.
- Documented destructive actor-profile migration behavior in the public data model.
- Updated historical internal-review notes to mark removed demo helper behavior as superseded.
- Changed the internal-review evidence gate so ordinary `docs/internal_reviews` notes are documentation, while current gate-satisfying evidence must live in `.agent-loop/...-internal-review-evidence.md`.
- Updated this evidence with full reviewer run IDs and project/checker route-registration scope.

## Commands Run

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

Results:

- Ruff: passed.
- Stale wording scan: passed.
- Markdown link check: passed for 24 changed Markdown files.
- Diff whitespace check: passed.
- Agent gate tests: 26 passed.
- Internal review evidence gate: passed after this evidence update.
- Migration/actor/auth tests: 41 passed in 348.89s.
- Demo route regression: 1 passed in 14.77s.
- Task eligibility regressions: 2 passed in 84.84s.
- Local XLSX export: not present.

## Remaining Risks

- Actor profile audit writes use the existing task-owned audit ledger helper in v0.1. This keeps one audit source of truth for now, but a future shared audit module should extract the code boundary before actor/reputation work grows.
- Existing routes outside the chunk may continue using pure `get_current_actor` until deliberately migrated. This chunk adds registration side effects to `/auth/me`, worker profile setup, project routes, checker routes, and task routes touched here.
- The next Terminal Benchmark live API drill still needs to run through real HTTP calls against this implementation after PR review.
