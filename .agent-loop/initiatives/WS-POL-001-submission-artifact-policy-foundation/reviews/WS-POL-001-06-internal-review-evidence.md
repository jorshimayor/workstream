# Internal Review Evidence: WS-POL-001-06

## Chunk

WS-POL-001-06

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: pending-final-commit-sha

Reviewed at: pending-final-review-timestamp

Reviewer run IDs: 019f3010-b6a4-7cf0-9408-f5dff13b6eaf, 019f3017-56f2-7040-95fb-51d26577d818, 019f3010-fd7f-7261-9990-dcc50edbd542, 019f3017-7612-7582-974d-a5765b07c983, 019f3011-3f7c-73b3-9044-75aa70d29b4c, 019f3017-9d0a-7e02-bca4-221ed52463ba, 019f3017-c65d-7802-a56f-f98b480d3a25, 019f301c-22ff-75d3-b0b8-4c3192e69b51, 019f3017-f130-7613-be94-128ac8c8f1ec

## Reviewed Change

Branch: `codex/ws-pol-001-06-terminal-benchmark-drill`

Scope:

- `.agent-loop/LOOP_STATE.md`
- `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/**`
- `backend/app/adapters/project_agents/openai_agent_sdk.py`
- `backend/app/interfaces/project_agents.py`
- `backend/tests/test_projects.py`
- `examples/terminal_benchmark/**`

This chunk proves Workstream against real Terminal Benchmark material without
making Terminal Benchmark a Workstream product dependency.

## Live Manual API Evidence

The authoritative proof was a manual HTTP drill against a live local uvicorn
server and local Postgres. The existing Python example scaffold is historical
regression material only and was not used as the proof for this chunk.

Live setup:

- API: `http://127.0.0.1:8117`
- database: local `workstream_test`
- auth: local Flow-compatible HMAC tokens through the normal bearer-token auth
  dependency
- project agent runtime: `openai_agent_sdk`
- fixture: local Terminal Benchmark reviewer fixture; committed evidence uses
  the fixture label only, not the private absolute path

Agent runtime configuration used during the drill:

```text
WORKSTREAM_AUTH_PROVIDER=flow
WORKSTREAM_PROJECT_AGENT_RUNTIME_ADAPTER=openai_agent_sdk
WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MODEL=<local non-secret model name>
WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_TIMEOUT_SECONDS=<local timeout>
WORKSTREAM_PROJECT_AGENT_OPENAI_AGENT_SDK_MAX_PROMPT_BYTES=<local prompt budget>
```

The OpenAI API key was loaded from ignored local `.env` files and was not
printed, stored in API responses, or committed.

Live API sequence:

1. `GET /api/v1/health` returned `{"status":"ok"}`.
2. Project manager created project
   `6e87e2c2-91a1-4140-8f66-6d0c5bd4b966`.
3. Project manager created guide
   `b2857abb-6bb0-4e27-89e8-bfb3bfedb8f2` with full Termius submission
   program, reviewer project guide, reviewer program, selected task TOML, and
   review packet content.
4. Project manager created guide-source snapshot
   `185e80bb-5676-4370-a09f-1c51853bd400` with bundle hash
   `sha256:2a4db4dc9d80c8843d3f9924b99e94313cbe309b2995ae16dc645ed4e42ed549`.
5. `ProjectGuideSufficiencyAgent` endpoint returned `passed` with report
   `8368e1c5-cbd6-4503-94f8-74e647a15550`.
6. `SubmissionArtifactPolicyDerivationAgent` endpoint returned immutable
   agent-derived draft policy `2838434c-7695-4037-a6d4-531f860a07a6`.
7. Agent-derived policy mutation was rejected with
   `agent-derived policy bodies are immutable; create a manual policy to adjust`.
8. Project manager created exact admin policy
   `dc2e054b-5ce1-49fe-8388-49eb0ec7f992` after reviewing the agent draft.
9. Policy approval produced effective policy
   `ebea6a94-12ec-4d98-adc4-706eb06e9791` with hash
   `sha256:38213716e58f10f0916029f91a882681dc52136c9460a958bb4780b070da82f8`.
10. Guide activation returned compiled project pre-submit checker
    `9ba68c67-4cc1-4e62-a625-bb9db3fa2d5a` with bundle hash
    `sha256:1dc2e4b8e9a509e26f6fff8a6da68fbc7340654ecc135d025351173501265855`.
11. Task `9fd7be8f-5886-403b-8ce7-faba37705e72` was created, screened,
    released, claimed, and started. Screening locked guide version `v1`, the
    guide-source snapshot hash, the effective project submission artifact
    policy hash, and the project pre-submit checker hash. Task `required_files` and
    `required_evidence` remained empty.
12. Worker pre-submit with missing `static_guard.txt` returned
    `status=failed`, `eligible_to_submit=false`; failed checkers included
    `check_required_files` and `check_evidence_present`.
13. Direct submission creation with the same bad packet returned
    `code=pre_submission_checker_failed`; submission count stayed `0`.
14. Complete packet passed pre-submit with all seven pre-submit checks passing.
15. Submission `ad0d08f9-4b91-4363-85e9-d8a7b6e055a8` was created and locked
    with the same locked policy context.
16. Durable checker run `4e72cf39-3348-48b1-8d1a-b3ae17433c65` completed with
    `routing_recommendation=allow_review`, `passed_count=8`, `failed_count=0`,
    and task status `review_pending`.
17. Revision-path task `3ae5db8a-eb40-49bb-8a2a-87ccb1f6594f` was created,
    screened, released, claimed, and started with the same project policy
    context.
