# Internal Review Evidence: WS-POL-001-16

## Chunk

WS-POL-001-16-terminal-benchmark-live-api-drill

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 4471549742041e2818d3e3cd89e36518d7126993

Reviewed at: 2026-07-09T04:14:08Z

Reviewer run IDs: senior-engineering-final-019f4506-2be4-7bb3-a66e-a96893f34b1d, qa-test-final-019f450b-de80-7101-9b06-f41167c0df00, security-auth-final-019f450b-e649-7aa1-8399-7b8a5968ee0b, product-ops-final-019f4506-48d3-7c91-b162-8bf72ec5c4de, architecture-final-019f4512-7cef-7a02-9cf6-78fbad3f73af, docs-final-019f4506-11cf-73d2-942a-9327cc22cadf, reuse-dedup-final-019f4512-9182-7990-99ac-ccc438b5fb6b, test-delta-final-019f4506-598d-7880-8927-a85e5b4b0cbb, ci-integrity-final-019f450b-ee14-7992-b45b-51225962b7fd

After the reviewed SHA, only allowed review evidence, PR trust-bundle, status,
loop-state files, and the documented privacy-scrub amendment files may change.

## Reviewed Change

Scope:

- Recorded the final clean Terminal Benchmark live API drill evidence for `WS-POL-001-16`.
- Captured sanitized source snapshot material, setup-run status, sufficiency output, derived submission artifact policy, effective project policy, and compiled project pre-submit checker policy.
- Added explicit sufficiency-agent input and submission-policy-derivation input summaries using the real `GuideSourceMaterial` envelope, with public source-material fingerprints redacted.
- Added a redacted HTTP body appendix for every final-run API request and response body, including all 14 setup-run polls.
- Proved blocked pre-submit with `pre_submission_checker_failed`, empty task submission list, and audit-event evidence; checker-run visibility is proven only after a submission id exists because checker-run list/get APIs are submission-scoped.
- Proved successful pre-submit, submission creation, manager finalization, automatic checker run, durable checker results, audit events, and final `review_pending` task state without database inspection as lifecycle proof.
- Updated initiative and loop status to show this chunk is evidence complete and awaiting PR/human checkpoint.
- Repaired the chunk contract wording for blocked-intake checker-run evidence so it matches the existing submission-scoped checker-run API design.
- Added a privacy-scrub amendment after human review found private/local source
  identifiers in the standalone Terminal Benchmark example and older evidence.
- Scrubbed standalone example naming, older Terminal Benchmark evidence, local
  secret-env paths, private fixture/source identifiers, exact source-material
  hashes, exact byte counts, local drill UUIDs, and source-specific task tags
  from public PR evidence.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Confirmed the privacy scrub is scoped, maintainable, and does not change backend/product behavior. |
| qa/test | PASS WITH LOW RISKS | None | Initial rerun found top-level fixture/startup failure paths could leak local labels. The example now emits a generic sanitized failure by default and preserves raw output only behind explicit debug opt-in. |
| security/auth | PASS | None | Confirmed no private source names, raw local paths, raw local UUIDs, exact source fingerprints, credentials, or raw server logs remain in public evidence/example output by default. |
| product/ops | PASS WITH LOW RISKS | None | Confirmed the Terminal Benchmark material remains a standalone Workstream reference example, not a leaked external/company workflow. |
| architecture | PASS WITH LOW RISKS | None | Confirmed the privacy scrub stays in docs/evidence/example scope and does not change Workstream product architecture, checker authority, or task-specific checker generation. |
| docs | PASS WITH LOW RISKS | None | Confirmed public evidence, trust bundle, roadmap status, and historical evidence amendments are standalone and privacy-safe. |
| reuse/dedup | PASS | None | Confirmed the redaction helper is local to the optional example and does not duplicate backend/runtime/checker abstractions. |
| test delta | PASS WITH LOW RISKS | None | Confirmed no tests/checks were weakened and final evidence records parse, privacy-scan, and redaction checks. |
| ci integrity | PASS WITH LOW RISKS | None | Confirmed no CI/workflow/package/test gate was weakened and this evidence can bind to the reviewed revision with evidence-only updates after it. |

