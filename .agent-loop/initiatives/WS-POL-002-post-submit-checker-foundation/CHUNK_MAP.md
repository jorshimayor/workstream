# Chunk Map: WS-POL-002 - Post-Submit Checker Foundation

## Rule

Only one chunk may be active at a time. Do not start the next chunk until the
current chunk is implemented, verified, internally reviewed, externally
reviewed, merged by explicit human approval, and followed by a memory update.

## Chunks

| Chunk | Title | Risk | Status |
|---|---|---:|---|
| `WS-POL-002-01` | Post-Submit Compiler Contract | L1 | Merged |
| `WS-POL-002-02` | Post-Submit Derivation Agent And Resumable Setup Integration | L1 | Merged |
| `WS-POL-002-03` | Server-Owned Policy Approval And Visibility APIs | L1 | Implemented separately; PR #90 in external review |
| `WS-POL-002-04` | Locked Runtime Execution And Routing Hardening | L1 | Inactive pending PR #90 merge, auth proof, and explicit start |
| `WS-POL-002-05` | Terminal Benchmark Post-Submit Live API Proof | L1 | Proposed |

## Dependency Order

```text
WS-POL-002-01
-> WS-POL-002-02
-> WS-POL-002-03
-> WS-POL-002-04
-> WS-POL-002-05
```

## Stop Condition

After each implementation chunk is reviewed, externally checked, and merged by
explicit human approval, perform the memory update before starting the next
chunk.

PR #90 owns chunk 03 independently. Do not start chunk 04 automatically.
