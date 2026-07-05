# Chunk Contract: WS-POL-001-06 - Terminal Benchmark Real Fixture Drill

## Initiative

WS-POL-001 - Submission Artifact Policy Foundation

## Goal

Use a real Terminal Benchmark reviewer fixture from the local Termius workspace
to prove the current Workstream project guide, setup-agent, policy bundle, task
locked context, pre-submit feedback, submission versioning, post-submit checker
gate, and revision resubmission path over live HTTP calls and local Postgres.

This chunk is proof and runtime-unblock work. It must not make Terminal
Benchmark a Workstream product dependency and must not add
Terminal Benchmark-specific logic to Workstream runtime modules.

## Risk

L1

The chunk touches real API proof code, the OpenAI Agents SDK adapter boundary,
and local evidence for the policy and checker lifecycle. It also handles
private local fixture paths and a local OpenAI API key environment, so secret
handling and path redaction matter.

## Depends On

`WS-POL-001-05` merged to `main`.

## Allowed Files

```text
examples/terminal_benchmark/**
backend/app/adapters/project_agents/openai_agent_sdk.py
backend/app/interfaces/project_agents.py
backend/tests/test_projects.py
.agent-loop/LOOP_STATE.md
.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/**
```

## Not Allowed

```text
backend/app/** except:
  backend/app/adapters/project_agents/openai_agent_sdk.py
  backend/app/interfaces/project_agents.py
backend/alembic/**
backend/tests/** except:
  backend/tests/test_projects.py
backend/scripts/**
.github/workflows/**
demos/**
frontend/**
payment/reputation/blockchain code
production secrets or committed .env files
Terminal Benchmark-specific product runtime code
```

If the drill exposes any additional runtime bug outside the listed adapter
boundary, stop and create a separate implementation chunk instead of widening
this proof harness again.

## Acceptance Criteria

- The Terminal Benchmark drill uses the current project policy-bundle path:
  guide source snapshot, guide sufficiency report, project
  `SubmissionArtifactPolicy`, effective project submission artifact policy, and
  compiled project `PreSubmitCheckerPolicy`.
- The guide sufficiency and submission artifact policy derivation endpoints run
  through the configured OpenAI Agents SDK adapter during the live manual drill.
- The OpenAI Agents SDK adapter accepts Workstream's intentionally open
  `policy_body` object without weakening server-side validation of the returned
  `SubmissionArtifactPolicyInput`.
- The agent-derived policy row remains immutable; if admin review needs exact
  project-specific filenames, the manager creates a separate manual/admin
  policy before approval.
- The drill does not rely on `ProjectGuide.evidence_policy` as the intake
  contract.
- The drill does not rely on task `required_files` or `required_evidence` as the
  source of pre-submit truth.
- The guide source snapshot is built from real Termius material, including the
  Terminal Benchmark submission guide/program material, reviewer program or
  guide material, the selected task TOML, and the selected review packet.
- Persisted fixture identifiers and normal success output do not reveal absolute
  local paths or secrets.
- The project submission artifact policy is Terminal Benchmark-shaped but
  project-scoped, compiled once, and reused by all tasks in the drill.
- Two tasks under the same project lock the same guide source snapshot hash,
  effective project submission artifact policy hash, and project pre-submit
  checker bundle hash.
- Pre-submit feedback runs against the task's locked project
  `PreSubmitCheckerPolicy` and creates no durable submission or checker rows.
- A blocking pre-submit failure returns worker-facing pre-submit failure details
  and creates no submission version.
- A deliberately incomplete v1 submission can still be forced through the API
  path only where the current v0.1 drill intentionally proves post-submit
  checker-caused `needs_revision`.
- A fixed v2 submission supersedes v1, keeps v1 immutable, and reaches
  `review_pending`.
- Database invariants prove submission, evidence, checker-run, audit, route,
  locked-context, and versioning state for the clean, failed, and fixed paths.
- The README explains that this is an external-project proof harness, not
  formal runtime code or CI-required evidence.

## Verification Commands

```bash
git diff --check
python3 scripts/check_stale_workstream_wording.py
cd backend && .venv/bin/python -m ruff check app tests scripts ../examples/terminal_benchmark
cd backend && .venv/bin/docstr-coverage app scripts --config .docstr.yaml
cd backend && .venv/bin/python -m pytest tests/test_projects.py -k 'openai_agent_sdk_adapter'
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test WORKSTREAM_TERMINAL_BENCH_FIXTURE=/path/to/local/terminal-benchmark-fixture .venv/bin/python ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
```

The fixture path may be changed to another local Termius reviewer fixture that
contains the required files. The command must stay local-only and must never run
against production or shared databases.

The required proof is the live manual HTTP drill. The example command above is
secondary regression coverage only and does not replace the manual transcript
recorded in internal evidence.

## Required Internal Reviewers

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- reuse/dedup
- test delta

## Human Review Focus

- The example remains proof harness code and does not leak into product runtime.
- The drill uses current policy-bundle APIs instead of legacy guide/task intake
  fields.
- The real fixture path and OpenAI key stay local and uncommitted.
- The Terminal Benchmark terms are examples of an external project shape, not
  Workstream product terminology.
