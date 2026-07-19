# Internal Review Evidence: WS-ART-001-02C1

## Chunk

`WS-ART-001-02C1`: Admission And Put-Attempt Foundation

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: `b4d54469b1590cf43fd9f496c64b6172577c0eec`

Reviewed at: 2026-07-19T08:09:47Z

Reviewer run IDs: senior-engineering=019f795c-78be-7701-b920-ac956612bf3d; QA/test=019f795c-7b83-7602-a5d2-aa19f4f4c7c9; security/auth=019f795c-81a9-7cd0-9f4c-e6adf9f4b558; product/ops=019f795c-8985-7582-b695-c528c99d4321; architecture=019f795c-9173-70e0-86a9-709afb162a52; reuse/dedup=019f795c-9ba9-7153-b7e9-4f6f900dbe21; CI-integrity=019f7966-0cb2-7343-a08e-946e26c51127; test-delta=019f7966-168e-7053-93e6-f43d184e96da; docs=019f7966-1dec-7be2-8417-c4ea9bc5329a

The reviewed base is trusted `main` at
`93dd392484b397cfdfaaa833631dc2c27f591ed7`, including merged AUTH PR #152.
Only review artifacts and initiative status may change after the reviewed SHA.
Any implementation, test, workflow, policy, or chunk-contract change invalidates
this evidence and requires a new exact-SHA review cycle.

## Reviewed Change

- Added durable task, producer, project, and deployment admission scopes with
  server-owned limits and unique content charges.
- Added closed guide, contributor, and checker-output admission requests whose
  relationships and producer authority are resolved and locked by Workstream.
- Atomically claims the storage namespace, reserves capacity, writes audit
  evidence, and creates one `prepared` `ArtifactPutAttempt` before provider I/O.
- Deduplicates exact replay while reacquiring released charges only after
  capacity and linked-charge revalidation.
- Locks guide source items and snapshots during authoritative admission so the
  persisted attempt cannot race mutable guide facts.
- Keeps provider execution, verification, publication, recovery, routes, and
  product cutover out of scope and inactive.
- Adds migration `0027` with populated-state downgrade refusal across scopes,
  charges, attempts, and attempt-charge links.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Transaction, replay, rollback, failure, and scope behavior are maintainable and bounded. |
| QA/test | PASS | None | Real PostgreSQL concurrency, lock, rollback, relationship, and migration cases satisfy the contract. |
| security/auth | PASS | None | Exact actor, identity-link, service-identity, relationship, scope, and replay checks fail closed. |
| product/ops | PASS | None | Admission remains internal and does not alter task, review, revision, contribution, or compensation lifecycle state. |
| architecture | PASS | None | Provider-neutral boundaries and transaction ownership are preserved with no route or provider execution drift. |
| reuse/dedup | PASS | None | Canonical artifact interfaces are reused and no parallel provider-reference or admission abstraction remains. |
| CI integrity | PASS | None | The new audit coverage gate is additive; the repository 78 percent floor and cumulative 90 percent gates remain fail closed. |
| test delta | PASS | None | No skipped or weakened tests; removed direct-write tests correspond to the deliberately removed provider-finalization path. |
| docs | PASS | None | Active docs, migration behavior, terminology, scope exclusions, and links match the implementation. |

## Valid Findings Addressed

- Replaced read-only guide admission facts with row locks on both the exact
  source item and its immutable snapshot, plus a two-transaction lock-timeout
  regression test.
- Proved capacity failure leaves no scope, charge, attempt, or audit residue.
- Proved an attempt-only populated state prevents destructive migration
  downgrade.
- Moved provider-object reference parsing and construction behind the canonical
  provider-neutral artifact interface.
- Revalidated canonical active human profiles and identity links during guide
  and contributor admission.
- Revalidated replay capacity and the exact attempt-charge set before returning
  an existing attempt.
- Bound checker output to the canonical submission and task relationship.

## Commands Run

```bash
cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest tests/test_artifact_admission.py tests/test_artifact_architecture.py tests/test_artifact_cleanup_wiring.py tests/test_artifact_preparation.py tests/test_artifact_store_conformance.py tests/test_artifacts.py tests/test_local_artifact_store.py tests/test_s3_artifact_store.py tests/test_audit.py tests/test_config.py -q --cov=app.interfaces.artifact_operations --cov=app.modules.artifacts --cov=app.modules.audit --cov=app.core.config --cov-report=term-missing --cov-fail-under=90
cd backend && .venv/bin/ruff check app tests
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/test_agent_gates.py
python3 scripts/check_markdown_links.py
git diff --check
```

Results: 369 tests passed in 650.13 seconds with 94.32 percent scoped
coverage. Ruff, the stale artifact contract scan, 88 agent-gate tests,
Markdown links, and diff integrity passed. GitHub Backend CI remains
authoritative for the isolated full repository suite and 78 percent floor.

## Remaining Risks

- Provider execution, provider acknowledgement verification, and publication
  remain intentionally unavailable until separately approved later chunks.
- Native AWS remains runtime-ineligible pending its separately owned live proof.
- The admission service remains an internal foundation and is not yet wired to
  project or submission product routes.

## Stop Condition

Publish this evidence-bound candidate for GitHub Actions, CodeRabbit, and
explicit human review. Do not merge without the user's approval and do not
start `WS-ART-001-02C2` automatically.
