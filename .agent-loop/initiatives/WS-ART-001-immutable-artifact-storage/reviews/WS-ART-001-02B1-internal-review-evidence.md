# Internal Review Evidence: WS-ART-001-02B1

## Chunk

`WS-ART-001-02B1`: S3-Compatible MinIO And AWS

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: `9cd41ab907aba323f1fbd79dac8bbe1602bcc30f`

Reviewed at: 2026-07-18T19:49:08Z

Reviewer run IDs: senior-engineering=019f7698-ca9c-75a0-9ad9-5ddb553144ee; architecture=019f7698-d670-7b02-9336-93111bfb0905; QA/test=019f7698-ea1c-7632-8c76-3b2bddc1a709; security/auth=019f76b8-a76d-7060-95a2-e3296813464e; product/ops=019f76b8-acef-7cc1-a7ba-24f9262521de; reuse/dedup=019f76b8-b3b7-7961-85d9-5dfd9cddaaec; CI-integrity=019f76be-436c-7473-92da-50ee58380fd4; test-delta=019f76be-4869-7350-a737-fa75a6123fd0; docs=019f76be-52ed-7cf1-b589-aa9dc1ddd1bb

The reviewed base is `origin/main` at
`99ae4c963e53f317175dcb308b9e47c93ccf19ed`, including AUTH PR #148.
Only review artifacts and initiative status may change after the reviewed SHA.
Any implementation, test, workflow, policy, or chunk-contract change invalidates
this evidence and requires a new exact-head review cycle.

## Reviewed Change

- Added one S3-protocol ArtifactStore implementation shared by MinIO and the
  inactive native AWS profile.
- Proved the active local/CI path against real digest-pinned MinIO with the same
  ArtifactStore v2 contract used by LocalStorage.
- Kept native AWS runtime-ineligible until Chunk 07 supplies an immutable live
  activation proof.
- Isolated each AWS workload-identity method from ambient credential, proxy,
  file, process, cache, and unselected metadata sources.
- Preserved server-derived content keys, sealed source validation, exact replay,
  bounded object size, no multipart/list/delete/copy surface, and sanitized
  provider failures.
- Added canonical global general-purpose bucket, region, prefix, and MinIO
  endpoint validation, including rejection of secret-bearing endpoint input.
- Retained the full repository 78 percent CI floor and every cumulative focused
  90 percent gate while adding exact S3 adapter and validation gates.
- Integrated AUTH PR #148 without editing or activating AUTH-owned runtime
  behavior.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | The shared adapter remains maintainable, AWS remains unavailable before live proof, and no operational issue remains. |
| qa/test | PASS | None | Real MinIO, credential isolation, namespace fencing, configuration, and CI evidence cover the chunk contract without weakened tests. |
| security/auth | PASS | None | Secret-bearing endpoint and metadata failures are sanitized, credential sources are closed, and ART/AUTH ownership remains intact. |
| product/ops | PASS | None | No operator recovery, contributor, reviewer, contribution, compensation, fulfillment, or reputation behavior is activated. |
| architecture | PASS | None | One typed adapter path remains, concrete S3 construction stays in ART composition, and product services receive no concrete store. |
| ci integrity | PASS | None | The 78 percent repository gate and all cumulative 90 percent gates remain fail closed with no bypass. |
| docs | PASS | None | README, artifact specification, settings, provider eligibility, and loop state match the implementation. |
| reuse/dedup | PASS | None | Provider references, S3 validation, runtime guards, and deep secret assertions reuse canonical helpers without parallel implementations. |
| test delta | PASS | None | Removed placeholder assertions were replaced by stronger active-MinIO and inactive-AWS behavior proof; no test was skipped or weakened. |

## Valid Findings Addressed

- Replaced permissive S3 region validation with a bounded canonical region
  grammar and complete positive/negative tests.
- Made invalid MinIO endpoint errors discard userinfo, malformed ports, and raw
  source values across constructor, Pydantic mapping/JSON/string validation,
  environment, dotenv, traceback, and structured error paths.
- Documented the intentional v0.1 global general-purpose bucket boundary and
  rejection of account-regional `-an` names because Workstream does not emit
  the account-regional namespace header.
- Rejected every AWS reserved general-purpose bucket prefix and suffix and
  validated every dotted bucket label.
- Sanitized ECS and IMDS credential failure paths so SDK exceptions cannot
  retain response bodies, authorization tokens, endpoints, or credentials.
- Bound replay to the sealed committed source before any provider operation and
  removed stale provider-reference divergence.
- Reconciled authored ART loop state and work queue with AUTH PR #148 while
  keeping AUTH-09D-B and every later ART chunk inactive.

## Commands Run

```bash
docker compose up -d --wait postgres redis minio
cd backend && .venv/bin/ruff check app tests
cd backend && .venv/bin/pip check
cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python -m pytest tests/test_artifact_architecture.py tests/test_artifact_cleanup_wiring.py tests/test_artifact_preparation.py tests/test_artifact_store_conformance.py tests/test_local_artifact_store.py tests/test_s3_artifact_store.py tests/test_aws_credential_isolation.py tests/test_config.py tests/test_assertion_helpers.py tests/test_audit.py -q --cov=app.adapters.artifacts --cov=app.interfaces.artifact_operations --cov=app.interfaces.artifacts --cov=app.core.config --cov=app.core.s3_validation --cov-report=term-missing --cov-fail-under=90
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_review_contracts.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/test_agent_gates.py
git diff --check
```

Results: 428 real-service focused tests passed after AUTH PR #148 integration.
`S3CompatibleArtifactStore` coverage is 92 percent, S3 validation coverage is
100 percent, and combined changed-subsystem coverage is 92.95 percent. Ruff,
dependency integrity, stale contract/authorization/review/wording scans,
Markdown links, 87 agent-gate tests, and diff checks passed.

The isolated full repository suite and 78 percent whole-app floor remain
authoritative in GitHub Backend CI, as explicitly chosen because local execution
is prohibitively slow. The CI reviewer confirmed that exact gate is retained.

## Remaining Risks

- Native AWS operations remain deliberately unavailable until Chunk 07 adds the
  release-bound live proof and production composition guard.
- MinIO is a local/CI protocol proof, not production activation evidence.
- Provider acknowledgement remains non-bindable pending later admission,
  verification, publication, and recovery chunks.

## Stop Condition

Publish this evidence-bound candidate for GitHub CI, CodeRabbit, and explicit
human review. Do not merge without the user's approval and do not start
`WS-ART-001-02C1` automatically.
