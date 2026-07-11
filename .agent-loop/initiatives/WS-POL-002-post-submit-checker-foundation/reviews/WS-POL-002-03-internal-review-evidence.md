# Internal Review Evidence: WS-POL-002-03

## Chunk

WS-POL-002-03 - Server-Owned Policy Approval And Visibility APIs

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: e42b9506815a2eef155230928e791d5a737a6155

Reviewed at: 2026-07-11T15:51:10Z

Reviewer run ids: senior-engineering-019f5133-8882, qa-test-019f5133-9349, security-auth-019f5133-a018, product-ops-019f5133-b385, architecture-019f5133-cc0e, docs-019f5133-d78d, security-auth-rerun-019f513f-0255, product-ops-rerun-019f513e-fcdf, reuse-dedup-019f513f-0938, test-delta-019f513f-116c, ci-integrity-019f513f-1ce8

## Reviewed Change

Branch: `codex/ws-pol-002-03-post-submit-approval-visibility`

Scope:

- Adds operator-only setup visibility for generated project `PostSubmitCheckerPolicy` state.
- Adds server-owned approval and correction endpoints for generated post-submit checker policies.
- Keeps obsolete client-owned `post_submit_checker_policy` guide payloads rejected.
- Requires approved post-submit policy context to match the current guide, source snapshot, effective project policy, and compiled pre-submit checker.
- Records immutable approval provenance without accepting caller-provided approval notes.
- Clears unapproved generated output during correction and immediately requeues the existing setup continuation.
- Redacts raw source text, local paths, exact source hashes, source item refs, policy bodies, secrets, and credential-shaped values from setup visibility responses.
- Adds negative authorization coverage for worker, reviewer, finance, and auditor roles.
- Updates operator/product/data-model docs and active loop state for this chunk.
- Reconciles CodeRabbit-discovered lifecycle drift across WS-POL-002 and
  WS-AUTH-001 artifacts so `WS-POL-002-03` is the current PR #90 review chunk
  and future WS-POL chunks remain separately gated. Related lifecycle wording
  touched `WS-AUTH-001-01`, `WS-AUTH-001-12`, `WS-AUTH-001-16`, and
  `WS-AUTH-001-PLAN` records.

## Reviewer Results

These are Codex engineering-loop reviewer verdicts, not Workstream product
review decisions. Product review decisions remain `accept`, `needs_revision`,
and `reject`; internal reviewer agents report `PASS`, `PASS WITH LOW RISKS`,
`PASS AFTER FIXES`, or `FAIL` so process evidence stays separate from product
lifecycle records.

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Confirmed the service/repository boundary stayed narrow and no task runtime behavior was pulled into this chunk. |
| QA/test | PASS WITH LOW RISKS | None | Found ignored approval-note input; fixed by removing the field and keeping the approval body empty with `extra="forbid"`. |
| security/auth | PASS | None | Initial credential-shaped redaction concern was fixed and retested with `sk-` style redaction in correction metadata. |
| product/ops | PASS WITH LOW RISKS | None | Initial correction dead-end and visibility-summary concerns were fixed with automatic setup continuation and bounded derivation input summary. |
| architecture | PASS WITH LOW RISKS | None | Confirmed the server-owned setup path remains project-scoped and does not introduce runtime agent judgment or per-task checker generation. |
| docs | PASS WITH LOW RISKS | None | Found checklist drift around post-submit policy approval; fixed in the operator manual and product flow docs. |
| reuse/dedup | PASS WITH LOW RISKS | None | Found no blocking duplication; service helpers stayed local to the projects boundary. |
| test delta | PASS WITH LOW RISKS | None | Requested broader leakage assertions; fixed by asserting policy body, source refs, source hashes, and guide text are absent. |
| CI integrity | PASS WITH LOW RISKS | None | Confirmed no CI/test weakening; final project/auth and Alembic tests were rerun after fixes. |

## Valid Findings Addressed

- Removed caller-supplied approval notes from `PostSubmitCheckerPolicyApproval` so approval provenance is server-owned and no ignored input is accepted.
- Added credential-shape redaction for bounded setup summaries and correction metadata.
- Added automatic setup continuation enqueue after correction clears unapproved generated output.
- Added bounded `derivation_input_summary` so operators can see source/effective/pre-submit context without raw source material or policy bodies.
- Changed product wording from "task display" to "operator-visible post-submit checker policy summary".
- Expanded tests to assert no policy body, source item ref, source item hash, raw source hash, or guide text leaks in setup visibility responses.
- Addressed CodeRabbit feedback that correction requests could be read as an
  activation alternative; product and operator docs now state correction blocks
  activation, clears unapproved output, and returns to regeneration.
- Addressed CodeRabbit feedback that loop artifacts had conflicting
  `WS-POL-002-03` lifecycle states; PR #90 is now represented as the active
  user-review chunk, while `WS-POL-002-04` and future WS-POL work remain
  inactive until explicit starts.

## Commands Run

```bash
cd backend && .venv/bin/pytest tests/test_projects.py::test_post_submit_checker_policy_approval_uses_server_provenance tests/test_projects.py::test_post_submit_checker_policy_correction_clears_unapproved_output -q
cd backend && .venv/bin/pytest tests/test_projects.py -q -k "post_submit_checker_policy or post_submit_setup_visibility"
cd backend && .venv/bin/pytest tests/test_auth.py -q
cd backend && .venv/bin/pytest tests/test_alembic.py -q
cd backend && .venv/bin/pytest tests/test_projects.py tests/test_auth.py -q
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/check_loop_memory_state.py
git diff --check
```

Results:

- Targeted approval/correction tests: 2 passed.
- Focused post-submit project setup slice: 9 passed, 224 deselected.
- Auth suite: 21 passed.
- Alembic suite: 6 passed.
- Final project/auth suite: 254 passed in 2825.49s.
- Stale wording scan: passed.
- Markdown link check: passed.
- Loop memory state check: passed.
- Diff whitespace check: passed.

Rebind note:

- The PR branch was updated with current `main` after the original evidence was
  recorded. CI correctly failed the stale reviewed-SHA gate because non-evidence
  files from `main` appeared above the prior reviewed commit.
- A later CodeRabbit pass found lifecycle-state drift between WS-POL and WS-AUTH
  loop artifacts. This evidence now binds to the non-evidence commit that
  reconciles those artifacts before this evidence-only rebind commit.

## Remaining Risks

- GitHub Actions and CodeRabbit passed on PR head
  `19680969d267c339907bc507ec37b22c65665298` before the local
  CodeRabbit-response fixes. They must rerun after these fixes are pushed.
- Project-scoped `project_manager` role grants remain future Workstream role-assignment work; this chunk keeps the current bootstrap authorization boundary and documents that limit.
- `WS-POL-002-04` still owns runtime hardening for locked post-submit policy execution and routing.
