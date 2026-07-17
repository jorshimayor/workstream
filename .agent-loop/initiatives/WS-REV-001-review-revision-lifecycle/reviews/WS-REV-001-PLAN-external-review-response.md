# External Review Response: WS-REV-001-PLAN

## Pull Request

PR #128: `https://github.com/Flow-Research/workstream/pull/128`

Reviewed branch head before repair:
`e6417c37f8aef4ae4556cacb0dbe84bc481e45a4`

Reviewed repaired code SHA:
`86ee0a5e263ac306b3bf195a9fb9043aa5439416`

## Comments Addressed

| Thread | Disposition | Repair |
|---|---|---|
| `PRRT_kwDOSwL_U86RL5kg` | Fixed | Added the exact WS-IMP Markdown/PDF archival pair to chunk 01 allowed files; existing checksum/provenance acceptance criteria now have matching scope. |
| `PRRT_kwDOSwL_U86RL5km` | Fixed | Clarified that the WS-CON compensation-policy persistence contract must be merged with its exact lease-freeze FK/field types before REV-03 activation. |
| `PRRT_kwDOSwL_U86RL5kq` | Fixed | Expanded REV-13's final conformance command to include lifecycle-control, task, checker, outbox, audit, and configuration tests. |
| `PRRT_kwDOSwL_U86RaIER` | Fixed | Added task/app composition tests and task-router/checker-worker/composition lint paths to REV-05 verification and allowed test scope. |
| `PRRT_kwDOSwL_U86RaIEX` | Fixed | Corrected `later-admitted` compound-modifier wording. |
| `PRRT_kwDOSwL_U86RaIEa` | Fixed | Defined chain ownership as the canonical contributor on the exact TaskAssignment associated with a Submission in the requested chain. |
| `PRRT_kwDOSwL_U86RaIEc` | Fixed | Added `test_app.py` OpenAPI path-inventory verification to REV-07 and REV-09A so hidden lifecycle routes are proved absent before activation. |
| `PRRT_kwDOSwL_U86RaIEi` | Fixed | Expanded the REV-13 90 percent coverage gate from the lifecycle-control router to the complete lifecycle-control package. |
| `PRRT_kwDOSwL_U86Rr721` | Fixed | Made `delivery_draining` reachable, moved the full zero-obligation guard to `disabled`, added a CON-derived immutable root cutoff and mandatory writer fencing, restricted the drain to pre-cutoff completion work, and specified audited same-root claim recovery for denied dispatch. |

## Comments Deferred

None.

## Internal Re-Review

| Tracks | Agent | Result |
|---|---|---|
| Senior engineering, architecture, reuse/dedup | `/root/final_art_senior_review` | PASS |
| QA/test, product/ops | `/root/final_art_qa_review` | PASS |
| Security/auth, docs, CI integrity | `/root/final_art_security_review` | PASS AFTER FIXES |

The first re-review rejected `test_api_contract_e2e.py` as insufficient OpenAPI
proof. REV-07/09A were repaired to allow, run, and lint the established
`test_app.py` application path inventory before the final PASS.

The 2026-07-17 refresh review first exposed an unreachable delivery-drain phase.
Internal review then hardened the repair through four bounded cycles: durable
pre-cutoff lineage, mandatory fence coverage for every CON obligation writer,
exact command-class alignment, auditable already-claimed denial recovery, and
matching high-level architecture summaries. Exact snapshot
`86ee0a5e263ac306b3bf195a9fb9043aa5439416` passed all required tracks.

## Human Decisions Needed

None beyond the existing explicit human merge approval for PR #128 and the
separate post-merge start decision for `WS-REV-001-01`.

## Commands Rerun

```text
git diff --check
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_authorization_docs.py
sha256sum -c docs/reference_specs/SHA256SUMS
python3 scripts/check_loop_memory_state.py
python3 scripts/test_agent_gates.py
python3 scripts/check_internal_review_evidence.py
cd backend && .venv/bin/python -m pytest -q tests/test_app.py
```

All applicable REV commands pass after the evidence-only binding. The OpenAPI
inventory suite passes 4 tests. The repository-wide loop-memory check still
reports the AUTH-owned stale status on trusted main; this REV response does not
edit AUTH memory.

## Remaining Risks

- Reviewer-specific ART read/intake port ownership remains a future ART-owned
  fail-closed gate at REV-07.
- CON must merge the obligation-writer, dispatch, and callback fence hooks,
  monotonic root ordinal, and drain-cutoff/observation port before REV-12A.
- This response changes planning contracts only; every named future test and
  coverage command must exist and pass when its owning implementation chunk is
  activated.
