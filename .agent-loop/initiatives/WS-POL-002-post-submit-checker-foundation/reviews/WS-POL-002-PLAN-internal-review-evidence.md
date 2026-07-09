# Internal Review Evidence: WS-POL-002-PLAN

## Chunk

`WS-POL-002-PLAN` - Post-Submit Checker Foundation Planning

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Base SHA: `a3d2a3f1701391c8dafdca6cff2f0f80dbebda3b`

Reviewed at: 2026-07-09T07:51:21Z

Reviewer run IDs:

- senior-engineering: `019f45cc-18c8-7773-96e5-69718376bc68`
- QA/test: `019f45d6-0b10-7711-b93a-36829979e9b4`
- security/auth: `019f45d3-1319-7171-873b-85670bfcf071`
- product/ops: `019f45cc-3125-72c1-9396-4346ae293529`
- architecture: `019f45d3-0d52-7423-82a5-524a61841f86`
- docs: `019f45cc-453d-73c0-acd9-58f906dd27f4`
- reuse/dedup: `019f45d3-5206-75b1-a245-0c5fc8f015b3`
- test delta: `019f45d3-6067-78c0-8f2b-cc5001da3e17`
- CI integrity: `019f45d9-2c32-7df2-bdae-98d90a46e6d1`

## Reviewed Change

Scope:

- Closed stale `WS-POL-001-16` loop memory after PR #84 merged.
- Started `WS-POL-002` planning for post-submit checker foundation.
- Added intent, discovery, plan, risks, decisions, status, chunk map, and chunk
  contracts.
- Preserved project-scoped `PostSubmitCheckerPolicy`; no task-specific checker
  generation is introduced.
- Defined a resumable setup boundary: initial guide/source setup stops at
  `policy_draft_ready`; post-submit derivation starts only after setup-approved
  submission artifact policy approval creates the effective policy and compiled
  project pre-submit checker bundle.
- Kept v0.1 setup authorization honest: verified `admin` / `project_manager`
  roles remain the current bootstrap boundary; project-scoped role assignment is
  out of scope for WS-POL-002.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Confirmed real Celery files, persistence scope, planning contract, and narrowed runtime scope after fixes. |
| QA/test | PASS | None | Confirmed feasible commands and resolved source-hash evidence contradiction. |
| security/auth | PASS | None | Confirmed v0.1 setup authorization wording, prompt-injection controls, redaction, and default-checker protections. |
| product/ops | PASS WITH LOW RISKS | None | Confirmed lifecycle/product routing boundaries; low clarifications were folded into final proof and runtime contracts. |
| architecture | PASS | None | Confirmed current authorization boundary, setup trigger boundary, model/migration scope, planning contract, and privacy scan path. |
| docs | PASS WITH LOW RISKS | None | Confirmed persistence scope, canonical wording, command shape, and docs clarity; env prerequisites were added. |
| reuse/dedup | PASS WITH LOW RISKS | None | Confirmed reuse of existing post-submit helpers and setup boundary; low notes were folded into chunk contracts. |
| test delta | PASS WITH LOW RISKS | None | Confirmed no tests were weakened; low notes on privacy scan lint and redacted hash proof were addressed. |
| CI integrity | PASS | None | Confirmed no CI changes and CI integrity reviewer is required where tests/scripts can change. |

## Valid Findings Addressed

- Added model/migration scope for post-submit policy provenance, approval
  provenance, setup-run post-submit outputs, and lifecycle status.
- Added real setup worker/queue files to the derivation chunk.
- Corrected setup trigger boundary so post-submit derivation starts after
  setup-approved submission artifact policy approval and pre-submit compilation,
  not during initial source capture.
- Added explicit planning chunk contract.
- Replaced non-canonical `ProjectSubmissionArtifactPolicy` wording with
  `SubmissionArtifactPolicy`.
- Required default-only post-submit policy support while preserving exact
  platform default checker identity.
- Required prompt-injection tests and bounded/redacted setup summaries.
- Corrected authorization wording from project-scoped manager claims to the
  current v0.1 verified `admin` / `project_manager` setup boundary.
- Required worker/reviewer/finance/auditor denials for new setup visibility and
  approval endpoints.
- Added operator-visible internal route evidence requirements.
- Preserved checker-caused `needs_revision` provenance as
  `outcome_source = auto_checker` with no human review decision id.
- Added executable Terminal Benchmark drill prerequisites and privacy scan
  script scope.
- Required privacy scan lint/compile checks and redacted source-hash proof.
- Added CI integrity to chunks that allow tests or scripts.

## Commands Run

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
find .agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation -type f -print0 | xargs -0 -n1 sh -c 'for f do if grep -n "[[:blank:]]$" "$f"; then echo "trailing whitespace in $f"; exit 1; fi; done' sh
```

Results:

- Stale wording check: passed.
- Markdown link check: passed for 18 changed Markdown files.
- `git diff --check`: passed.
- Extra whitespace scan over new untracked WS-POL-002 files: passed.

## Residual Risks

- `WS-POL-002-04` still allows broad task/checker module globs, but its target
  behavior and acceptance criteria are narrowed to generated-policy runtime
  deltas. Senior engineering accepted this as low risk.
- Project-scoped role assignment remains future Workstream authorization work.
  WS-POL-002 must not pretend it exists.

## Stop Condition

No implementation chunk is active. `WS-POL-002-01` remains proposed and must not
start until the planning PR is reviewed, merged, and the user explicitly starts
the implementation chunk.
