# STATUS: WS-ENG-001

## Current

- `WS-ENG-001-01`: merged through PR #23 on 2026-06-20; complete
- `WS-ENG-001-02`: merged through PR #122 as `fc89fb6`; complete
- `WS-ENG-001-03`: corrective schema-v2 contract for initiative-local next gates
- `WS-ENG-001-04A`: planning/specification and all nine internal reviewer tracks
  pass after repair; implementation has not started
- `WS-ENG-001-04B`: proposed only; requires 04A merge/replay and a separate start
- Current gate: explicit human approval to implement reviewed 04A contract
- Product runtime: unchanged

## Last Update

The first live generated state proved signing, protected-main freshness, and
workflow isolation, but exposed that schema v1 allowed `WS-ENG-001-02` to name
`WS-AUTH-001-06` as a global next chunk. The corrective chunk makes successor
authority initiative-local, rejects schema v1 without compatibility, and
rebootstraps generated state at schema v2. No artifact, authorization, or other
Workstream product runtime is active in this engineering chunk.

## Next Required Event

Stop for explicit human approval before changing workflow or generator code.
AUTH ART custody merged through PR #158 and REV custody merged through PR #160
while this plan was under review. Live replay must bind dynamically to current
protected `main`; those transitions remain historical regression fixtures.
