# Internal Review Evidence: WS-ART-001-02A2

## Chunk

`WS-ART-001-02A2`: Committed Source And Local Preparation

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 967e12cb5d11b895b59be206fee36af911576d66

Reviewed at: 2026-07-16T00:27:35Z

Reviewer run IDs: senior-engineering=019f6847-65d7-7ae0-95dd-d54f5d0a9ed1; architecture=019f6847-6c8c-7950-9e8d-1c1cc8c49aeb; QA/test=019f6847-739b-7981-99e9-df26a75ac35e; security/auth=019f6847-7e09-7de3-8163-75e91fe0888f; product/ops=019f6847-8881-7f91-a547-877d41a1967e; reuse/dedup=019f6847-92dd-7501-84eb-b8f89a18d4f5; CI-integrity=019f684d-81c8-7bb3-a24a-4a2c26e19867; test-delta=019f684d-88c6-7090-bda1-ba4694935c92; docs=019f684d-9178-7ed2-8066-cb2561c7244c

After the reviewed SHA, only initiative review evidence and status files may
change without invalidating this review.

## Reviewed Change

- Added the inactive provider-neutral `PreparedArtifact` and
  `CommittedArtifactSource` boundary. A server commitment remains inseparable
  from the exact second-pass bytes.
- Added bounded, private, cross-process scratch custody with aggregate quota,
  file/concurrency limits, free-space admission, deadlines, stale cleanup, and
  fail-closed filesystem validation.
- Bound stale reservation ownership to Linux boot identity plus process start,
  preventing PID reuse from retaining abandoned quota.
- Kept anonymous read descriptors and ledger reservations under one cleanup
  owner until reader close and durable release both succeed.
- Added one shared bounded flock primitive for scratch and LocalStorage private
  operation locks, including cancellation-preserving timeout behavior.
- Preserved the active ArtifactStore v1 interface, provider selection, routes,
  schema, and product lifecycle.
- Expanded the cumulative 90 percent CI coverage contract to include the shared
  lock primitive.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Exact code SHA and focused gates passed. |
| QA/test | PASS | None | Cancellation-time lock failure was repaired before final review. |
| security/auth | PASS | None | No auth, permission, secret, payment, or tenant boundary changed. |
| product/ops | PASS | None | No operator, contributor, reviewer, payment, or reputation workflow changed. |
| architecture | PASS WITH LOW RISKS | None | Linux `/proc` process identity and concrete sealed-source custody remain localized. |
| CI integrity | PASS | None | The 78 percent repository gate and cumulative scoped 90 percent gates remain fail closed. |
| docs | PASS | None | Settings, defaults, scope, and inactive-cleanup behavior are documented. |
| reuse/dedup | PASS WITH LOW RISKS | None | Shared lock/cancellation paths are reused; v1 digest helpers should consolidate during 02A3. |
| test delta | PASS | None | No test was removed, skipped, xfailed, or weakened. |

## Valid Findings Addressed

- Rejected non-finite duration values instead of admitting `NaN` or infinity.
- Deferred root-marker content validation until after the ledger lock and made
  multiprocessing result collection bounded.
- Prevented failed reader close from releasing quota while bytes remained open.
- Closed the anonymous read descriptor when first-pass descriptor ownership
  became uncertain.
- Replaced the constructor's unbounded ledger lock with the shared deadline.
- Replaced PID-only stale ownership with boot/process-start identity.
- Replaced LocalStorage's unbounded private flock with the same bounded helper.
- Preserved the caller's `CancelledError` when a background lock acquisition
  later reaches its deadline.

## Commands Run

```bash
cd backend && .venv/bin/ruff check app tests
cd backend && .venv/bin/pytest \
  tests/test_artifact_preparation.py \
  tests/test_local_artifact_store.py \
  tests/test_config.py -q \
  --cov=app.core.cancellation \
  --cov=app.core.file_locks \
  --cov=app.modules.artifacts.preparation \
  --cov=app.modules.artifacts.sources \
  --cov=app.core.config \
  --cov-report=term-missing --cov-fail-under=90
cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres \
  .venv/bin/python scripts/run_isolated_tests.py \
  --metadata-json <temporary-path>/result.json --timeout-seconds 900 -- \
  .venv/bin/python -m pytest tests/test_artifacts.py -q
cd backend && .venv/bin/docstr-coverage --config .docstr.yaml
python3 scripts/test_agent_gates.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
```

Results: Ruff passed; 154 focused tests passed at 94.40 percent scoped
coverage; the shared lock primitive is at 100 percent; 38 PostgreSQL artifact
integration tests passed in an isolated disposable database; repository
docstring coverage passed at 94.8 percent; 71 agent-gate tests passed; stale
artifact, stale wording, Markdown link, and diff checks passed.

The full repository suite and 78 percent whole-app floor remain authoritative
in GitHub Backend CI for the published evidence-bound head.

## Remaining Risks

- Linux `/proc` is an explicit runtime dependency of this Linux/`fcntl` scratch
  implementation and must remain true at hosted activation.
- Live-process ambiguous descriptor custody intentionally retains quota until
  explicit cleanup or process exit.
- `02A3` should consolidate temporary v1 digest/stream helpers during the clean
  cut instead of carrying duplicate conventions forward.
- This boundary remains inactive until the separately approved `02A3` cutover.

## Stop Condition

Publish the evidence-bound head for external CI, CodeRabbit, and human review.
Do not merge without explicit user approval and do not start `02A3`.
