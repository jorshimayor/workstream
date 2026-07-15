# Status: WS-CON-001 Contribution Record And Compensation Boundary

## Current status

Base planning and the latest merged AUTH-07A/active REV-12A delta
reconciliation have passed internal re-review. Application code is unchanged.
The reconciled working Markdown transcription, supplied generation-2 PDF,
original archival PDF, current backend, active docs, merged WS-AUTH
authorization catalogue, and active parallel WS-REV plan delta have been mapped.

The candidate cannot be canonically adopted as written because it conflicts
with `/api/v1`, the ActionId/PermissionId model, artifact-storage ownership and
providers, existing versioned `Submission`, and active payment architecture.

## Active chunk

`WS-CON-001-PLAN` only. The human approved complete PaymentPolicy removal on
2026-07-15. The latest AUTH/REV reconciliation and scanner-contract repair are
internally reviewed and bound to local evidence. No implementation is active.

## Chunk status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-CON-001-PLAN` | Internally reviewed | `codex/ws-con-001-plan` | - | Approved D2 removal is split into 05A/05B; the reviewed refresh records merged AUTH-07A/ADR 0014 foundations, exact archive-scanner ownership, and the active non-consumable REV-12A working delta atop `3e09e99`. |
| `WS-CON-001-01` | Proposed | - | - | No runtime work. |
| `WS-CON-001-02A` through `11` | Proposed | - | - | Each requires separate explicit start; REV-13 owns final activation. |

## Blockers

| Blocker | Owner | Next action |
|---|---|---|
| Active-contract/archive handling approval | Human | Approve D1. |
| Legacy PaymentPolicy/task/assignment row handling | Human | Choose pre-production rebuild or an explicit classified backfill before 05A/05B; PaymentPolicy removal itself is approved. |
| Exact WS-CON action registrations plus callback and shared-outbox service permissions | WS-AUTH + human | Approve dependency proposal; implement only in AUTH-owned chunk. |
| Contribution evidence typed capability | WS-ART + human | Create and approve the named `WS-ART-001-CON-EVIDENCE` prerequisite before CON-09A. |
| ReviewLease/Review contracts | WS-REV | Merge owning persistence/behavior chunks at declared gates. |
| Shared outbox | WS-CON-001-02A/B after approval | Land persistence and dispatcher before asynchronous integration. |
| REV-12A/13 joint scope is content-reviewed only as an uncommitted sibling delta atop `3e09e99` | WS-REV owner + human | Commit the exact repaired snapshot, run commit-bound freshness review, refresh against trusted main without losing the handoff, and merge; both surfaces stay hidden until its contract and later implementation gates land on trusted `main`. |
| REV-12A draft assigns shared-outbox claim wording to the CON handler | WS-REV owner | Consume an already-claimed command and return a typed outcome; preserve CON-02B as sole outbox transition owner before sibling review/merge. |
| External publication | Human | Push or open a PR only after explicit direction; local review evidence does not authorize publication. |

## Follow-ups

| Item | Source | Priority |
|---|---|---:|
| Re-read merged AUTH-07A catalogue plus later AUTH-07B/kernel/grant/service-actor state at each activation. | Trusted `main` | P1 |
| Re-read REV contracts at CON-03C/06/07 activation. | Parallel worktree | P1 |
| Re-read ART v2/capability ports before CON-09A. | ADR 0013/spec | P1 |
| Decide pre-production row rebuild vs classified backfill. | Migration risk | P1 |

## Stop condition

Do not edit runtime code or start `WS-CON-001-01` from this planning turn.
Present the plan, risks, and human decisions, then wait for explicit approval.
