# Work Queue

## In Progress

| Chunk | Title | Risk | Status |
|---|---|---:|---|
| `WS-QUAL-001-01B1B-R3` | Symtable Lexical Binding Closure | L1 | Cycle-zero review failed at `10ca508`; cycle-one contract clarification pending review |

## Planned Next

| Chunk | Title | Risk | Status |
|---|---|---:|---|
| `WS-QUAL-001-01B2` | Baseline Evidence And CI Ratchet | L1 | Inactive until B1B-R3 merge/memory plus explicit user start |
| `WS-QUAL-001-02` | Project Service Coverage | L1 | Inactive until B1B-R3 and 01B2 merge/memory plus explicit user start |
| `WS-AUTH-001-02` | Verified Issuer Token And JWKS Boundary | L1 | Resumed off-main in a separate worktree by explicit user direction; independent review required before PR/merge |
| `WS-POL-002-04` | Locked Runtime Execution And Routing Hardening | L1 | Inactive pending relevant authorization proof and a separate explicit user start |
| `WS-ART-001-02` | Flow Node Adapter And Reconciliation | L1 | Proposed; inactive pending separate explicit user start |

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
| `WS-POL-001-14` | Submission Finalize And No-DB Terminal Benchmark Proof | L1 | Merged through PR #79 as `53a57c3` on 2026-07-08 |
| `WS-POL-001-15` | Agent Derivation Policy Conflict Hardening | L1 | Merged through PR #81 as `b1a9851` on 2026-07-08 |
| `WS-POL-001-16` | Terminal Benchmark Live API Drill | L1 | Merged through PR #84 as `a3d2a3f` on 2026-07-09 |
| `WS-POL-002-PLAN` | Post-Submit Checker Foundation Planning | L1 | Merged through PR #85 as `3fc1a68` on 2026-07-09 |
| `WS-POL-002-01` | Post-Submit Compiler Contract | L1 | Merged through PR #87 as `ed52c21` on 2026-07-09 |
| `WS-POL-002-02` | Post-Submit Derivation Agent And Resumable Setup Integration | L1 | Merged through PR #88 as `32af6a7` on 2026-07-11 |
| `WS-POL-002-03` | Server-Owned Policy Approval And Visibility APIs | L1 | Merged through PR #90 as `a7aa474` on 2026-07-11 |
| `WS-AUTH-001-PLAN` | Authorization Service Planning | L0 | Merged through PR #91 as `ad6d644` on 2026-07-11 |
| `WS-AUTH-001-01` | Adopt Authorization Baseline And Repository Contracts | L1 | Merged through PR #93 as `772af1d` on 2026-07-11 |
| `WS-ART-001-PLAN` | Immutable Artifact Storage And Flow Node Integration Planning | L1 | Merged through PR #97 as `8644a43` on 2026-07-12 |
| `WS-QUAL-001-PLAN` | Backend Coverage Floor Planning | L1 | Merged through PR #99 as `9046d52` on 2026-07-12 |
| `WS-ART-001-01` | Artifact Domain And Local Adapter | L1 | Merged through PR #101 as `050eb15` on 2026-07-12 |
| `WS-QUAL-001-01A` | Isolated Database Runner | L1 | Merged through PR #103 as `2901a3e` on 2026-07-12 |
| `WS-QUAL-001-01B1A-R2` | Canonical Coverage Grammar | L1 | Merged through PR #105 as `8a4182e` on 2026-07-12 |

## Proposed Next

Implement and review only B1B-R3. AUTH-02 proceeds independently in its
existing worktree. Do not start 01B2 or chunk 02.

`WS-ART-001-01` is merged. Do not start `WS-ART-001-02` or edit Flow Node until
the user gives a separate explicit start signal.

## Blocked

| Chunk | Blocker | Next action |
|---|---|---|
| `WS-QUAL-001-01B1` | 496/500 lines after two semantic-integrity repair cycles | Superseded by the proposed 01B1A/01B1B split; do not resume |
| `WS-QUAL-001-01B1A` | 394/400 lines after two parser-normalization repair cycles; final QA/security review found two valid bypass variants | Replan the parser boundary before any further implementation |
| `WS-QUAL-001-01B1A-R1` | Additional valid false-positive finding outside its two-fix contract | Superseded by R2 canonical-grammar proposal; do not resume |
| `WS-QUAL-001-01B1B` | 223/300 after two binding/AST repair cycles; final test-delta review found lexical-shadow false positives and a weakened local-skipTest expectation | Replaced through stopped R1/R2 by current proposed B1B-R3; do not resume |
| `WS-QUAL-001-01B1B-R1` | Shared resolver measured 282 lines before its required behavior matrix, exceeding the 270 checkpoint and making the 300 cap infeasible | Replaced through stopped R2 by current proposed B1B-R3; no implementation draft retained |
| `WS-QUAL-001-01B1B-R2` | 348/350 candidate failed cycle-zero implementation review on standard lexical/control-flow cases with only two lines reserve | Superseded by proposed B1B-R3; do not repair in place |
