# External Review Response: WS-REV-001-PLAN

## Pull Request

PR #128: `https://github.com/Flow-Research/workstream/pull/128`

Reviewed branch head before repair:
`6faccc04e9dbad7c746b081e55a47750f678d37c`

External-repair non-review initiative snapshot digest:
`5e14cd65270e699b27506e428f7ac876f6a18524ecf052eef51d19ea0a9ea03c`

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

## Comments Deferred

None.

## Human Decisions Needed

None beyond the existing explicit human merge approval for PR #128 and the
separate post-merge start decision for `WS-REV-001-01`.

## Commands Rerun

```text
git diff --check
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_loop_memory_state.py
python3 scripts/test_agent_gates.py
python3 scripts/check_internal_review_evidence.py
```

## Remaining Risks

- Reviewer-specific ART read/intake port ownership remains a future ART-owned
  fail-closed gate at REV-07.
- This response changes planning contracts only; every named future test and
  coverage command must exist and pass when its owning implementation chunk is
  activated.
