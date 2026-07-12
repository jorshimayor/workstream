# Chunk Map: WS-QUAL-001 Backend Coverage Floor

| Chunk | Scope | Risk | State |
|---|---|---:|---|
| `WS-QUAL-001-01` | Coverage harness, isolated database proof, clean main baseline, initial non-decreasing CI ratchet | L1 | Proposed; inactive pending post-merge memory and explicit user start |
| `WS-QUAL-001-02` | Project setup/policy/correction service coverage; floor at least 82% | L1 | Inactive |
| `WS-QUAL-001-03` | Project repository/router coverage; floor at least 84% | L1 | Inactive |
| `WS-QUAL-001-04` | Task service/repository/router coverage; floor at least 86% | L1 | Inactive |
| `WS-QUAL-001-05` | Checker service/runner/repository/router/worker coverage; floor at least 88% | L1 | Inactive |
| `WS-QUAL-001-06` | Enumerated residual gaps and permanent 90% CI floor | L1 | Inactive |

Each coverage-test chunk is limited to 500 implementation lines, defined in the
plan. Missing its numeric floor or size budget stops the chunk for replanning;
scope does not spill into the next chunk. A later chunk may start only after the
prior PR merges, post-merge evidence plus initiative `STATUS.md` and global
`LOOP_STATE.md`, `WORK_QUEUE.md`, and `REVIEW_LOG.md` are updated and merged,
and the user provides a new start signal.
