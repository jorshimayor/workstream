# Status: WS-QUAL-001 Backend Coverage Floor

## Current state

- Phase: `WS-QUAL-001-01B` circuit-breaker replan
- Branch: `codex/ws-qual-001-01b-coverage-policy-baseline`
- Authoritative target: 90 percent complete backend application statement coverage
- Diagnostic AUTH-02 baseline: 78.26 percent after database isolation repair
- Final reviewed planning SHA: `0d9dd987d546c864fa8de7bae462e5e73a1b5ea9`
- Final evidence-bound branch head: `3da1769882e9f6db4c48ef3dba33da8380e6a613`
- Planning merge commit: `9046d52f31c7c39f06e06c45c43783bb08a5181c`
- Internal review: PASS after cleanup, signal, authority, CI, and split repairs
- Active implementation chunk: none
- 01A implementation PR: `https://github.com/Flow-Research/workstream/pull/103` (merged)
- 01A final reviewed implementation SHA: `d1582ec64b9176c5ead62f695c7a23b48e4c72b9`
- 01A final evidence-bound branch head: `8cd7616b497ceb46d8359c25de689192632dfee8`
- 01A implementation merge commit: `2901a3ebe68b7c770ccb1ff06841d79ce0c20d94`
- 01A post-merge memory PR: `https://github.com/Flow-Research/workstream/pull/104` (merged)
- 01A post-merge memory commit: `8829a7ec3aa5199aae0aecbe5fda030c42a051cd`
- Planning PR: `https://github.com/Flow-Research/workstream/pull/99` (merged)
- 01A implementation base: `58d44596f614895964b82bb344e0ed98596eaae8`
- Start signal: explicit user start on 2026-07-12
- Split review: combined 01 rejected; 01A database boundary accepted for repair
- Measured whole-app coverage: 79.25 percent; artifact scope: 91.07 percent
- External review: seven CodeRabbit requests repaired and internally re-reviewed
  at `d1582ec64b9176c5ead62f695c7a23b48e4c72b9`
- Merge checks: Agent Gates, Backend, and CodeRabbit passed
- 01B start signal: explicit user instruction on 2026-07-12 after PR #104 merge
- 01B plan review: PASS at `7a16ee4e851b1b10315e32d3f81957acc56bf316`
- Circuit breaker: 480/500 implementation lines before configuration, workflow,
  runbook, and complete negative proof; executable draft removed
- Proposed split: 01B1 policy core, then 01B2 baseline/CI ratchet
- Next gate: internal split review and explicit human approval

## Stop condition

No implementation is authorized while the split is proposed. Do not start 01B1,
01B2, or chunk 02 automatically; AUTH remains paused until coverage completes.
