# Internal Review Evidence: WS-ART-001-02A2

## Chunk

`WS-ART-001-02A2`: Committed Source And Local Preparation

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: aba8325321b35a92778ffe3ddfb414ac7772f57f

Reviewed at: 2026-07-16T07:17:30Z

Reviewer run IDs: senior-engineering=019f69c0-9c33-7433-ac6a-b0f4a42ae628; architecture=019f69c0-9e67-7090-b5e1-9e58637811bc; QA/test=019f69c0-a0a6-7f03-a782-34134a04a80b; security/auth=019f69c0-a2ce-72a1-8027-a48ccc522795; product/ops=019f69c0-a4e7-7960-a6f8-65f752658e31; reuse/dedup=019f69c0-a70a-7940-8a1a-5c2eb382b65b; CI-integrity=019f69c5-cb1a-7530-8ffb-ec33e15449ed; test-delta=019f69c5-ce97-7793-a201-d084ff4554e5; docs=019f69c5-d43d-7990-8615-54ca195ff16e

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
| QA/test | PASS | None | Exact cancellation identity, retryable `.part` custody, and lock-order proof passed. |
| security/auth | PASS | None | No auth, permission, secret, payment, or tenant boundary changed. |
| product/ops | PASS | None | No operator, contributor, reviewer, payment, or reputation workflow changed. |
| architecture | PASS | None | No alternate provider, factory, runtime, or product path was introduced. |
| CI integrity | PASS | None | The 78 percent repository gate and cumulative scoped 90 percent gates remain fail closed. |
| docs | PASS | None | Settings, defaults, scope, and inactive-cleanup behavior are documented. |
| reuse/dedup | PASS | None | Existing cancellation ownership helper is reused; test-only order instrumentation is localized. |
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
- Preserved the exact original caller cancellation when unpublished temporary
  cleanup fails, retained the `.part` file under retryable intent ownership,
  and proved later canonical cleanup plus exact-request retry.
- Replaced timing-dependent marker-order proof with explicit spawned-child,
  lock-attempt, lock-acquired, and marker-validation events; widened only the
  bounded cold-start allowance after a reviewer reproduced a loaded-run flake.

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
