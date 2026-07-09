# Internal Review Evidence: WS-POL-002-01

## Chunk

WS-POL-002-01

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: dcaa703c6e53e7b3144edb4ba793b77530c1dbe5

Reviewed at: 2026-07-09T16:02:30Z

Reviewer run IDs: senior-engineering-019f4760-6ed1-7250-9fff-b9848c51ed03, qa-test-019f4760-9f01-7730-af60-195bb2d198c2, security-auth-019f4760-c653-71a3-9d0b-2cfd391c26c0, product-ops-019f4760-f05d-7ad2-ae8a-cb991473c287, architecture-019f4761-1582-7eb0-8f3f-3525822c118a, docs-019f4761-4d3c-76c1-9953-cf03998391cc, reuse-dedup-019f479e-04bb-7063-9df0-2a6c5b2d20d6, test-delta-019f4731-f095-78c2-9c1b-472970127ad9, ci-integrity-019f479e-2886-7f53-8777-b7f93f4a033b

## Reviewed Change

Branch: `codex/ws-pol-002-01-post-submit-compiler`

Scope:

- Adds the trusted project-scoped post-submit checker compiler contract.
- Keeps compiler ownership in `backend/app/modules/projects/post_submit_policy.py`.
- Keeps the pre-submit compiler module separate and unmodified.
- Makes default-only project post-submit policies valid while preserving
  mandatory platform defaults through `default_checkers` and
  `execution_checkers`.
- Fails closed on unknown checker names, duplicate/conflicting classifications,
  warning-only default overrides, non-list spec fields, default-list drift, and
  blocking severity downgrades.
- Maps compiler failures to generic API-safe setup errors.
- Aligns existing real API drill payloads with the non-weakenable
  `["critical", "high"]` severity floor.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | No code-level blockers; initial process finding was missing evidence artifacts, addressed by this file and the PR trust bundle. |
| QA/test | PASS WITH LOW RISKS | None | Confirmed compiler/body/hash behavior and tests; exact contract backend command later passed with 282 tests. |
| security/auth | PASS WITH LOW RISKS | None | Confirmed fail-closed compiler behavior, generic public error mapping, and no auth/PII/secret/payment risks. |
| product/ops | PASS WITH LOW RISKS | None | No product behavior blockers; initial process finding was missing evidence artifacts, addressed here. |
| architecture | PASS | None | Confirmed scope, project-scoped compiler boundary, and no forbidden module changes. |
| docs | PASS | None | Confirmed compiler boundary, critical/high floor, default-list compatibility wording, and live-drill scope. |
| reuse/dedup | PASS WITH LOW RISKS | None | Low future drift risk from duplicating severity literals; no blocking missed abstraction. |
| test delta | PASS | None | Confirmed additive tests and no skipped, xfailed, or weakened tests. |
| ci integrity | PASS WITH LOW RISKS | None | No workflow/config weakening; full CI still runs complete backend pytest. |

## Valid Findings Addressed

- Pre-implementation architecture review found the chunk too broad. The chunk
  contract was narrowed to compiler/body/hash behavior only.
- Reviewers found the locked parser accepted severity downgrade and default-list
  drift scenarios. The parser now requires the current server-owned default
  list, canonical execution list, matching hash, and the critical/high severity
  floor.
- Reviewers found compiler errors could leak raw checker details through API
  setup paths. Project service now maps compiler failures to
  `post-submit checker policy compilation failed`.
- Security review found an activation fallback could leak raw unregistered
  checker names for corrupted persisted rows. Activation now returns a generic
  unregistered-checker message.
- Test-delta found missing API-level explicit empty severity coverage and
  weaker default-list drift coverage. Added guide-create API coverage for
  `blocking_severities: []`, self-consistent default drift, conflicting locked
  classifications, and raw-spec downgrade tests.
- QA found tuple-shaped spec fields were still accepted by the shared validator.
  The compiler now accepts only JSON-list-shaped `list` values and has a
  tuple-spec regression test.
- Docs review found data-model wording overstated locked-body independence from
  future default-list compatibility. Updated the docs to require an approved
  versioning, compatibility, or migration path for future default-list changes.
- Product/ops and QA found stale live-drill payloads with old severity lists.
  Updated the API contract and Terminal Benchmark example payloads to include
  `critical` and `high`.
- Senior/product/docs initially failed only because final evidence artifacts
  were missing. This evidence file and the PR trust bundle address that process
  blocker.

## Commands Run

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
cd backend && .venv/bin/ruff check app/modules/projects/post_submit_policy.py app/modules/projects/service.py app/modules/projects/schemas.py tests/test_checkers.py tests/test_projects.py tests/test_tasks.py scripts/api_contract_e2e.py ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
cd backend && .venv/bin/pytest tests/test_projects.py -q -k 'default_only_post_submit or unregistered_checker_names or post_submit_compiler_validation'
cd backend && .venv/bin/pytest tests/test_checkers.py -q
cd backend && .venv/bin/pytest tests/test_projects.py tests/test_checkers.py -q
```

Results:

- Stale wording scan: passed.
- Markdown link check: passed for 21 changed Markdown files.
- Diff whitespace check: passed.
- Ruff: passed.
- Focused project API compiler slice: 5 passed, 208 deselected.
- Full checker suite: 69 passed.
- Exact contracted backend command: 282 passed in 2494.22s.

## Remaining Risks

- Reuse/dedup noted a low future drift risk because
  `post_submit_policy.py` owns explicit ordered severity strings while
  `checkers.runner` also has severity constants. This is accepted for this
  chunk because the compiler floor is a policy contract; future severity model
  changes should consolidate or version this intentionally.
- CI integrity noted the local chunk contract no longer lists Alembic tests.
  This is accepted because this compiler-only chunk does not change models,
  repositories, or migrations, and backend CI still runs full `pytest -q`.
- CodeRabbit and GitHub Actions still need to run on the PR after push. External
  comments must be recorded separately in
  `WS-POL-002-01-external-review-response.md`.
