# Terminal Benchmark Real API Drill Local Validation Notes

This file records local validation notes for the Terminal Benchmark example
drill. It is not Workstream internal-review evidence for a product chunk and
does not make this example part of required CI.

Date: 2026-06-15

Example scope:

- `examples/terminal_benchmark/terminal_benchmark_api_e2e.py`
- historical local checker revision experiment, not included in this example
- historical local checker tests, not included in this example

Purpose:

This historical note covered the earlier Terminal Benchmark API drill shape:

- project and active guide creation
- task screening, release, claim, and start
- pre-submit checker feedback for intake
- submission packet creation
- submission lock
- automatic durable checker gate
- `review_pending`
- `needs_revision`
- fixed resubmission from revision state

## Local Observations

Engineering observations:

- The default fixture path was private/local, and ambiguous fixture file
  selection could hide mixed artifacts.
- The pre-submit checker set and persisted fixture artifact/evidence contract
  were under-asserted.
- The example now requires an explicit `WORKSTREAM_TERMINAL_BENCH_FIXTURE`,
  fails on ambiguous fixture matches, and asserts pre-submit checker set,
  artifact manifest, evidence rows, hashes, sizes, labels, checker statuses,
  and checker counts.

QA observations:

- Successful pre-submit non-durability and exact checker result counts were not
  proven in the first local draft.
- The fixed revision packet skipped pre-submit feedback in the first local draft.
- The example asserts no durable submissions are created by pre-submit checks,
  exact run counters and statuses match expectations, and the fixed revision
  packet runs pre-submit feedback before v2 submission.

Security observations:

- An inherited non-local database override could allow writes outside local test
  Postgres.
- Fixture paths could leak through persisted identifiers or normal success
  output.
- The example uses a strict local-only Postgres guard, derives a stable fixture
  id from content hashes, persists sanitized fixture identifiers, and normal
  success output does not print the absolute fixture path.

Product/ops observations:

- Demo worker profile bootstrap could be confused with canonical workflow.
- Locked wording used time-relative and external-tool-specific phrasing.
- Demo bootstrap is explicitly labeled as non-canonical v0.1 setup, output
  includes `worker_profile_setup=demo_bootstrap_not_canonical_workflow`, and
  guide/submission wording uses stable Terminal Benchmark fixture language.

## Validations

Commands run:

```bash
cd backend && .venv/bin/python -m ruff check app tests scripts
cd backend && .venv/bin/docstr-coverage app scripts --config .docstr.yaml
git diff --check
cd backend && .venv/bin/python -m pytest tests/test_checkers.py -k 'pre_submit_check_allows_worker_revision_packet_feedback or pre_submit_check_returns_feedback_without_durable_run'
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test WORKSTREAM_TERMINAL_BENCH_FIXTURE=/path/to/terminal-benchmark-source-material .venv/bin/python ../examples/terminal_benchmark/terminal_benchmark_api_e2e.py
cd backend && .venv/bin/python -m pytest
```

Results:

- ruff passed
- docstring coverage passed at 100.0%
- diff whitespace check passed
- targeted checker tests passed: 2 passed
- Terminal Benchmark real API drill passed
- full backend pytest passed: 115 passed

These notes are historical local validation notes only. They do not certify any
future chunk and do not replace required internal reviewer evidence.

## Manual Policy-Bundle Proof Note

Date: 2026-07-05

Purpose:

Record that a real Terminal Benchmark reviewer fixture was used in formal
`.agent-loop` evidence to prove the current Workstream policy-bundle path:

- project guide creation
- immutable guide-source snapshot from real Termius guide, reviewer, task, and
  review packet material
- guide sufficiency report
- project `SubmissionArtifactPolicy`
- effective project submission artifact policy
- compiled project `PreSubmitCheckerPolicy`
- two tasks locking the same project policy context
- activation of a newer guide version with a distinct project
  `PreSubmitCheckerPolicy`
- proof that an already-started task still uses its locked v1 checker bundle
- pre-submit blocking before submission creation
- post-submit checker-caused `needs_revision`
- fixed v2 resubmission reaching `review_pending`

Commands run:

```bash
python3 scripts/check_stale_workstream_wording.py
cd backend && .venv/bin/python -m ruff check app tests scripts ../examples/terminal_benchmark
cd backend && .venv/bin/docstr-coverage app scripts --config .docstr.yaml
git diff --check
python3 scripts/check_markdown_links.py
```

Results:

