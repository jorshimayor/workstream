# Status: WS-CON-001 Contribution Record And Compensation Boundary

## Current status

Planning amendment under internal review. Application code is unchanged. The supplied revised Markdown/PDF,
original archival PDF, current backend, active docs, parallel WS-AUTH
authorization catalogue, and parallel WS-REV plan have been mapped.

The candidate cannot be canonically adopted as written because it conflicts
with `/api/v1`, the ActionId/PermissionId model, artifact-storage ownership and
providers, existing versioned `Submission`, and active payment architecture.

## Active chunk

`WS-CON-001-PLAN` only. The human approved complete PaymentPolicy removal on
2026-07-15; the resulting plan amendment requires reviewer closure. No
implementation is active.

## Chunk status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-CON-001-PLAN` | D2 removal amendment review pending | `codex/ws-con-001-plan` | - | Prior review predates the approved removal direction. |
| `WS-CON-001-01` | Proposed | - | - | No runtime work. |
| `WS-CON-001-02A` through `11` | Proposed | - | - | Each requires separate explicit start; REV-13 owns final activation. |

## Blockers

| Blocker | Owner | Next action |
|---|---|---|
| Active-contract/archive handling approval | Human | Approve D1. |
| PaymentPolicy/CompensationPolicy authority relationship | Human | D2 approved: complete removal; only legacy reset/backfill rule remains. |
| Exact WS-CON action registrations plus callback and shared-outbox service permissions | WS-AUTH + human | Approve dependency proposal; implement only in AUTH-owned chunk. |
| Contribution evidence typed capability | WS-ART + human | Create and approve the named `WS-ART-001-CON-EVIDENCE` prerequisite before CON-09A. |
| ReviewLease/Review contracts | WS-REV | Merge owning persistence/behavior chunks at declared gates. |
| Shared outbox | WS-CON-001-02A/B after approval | Land persistence and dispatcher before asynchronous integration. |
| Current REV-13 scope omits the joint CON surface/docs/drill | WS-REV owner + human | Incorporate and review `JOINT_RELEASE_HANDOFF.md`; both surfaces stay hidden until then. |
| Exact-head evidence gate requires a committed candidate | Primary agent after human publication direction | Do not claim PR readiness; commit only when authorized, rerun reviewers, and require the gate to pass. |

## Follow-ups

| Item | Source | Priority |
|---|---|---:|
| Re-read AUTH-07A/07B and later merged catalogue at each activation. | Parallel worktree | P1 |
| Re-read REV contracts at CON-03C/06/07 activation. | Parallel worktree | P1 |
| Re-read ART v2/capability ports before CON-09A. | ADR 0013/spec | P1 |
| Decide pre-production row rebuild vs classified backfill. | Migration risk | P1 |

## Stop condition

Do not edit runtime code or start `WS-CON-001-01` from this planning turn.
Present the plan, risks, and human decisions, then wait for explicit approval.
