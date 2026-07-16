# Status: WS-CON-001 Contribution Record And Compensation Boundary

## Current status

Base planning and its AUTH-07B/AUTH-08 reconciliations passed earlier review.
The branch is now rebased onto trusted main `9a04434`, which merges ART-02A2 PR
#129 and includes AUTH-08 at `aa0fdcd`. The ART delta reconciliation passed
fresh architecture/senior/reuse, QA/product/docs and security/auth review after
repairing preparation timing, continuation custody, exact ART/AUTH gates and
D12 closed-owner parity. Application code is unchanged.
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
| `WS-CON-001-PLAN` | Reviewed; D11/D12 human gates | `codex/ws-con-001-plan` | - | Approved D2 removal remains split into 05A/05B; reviewed refresh records PR #129 as inactive ART preparation only, exact ART/AUTH prerequisites and ownership, and treats concurrent REV work as non-consumable discovery until merged. |
| `WS-CON-001-01` | Proposed | - | - | No runtime work. |
| `WS-CON-001-02A` through `11` | Proposed | - | - | Each requires separate explicit start; REV-13 owns final activation. |

## Blockers

| Blocker | Owner | Next action |
|---|---|---|
| Active-contract/archive handling approval | Human | Approve D1. |
| Legacy PaymentPolicy/task/assignment row handling | Human | Choose pre-production rebuild or an explicit classified backfill before 05A/05B; PaymentPolicy removal itself is approved. |
| Exact WS-CON executable authorization integration | WS-AUTH + human | Approve and implement registration, typed contexts/evaluators, matched authorities, grants/service assignments, prepared `T` protocol and active availability only in AUTH-owned chunks. |
| D11 AUTH/CON human-role conflicts | Human + WS-AUTH | Choose Operator delivery reconciliation, Project Manager award detail and WS-CON audit/export role sets. AUTH amends only chosen behavior that differs from its merged matrix; CON-01 updates the active contract before registration. |
| D12 ActionOwner/activation custody | Human + WS-AUTH | Approve exact AUTH-owned custody for 23 WS-CON, two coupled review and eleven existing ART-02D actions, or approve global feature-owner semantics plus a separate closed custody type with the same mappings. Do not register/activate with dual ownership. |
| Upstream `task.claim` ActionId is absent | WS-AUTH-001-13 or reviewed AUTH successor | Register/evaluate/activate `task.claim` against existing PermissionId before CON-05A integrates compensation freeze. |
| Contribution evidence typed capabilities | WS-ART + human | Create and approve the named `WS-ART-001-CON-EVIDENCE` write/read ports after 02D; write gates CON-09A, read gates CON-09B, and both gate CON-11. |
| ART provider/admission/verification/recovery chain remains incomplete | WS-ART + WS-AUTH | PR #129 supplies only 02A2 preparation. D12 must transfer all eleven ART-02D activation custodians; AUTH-09 must register fixed internal identities/assignments; ART must merge 02A3-02D hidden behavior; AUTH then separately activates Operator recovery and the three internal actions before the named contribution ports are ready. |
| ReviewLease/Review contracts | WS-REV | Merge owning persistence/behavior chunks at declared gates. |
| REV-06/08/10 authorization choreography predates the prepared-handle repair | WS-REV + WS-AUTH | Repair core claim/decision sites in REV-06/08 and final CON composition in REV-10 to AUTH registration -> CON capability/participant -> REV hidden planned-action composition -> AUTH activation; commit-bind and review before consumption. |
| Shared outbox | WS-CON-001-02A/B after approval | Land persistence and dispatcher before asynchronous integration. |
| REV reviewed baseline plus active external-review repairs remains non-consumable | WS-REV owner + human | Repair prepared authorization/activation choreography, D12 custody and dispatcher-owned outbox transitions, bind review, and merge; WS-CON does not pin the concurrent live worktree. |
| REV-12A draft assigns shared-outbox claim wording to the CON handler | WS-REV owner | Consume an already-claimed command and return a typed outcome; preserve CON-02B as sole outbox transition owner before sibling review/merge. |
| External publication | Human | Push or open a PR only after explicit direction; local review evidence does not authorize publication. |

## Follow-ups

| Item | Source | Priority |
|---|---|---:|
| Re-read merged AUTH kernel plus later AUTH-09/10 service/project-grant state and each WS-CON evaluator gate at activation. | Trusted `main` | P1 |
| Re-read REV contracts at CON-03C/06/07 activation. | Parallel worktree | P1 |
| Re-read merged ART v2/admission/verification and named capability ports before CON-09A; do not treat 02A2 preparation as capability readiness. | ADR 0013/spec/trusted main | P1 |
| Decide pre-production row rebuild vs classified backfill. | Migration risk | P1 |

## Stop condition

Do not edit runtime code or start `WS-CON-001-01` from this planning turn.
Present the plan, risks, and human decisions, then wait for explicit approval.
