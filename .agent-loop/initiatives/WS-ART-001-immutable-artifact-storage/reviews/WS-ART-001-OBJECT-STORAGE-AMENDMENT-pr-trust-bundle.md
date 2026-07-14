# PR Trust Bundle

## Chunk

`WS-ART-001-OBJECT-STORAGE-AMENDMENT` - AWS-First Object Storage Planning
Amendment

## Goal

Replace the earlier Flow Node-first delivery sequence with a smaller v0.1
object-storage plan that can ship safely: AWS S3 in production, MinIO for
local/CI protocol proof, LocalStorage for focused development, and deferred R2
and Flow Node adapters.

## Human-Approved Intent

- Intent: `../INTENT.md`
- Decisions: `../DECISIONS.md`
- Plan: `../PLAN.md`
- Chunk map: `../CHUNK_MAP.md`
- Chunk contract: `../chunks/WS-ART-001-OBJECT-STORAGE-AMENDMENT.md`

## What Changed

- Replanned the provider and implementation sequence around AWS S3.
- Locked ArtifactStore v2, clean LocalStorage/schema cutover, and typed external
  service adapter/factory boundaries.
- Split admission, verification publication, recovery execution, and Operator
  operations into bounded implementation chunks.
- Defined release-bound AWS readiness, runtime IAM, conditional writes,
  missing-key classification, fail-closed errors, and live activation proof.
- Added executable stale-contract and CI-integrity enforcement, including
  cumulative artifact subsystem coverage.

## Why It Changed

Operating and reducing Flow Node before Workstream had a proven object-storage
boundary added delivery and maintenance complexity. The amended plan ships the
provider-neutral artifact contract first through AWS S3 while preserving Flow
Node as a later adapter initiative, not as v0.1 infrastructure.

## Design Chosen

```text
v0.1 production bytes -> S3CompatibleArtifactStore -> AWS S3
local/CI protocol proof -> S3CompatibleArtifactStore -> MinIO
focused development -> LocalStorageAdapter
future optional provider -> separately approved Flow Node adapter initiative
```

Product services receive narrow artifact capabilities. Artifact orchestration
owns the writable store port. Composition roots select providers through the
shared typed external-service adapter/factory convention. PostgreSQL stores
artifact metadata and provenance, not artifact bytes.

## Alternatives Rejected

- Operating Flow Node as v0.1 production storage: rejected because Workstream
  does not need to own that additional service before the artifact contract is
  proven.
- Cloudflare R2 in v0.1: rejected because its credential model adds another
  production provider before AWS proof exists.
- Artifact bytes in PostgreSQL: rejected because PostgreSQL is the record
  database, not object storage.
- Ad hoc provider factories, concrete imports in product services, compatibility
  aliases, and dual adapter paths: rejected by ADR 0014 and the clean-cut rule.
- Removing `s3:ListBucket`: rejected because AWS then masks missing
  `HeadObject` responses as 403, preventing trustworthy absence
  classification.

## Scope Control

### Allowed Files Changed

- Initiative intent, discovery, decisions, risks, plan, status, chunk map, and
  chunk contracts.
- ADRs, architecture/specification docs, glossary/roadmap references, and
  durable loop memory.
- Agent Gates and backend workflow coverage enforcement.
- Stale-contract scanner, its pinned dependency, and regression tests.

### Files Outside Scope

- No changes under `backend/app/`, `backend/alembic/`, `backend/pyproject.toml`,
  or `docker-compose.yml`.
- No provider runtime, AWS resource, Flow Node service, product route, schema,
  Celery task, or migration was implemented.

## Product Behavior

- [x] No Workstream product runtime behavior changed.
- [x] No public artifact API or provider runtime was activated.

## Acceptance Criteria Proof

- [x] AWS S3 is the only v0.1 production provider.
- [x] MinIO and LocalStorage responsibilities are explicit and bounded.
- [x] R2 and Flow Node remain deferred with fail-closed stale-contract gates.
- [x] Exact AWS runtime/readiness/negative-probe custody and IAM matrices are
  documented and mutation-tested.
- [x] Missing-key 404 versus denied 403 semantics are executable contracts.
- [x] Cumulative 90 percent subsystem coverage and the 78 percent repository
  floor cannot be silently weakened.
- [x] No backend runtime path entered the planning chunk.
- [x] All nine internal reviewer tracks passed exact SHA
  `8f29e46f84415b3506d211e3229f224e6ad4e085`.

## Tests And Checks Run

```bash
backend/.venv/bin/ruff check scripts/test_agent_gates.py scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_loop_memory_state.py
python3 scripts/check_markdown_links.py --changed-only origin/main...HEAD
(agent_gate_venv="$(mktemp -d)" && \
  trap 'rm -rf "$agent_gate_venv"' EXIT && \
  python3 -m venv "$agent_gate_venv" && \
  "$agent_gate_venv/bin/python" -m pip install --disable-pip-version-check --require-hashes -r scripts/agent-gate-requirements.txt && \
  "$agent_gate_venv/bin/python" scripts/test_agent_gates.py)
git diff --check
test -z "$(git diff --name-only origin/main...HEAD -- backend/app backend/alembic backend/pyproject.toml docker-compose.yml)"
```

