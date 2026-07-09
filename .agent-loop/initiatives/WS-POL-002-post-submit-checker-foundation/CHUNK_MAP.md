# Chunk Map: WS-POL-002 - Post-Submit Checker Foundation

## Rule

Only one chunk may be active at a time. Do not start the next chunk until the
current chunk is implemented, verified, internally reviewed, externally
reviewed, merged by explicit human approval, and followed by a memory update.

## Chunks

| Chunk | Title | Risk | Status |
|---|---|---:|---|
| `WS-POL-002-01` | Post-Submit Provenance And Compiler Contract | L1 | Proposed |
| `WS-POL-002-02` | Post-Submit Derivation Agent And Resumable Setup Integration | L1 | Proposed |
| `WS-POL-002-03` | Server-Owned Policy Approval And Visibility APIs | L1 | Proposed |
| `WS-POL-002-04` | Locked Runtime Execution And Routing Hardening | L1 | Proposed |
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

After this planning chunk is reviewed, stop. The first implementation chunk is
inactive until the user explicitly starts `WS-POL-002-01`.
