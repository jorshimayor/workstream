# Status: WS-CON-001 Contribution Record And Compensation Boundary

## Current status

Base planning and its AUTH-07B reconciliation passed earlier review. The branch
is now rebased onto merged AUTH-08 at `aa0fdcd`; the resulting catalogue,
AdminRoleGrant, decision-evidence, transaction, ActionOwner and role-matrix
delta passed fresh internal review. Application code is unchanged.
The reconciled working Markdown transcription, supplied generation-2 PDF,
original archival PDF, current backend, active docs, merged WS-AUTH
authorization catalogue, and active parallel WS-REV plan delta have been mapped.

The candidate cannot be canonically adopted as written because it conflicts
with `/api/v1`, the ActionId/PermissionId model, artifact-storage ownership and
providers, existing versioned `Submission`, and active payment architecture.

## Active chunk

`WS-CON-001-PLAN` only. The human approved complete PaymentPolicy removal on
2026-07-15. AUTH-08 proves that durable grant and permission candidacy still do
not activate a WS-CON action, so the plan keeps typed evaluators, exact per-
action role filters, principal truth, active availability and a prepared cross-
domain mutation protocol AUTH-owned. No implementation is active.

## Chunk status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-CON-001-PLAN` | Reviewed; D11/D12 human gates | `codex/ws-con-001-plan` | - | Approved D2 removal remains split into 05A/05B; reviewed refresh records merged AUTH-08 at `aa0fdcd`, unresolved D11/D12 decisions, exact AUTH executable gates, archive-scanner ownership, and clean but non-consumable REV head `a13bf35`. |
| `WS-CON-001-01` | Proposed | - | - | No runtime work. |
| `WS-CON-001-02A` through `11` | Proposed | - | - | Each requires separate explicit start; REV-13 owns final activation. |

## Blockers

| Blocker | Owner | Next action |
|---|---|---|
| Active-contract/archive handling approval | Human | Approve D1. |
| Legacy PaymentPolicy/task/assignment row handling | Human | Choose pre-production rebuild or an explicit classified backfill before 05A/05B; PaymentPolicy removal itself is approved. |
| Exact WS-CON executable authorization integration | WS-AUTH + human | Approve and implement registration, typed contexts/evaluators, matched authorities, grants/service assignments, prepared `T` protocol and active availability only in AUTH-owned chunks. |
| D11 AUTH/CON human-role conflicts | Human + WS-AUTH | Choose Operator delivery reconciliation, Project Manager award detail and WS-CON audit/export role sets. AUTH amends only chosen behavior that differs from its merged matrix; CON-01 updates the active contract before registration. |
| D12 ActionOwner/activation custody | Human + WS-AUTH | Approve the exact AUTH-owned activation owners in the handoff, or approve a global feature-owner semantic plus a separate activation-custody type. Do not register/activate with dual ownership. |
| Upstream `task.claim` ActionId is absent | WS-AUTH-001-13 or reviewed AUTH successor | Register/evaluate/activate `task.claim` against existing PermissionId before CON-05A integrates compensation freeze. |
| Contribution evidence typed capability | WS-ART + human | Create and approve the named `WS-ART-001-CON-EVIDENCE` prerequisite before CON-09A. |
| ReviewLease/Review contracts | WS-REV | Merge owning persistence/behavior chunks at declared gates. |
| REV-06/10 authorization choreography predates AUTH-07B repair | WS-REV + WS-AUTH | Refresh sibling contracts to AUTH registration -> CON participant -> REV hidden planned-action composition -> AUTH activation; commit-bind and review before consumption. |
| Shared outbox | WS-CON-001-02A/B after approval | Land persistence and dispatcher before asynchronous integration. |
| REV committed head `a13bf35` remains non-consumable | WS-REV owner + human | Preserve its AUTH-08 refresh, then repair CON review choreography, D12 custody and outbox claim ownership; wait for ART, bind final publication review, and merge. |
| REV-12A draft assigns shared-outbox claim wording to the CON handler | WS-REV owner | Consume an already-claimed command and return a typed outcome; preserve CON-02B as sole outbox transition owner before sibling review/merge. |
| External publication | Human | Push or open a PR only after explicit direction; local review evidence does not authorize publication. |

## Follow-ups

| Item | Source | Priority |
|---|---|---:|
| Re-read merged AUTH kernel plus later AUTH-09/10 service/project-grant state and each WS-CON evaluator gate at activation. | Trusted `main` | P1 |
| Re-read REV contracts at CON-03C/06/07 activation. | Parallel worktree | P1 |
| Re-read ART v2/capability ports before CON-09A. | ADR 0013/spec | P1 |
| Decide pre-production row rebuild vs classified backfill. | Migration risk | P1 |

## Stop condition

Do not edit runtime code or start `WS-CON-001-01` from this planning turn.
Present the plan, risks, and human decisions, then wait for explicit approval.
