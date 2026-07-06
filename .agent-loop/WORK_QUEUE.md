# Work Queue

## Planned Next

| Chunk | Title | Risk | Status |
|---|---|---:|---|
| `WS-POL-001-11` | Actor Identity And Profile Registry Contract | L1 | Contract-only branch active; implementation waits for human review |

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

## Proposed Next

The next implementation chunk should create local Workstream actor identity and
actor profile registries for verified Flow actors. It must not turn Workstream
into the auth provider, and persisted profiles must not become permission
authority. After that merge, rerun the Terminal Benchmark live API drill through
real HTTP calls.

## Blocked

None.
