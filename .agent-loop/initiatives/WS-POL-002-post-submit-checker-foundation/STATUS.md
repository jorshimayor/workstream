# Status: WS-POL-002 - Post-Submit Checker Foundation

## Current Status

Planning completed and merged through PR #85 as
`3fc1a688743f13476d6092078d40792592823d27`.

`WS-POL-002-01` merged through PR #87 as `ed52c21` on 2026-07-09. It
implemented the version-stamped trusted post-submit compiler contract,
default-checker snapshot validation, canonical policy hashing, and tests around
default-drift safety.

`WS-POL-002-02` is active after the user's explicit start signal. Its
implementation, deterministic proof, internal reviewer fanout, internal review
evidence, and PR trust bundle are refreshed for `fa7afaf`. PR #88 is open; the
current gate is external checks and human checkpoint after the latest push.

## Active Planning Chunk

None.

## Active Implementation Chunk

`WS-POL-002-02` - Post-Submit Derivation Agent And Resumable Setup Integration.

## Current Implementation Branch

`codex/ws-pol-002-02-post-submit-derivation`

## Chunk Status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-POL-002-PLAN` | Merged | `codex/ws-pol-002-post-submit-checker-planning` | #85 | Defines intent, discovery, design, risks, decisions, and implementation chunks. |
| `WS-POL-002-01` | Merged | `codex/ws-pol-002-01-post-submit-compiler` | #87 | Post-Submit Compiler Contract; merged as `ed52c21`. |
| `WS-POL-002-02` | Active | `codex/ws-pol-002-02-post-submit-derivation` | #88 | Post-submit derivation agent and resumable setup integration after pre-submit approval/compile; external checks must rerun on latest evidence refresh. |
| `WS-POL-002-03` | Proposed | - | - | Server-owned approval and setup visibility APIs for compiled post-submit policies. |
| `WS-POL-002-04` | Proposed | - | - | Runtime hardening for locked post-submit policy execution and routing. |
| `WS-POL-002-05` | Proposed | - | - | Terminal Benchmark-style live API proof and report. |

## Blockers

| Blocker | Owner | Next action |
|---|---|---|
| none | none | none |
