# Chunk Map: WS-QUAL-001 Backend Coverage Floor

| Chunk | Scope | Risk | State |
|---|---|---:|---|
| `WS-QUAL-001-01` | Combined harness/baseline contract | L1 | Split after circuit-breaker review |
| `WS-QUAL-001-01A` | Isolated least-privilege database runner and two-phase complete-suite CI | L1 | Merged through PR #103 as `2901a3e` |
| `WS-QUAL-001-01B` | Combined coverage policy, baseline, and CI ratchet | L1 | Circuit breaker triggered at 480/500 before required proof; split proposed |
| `WS-QUAL-001-01B1` | Coverage policy core and contract tests | L1 | Explicitly approved; implementation active |
| `WS-QUAL-001-01B2` | Git provenance, configured baseline evidence, and CI ratchet | L1 | Proposed after 01B1 merge and memory; inactive |
| `WS-QUAL-001-02` | Project setup/policy/correction service coverage; floor at least 82% | L1 | Inactive |
| `WS-QUAL-001-03` | Project repository/router coverage; floor at least 84% | L1 | Inactive |
| `WS-QUAL-001-04` | Task service/repository/router coverage; floor at least 86% | L1 | Inactive |
| `WS-QUAL-001-05` | Checker service/runner/repository/router/worker coverage; floor at least 88% | L1 | Inactive |
| `WS-QUAL-001-06` | Enumerated residual gaps and permanent 90% CI floor | L1 | Inactive |

Each coverage-test chunk is limited to 500 implementation lines, except the
reviewed chunk-01A genuine-proof exception capped at 700. Missing its numeric
floor or size budget stops the chunk for replanning;
scope does not spill into the next chunk. A later chunk may start only after the
prior PR merges, post-merge evidence plus initiative `STATUS.md` and global
`LOOP_STATE.md`, `WORK_QUEUE.md`, and `REVIEW_LOG.md` are updated and merged,
and the user provides a new start signal.
