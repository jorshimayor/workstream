# PR Trust Bundle: WS-POL-001-06

## Chunk

`WS-POL-001-06` - Terminal Benchmark Real Fixture Drill

## Goal

Use a real Terminal Benchmark reviewer fixture as an external-project proof for
the current Workstream setup-agent, project policy-bundle, task locked-context,
pre-submit, post-submit checker, and revision resubmission lifecycle.

## Human-Approved Intent

The user asked to prove Workstream against real Terminal Benchmark material from
the local Termius workspace without turning Workstream into Terminal Benchmark.
The proof must behave like real users using the API one endpoint at a time:
project manager setup, worker pre-submit, submission creation, lock, checker
execution, revision, and fixed resubmission.

## What Changed

- Added the `WS-POL-001-06` chunk contract and loop/status updates.
- Updated Terminal Benchmark docs/notes to record a live manual HTTP transcript.
- Kept Terminal Benchmark as example proof material only.
- Fixed the OpenAI Agents SDK adapter so the policy-derivation endpoint accepts
  Workstream's open `policy_body` output object while preserving server-side
  validation through `SubmissionArtifactPolicyInput`.
- Tightened the policy-derivation prompt to return Workstream's constrained
  project submission artifact policy shape.
- Updated adapter isolation tests for the SDK schema wrapper.
- Left the optional Terminal Benchmark Python scaffold as historical regression
  material; it is not the proof surface for this chunk.

## Why It Changed

The live manual drill exposed that the OpenAI Agents SDK adapter could run guide
sufficiency but failed policy derivation before the model call completed because
the SDK strict schema path rejected the open `policy_body` object. That made the
real setup-agent route unusable for exactly the flow this chunk was meant to
prove.

The fix keeps the trust boundary intact: the agent may return an open JSON
object, but Workstream validates and compiles only a constrained
`SubmissionArtifactPolicyInput` before activation.

## Design Chosen

Use the real product APIs over HTTP as the authoritative proof:

```text
Project
-> ProjectGuide with Termius material
-> GuideSourceSnapshot
-> ProjectGuideSufficiencyAgent
-> SubmissionArtifactPolicyDerivationAgent
-> immutable agent draft
-> admin exact policy
-> approved effective project policy
-> compiled project PreSubmitCheckerPolicy
-> task locked context
-> worker pre-submit
-> submission lock
-> durable checker run
-> review_pending / needs_revision / fixed v2 review_pending
```

The agent-derived policy remains immutable. If admin review needs exact
project-specific filenames, the manager creates a separate manual/admin policy
for approval. That matches the zero-trust setup model: agent output informs the
process but does not become trusted until Workstream validates and an authorized
operator approves the final policy.

## Alternatives Rejected

- Treat the Python example script as the proof: rejected after user pushback.
  The script is secondary regression scaffolding only.
- Mutate the agent-derived policy row: rejected by the API and by design.
- Add Terminal Benchmark-specific backend logic: rejected because this is an
  external-project proof, not product runtime.
- Weaken policy-body validation to make the SDK happy: rejected. The adapter
  schema wrapper changed, but server validation stayed strict.

## Scope Control

Allowed runtime files:

- `backend/app/adapters/project_agents/openai_agent_sdk.py`
- `backend/app/interfaces/project_agents.py`
- `backend/tests/test_projects.py`

Allowed evidence/example files:

- `.agent-loop/**`
- `examples/terminal_benchmark/**`

No changes were made to migrations, workflows, payment/reputation/blockchain,
frontend/demo runtime, or Terminal Benchmark-specific product runtime.

## Product Behavior

The live drill proved:

- pre-submit failure is `pre_submission_checker_failed`, not `needs_revision`
- blocked pre-submit and blocked submission creation create no submission rows
- post-submit checker-caused failure can move the task to `needs_revision`
- fixed v2 submission supersedes v1 and moves the task back to
  `review_pending`
- task-level `required_files` and `required_evidence` are not the intake
  authority
- tasks lock project guide/source/policy/checker context at screening
- project manager/admin approval owns exact policy acceptance after agent
  derivation

## Live API Proof

The manual HTTP transcript is recorded in
`.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-06-internal-review-evidence.md`.

Key local outcomes:

- sufficiency agent: `passed`
- sufficiency and derivation agent calls used the live product endpoints and
  persisted server-owned agent provenance
- derivation agent: immutable draft policy persisted
- admin exact policy approved and compiled
- active guide exposed compiled project pre-submit checker hash
- missing `static_guard.txt`: pre-submit failed, submission count stayed `0`,
  blocked create returned `pre_submission_checker_failed`
- complete packet: pre-submit passed, durable checker run passed `8/8`, task
  reached `review_pending`
- placeholder packet: pre-submit warning, durable checker routed
  `needs_revision`
- fixed v2: superseded v1 and returned to `review_pending`

## Tests/Checks Run So Far

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/test_agent_gates.py
cd backend && .venv/bin/python -m pytest tests/test_projects.py -k 'openai_agent_sdk_adapter'
cd backend && .venv/bin/python -m ruff check app tests scripts ../examples/terminal_benchmark
cd backend && .venv/bin/docstr-coverage app scripts --config .docstr.yaml
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@127.0.0.1:5433/workstream_test .venv/bin/python -m pytest tests
git diff --check && git diff --cached --check
```

Full final verification completed locally.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Confirmed chunk map reviewer alignment, endpoint/provenance evidence, and narrow adapter/interface/test maintainability after fixes. |
| QA/test | PASS AFTER FIXES | None | Confirmed live manual API evidence proves setup-agent route, agent draft immutability, admin exact policy, pre-submit, post-submit, and fixed v2 path. |
| security/auth | PASS WITH LOW RISKS | None | Confirmed SDK schema relaxation remains behind Pydantic/service validation and no secret/path leakage was found. |
| product/ops | PASS WITH LOW RISKS | None | Confirmed project-manager/admin/worker lifecycle, pre-submit failure boundary, durable checker `needs_revision`, and fixed v2 path. |
| architecture | PASS AFTER FIXES | None | Confirmed allowed scope and no Terminal Benchmark product-runtime leakage; earlier blocker was evidence closure only. |
| docs | PASS | None | Confirmed manual proof is authoritative, script wording is historical/regression only, and Terminal Benchmark remains example material. |
| reuse/dedup | PASS | None | Confirmed optional script diff was removed and no current-policy scaffold duplication remains after wording fixes. |
| test delta | PASS | None | Confirmed adapter regression tests cover schema wrapper and no assertions were weakened. |

## External Review

Not run yet for this branch. CodeRabbit and GitHub Actions are external checks
that should run after the PR is opened.

## Remaining Risks

- The real fixture drill is local-only and not CI-required.
- The live OpenAI agent run depends on ignored local `.env` configuration.
- The example scaffold imports backend E2E helpers; it remains example code, not
  runtime structure.

## Human Review Focus

- Confirm Terminal Benchmark remains example proof only.
- Confirm the OpenAI Agents SDK adapter fix preserves server validation.
- Confirm agent-derived policy immutability and manual admin policy adjustment
  match the intended setup lifecycle.
- Confirm pre-submit versus `needs_revision` boundary is clear.
- Confirm no local fixture path or secret is committed.

## Human Merge Ownership

Only the user can approve and merge the PR. The agent must not merge without
explicit user approval for that specific PR.
