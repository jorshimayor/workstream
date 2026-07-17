# Status: WS-CON-001 Contribution Record And Compensation Boundary

## Current status

`WS-CON-001-PLAN3` is reconciling merged AUTH PR #140 at trusted main
`d541521` with the previously reviewed CON plan. PLAN2 already reconciled the
human-approved v0.1
`Review(accept) -> FinalAcceptance -> accepted_submission` boundary against the
previously reviewed WS-XINT plan. Runtime code is unchanged. The addendum passed
architecture, QA/product/test-delta, and security/auth review on 2026-07-17 and
remains unpublished pending human direction.
The prior plan is superseded where it used the older policy aggregate, made ART
evidence mandatory, described service action rows as persisted assignments,
allowed partial activation-custody transfer, or let outbox dispatch imply
feature-handler authority.

## Corrected boundary

- ContributionPolicyVersion and ContributionRule decide award eligibility.
- Core Review -> ContributionRecord/Award is one PostgreSQL transaction with no
  ART call or evidence projection.
- REV creates FinalAcceptance only for accept. Reviewer contributions source
  Review directly; submitter contributions source FinalAcceptance only.
- Shipping authority uses exact submitter and reviewer grants only; unrelated
  grants do not substitute and WS-CON has no adjudication dependency.
- Fixed services require closed ServiceIdentity, exact static matrix membership,
  provisioned ActorProfile/link, AUTH-09E admission, and active action.
- ActionOwner is AUTH activation custody. Complete ART/REV transfers are
  referenced from WS-XINT and not partially restated by CON.
- Outbox dispatch owns outbox mechanics only. Protected handlers need exact
  independent authority.
- CON-09A/09B are deferred optional successors and do not gate the core release.
- AUTH PR #140 registers no CON ActionId and activates no feature action. Its
  exact custody and prepared-protocol contracts are now upstream gates.
- `task.claim` activation must follow, not precede, the CON-05A hidden
  TaskAssignment contribution-policy freeze.

## Active chunk

`WS-CON-001-PLAN3` only. No implementation chunk is active.

| Chunk | Status | Notes |
|---|---|---|
| `WS-CON-001-PLAN` | Complete; superseded baseline | Based on PR #139 / `5d353b6`; reviewed content `c4242e0` |
| `WS-CON-001-PLAN2` | Complete; unpublished | FinalAcceptance is REV-owned; CON trigger changes only; all required internal tracks pass |
| `WS-CON-001-PLAN3` | Reconciliation and internal review in progress | AUTH PR #140 exact PREP/custody/activation sequencing only |
| `WS-CON-001-01` through `08B`, `10A` through `11` | Proposed | Separate explicit start required after PLAN3 and upstream merge refresh |
| `WS-CON-001-09A/09B` | Deferred optional | Separate approval and fresh ART/AUTH review required |

## Open gates

| Gate | Owner | Required action |
|---|---|---|
| FinalAcceptance and decision integration | REV + CON | Merge REV-owned persistence and locked lineage first; then CON-03C/07; then REV consumes CON-07 in hidden single-commit composition before AUTH activation |
| Active specification/archive handling | Human | Approve CON-01 repository-owned specification |
| Pre-production legacy rows | Human | Choose deterministic rebuild or explicit classified migration before 05A/05B |
| D11 AdminRole candidates | Human + AUTH | Fix award-detail, delivery-recovery, and audit candidates before registration |
| Core WS-CON action registration/activation | AUTH | Add reviewed registration and later activation chunks; CON remains hidden |
| Fixed service runtime | AUTH | Complete AUTH-09A through 09E before protected service calls |
| Feature handler authority | Human + AUTH + CON | Approve exact identities/actions/static rows; no dispatcher inheritance |
| AUTH prepared protocol | AUTH | Merge AUTH-PREP after AUTH-09E; all CON-sensitive mutations consume its exact opaque handle contract |
| task.claim | AUTH + task + CON | Only PermissionId exists; after AUTH-10/PREP and stable task seam, merge CON-05A freeze and task-owned composition; AUTH-13 enumerates/registers/evaluates/activates afterward |
| review.claim/review.decision | AUTH + REV + CON | Complete REV custody transfer and AUTH-PREP; merge hidden CON participants and REV composition; AUTH-REV-06/08 activate afterward |
| Shared outbox | CON-02A/B | Land generic persistence/dispatcher after approval |
| Joint release | REV + CON + AUTH | Consume exact hidden manifest; optional evidence and ART are not prerequisites |

## Stop condition

Do not edit runtime code, start CON-01, push, open, or merge a PR without
explicit human direction. PLAN3 may prepare its trust bundle and merge intent
for review readiness only.