## Valid Findings Addressed

- Added a redacted HTTP request/response body appendix for every human-review API step.
- Added every setup-run poll response body from `03_setup_poll_01` through `03_setup_poll_14`.
- Added sufficiency-agent input and submission-policy-derivation input summaries tied to the source snapshot, with public source-material fingerprints redacted.
- Expanded blocked pre-submit proof to include audit evidence and clarified why checker-run list/get is only valid after submission creation.
- Repaired the chunk contract acceptance criterion for blocked intake to match the submission-scoped checker-run API design.
- Moved roadmap wording from completed to under-review state for `WS-POL-001-16`.
- Corrected the compact setup-poll summary so it matches the appendix body statuses.
- Staged the formal live evidence file so it is no longer untracked.
- Added a public-evidence redaction boundary so reviewers can distinguish the
  local live drill from the privacy-redacted public transcript.
- Removed private/local source names, exact source-material fingerprints, exact
  source byte counts, local database UUIDs, and source-specific task labels
  from current and older public evidence.
- Redacted agent-derived `policy_version` values that exposed source snapshot
  hash prefixes in public evidence.
- Renamed legacy private-source environment wording to public
  `WORKSTREAM_TERMINAL_BENCH_*` wording.
- Suppressed shared helper progress output and checker polling output by
  default in the optional Terminal Benchmark example.
- Added public-safe exception and top-level failure handling so copied failure
  transcripts do not expose fixture labels, local paths, raw server logs, UUIDs,
  fixture ids, or source hashes unless
  `WORKSTREAM_TERMINAL_BENCH_PRINT_RAW_LOCAL_IDS=1` is explicitly set.

## Commands Run

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
cd backend && .venv/bin/pytest tests/test_projects.py tests/test_tasks.py tests/test_checkers.py -q
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/api_contract_e2e.py
cd backend && .venv/bin/python -m ruff check ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
cd backend && python3 -m py_compile ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
redaction helper inline check for UUID, fixture-id, hash, and local-path sanitization
default missing-agent-env failure check for sanitized stderr and nonzero exit
targeted privacy scan for private source names, local paths, fixture-id shapes, source-task labels, and agent hash prefixes
git diff --check
```

Results:

- Stale wording check: passed.
- Markdown link check: passed for 25 changed Markdown files.
- Focused backend tests: `342 passed in 4305.43s (1:11:45)`.
- API contract drill: `API contract real API e2e passed`.
- Terminal Benchmark example Ruff and py_compile: passed.
- Public-safe exception helper check: `terminal benchmark public-safe exception redaction passed`.
- Default missing-agent-env failure check: emitted only
  `RuntimeError: Terminal Benchmark API drill failed. Raw local failure details are hidden by default; set WORKSTREAM_TERMINAL_BENCH_PRINT_RAW_LOCAL_IDS=1 for local debugging.`
  and printed `terminal benchmark public failure output redaction passed`.
- Privacy scan: only intentional backend test literals remained for unsafe-path
  and reserved `agent-` prefix validation.
- Diff whitespace check: passed.

## Evidence Gate

Evidence gate: PASS.

Scope:

- Changed files stay inside the `WS-POL-001-16` allowed evidence/status scope.
- The privacy-scrub amendment explicitly allows the standalone example and
  older evidence/doc files touched to remove private/local source identifiers.
- No backend, migration, backend script, test, CI, dependency, frontend,
  payment, reputation, blockchain, or auth behavior files changed.
- No Workstream default checker was weakened.
- No task-specific checker generation was introduced.

## External Review Separation

CodeRabbit, GitHub checks, and human PR review are external review. They will be tracked separately if comments arrive after PR creation.

## Remaining Risks

- The redacted HTTP appendix is large because the contract required human-reviewable request and response bodies. It is evidence-only and does not add runtime code.
- The live drill proves the final clean Terminal Benchmark path; future review lifecycle chunks still need reviewer packet and `needs_revision` API coverage.
- Default failure output may include unrelated Alembic INFO lines before the
  sanitized failure if migration logging is enabled, but reviewer reruns
  confirmed it does not expose fixture/source details, paths, hashes, UUIDs,
  or tracebacks.
