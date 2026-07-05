# Terminal Benchmark Example

This directory contains Terminal Benchmark example material used to validate
Workstream behavior against a realistic external-project packet shape.

It is not Workstream product runtime code, not a required CI test, not formal
internal review evidence, and not a canonical checker implementation.

Do not cite files in this directory as proof that a Workstream implementation
chunk passed the zero-trust loop. Formal chunk evidence must live under the
approved `.agent-loop` or `docs/internal_reviews` paths for that chunk.

## Contents

- `terminal_benchmark_api_e2e.py`: manual real-API drill that exercises the
  current setup-agent policy-bundle route with a local Terminal Benchmark
  fixture and the OpenAI Agents SDK adapter.
- `LOCAL_VALIDATION_NOTES.md`: notes from the earlier local validation of the drill.

## Requirements

- Local Postgres test database only.
- `OPENAI_API_KEY`.
- `WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL`.
- `WORKSTREAM_TERMINAL_BENCH_FIXTURE` pointing at one local Terminal Benchmark
  fixture directory.
- `WORKSTREAM_TERMIUS_REVIEWER_ROOT` when the fixture directory is not under a
  Termius reviewer root containing `PROJECT_GUIDE.md` and
  `REVIEWER_PROGRAM.md`.
- Backend dependencies installed.

The script fails closed unless `WORKSTREAM_DATABASE_URL` points to local async
Postgres using `workstream_test` or `test_workstream`.

The fixture path should point at a local Termius reviewer directory containing
`extracted/task.toml`, one `*_submission_*.zip`, one `review_packet_*.md`,
`static_guard.txt`, `docker_build.log`, `oracle_test.log`, and
`starter_m1_test.log`. Keep the concrete local path in your shell environment;
do not commit operator-specific fixture paths.

The script forces `WORKSTREAM_PROJECT_AGENT_RUNTIME_ADAPTER=openai_agent_sdk`
before starting the API server. It does not fall back to the deterministic local
fixture adapter.

## Manual Proof Shape

The authoritative proof for `WS-POL-001-06` was a live manual HTTP drill:

1. create a project;
2. create a project guide containing Termius submission, reviewer, task, and
   review packet material;
3. create a guide-source snapshot with source hashes and excerpts;
4. run the guide sufficiency agent endpoint;
5. run the submission artifact policy derivation agent endpoint;
6. create an admin-reviewed exact project submission artifact policy;
7. approve the policy and activate the guide;
8. create, screen, release, claim, and start a task;
9. run pre-submit checks, blocked submission creation, successful submission
   creation, submission lock, durable checker run, and revision resubmission
   through the HTTP APIs.

## Manual Drill Command

```bash
cd backend
WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test \
OPENAI_API_KEY="$OPENAI_API_KEY" \
WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL="${WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL:?set model}" \
WORKSTREAM_TERMINAL_BENCH_FIXTURE=/path/to/terminal-benchmark-fixture \
WORKSTREAM_TERMIUS_REVIEWER_ROOT=/path/to/termius_reviewer \
.venv/bin/python ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
```
