# Status: WS-AUTH-001 - Workstream Authorization Service

## Current status

Planning merged through PR #91 as
`ad6d6444e497b76d7cb925f3b0999ed4b74a3dac` after required internal reviews,
Agent Gates, and Backend passed. CodeRabbit produced a walkthrough with no
actionable findings, then its final check was cancelled when the PR closed. The
initiative is stopped at the L0 human checkpoint: D1-D3 are approved; D4-D10
require explicit durable approval before implementation.

## Checkpointed planning artifact

`WS-AUTH-001-PLAN` is merged and stopped at the L0 human checkpoint. No active
planning chunk is running.

## Active implementation chunk

None.

## Current implementation branch

None.

## Chunk status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-AUTH-001-PLAN` | Merged | `authorization-service` | #91 | Merged as `ad6d644`; D4-D10 human approval pending. |
| `WS-AUTH-001-01` | Proposed | - | - | Baseline adoption and repository contract reconciliation. |
| `WS-AUTH-001-02` | Proposed | - | - | Verified issuer token and JWKS boundary. |
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

None for planning closure.

`WS-AUTH-001-01` activation remains gated on explicit, durable human approval
of proposed architecture/data-model decisions D4-D10 and a separate
implementation start signal.

Internal review evidence is recorded at
`reviews/WS-AUTH-001-PLAN-internal-review-evidence.md` and binds reviewed SHA
`7aed967da8783eb78e13805d4de00efadc8d0391`.

Production issuer configuration and legacy non-test actor classification are
future implementation/live-proof inputs and are tracked explicitly in
`DISCOVERY.md` and chunk stop conditions.