Result summary:

```text
Ruff passed.
Stale artifact, authorization, and wording scans passed.
Loop-memory and 73 changed Markdown link checks passed.
44 agent-gate regression tests passed in a hash-pinned temporary environment.
Diff hygiene passed; runtime-scope guard printed no paths.
```

## Test Delta

### Tests Added Or Strengthened

- Scanner discovery/history/runtime-path coverage.
- R2 and Flow Node deferral enforcement.
- Exact AWS action/resource and bucket-deny mutation matrices.
- Exact backend full-suite and cumulative artifact coverage step parsing.
- Pinned Agent Gates dependency and reproducible isolated execution.

### Tests Removed Or Skipped

- None.

## CI Integrity

- [x] Repository coverage floor remains 78 percent.
- [x] New/materially changed artifact subsystems retain a 90 percent floor.
- [x] Lint and typecheck were not weakened.
- [x] No `continue-on-error`, conditional, command, environment, shell, or
  working-directory bypass was introduced.
- [x] No package-script weakening or unpinned GitHub Action was introduced.
- [x] Checkout credential persistence remains disabled where checkout is used.

## External Review

External review response file will be created after external comments exist:

- `.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/reviews/WS-ART-001-OBJECT-STORAGE-AMENDMENT-external-review-response.md`

| Source | Status | Notes |
|---|---:|---|
| CodeRabbit | Pending | Must be reviewed separately from internal evidence. |
| GitHub checks | Pending | Must pass on the published evidence-bound head. |

## Reviewer Results

Reviewed code SHA: 8f29e46f84415b3506d211e3229f224e6ad4e085

Reviewed at: 2026-07-14T19:56:49Z

Reviewer run IDs: senior-engineering=019f622a-d6d9-7992-8363-2bd65e69dcaa; architecture=019f622a-e357-7ab1-ad29-fae832d112ed; QA/test=019f622b-0089-7a32-9fb7-64bb063f2a97; security/auth=019f622b-2040-7c21-aa63-ed0879a126d0; product/ops=019f622f-efed-7d53-a998-84301da54454; reuse/dedup=019f622f-f6de-7431-a44c-6d26c0195bec; CI-integrity=019f6230-0105-7d33-8d69-e1288c9005c9; test-delta=019f6230-0cca-7a23-8716-dd253d5de7f9; docs=019f6230-1621-7c31-904b-43eeca5c3a2a

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Publication-state exact SHA passed. |
| QA/test | PASS | None | Exact-head provenance and gate behavior passed. |
| security/auth | PASS | None | No security regression or unowned authority surface. |
| product/ops | PASS | None | No product workflow or decision drift. |
| architecture | PASS | None | Provider and capability boundaries remain sound. |
| CI integrity | PASS | None | No gate or coverage weakening. |
| docs | PASS | None | Active terminology and durable state are consistent. |
| reuse/dedup | PASS | None | Equality-guarded standalone scanner data accepted. |
| test delta | PASS | None | No removed, skipped, or weakened test. |

Internal evidence:

- `WS-ART-001-OBJECT-STORAGE-AMENDMENT-internal-review-evidence.md`

## Remaining Risks

- Live AWS IAM, conditional-write, private-bucket, and missing-key behavior is
  not proven in this planning PR; Chunk 07 owns the release-bound proof.
- Bucket-level `s3:ListBucket` creates contained enumeration capability if the
  runtime principal is compromised. The dedicated bucket, opaque keys, and
  absent application list surface are the accepted controls.
- Lexical scanners cannot replace architecture review for novel wording.

## Follow-Up Work

After explicit merge and a separate user start signal, execute only
`WS-ART-001-02A1`. Do not start `02A2`, provider runtime, or Flow Node work
automatically.

## Human Review Focus

- Whether AWS S3 is correctly limited to v0.1 production while R2 and Flow Node
  remain genuinely deferred.
- Whether `s3:ListBucket` is sufficiently contained and only supports reliable
  missing-key classification.
- Whether adapter/factory, capability-port, and clean-cut ownership remain
  enforceable during implementation.
- Whether the chunk sequence keeps admission, verification, recovery, and
  Operator operations independently reviewable.
- Whether the cumulative 90 percent subsystem coverage contract can be
  maintained without weakening the 78 percent repository floor.

## Human Ownership

- [ ] I can explain what changed.
- [ ] I can explain why it changed.
- [ ] I know what could break during implementation.
- [ ] I accept the remaining risks.
- [ ] The user explicitly approved this specific PR for merge.