18. Placeholder summary passed pre-submit with a
    `check_low_quality_generated_artifacts` warning, then durable checker run
    `b4c9fb23-bf83-48f2-a9ca-5e145aaa707d` routed to `needs_revision` with
    `outcome_source=auto_checker`.
19. Fixed submission `a233eefd-598e-4c1b-89c5-c1a93b077682` became version `2`,
    superseded v1 `77a5614b-d0cd-4875-abe2-6e4a83d213cb`, passed all eight
    durable checkers, and moved the task back to `review_pending`.

### Agent Endpoint Proof

The live guide sufficiency call used the product route:

```text
POST /api/v1/projects/6e87e2c2-91a1-4140-8f66-6d0c5bd4b966/guides/b2857abb-6bb0-4e27-89e8-bfb3bfedb8f2/source-snapshots/185e80bb-5676-4370-a09f-1c51853bd400/run-sufficiency-agent
```

The redacted response was verified with these persisted fields:

```json
{
  "id": "8368e1c5-cbd6-4503-94f8-74e647a15550",
  "source_snapshot_id": "185e80bb-5676-4370-a09f-1c51853bd400",
  "source_snapshot_hash": "sha256:2a4db4dc9d80c8843d3f9924b99e94313cbe309b2995ae16dc645ed4e42ed549",
  "status": "passed",
  "agent_name": "ProjectGuideSufficiencyAgent",
  "agent_version": "workstream-sufficiency-agent-v0.1"
}
```

The live submission artifact policy derivation call used the product route:

```text
POST /api/v1/projects/6e87e2c2-91a1-4140-8f66-6d0c5bd4b966/guides/b2857abb-6bb0-4e27-89e8-bfb3bfedb8f2/source-snapshots/185e80bb-5676-4370-a09f-1c51853bd400/derive-submission-artifact-policy
```

The redacted response was verified with these persisted fields:

```json
{
  "id": "2838434c-7695-4037-a6d4-531f860a07a6",
  "policy_version": "agent-2a4db4dc9d80c8843d3f9924",
  "status": "draft",
  "source_snapshot_id": "185e80bb-5676-4370-a09f-1c51853bd400",
  "source_snapshot_hash": "sha256:2a4db4dc9d80c8843d3f9924b99e94313cbe309b2995ae16dc645ed4e42ed549",
  "derivation_source": "agent_derivation",
  "derivation_agent_name": "SubmissionArtifactPolicyDerivationAgent",
  "derivation_agent_version": "workstream-policy-derivation-agent-v0.1"
}
```

The same drill then attempted to edit the agent-derived policy row through:

```text
PATCH /api/v1/projects/6e87e2c2-91a1-4140-8f66-6d0c5bd4b966/guides/b2857abb-6bb0-4e27-89e8-bfb3bfedb8f2/submission-artifact-policies/2838434c-7695-4037-a6d4-531f860a07a6
```

The API rejected the mutation with
`agent-derived policy bodies are immutable; create a manual policy to adjust`.
The project manager then created a separate exact policy row:

```json
{
  "id": "dc2e054b-5ce1-49fe-8388-49eb0ec7f992",
  "policy_version": "v1-admin-terminal-benchmark",
  "status": "draft",
  "source_snapshot_id": "185e80bb-5676-4370-a09f-1c51853bd400",
  "source_snapshot_hash": "sha256:2a4db4dc9d80c8843d3f9924b99e94313cbe309b2995ae16dc645ed4e42ed549",
  "derivation_source": "manual_admin_derivation"
}
```

This proves the setup path used the live setup-agent routes, persisted
server-owned agent provenance, rejected mutation of the agent draft, and moved
approval to a separate project-manager/admin-reviewed policy record.

## Runtime Bug Found And Fixed

The live drill exposed a real OpenAI Agents SDK adapter bug:

- `SubmissionArtifactPolicyDerivationResult.policy_body` is intentionally an
  open JSON object because Workstream validates it after the agent returns.
- The OpenAI Agents SDK strict schema path rejected that open object before the
  call could complete.
- The adapter now wraps output types with
  `AgentOutputSchema(..., strict_json_schema=False)`.
- Server-side validation is still strict: returned policy bodies must validate
  as `SubmissionArtifactPolicyInput` before they can persist.
- The derivation prompt now states the exact constrained policy-body shape so
  the agent produces a compiler-ready specification, not a broad policy memo.

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

## Valid Findings Addressed

- Replaced committed absolute fixture paths with placeholders.
- Removed brittle Markdown link count from validation notes.
- Ran the live manual HTTP flow requested by the user instead of treating a
  Python E2E script as the proof.
- Installed and exercised the OpenAI Agents SDK local optional dependency in the
  backend venv for the live drill.
- Fixed the OpenAI Agents SDK adapter so the derivation endpoint can return
  Workstream's open policy-body contract while preserving server validation.
- Verified the agent-derived policy row remains immutable and admin adjustment
  creates a separate manual policy.
- Restored the optional Python example scaffold to the main-branch version so
  it cannot be mistaken for proof of the setup-agent/admin exact-policy route.
- Added `reuse/dedup` to the WS-POL-001-06 chunk map reviewer list.
- Reworded Terminal Benchmark example docs so the old Python scaffold is
  historical regression material only, not the current setup-agent proof.
- Added endpoint-level and persisted-provenance evidence for the live guide
  sufficiency and policy-derivation agent calls.

## Commands Run

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

Full final verification completed locally before reviewer re-check, and
reviewer sessions were closed before this evidence was finalized.

## Remaining Risks

- The real Terminal Benchmark fixture is local/private and not available to CI.
- The live OpenAI Agents SDK call depends on a local API key in ignored `.env`
  files; no secret is committed.
- `examples/terminal_benchmark/terminal_benchmark_api_e2e.py` remains an
  example scaffold, not product runtime or formal CI evidence.
