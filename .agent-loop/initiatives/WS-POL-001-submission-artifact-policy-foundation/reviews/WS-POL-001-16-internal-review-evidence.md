# Internal Review Evidence: WS-POL-001-16

## Chunk

WS-POL-001-16-terminal-benchmark-live-api-drill

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 48cdcd2512428632225f2f97359b68271ab03575

Reviewed at: 2026-07-09T01:21:17Z

Reviewer run IDs: senior-engineering-initial-019f4468-0149-7331-8432-375a955e4617, senior-engineering-rerun-019f446e-568e-7c00-9728-3e15f65b28a6, senior-engineering-final-019f4472-4bd5-7693-a477-1fae8be3b573, qa-test-initial-019f4468-085b-7bd1-ab51-7bb5a1c6242b, qa-test-rerun-019f446e-4dd4-7c80-a020-799f61f45c37, security-auth-initial-019f4468-146c-7c40-a44a-327b5e619453, security-auth-rerun-019f446e-5f86-7b50-90af-2e7bb3144a09, product-ops-initial-019f4468-22bf-7b81-aff1-82f91df7f853, product-ops-rerun-019f446e-6b96-7df3-a525-7894302969e6, architecture-initial-019f4468-2fb0-7aa3-a3f7-3f08a4efc3ea, architecture-rerun-019f446e-7dc0-7963-949d-da760eaa0779, docs-initial-019f4468-397a-7752-ab7f-e536b304ecd8, docs-rerun-019f446e-8b52-73e1-a1cb-50e7acd11abe, reuse-dedup-019f4472-4ff2-70e1-8a06-32fcfecdd4b5, test-delta-019f4472-5431-7a41-af36-00f19813b272

After the reviewed SHA, only allowed review evidence, PR trust-bundle, status, and loop-state files may change.

## Reviewed Change

Scope:

- Recorded the final clean Terminal Benchmark live API drill evidence for `WS-POL-001-16`.
- Captured sanitized source snapshot material, source hashes, setup-run status, sufficiency output, derived submission artifact policy, effective project policy, and compiled project pre-submit checker policy.
- Added explicit sufficiency-agent input and submission-policy-derivation input summaries using the real `GuideSourceMaterial` envelope and source snapshot hashes.
- Added a redacted HTTP body appendix for every final-run API request and response body, including all 14 setup-run polls.
- Proved blocked pre-submit with `pre_submission_checker_failed`, empty task submission list, and audit-event evidence; checker-run visibility is proven only after a submission id exists because checker-run list/get APIs are submission-scoped.
- Proved successful pre-submit, submission creation, manager finalization, automatic checker run, durable checker results, audit events, and final `review_pending` task state without database inspection as lifecycle proof.
- Updated initiative and loop status to show this chunk is evidence complete and awaiting PR/human checkpoint.
- Repaired the chunk contract wording for blocked-intake checker-run evidence so it matches the existing submission-scoped checker-run API design.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Initial and rerun reviews found missing full body transcript, missing agent inputs, checker-run proof wording mismatch, and missing setup-poll body entries. Evidence and contract wording were fixed. Final low note about poll-summary mismatch was corrected. |
| qa/test | PASS AFTER FIXES | None | Initial review failed on summarized transcript, missing agent inputs, incomplete blocked proof, and abbreviated pre-submit response. Rerun confirmed redacted bodies, full pre-submit structures, agent input/output, blocked audit proof, and checker-run visibility after submission exists. |
| security/auth | PASS AFTER FIXES | None | Confirmed no bearer token values, API key values, signed URLs, raw local filesystem paths, unsafe source refs, or auth expansion. Forbidden-pattern strings such as `api_key`, `secret`, and `token` are checker policy patterns only. |
| product/ops | PASS AFTER FIXES | None | Confirmed lifecycle clarity, worker/operator visibility, no product decision leakage in pre-submit, no Terminal Benchmark fork, and correct blocked/success/finalize/checker/audit state. |
| architecture | PASS AFTER FIXES | None | Confirmed docs/evidence-only scope, no task-specific checker generation, no DB-only lifecycle proof, no backend behavior change, no default-checker weakening, and valid checker-run visibility contract repair. |
| docs | PASS AFTER FIXES | None | Confirmed stale wording, Markdown links, whitespace, roadmap/status wording, and redacted appendix readability after fixes. |
| reuse/dedup | PASS | None | Confirmed no new scripts, helpers, backend code, or duplicate implementation; the appendix is evidence, not parallel implementation. |
| test delta | PASS | None | Confirmed no tests were added, modified, removed, skipped, or weakened; verification evidence matches the chunk contract. |

## Valid Findings Addressed

- Added a redacted HTTP request/response body appendix for every human-review API step.
- Added every setup-run poll response body from `03_setup_poll_01` through `03_setup_poll_14`.
- Added sufficiency-agent input and submission-policy-derivation input summaries tied to the source snapshot and content hashes.
- Expanded blocked pre-submit proof to include audit evidence and clarified why checker-run list/get is only valid after submission creation.
- Repaired the chunk contract acceptance criterion for blocked intake to match the submission-scoped checker-run API design.
- Moved roadmap wording from completed to under-review state for `WS-POL-001-16`.
- Corrected the compact setup-poll summary so it matches the appendix body statuses.
- Staged the formal live evidence file so it is no longer untracked.

## Commands Run

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
cd backend && .venv/bin/pytest tests/test_projects.py tests/test_tasks.py tests/test_checkers.py -q
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/api_contract_e2e.py
git diff --cached --check
```

Results:

- Stale wording check: passed.
- Markdown link check: passed for 6 changed Markdown files.
- Focused backend tests: `342 passed in 4305.43s (1:11:45)`.
- API contract drill: `API contract real API e2e passed`.
- Diff whitespace check: passed.

## Evidence Gate

Evidence gate: PASS.

Scope:

- Changed files stay inside the `WS-POL-001-16` allowed evidence/status scope.
- No backend, migration, script, test, CI, dependency, frontend, payment, reputation, blockchain, or auth behavior files changed.
- No Workstream default checker was weakened.
- No task-specific checker generation was introduced.

## External Review Separation

CodeRabbit, GitHub checks, and human PR review are external review. They will be tracked separately if comments arrive after PR creation.

## Remaining Risks

- The redacted HTTP appendix is large because the contract required human-reviewable request and response bodies. It is evidence-only and does not add runtime code.
- The live drill proves the final clean Terminal Benchmark path; future review lifecycle chunks still need reviewer packet and `needs_revision` API coverage.
