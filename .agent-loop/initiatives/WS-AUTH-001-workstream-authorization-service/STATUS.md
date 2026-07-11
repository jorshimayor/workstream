# Status: WS-AUTH-001 - Workstream Authorization Service

## Current status

Planning and all required internal reviewer tracks passed after repair. The
initiative is stopped at the L0 human checkpoint: D1-D3 are approved; D4-D10
require explicit durable approval before implementation activation.

## Active planning chunk

`WS-AUTH-001-PLAN`

## Active implementation chunk

None.

## Current implementation branch

`authorization-service`

## Chunk status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-AUTH-001-PLAN` | Internally reviewed | `authorization-service` | - | L0 plan complete; D4-D10 human approval pending. |
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
`5739e1d6fc8df0fa620bd007c45e370530ac8d12`.

Production issuer configuration and legacy non-test actor classification are
future implementation/live-proof inputs and are tracked explicitly in
`DISCOVERY.md` and chunk stop conditions.
