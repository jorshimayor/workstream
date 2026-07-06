# PR Trust Bundle: WS-POL-001-11

## Chunk

`WS-POL-001-11` - Actor Identity And Profile Registry

## Goal

Approve the implementation contract for Workstream's local actor identity and
shared actor profile registry before coding the next backend chunk.

## Human-Approved Intent

The user asked to avoid adding only a worker profile path and instead define
one shared actor/profile model for the current actor types: worker, reviewer,
admin, project manager, and project owner.

Chunk contract:

- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/chunks/WS-POL-001-11-actor-identity-profile-registry.md`

## What Changed

- Added a `WS-POL-001-11` chunk contract.
- Updated loop state, work queue, initiative status, and chunk map after PR #72
  merged.
- Updated data model, glossary, system architecture, roles/permissions, and the
  older task queue spec to align with the actor identity/profile contract.
- Clarified that Flow token roles authorize routes and persisted profiles only
  support workflow eligibility, audit, display, and later reputation context.
- Clarified `project_owner` as scoped source/contact metadata, not a
  route-authorizing Workstream role.
- Required old worker/reviewer profile storage to migrate into shared
  `ActorProfile` authority without wrappers, shadow tables, or dual writes.
- Added implementation scope for stale demo/script helper cleanup so live API
  drills use `POST /api/v1/workers/me/profile`.

## Why It Changed

The live Terminal Benchmark drill showed worker profile setup was now real, but
the broader actor model still needed to be locked before implementation. Without
this contract, worker, reviewer, admin, and project-owner metadata could drift
into separate one-off models or, worse, become hidden permission authority.

## Design Chosen

- `ActorIdentity` is the local durable record for a verified Flow actor.
- `ActorProfile` is the shared profile and workflow eligibility record.
- `get_current_actor` stays pure token verification.
- A separate registration dependency records actor/profile metadata when a
  route deliberately needs that side effect.
- Route access is always derived from the current verified Flow token role.
- Profile status values are `observed`, `active`, and `disabled`.
- Task claim requires both verified `worker` token role and active worker
  profile.

## Alternatives Rejected

- Separate worker/reviewer/admin profile tables: rejected because they create
  duplicated profile authority.
- Persisted profiles as route permissions: rejected because Flow token claims
  are the route authorization source.
- Automatic worker/reviewer eligibility from token observation: rejected
  because eligibility must come from explicit profile workflows.
- Keeping old worker/reviewer profile wrappers: rejected because v0.1 is still
  under construction and should not preserve stale compatibility layers.

## Scope Control

No backend implementation code changed. No migrations, APIs, services, tests,
CI, frontend, payment, reputation, review lifecycle, checker runtime, agent
runtime, Celery behavior, blockchain behavior, or object storage behavior were
implemented.

## Product Behavior

- No runtime Workstream product behavior changed in this PR.
- Product review decisions remain only `accept`, `needs_revision`, and
  `reject`.
- The PR only locks the implementation contract for the next backend chunk.

## Acceptance Criteria Proof

- Actor identity/profile contract exists and is tracked in git.
- Public docs now distinguish Flow auth, `ActorContext`, `ActorIdentity`,
  `ActorProfile`, route authorization, and workflow eligibility.
- Permissions docs make task claim worker-only.
- Architecture docs no longer imply local actor/profile records grant route
  permissions.
- The contract requires migration backfill tests, spoofing tests, persisted
  profile privilege-escalation tests, status preservation tests, stale helper
  scans, and full task test coverage.

## Tests/Checks Run

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check HEAD~1..HEAD
git diff --check
```

Result summary:

- Stale wording scan: passed.
- Markdown link check: passed for 11 changed Markdown files.
- Diff whitespace checks: passed.
- Local XLSX export: not present.

## Test Delta

- Tests added: none.
- Tests modified: none.
- Tests removed/skipped: none.
- The next implementation contract explicitly requires the relevant tests.

## CI Integrity

- Coverage threshold unchanged.
- Lint configuration unchanged.
- Typecheck configuration unchanged.
- No workflow weakening.
- No package script weakening.
- No new GitHub Actions.
- No dependency changes.

## Reviewer Results

Internal review evidence:

- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-11-internal-review-evidence.md`

Reviewed code SHA: `b769b70c07d22f7a802f6d4219201e7bbd2a3ab0`

Reviewed diff digest before evidence files:
`86a15c53c7e407b902094212a5c08143e9c91cf154544e38ddbfc5e9f123983d`

Reviewer run IDs: see `WS-POL-001-11-internal-review-evidence.md`.

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Final scope and implementability confirmed. |
| QA/test | PASS | None | Required migration, profile, stale-helper, and task-test coverage confirmed. |
| security/auth | PASS | None | Token authority and profile non-permission boundary confirmed. |
| product/ops | PASS | None | Worker/reviewer/operator semantics confirmed. |
| architecture | PASS | None | Module boundary and demo/script cleanup scope confirmed. |
| CI integrity | N/A - with approved reason | N/A | No CI/workflow/package/dependency/config changes. |
| docs | PASS | None | Standing docs and chunk map align with the contract. |
| reuse/dedup | PASS | None | Single actor module/profile authority confirmed. |
| test delta | PASS | None | No tests changed; planned coverage is explicit. |

## External Review

External review has not run yet. CodeRabbit and GitHub checks should run after
the PR is opened.

## Remaining Risks

- The next PR must implement and prove the contract with real backend code and
  tests.
- Existing routes outside the next chunk may continue using pure
  `get_current_actor` until they are deliberately migrated.
- The next Terminal Benchmark drill must use the real worker profile endpoint,
  not `/api/v1/demo/worker-profile`.

## Follow-Up Work

- Implement `WS-POL-001-11` after human approval.
- Run the Terminal Benchmark live API drill with real HTTP requests after the
  actor/profile registry implementation merges.

## Human Review Focus

Please inspect:

- The route authority boundary: Flow token role first, profile eligibility
  second.
- The old worker/reviewer profile migration and no-compatibility stance.
- The `project_owner` wording as scoped source/contact metadata.
- The stale demo/script cleanup scope for the next live API drill.

## Human Merge Ownership

Only the user can approve and merge this PR. Codex must not merge it without
explicit user approval for that specific PR.
