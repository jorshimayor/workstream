# Work Queue

## Planned Next

| Chunk | Title | Risk | Status |
|---|---|---:|---|
| `WS-POL-001-14` | Submission Finalize And No-DB Terminal Benchmark Proof | L1 | Inactive; start only after explicit user signal |
| `TERMINAL-BENCHMARK-LIVE-DRILL` | Accepted No-DB Terminal Benchmark Drill | L1 | Blocked behind `WS-POL-001-14`; use real HTTP calls only after finalize/system actor semantics are implemented |

## Completed

| Chunk | Title | Risk | Status |
|---|---|---:|---|
| `WS-ENG-001-01` | Codex-native zero-trust loop bootstrap | L1 | Merged through PR #23 on 2026-06-20 |
| `EXAMPLE-TERMINAL-BENCHMARK` | Terminal Benchmark example drill | L3 | Merged through PR #25 on 2026-06-21 |
| `WS-POL-001-PLAN` | Submission Artifact Policy Foundation planning | L1 | Merged through PR #26 on 2026-06-27 |
| `WS-POL-001-01` | Submission Artifact Policy Foundation | L1 | Merged through PR #28 |
| `WS-POL-001-02` | Async Guide Analysis And Policy Derivation | L1 | Merged through PR #61 |
| `WS-POL-001-03` | Task Locked Context And Submission Creation | L1 | Merged through PR #63 on 2026-07-03 |
| `WS-POL-001-04` | Post-Submit Checker Policy Provenance | L1 | Merged through PR #65 |
| `WS-POL-001-05` | Revision Resubmission And Real API Drill | L1 | Merged through PR #66 |
| `WS-POL-001-06` | Terminal Benchmark Real Fixture Drill | L1 | Merged through PR #67 |
| `WS-POL-001-07` | Task Contract Artifact Field Cleanup | L1 | Merged through PR #68 |
| `WS-POL-001-08` | Celery Project Setup Pipeline | L1 | Merged through PR #69 |
| `WS-POL-001-09` | OpenAI Agents SDK Runtime Only | L1 | Merged through PR #71 |
| `WS-POL-001-10` | Pre-Submit Live Drill Hardening | L1 | Merged through PR #72 |
| `WS-POL-001-11` | Actor Identity And Profile Registry | L1 | Merged through PR #74 on 2026-07-07 |
| `WS-POL-001-12` | Project Setup And Policy Visibility APIs | L1 | Merged through PR #76 as `46e74de` |
| `WS-POL-001-13` | Task Context And Submission Requirement APIs | L1 | Merged through PR #77 as `b567bac` on 2026-07-08 |

## Proposed Next

`WS-POL-001-14` should replace public submission lock wording with finalize
semantics, define system actor audit behavior, and enable the accepted
Terminal Benchmark proof without DB inspection. Do not start it until the user
explicitly asks.

## Blocked

| Chunk | Blocker | Next action |
|---|---|---|
| `TERMINAL-BENCHMARK-LIVE-DRILL` | Accepted no-DB proof requires submission finalize semantics and system actor audit behavior. | Complete and review `WS-POL-001-14`, then rerun the drill through real HTTP calls. |
