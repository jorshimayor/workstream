# Internal Review Evidence: WS-ART-001-01

## Chunk

`WS-ART-001-01`: artifact domain and local adapter

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: d67ccf17c837a20c235ea16d9ca4a3110dd3e579

Reviewed at: 2026-07-12T08:56:53Z

Reviewer run IDs: senior-engineering=019f5412-7b62-7fa3-94a5-e16bc47d538b; QA/test=019f5412-64d7-7033-ac07-8c75c1e52684; security/auth=019f5412-87f9-72d3-bc37-c3abc1151a63; product/ops=019f554d-60b0-7321-9412-4fb71eb074f9; architecture=019f5412-5588-7c60-8bd9-da0a2fe46924; CI-integrity=019f554d-6633-7143-9c93-f10b0f565fe3; docs=019f554d-6ade-73d0-98ad-76e7d5a0474d; reuse/dedup=019f554d-73a7-7932-bf74-553d421590d6; test-delta=019f5565-2802-7462-b066-d178464cc479

## Reviewed Change

- Added the provider-neutral artifact contract, immutable artifact records,
  upload coordination, recovery, retention, quarantine, and shared audit path.
- Added a private local object-storage adapter with bounded streaming,
  no-follow filesystem handling, atomic publication, durable receipts, and
  deterministic crash recovery.
- Added additive migration `0016`, configuration guards, versioned JSON
  contract fixtures, a phased stale-contract gate, and focused CI coverage.
- Kept public APIs, Flow Node, product cutovers, and later artifact chunks out
  of scope.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Recovery and transaction ownership are explicit and maintainable. |
| QA/test | PASS | None | Fault, replay, migration, and coordinator matrices cover the chunk contract. |
| security/auth | PASS AFTER FIXES | None | Filesystem, identifier, principal, receipt, and quarantine risks were repaired. |
| product/ops | PASS | None | Record separation and audit attribution preserve the intended product boundary. |
| architecture | PASS | None | Provider-neutral port and storage/domain separation match ADR 0013. |
| CI integrity | PASS | None | Global 78 percent floor remains while artifact scope fails below 90 percent. |
| docs | PASS | None | ADR, specification, plan, decisions, and chunk contracts are aligned. |
| reuse/dedup | PASS | None | Shared hashing and audit paths are reused without parallel frameworks. |
| test delta | PASS AFTER FIXES | None | Every seeded 0015 row and unaffected binding/replica column is preserved. |

## Commands Run

```bash
cd backend && .venv/bin/ruff check app tests scripts
cd backend && .venv/bin/docstr-coverage --config .docstr.yaml
cd backend && pytest -q tests/test_artifacts.py \
  --cov=app.adapters.artifacts --cov=app.interfaces.artifacts \
  --cov=app.modules.artifacts --cov-report=term-missing --cov-fail-under=90
cd backend && pytest -q tests/test_alembic.py tests/test_config.py
python3 scripts/test_agent_gates.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/check_loop_memory_state.py
git diff --check
```

Results: Ruff passed; docstring coverage was 100 percent; 38 artifact tests
passed with 90.26 percent artifact-subsystem coverage; 17 migration/config
tests passed; 36 agent-gate tests passed; all stale, link, loop-memory, and diff
checks passed. Focused reviewer reruns also passed the repaired migration,
coordinator, ambiguous-replay, create-fault, and bounded-I/O cases.

The repository-wide suite is intentionally not duplicated in this worktree
while the separately authorized WS-QUAL agent runs that proof. GitHub Backend
CI remains the fail-closed current-head global-coverage authority for this PR.

## Findings Addressed

- Ambiguous provider outcomes now require replay unless both expected digest
  and size were persisted after confirmed provider success.
- Cancellation, receipt corruption, missing intent/object, and ready-content
  integrity paths now fail closed with bounded recovery and audit evidence.
- Migration proof now compares every column of representative populated 0015
  project, guide, policy, task, submission, and checker rows and promotes none.
- Coordinator tests prove exact row/object/audit counts and byte-for-byte
  preservation of unaffected bindings and replicas.
- Adapter tests now prove bounded read/write slices and deterministic create,
  open, write, fsync, publish, metadata, receipt, verify, and quarantine faults.

## Remaining Risks

- Local storage is development-only and deliberately rejected in production.
- Flow Node adapter behavior and reconciliation against a remote provider remain
  owned by inactive chunk `WS-ART-001-02`.
- Public artifact APIs and product cutovers remain blocked on their named later
  chunks and authorization dependencies.

## Stop Condition

Publish this chunk for external and human review, then stop. Do not start
`WS-ART-001-02` and do not merge without explicit user approval.