- stale wording check passed
- ruff passed
- docstring coverage passed at 100.0%
- diff whitespace check passed
- Markdown link check passed for changed Markdown files
- Terminal Benchmark manual API drill passed against the selected local
  source-material directory
- clean packet reached `review_pending`
- missing static guard was blocked at pre-submit and created no submission
- blocked pre-submit and blocked submission-create produced no durable
  submission, evidence, checker-run, checker-result, or audit side effects
- after a v2 guide and project checker became active, the already-started task
  still used its locked v1 checker bundle
- checker-caused v1 reached `needs_revision`
- fixed v2 superseded v1 and reached `review_pending`

This section is only a local pointer to the formal proof. Formal zero-trust
chunk evidence lives under `.agent-loop/`.

## Manual Live API Drill Update

Date: 2026-07-05

The current proof was rerun manually over HTTP against a live local uvicorn
server and local Postgres. The Python example scaffold was not used as the
authoritative proof for this pass.

Live API sequence:

- health check returned `ok`
- project manager created project
- project manager created a project guide with full Termius submission program,
  reviewer project guide, reviewer program, task TOML, and review packet content
- project manager created an immutable guide-source snapshot with source hashes
  and sanitized durable refs
- `ProjectGuideSufficiencyAgent` endpoint returned `passed`
- `SubmissionArtifactPolicyDerivationAgent` endpoint returned an immutable
  agent-derived draft policy
- project manager created a separate admin-reviewed exact Terminal Benchmark
  policy because the agent draft used generalized workspace paths
- policy approval produced an approved effective project submission artifact
  policy and compiled project `PreSubmitCheckerPolicy`
- guide activation returned the complete active guide-policy bundle
- task screening locked guide version `v1`, the guide-source snapshot hash, the
  effective project submission artifact policy hash, and the project
  pre-submit checker bundle hash
- incomplete packet missing `static_guard.txt` failed pre-submit and blocked
  submission creation with `pre_submission_checker_failed`
- blocked pre-submit and blocked create left submission count at `0`
- complete packet passed pre-submit, created a submission, locked policy context,
  ran the durable checker gate, and moved the task to `review_pending`
- placeholder summary passed pre-submit with a warning, failed the durable
  post-submit checker, and moved the revision-path task to `needs_revision`
- fixed v2 submission superseded v1 and moved the task back to `review_pending`

Live IDs from the local test database:

- project: `6e87e2c2-91a1-4140-8f66-6d0c5bd4b966`
- guide: `b2857abb-6bb0-4e27-89e8-bfb3bfedb8f2`
- guide-source snapshot: `185e80bb-5676-4370-a09f-1c51853bd400`
- sufficiency report: `8368e1c5-cbd6-4503-94f8-74e647a15550`
- agent-derived policy draft: `2838434c-7695-4037-a6d4-531f860a07a6`
- admin exact policy: `dc2e054b-5ce1-49fe-8388-49eb0ec7f992`
- effective project submission artifact policy hash:
  `sha256:38213716e58f10f0916029f91a882681dc52136c9460a958bb4780b070da82f8`
- compiled pre-submit checker hash:
  `sha256:1dc2e4b8e9a509e26f6fff8a6da68fbc7340654ecc135d025351173501265855`
- clean task: `9fd7be8f-5886-403b-8ce7-faba37705e72`
- clean submission: `ad0d08f9-4b91-4363-85e9-d8a7b6e055a8`
- clean checker run: `4e72cf39-3348-48b1-8d1a-b3ae17433c65`
- revision-path task: `3ae5db8a-eb40-49bb-8a2a-87ccb1f6594f`
- revision v1 submission: `77a5614b-d0cd-4875-abe2-6e4a83d213cb`
- revision v1 checker run: `b4c9fb23-bf83-48f2-a9ca-5e145aaa707d`
- fixed v2 submission: `a233eefd-598e-4c1b-89c5-c1a93b077682`

Runtime issue found and fixed:

- The OpenAI Agents SDK adapter initially rejected the derivation output schema
  because `policy_body` is intentionally an open JSON object and the SDK strict
  schema path does not accept that shape.
- The adapter now wraps output types with `AgentOutputSchema(...,
  strict_json_schema=False)`, while Workstream still validates the returned
  `policy_body` through `SubmissionArtifactPolicyInput` before persistence.
- The derivation prompt now names the exact constrained policy-body shape so
  the agent returns a compiler-ready specification instead of a broad policy
  memo.
