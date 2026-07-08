# Internal Review Evidence: WS-POL-001-15

## Chunk

WS-POL-001-15

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: b72a5b90979137d31127c2292f85ae350918f4f7

Reviewed at: 2026-07-08T16:23:01Z

Reviewer run IDs: senior-engineering-019f4264-c478-74c3-80fd-128bfa49c33a, qa-test-019f4264-c6ff-7c72-b9ca-024c0d611f28, security-auth-019f4264-cad2-7bb2-b10d-64ec8029d92b, product-ops-initial-019f4264-ce45-7f22-9797-9b466b294f1c, product-ops-final-019f4269-043e-7ca2-ad07-9a013898ffd6, architecture-019f4264-d2a0-74e2-a16a-77a79c5bd49e, docs-019f4264-da2d-7992-90cc-80781a5ccb79, reuse-dedup-019f4269-0874-7b91-90aa-c5d2a17993a5, test-delta-019f4269-0edf-7e30-aa23-eb86e99544a7

After the reviewed SHA, only evidence and review-bundle files changed.

## Reviewed Change

Scope:

- Added corrective chunk contract `WS-POL-001-15` after the accepted no-DB Terminal Benchmark drill from `main` failed during agent-derived submission artifact policy creation.
- Hardened `SubmissionArtifactPolicyDerivationAgent` instructions so derived policies must be project-level worker submission contracts, not reviewer packets or copies of source-snapshot material.
- Prohibited self-conflicting policies where forbidden artifact patterns match required artifact keys, paths, descriptions, required evidence keys, labels, or descriptions.
- Prohibited secret/credential/token wording in required artifact and evidence fields that the server treats as forbidden artifact surfaces.
- Required exact safe relative file paths for required artifacts; broad globs remain allowed only for forbidden artifact patterns.
- Added a prompt-contract regression test for the derivation instructions.
- Added a Terminal Benchmark-shaped validation case where `steps/milestone_1/tests/test_m1.py` is required while `steps/*/tests/*` is forbidden, preserving fail-closed server validation.
- Updated loop state, work queue, review log, status, chunk map, and roadmap status so the failed main-branch drill and corrective chunk are not stale.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Confirmed the fix is narrow and server validation remains the enforcement boundary. Low note: the prompt constant is growing. |
| qa/test | PASS WITH LOW RISKS | None | Confirmed acceptance criteria coverage, prompt-contract test, fail-closed validation regression, and live-drill evidence. Optional fake-runtime endpoint replay was noted as follow-up only. |
| security/auth | PASS WITH LOW RISKS | None | Found a low issue that descriptions were not explicitly covered by prompt wording; fixed before reviewed SHA. Confirmed default forbidden artifact validation remains fail-closed. |
| product/ops | PASS WITH LOW RISKS | None | Initial review failed on stale prompt-test assertions after security wording changed; assertions were fixed and final product/ops review passed. |
| architecture | PASS WITH LOW RISKS | None | Confirmed no task-level checker generation, new runtime provider, auth, model, migration, or checker boundary drift. |
| docs | PASS WITH LOW RISKS | None | Found stale current-gate wording in work queue, review log, and roadmap status; fixed before reviewed SHA. |
| reuse/dedup | PASS WITH LOW RISKS | None | Confirmed no duplicate validator/helper was added; the existing policy creation and forbidden-pattern path are reused. |
| test delta | PASS WITH LOW RISKS | None | Confirmed no tests were removed, skipped, or weakened. Low note: prompt string assertions are brittle but acceptable because the prompt is the contract. |

## Valid Findings Addressed

- Added required artifact and evidence descriptions to the derivation prompt's self-conflict prohibition.
- Added required evidence keys, labels, and descriptions to the secret/credential/token prompt prohibition.
- Updated prompt-pin test assertions to match the strengthened prompt wording.
- Updated `.agent-loop/WORK_QUEUE.md`, `.agent-loop/REVIEW_LOG.md`, and `docs/roadmap_status.md` so they no longer describe the accepted no-DB Terminal Benchmark drill as merely pending from `main`.
- Added `.agent-loop/WORK_QUEUE.md` to the `WS-POL-001-15` allowed-file lists after the docs review correctly identified it as in-scope state.
- Added the project-level artifact-intake criterion to the chunk-map summary so it matches the chunk contract.

## Commands Run

```bash
cd backend && .venv/bin/pytest tests/test_projects.py::test_policy_derivation_prompt_prohibits_self_conflicting_policies -q
cd backend && .venv/bin/pytest tests/test_projects.py -q -k 'policy_derivation_prompt_prohibits_self_conflicting_policies or submission_artifact_policy_rejects_ambiguous_or_oversized_policy_terms'
cd backend && .venv/bin/pytest tests/test_projects.py -q
bash -lc 'set -a; source /home/abiorh/flow/jarvis-live-agent-proof/.env; set +a; export WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test; export WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL=${WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL:-gpt-4.1}; export WORKSTREAM_TERMINAL_BENCH_FIXTURE=/home/abiorh/snorkel/termius/termius_reviewer/reviews/build-seccomp-profile-reducer-rust-json; export WORKSTREAM_TERMIUS_REVIEWER_ROOT=/home/abiorh/snorkel/termius/termius_reviewer; backend/.venv/bin/python examples/terminal_benchmark/terminal_benchmark_api_e2e.py'
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
```

Results:

- Prompt-contract test: `1 passed in 4.69s`.
- Targeted project subset: `16 passed, 193 deselected in 120.49s`.
- Full project suite on final diff: `209 passed in 1740.01s`.
- Terminal Benchmark real API E2E on final diff: passed with the real OpenAI Agents SDK derivation path.
- Terminal Benchmark scenario summary: `complete_packet=review_pending`, `missing_static_guard=pre_submit_blocked_no_submission`, `low_quality_v1=needs_revision`, `fixed_low_quality_v2=review_pending`, `worker_profile_setup=canonical_worker_profile_api`.
- Stale wording check: passed.
- Markdown link check: passed for 7 changed Markdown files.
- Diff whitespace check: passed.

## External Review Separation

CodeRabbit and GitHub checks are external review. They will be tracked
separately if comments arrive after the PR opens.

## Remaining Risks

- Prompt hardening improves the agent output contract, but the deterministic server guard remains the authority and may still reject invalid future model output.
- The server path validator already rejects empty/traversal/URL/storage/absolute paths; a stricter explicit no-glob path guard can be considered in a later checker-policy hardening chunk if real output requires it.
- A fake-runtime endpoint replay of the exact self-conflict could be added later, but the current chunk has shared-validator regression coverage and a passing real Terminal Benchmark API drill.
