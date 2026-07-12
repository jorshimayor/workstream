# Status: WS-AUTH-001 - Workstream Authorization Service

## Current status

Planning merged through PR #91 as
`ad6d6444e497b76d7cb925f3b0999ed4b74a3dac` after required internal reviews,
Agent Gates, and Backend passed. CodeRabbit produced a walkthrough with no
actionable findings, then its final check was cancelled when the PR closed.
D4-D10 were explicitly approved and WS-AUTH-001-01 was started by the user on
2026-07-11. The final branch head `b5217e1` passed required internal reviews,
Agent Gates, Backend, and CodeRabbit, then merged through PR #93 as `772af1d` on
2026-07-11. `WS-AUTH-001-02` was later implemented off-main on
`codex/ws-auth-001-02-verified-issuer-token` but remains paused before
publication. It is not active and this memory update does not resume it.

## Active planning chunk

None.

## Active implementation chunk

None.

## Current implementation branch

No active implementation branch. The completed off-main `WS-AUTH-001-02`
implementation remains paused on
`codex/ws-auth-001-02-verified-issuer-token`.

## Chunk status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-AUTH-001-PLAN` | Merged | `authorization-service` | #91 | Merged as `ad6d644`; D4-D10 later approved. |
| `WS-AUTH-001-01` | Merged | `codex/ws-auth-001-01-adopt-authorization-baseline` | #93 | Authorization baseline, Contributor terminology boundary, scanner, and repository contracts; merged as `772af1d`. |
| `WS-AUTH-001-02` | Implemented off-main; paused | `codex/ws-auth-001-02-verified-issuer-token` | - | Do not publish until WS-QUAL completes its permanent 90% CI floor and final post-merge memory, then the user explicitly resumes AUTH. |
| `WS-AUTH-001-03` | Proposed | - | - | Legacy actor classification preflight. |
| `WS-AUTH-001-04` | Proposed | - | - | Request, error, and API control foundation. |
| `WS-AUTH-001-05` | Proposed | - | - | Authority evidence and idempotency foundation. |
| `WS-AUTH-001-06` | Proposed | - | - | Canonical actor profile and identity link. |
| `WS-AUTH-001-07` | Proposed | - | - | Authorization kernel and permissions. |
| `WS-AUTH-001-08` | Proposed | - | - | Bootstrap and administrative grants. |
| `WS-AUTH-001-09` | Proposed | - | - | Actor/link states and service actors. |
| `WS-AUTH-001-10` | Proposed | - | - | Project contributor grants. |
| `WS-AUTH-001-11` | Proposed | - | - | Project identity/guide/source/read cutover. |
| `WS-AUTH-001-12` | Proposed | - | - | Project policy/setup mutation cutover. |
| `WS-AUTH-001-13` | Proposed | - | - | Task management and assignment cutover. |
| `WS-AUTH-001-14` | Proposed | - | - | Submission/checker/audit visibility cutover. |
| `WS-AUTH-001-15` | Proposed | - | - | Remaining system worker and obsolete authority removal. |
| `WS-AUTH-001-16` | Proposed | - | - | Conformance and live proof. |

## Blockers

No blocker for the merged baseline chunk. `WS-AUTH-001-02` remains paused
before publication until WS-QUAL completes through its permanent 90 percent CI
floor and final post-merge memory, followed by a separate explicit user resume
signal.

Chunk review evidence is recorded at
`reviews/WS-AUTH-001-01-internal-review-evidence.md`; external review response
and PR trust evidence are recorded alongside it.

Production issuer configuration and legacy non-test actor classification are
future implementation/live-proof inputs and are tracked explicitly in
`DISCOVERY.md` and chunk stop conditions.
