# PR Trust Bundle: WS-POL-002-01

## Chunk

`WS-POL-002-01` - Post-Submit Compiler Contract

## Goal

Introduce the trusted compiler contract that turns a constrained
project-scoped post-submit checker spec into the canonical
`PostSubmitCheckerPolicy` body and hash.

## Human-Approved Intent

Post-submit checker setup must follow the same discipline as pre-submit:
agent-derived setup output can propose a constrained specification later, but
Workstream's trusted compiler owns the runtime policy. The checker, not an
agent, evaluates finalized submissions.

This chunk is intentionally compiler-only. Derivation agents, setup-run fields,
approval APIs, and runtime routing hardening remain in later WS-POL-002 chunks.

## What Changed

- Added `build_project_post_submit_checker_spec`.
- Added `compile_project_post_submit_checker_spec`.
- Added `PostSubmitCheckerCompilerError` and compiled policy output type.
- Made default-only post-submit policies valid by allowing empty
  project-specific `required_checkers` and `warning_checkers`.
- Kept Workstream default durable checkers mandatory through
  `default_checkers` and `execution_checkers`.
- Enforced `["critical", "high"]` as the platform blocking severity floor.
- Rejected malformed specs, tuple/non-list spec fields, unknown checker names,
  duplicates, conflicting required/warning classifications, warning-only
  default checker overrides, default-list drift, and severity downgrades.
- Mapped post-submit compiler failures to generic API-safe errors.
- Updated docs and live API drill payloads to match the new severity floor.

## Design Chosen

The compiler is owned by `backend/app/modules/projects/post_submit_policy.py`.
It validates against the registered deterministic checker catalog but does not
move logic into `backend/app/modules/checkers/compiler.py`, which remains the
pre-submit compiler module.

Policy identity remains:

```text
policy_hash = sha256(canonical_json(policy_body))
```

The canonical body contains:

- `schema_version`
- `project_id`
- `guide_version`
- `default_checkers`
- `required_checkers`
- `warning_checkers`
- `execution_checkers`
- `blocking_severities`

## Alternatives Rejected

- Put post-submit compilation into the pre-submit compiler module: rejected to
  preserve subsystem separation.
- Represent defaults by duplicating them into project `required_checkers`:
  rejected because default-only projects should be clear and project-specific
  additions should stay separate from platform defaults.
- Allow project policy to block only `high`: rejected because the runner treats
  both `critical` and `high` as blocking, and project policy cannot weaken the
  platform floor.
- Execute generated checker code: out of scope and rejected for v0.1.

## Scope Control

No Alembic migrations, ORM models, repositories, task modules, frontend,
payment/reputation, blockchain, or agent runtime code changed.

The only script/example changes align existing live-drill bootstrap
`blocking_severities` payloads with the compiler floor.

## Product Behavior

Project setup can now create a post-submit checker policy through the trusted
compiler path. Default-only projects remain valid, but finalized submissions
will still execute all platform durable post-submit checkers once tasks lock
that project policy.

Public setup errors stay generic. Raw checker/spec details are not returned to
workers or project setup callers.

## Acceptance Criteria Proof

- Default durable checkers are always present in `execution_checkers`.
- `policy_body.default_checkers` must exactly equal
  `DEFAULT_DURABLE_CHECKERS`.
- Unknown checker names fail closed.
- Duplicate or contradictory checker classifications fail closed.
- Warning-only default checker overrides fail closed.
- Explicit `blocking_severities: []`, `["critical"]`, and `["high"]` fail
  closed.
- Policy hash equals `sha256(canonical_json(policy_body))`.
- Parser rejects default-list drift, self-consistent default drift, severity
  downgrades, conflicting classifications, and hash mismatches.
- No reverse dependency from `backend/app/modules/checkers/compiler.py`.

## Tests/Checks Run

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
cd backend && .venv/bin/ruff check app/modules/projects/post_submit_policy.py app/modules/projects/service.py app/modules/projects/schemas.py tests/test_checkers.py tests/test_projects.py tests/test_tasks.py scripts/api_contract_e2e.py ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
cd backend && .venv/bin/pytest tests/test_projects.py -q -k 'default_only_post_submit or unregistered_checker_names or post_submit_compiler_validation'
cd backend && .venv/bin/pytest tests/test_checkers.py -q
cd backend && .venv/bin/pytest tests/test_projects.py tests/test_checkers.py -q
```

Result summary:

- Stale wording scan: passed.
- Markdown link check: passed for 21 changed Markdown files.
- Diff whitespace check: passed.
- Ruff: passed.
- Focused project API compiler slice: 5 passed, 208 deselected.
- Full checker suite: 69 passed.
- Exact contracted backend command: 282 passed in 2494.22s.

## Reviewer Results

Internal review evidence:

- `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-01-internal-review-evidence.md`

Reviewed code SHA: `dcaa703c6e53e7b3144edb4ba793b77530c1dbe5`

Reviewed at: `2026-07-09T16:02:30Z`

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Process-only evidence blocker addressed by this bundle. |
| QA/test | PASS WITH LOW RISKS | None | Exact contracted backend command later completed with 282 passing tests. |
| security/auth | PASS WITH LOW RISKS | None | No security blockers; generic error mapping and fail-closed compiler reviewed. |
| product/ops | PASS WITH LOW RISKS | None | Product behavior accepted; process-only evidence blocker addressed. |
| architecture | PASS | None | Scope and dependency boundary approved. |
| docs | PASS | None | Docs consistency approved after data-model compatibility wording fix. |
| reuse/dedup | PASS WITH LOW RISKS | None | Low severity-constant duplication risk accepted. |
| test delta | PASS | None | Additive tests; no weakened/skipped coverage. |
| CI integrity | PASS WITH LOW RISKS | None | No workflow/config weakening; full CI still runs complete backend tests. |

## External Review

Backend CI found one stale test expectation after the first push. The test still
expected screening to accept a persisted post-submit policy body after default
checker list drift. That expectation contradicted the new compiler contract, so
it was updated to assert fail-closed `422` and no locked post-submit policy body.

The response is recorded separately in:

- `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-01-external-review-response.md`

After the CI fix push, Backend, Agent Gates, and CodeRabbit passed.

## Remaining Risks

- Severity constants are explicitly owned in the compiler contract and also
  exist in the checker runner. Future severity model changes must be versioned
  or consolidated deliberately.
- Human merge review is still required. No external-review blocker remains.

## Human Review Focus

- Confirm the compiler, not the future derivation agent, owns canonical runtime
  post-submit policy.
- Confirm project policy cannot weaken Workstream default durable checkers.
- Confirm default-only projects are valid without implying no default checkers
  run.
- Confirm no task-specific checker generation is introduced.

## Human Merge Ownership

Only the user can approve and merge this PR. Codex must not merge it without
explicit user approval for that specific PR.
