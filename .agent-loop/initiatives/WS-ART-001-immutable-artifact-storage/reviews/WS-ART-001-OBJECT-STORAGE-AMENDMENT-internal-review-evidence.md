# Internal Review Evidence: WS-ART-001-OBJECT-STORAGE-AMENDMENT

## Chunk

`WS-ART-001-OBJECT-STORAGE-AMENDMENT` - AWS-First Object Storage Planning
Amendment

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 8f29e46f84415b3506d211e3229f224e6ad4e085

Reviewed at: 2026-07-14T19:56:49Z

Reviewer run IDs: senior-engineering=019f622a-d6d9-7992-8363-2bd65e69dcaa; architecture=019f622a-e357-7ab1-ad29-fae832d112ed; QA/test=019f622b-0089-7a32-9fb7-64bb063f2a97; security/auth=019f622b-2040-7c21-aa63-ed0879a126d0; product/ops=019f622f-efed-7d53-a998-84301da54454; reuse/dedup=019f622f-f6de-7431-a44c-6d26c0195bec; CI-integrity=019f6230-0105-7d33-8d69-e1288c9005c9; test-delta=019f6230-0cca-7a23-8716-dd253d5de7f9; docs=019f6230-1621-7c31-904b-43eeca5c3a2a

After the reviewed SHA, only evidence and status files may change:

- `.agent-loop/initiatives/**/reviews/**`
- `.agent-loop/LOOP_STATE.md`
- `.agent-loop/initiatives/**/STATUS.md`
- `docs/internal_reviews/**`

## Reviewed Change

- Makes AWS S3 the only v0.1 production artifact provider.
- Keeps MinIO as local/CI S3 protocol proof and LocalStorage as focused
  development/test storage.
- Defers R2 and Flow Node without compatibility paths or inactive runtime
  symbols.
- Locks the typed adapter/factory sequence and the ArtifactStore v2 clean cut.
- Defines the exact AWS principal, action, resource, conditional-write,
  missing-key, activation, and live-proof contracts.
- Defines cumulative 90 percent artifact subsystem coverage while retaining the
  78 percent whole-repository CI floor.
- Adds fail-closed stale-contract scanning and mutation-focused agent-gate
  regression tests.
- Changes no backend application runtime, migration, dependency, or Compose
  runtime file.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Publication-state review confirmed the durable log, bounded scope, and reproducible gate command. |
| QA/test | PASS | None | Confirmed exact-head provenance, mutation coverage, and 44 passing gate tests. |
| security/auth | PASS | None | Confirmed no new auth/data surface and the exact AWS contract remains fail closed. |
| product/ops | PASS | None | Confirmed no product-decision, worker, reviewer, payment, or reputation drift. |
| architecture | PASS | None | Confirmed provider, capability-port, and composition-root boundaries remain intact. |
| CI integrity | PASS | None | Confirmed no gate weakening and retained 78/90 percent coverage contracts. |
| docs | PASS | None | Confirmed active terminology, links, and durable-state claims are consistent. |
| reuse/dedup | PASS | None | Confirmed the standalone scanner allowlists are safe because exact equality is regression-tested. |
| test delta | PASS | None | Confirmed no removed, skipped, or weakened tests and no post-candidate test drift. |

## Valid Findings Addressed

- Replaced a system-Python `pip install` verification step with a self-cleaning
  temporary virtual environment so the documented command works under PEP 668.
- Added exact AWS `HeadObject` missing-key semantics: bucket-scoped
  `s3:ListBucket` is used only to preserve trustworthy 404 classification;
  every 403 remains `provider_unavailable`, and no application listing API is
  added.
- Made the AWS principal/action/resource and bucket-deny matrices closed and
  mutation-tested rather than substring-checked.
- Removed active wording that contradicted the required bucket-level AWS
  permission and added a stale-contract regression rule for its return.
- Replaced the nonexistent formatted `ARTIFACT_COVERAGE_PHASE` identifier with
  the accurate phrase "active artifact implementation coverage phase."
- Rechecked the duplicated historical scanner allowlist. It remains local data
  for independently executable scanners, with exact equality enforced by a
  regression test; no shared runtime abstraction is required.
- Every failed candidate and reviewer session was closed. No failed-candidate
  result is reused as final approval.

## Commands Run

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

Results:

- Ruff: passed.
- Stale artifact, authorization, and Workstream wording scans: passed.
- Loop-memory state: passed.
- Markdown links: passed for 73 changed Markdown files.
- Agent gate regression suite: 44 passed in an isolated hash-pinned
  environment.
- Diff hygiene: passed.
- Runtime-scope guard: printed no paths.

## Remaining Risks

- This is planning and executable-contract proof, not live AWS provider proof.
  Chunk 07 remains responsible for release-bound private-bucket activation and
  the missing opaque-key 404 challenge.
- `s3:ListBucket` technically permits enumeration if the runtime principal is
  compromised. The accepted containment is one dedicated private Workstream
  artifact bucket plus opaque hash-only keys and no application list surface.
- Stale-contract scanners are lexical; unusual future wording still requires
  reviewer judgment and a regression case when discovered.

## Stop Condition

Do not start `WS-ART-001-02A1` until this amendment is externally reviewed,
explicitly merged by the user, and the user gives a separate start signal.
