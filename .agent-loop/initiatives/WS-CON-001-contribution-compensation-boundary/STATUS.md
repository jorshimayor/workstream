# Status: WS-CON-001 Contribution Record And Compensation Boundary

## Current status

Base planning passed its earlier review. The latest merged AUTH-07B executable
kernel reconciliation and resulting AUTH/CON activation-boundary repair passed
fresh internal review. Application code is unchanged.
The reconciled working Markdown transcription, supplied generation-2 PDF,
original archival PDF, current backend, active docs, merged WS-AUTH
authorization catalogue, and active parallel WS-REV plan delta have been mapped.

The candidate cannot be canonically adopted as written because it conflicts
with `/api/v1`, the ActionId/PermissionId model, artifact-storage ownership and
providers, existing versioned `Submission`, and active payment architecture.

## Active chunk

`WS-CON-001-PLAN` only. The human approved complete PaymentPolicy removal on
2026-07-15. AUTH-07B proves that registration alone is not activation, so the
plan now makes typed evaluators, principal truth, active availability and a
prepared cross-domain mutation protocol AUTH-owned prerequisites. No
implementation is active.

## Chunk status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-CON-001-PLAN` | Reviewed; human approval gate | `codex/ws-con-001-plan` | - | Approved D2 removal remains split into 05A/05B; reviewed refresh records merged AUTH-07B at `90eca12`, exact AUTH executable gates, archive-scanner ownership, and non-consumable REV head `e59e2bb`. |
| `WS-CON-001-01` | Proposed | - | - | No runtime work. |
| `WS-CON-001-02A` through `11` | Proposed | - | - | Each requires separate explicit start; REV-13 owns final activation. |

## Blockers

| Blocker | Owner | Next action |
|---|---|---|
| Active-contract/archive handling approval | Human | Approve D1. |
| Legacy PaymentPolicy/task/assignment row handling | Human | Choose pre-production rebuild or an explicit classified backfill before 05A/05B; PaymentPolicy removal itself is approved. |
| Exact WS-CON executable authorization integration | WS-AUTH + human | Approve and implement registration, typed contexts/evaluators, matched authorities, grants/service assignments, prepared `T` protocol and active availability only in AUTH-owned chunks. |
| Upstream `task.claim` ActionId is absent | WS-AUTH-001-13 or reviewed AUTH successor | Register/evaluate/activate `task.claim` against existing PermissionId before CON-05A integrates compensation freeze. |
| Contribution evidence typed capability | WS-ART + human | Create and approve the named `WS-ART-001-CON-EVIDENCE` prerequisite before CON-09A. |
| ReviewLease/Review contracts | WS-REV | Merge owning persistence/behavior chunks at declared gates. |
| REV-06/10 authorization choreography predates AUTH-07B repair | WS-REV + WS-AUTH | Refresh sibling contracts to AUTH registration -> CON participant -> REV hidden planned-action composition -> AUTH activation; commit-bind and review before consumption. |
| Shared outbox | WS-CON-001-02A/B after approval | Land persistence and dispatcher before asynchronous integration. |
| REV-12A/13 joint plan is committed at sibling merge head `e59e2bb` but stale | WS-REV owner + human | Repair outbox claim ownership and AUTH/CON freshness evidence against `90eca12`, rerun commit-bound review, and merge; both surfaces stay hidden meanwhile. |
| REV-12A draft assigns shared-outbox claim wording to the CON handler | WS-REV owner | Consume an already-claimed command and return a typed outcome; preserve CON-02B as sole outbox transition owner before sibling review/merge. |
| External publication | Human | Push or open a PR only after explicit direction; local review evidence does not authorize publication. |

## Follow-ups

| Item | Source | Priority |
|---|---|---:|
| Re-read merged AUTH kernel plus later AUTH-08/09/10 grants/service-actor state and each WS-CON evaluator gate at activation. | Trusted `main` | P1 |
| Re-read REV contracts at CON-03C/06/07 activation. | Parallel worktree | P1 |
| Re-read ART v2/capability ports before CON-09A. | ADR 0013/spec | P1 |
| Decide pre-production row rebuild vs classified backfill. | Migration risk | P1 |

## Stop condition

Do not edit runtime code or start `WS-CON-001-01` from this planning turn.
Present the plan, risks, and human decisions, then wait for explicit approval.
