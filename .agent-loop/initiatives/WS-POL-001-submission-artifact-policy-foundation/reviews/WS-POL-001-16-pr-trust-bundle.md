# PR Trust Bundle: WS-POL-001-16

## Intent

Prove the current Workstream project setup and submission intake lifecycle with a real Terminal Benchmark live API drill, using HTTP-visible evidence instead of database inspection.

This chunk exists because earlier Terminal Benchmark drills exposed real gaps in project setup visibility, worker requirements, finalization, and agent-derived submission policy quality. This pass proves the corrected flow slowly and visibly.

## Scope

Changed:

- `.agent-loop/LOOP_STATE.md`
- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/STATUS.md`
- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/chunks/WS-POL-001-16-terminal-benchmark-live-api-drill.md`
- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-16-live-api-drill-evidence.md`
- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-16-internal-review-evidence.md`
- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-16-pr-trust-bundle.md`
- `docs/roadmap_status.md`

Not changed:

- No backend code.
- No migrations.
- No tests or scripts.
- No CI/workflow files.
- No frontend/demo work.
- No auth, payment, reputation, settlement, or blockchain behavior.
- No task-specific checker generation.

## Design

The drill evidence follows the real Workstream chain:

```text
ProjectGuide
-> GuideSourceSnapshot
-> GuideSufficiencyReport
-> ProjectSubmissionArtifactPolicy
-> EffectiveProjectSubmissionArtifactPolicy
-> project PreSubmitCheckerPolicy
-> task locked context
-> worker pre-submit
-> submission finalization
-> durable checker run
-> review_pending
```

The evidence records:

- sanitized Terminal Benchmark source material and source snapshot hashes;
- automatic Celery setup status from queued through `policy_draft_ready`;
- sufficiency-agent and submission-policy-derivation inputs and outputs;
- policy approval, effective policy, checker policy, and guide activation;
- task creation, screening, release, worker profile activation, claim, and start;
- worker work-context and submission-requirements reads;
- blocked pre-submit and blocked create with no submission side effect;
- successful pre-submit, durable submission creation, manager finalization, checker-run list/get, audit events, and final `review_pending` task response.

The checker-run no-side-effect proof is aligned with the existing API design: checker-run list/get is submission-scoped, so blocked intake before a submission id is proved with task submissions plus audit events; checker-run visibility is proven after a submission exists and finalization starts the pre-review gate.

## Verification

Passed:

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
cd backend && .venv/bin/pytest tests/test_projects.py tests/test_tasks.py tests/test_checkers.py -q
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/api_contract_e2e.py
git diff --cached --check
```

Key results:

- `342 passed in 4305.43s (1:11:45)` for focused backend tests.
- `API contract real API e2e passed`.
- Stale wording check passed.
- Markdown link check passed for 6 changed Markdown files.
- Diff whitespace check passed.

## Live Drill Result

Final clean run:

```text
project_id: 36331e8e-c849-484d-9e9e-c8ebc2f70130
guide_id: fbe0b2ab-2793-4619-a414-ed083d9cc117
source_snapshot_id: 2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b
source_snapshot_hash: sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb
submission_artifact_policy_hash: sha256:aa0cf8add77b6d193e5f3ffa1bf22f0fd21f27e484e4aa027e693d77b3624136
effective_policy_hash: sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850
pre_submit_checker_bundle_hash: sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63
task_id: d8cfda33-6c7e-461a-bdcd-036a6cefeda3
submission_id: ba25f15a-e36a-4925-9891-09d394eae2ec
checker_run_id: d7885348-fd08-4820-b209-36a704765a2b
final_task_status: review_pending
```

Evidence:

- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-16-live-api-drill-evidence.md`

## Internal Review

| Reviewer | Result |
|---|---:|
| senior engineering | PASS WITH LOW RISKS |
| QA/test | PASS AFTER FIXES |
| security/auth | PASS AFTER FIXES |
| product/ops | PASS AFTER FIXES |
| architecture | PASS AFTER FIXES |
| docs | PASS AFTER FIXES |
| reuse/dedup | PASS |
| test delta | PASS |

Evidence:

- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-16-internal-review-evidence.md`

## Human Review Focus

- Confirm the live drill is understandable from HTTP-visible evidence without DB inspection.
- Confirm the Terminal Benchmark source material is treated as fixture/example evidence, not a Workstream product fork.
- Confirm the setup agent inputs/outputs, derived policy, effective policy, and compiled project checker remain project-scoped.
- Confirm blocked pre-submit creates no submission and does not rely on product review decisions.
- Confirm submission finalization, checker-run visibility, audit events, and final `review_pending` state match the intended lifecycle.

## Remaining Risks

- The evidence appendix is large because it records all redacted HTTP bodies required by the chunk contract.
- This chunk does not implement review packet assignment, human review decisions, or revision replay APIs; those remain future chunks.
