# Status: WS-POL-001 - Submission Artifact Policy Foundation

## Current Status

`WS-POL-001-01`, `WS-POL-001-02`, `WS-POL-001-03`, `WS-POL-001-04`, and
`WS-POL-001-05` are merged to `main`. `WS-POL-001-05` merged through PR #66 as
`b20988ba79626e1edbc03953aba60f54f2fc94ab` after deterministic verification,
internal reviewer fanout, GitHub Actions, and user merge approval.

`WS-POL-001-06` is active. It uses real Terminal Benchmark reviewer fixture
material as an external-project proof for the current Workstream setup-agent,
policy bundle, and submission/checker lifecycle. The live manual API proof
passed after fixing a narrow OpenAI Agents SDK adapter issue. Final verification
and internal reviewer re-check are in progress. It must not make Terminal
Benchmark a Workstream product dependency.

## Active Chunk

`WS-POL-001-06` - Terminal Benchmark Real Fixture Drill

## Chunk Status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-POL-001-01` | Merged | `codex/ws-pol-001-01-submission-artifact-policy` | 28 | Implements guide-source snapshots, guide sufficiency reports, submission artifact policy, effective project policy, project pre-submit checker contract, activation guards, and key-based artifact policy merge. |
| `WS-POL-001-02` | Merged | `codex/ws-pol-001-02-agent-runtime-compiler` | 61 | Adds async guide sufficiency / derivation agents, runtime port, OpenAI Agents SDK adapter boundary, trusted compiler path, and server-owned provenance guards. |
| `WS-POL-001-03` | Merged | `codex/ws-pol-001-03-task-locked-context` | 63 | Moves task locked-context and submission runtime to the effective policy and project checker bundle. |
| `WS-POL-001-04` | Merged | `codex/ws-pol-001-04-post-submit-policy` | 65 | Splits post-submit checker policy provenance and locks durable checker runs to post-submit policy context. |
| `WS-POL-001-05` | Merged | `codex/ws-pol-001-05-revision-resubmission` | 66 | Proves revision resubmission, real API drill, and `evaluation_pending` lifecycle status. |
| `WS-POL-001-06` | Final verification and internal review re-check | `codex/ws-pol-001-06-terminal-benchmark-drill` | - | Runs the Terminal Benchmark manual live API proof and fixes the OpenAI Agents SDK policy-derivation adapter issue found by the proof. |

## Blockers

| Blocker | Owner | Next action |
|---|---|---|
| None | - | Complete internal review re-check, then open PR. |

## Follow-Ups

| Item | Source | Priority |
|---|---|---|
| Add public revision lifecycle coverage instead of direct `needs_revision` test setup | Test-delta review | High for `WS-POL-001-05` |
| Add focused `0007 -> 0006` downgrade assertion for locked-context columns and constraints | QA/test-delta review | Medium follow-up |
| Extract shared artifact path and forbidden-pattern helpers before further checker-policy expansion | Reuse/dedup review | Medium follow-up |
