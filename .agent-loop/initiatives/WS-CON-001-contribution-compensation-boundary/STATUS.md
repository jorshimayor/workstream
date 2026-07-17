# Status: WS-CON-001 Contribution Record And Compensation Boundary

## Current status

`WS-CON-001-PLAN` is reconciled and internally reviewed against trusted `main`
`5d353b6`, which merged WS-XINT-001 boundary reconciliation through PR #139.
The reviewed content commit is `c4242e0`; runtime code is unchanged and the
result remains local/unpublished.
The prior plan is superseded where it used the older policy aggregate, made ART
evidence mandatory, described service action rows as persisted assignments,
allowed partial activation-custody transfer, or let outbox dispatch imply
feature-handler authority.

## Corrected boundary

- ContributionPolicyVersion and ContributionRule decide award eligibility.
- Core Review -> ContributionRecord/Award is one PostgreSQL transaction with no
  ART call or evidence projection.
- Project grants are independently submitter/reviewer/adjudicator.
- Fixed services require closed ServiceIdentity, exact static matrix membership,
  provisioned ActorProfile/link, AUTH-09E admission, and active action.
- ActionOwner is AUTH activation custody. Complete ART/REV transfers are
  referenced from WS-XINT and not partially restated by CON.
- Outbox dispatch owns outbox mechanics only. Protected handlers need exact
  independent authority.
- CON-09A/09B are deferred optional successors and do not gate the core release.

## Active chunk

`WS-CON-001-PLAN` only. No implementation chunk is active.

| Chunk | Status | Notes |
|---|---|---|
| `WS-CON-001-PLAN` | Reconciled and internally reviewed; unpublished | Based on PR #139 / `5d353b6`; reviewed content `c4242e0` |
| `WS-CON-001-01` through `08B`, `10A` through `11` | Proposed | Separate explicit start required |
| `WS-CON-001-09A/09B` | Deferred optional | Separate approval and fresh ART/AUTH review required |

## Open gates

| Gate | Owner | Required action |
|---|---|---|
| Active specification/archive handling | Human | Approve CON-01 repository-owned specification |
| Pre-production legacy rows | Human | Choose deterministic rebuild or explicit classified migration before 05A/05B |
| D11 AdminRole candidates | Human + AUTH | Fix award-detail, delivery-recovery, and audit candidates before registration |
| Core WS-CON action registration/activation | AUTH | Add reviewed registration and later activation chunks; CON remains hidden |
| Fixed service runtime | AUTH | Complete AUTH-09A through 09E before protected service calls |
| Feature handler authority | Human + AUTH + CON | Approve exact identities/actions/static rows; no dispatcher inheritance |
| Repository loop-memory state | AUTH / merged-main owner | `check_loop_memory_state.py` currently fails on the unchanged AUTH status inherited from `origin/main`; WS-CON must not repair that external initiative file |
| task.claim | AUTH/task owner | Register/evaluate/activate with exact submitter grant before CON-05A |
| review.claim/review.decision | AUTH + REV + CON | Complete hidden participants/composition, full REV custody transfer, then AUTH activation |
| Shared outbox | CON-02A/B | Land generic persistence/dispatcher after approval |
| Joint release | REV + CON + AUTH | Consume exact hidden manifest; optional evidence and ART are not prerequisites |

## Stop condition

Do not edit runtime code, start CON-01, publish, push, or open a PR without
explicit human direction.
