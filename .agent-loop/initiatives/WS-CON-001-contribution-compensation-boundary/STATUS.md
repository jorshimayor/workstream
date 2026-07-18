# Status: WS-CON-001 Contribution Record And Compensation Boundary

## Current status

`WS-CON-001-01` merged through PR #144 at trusted-main SHA `e118e33`. The
generated post-merge state on `automation/loop-memory` was signature-verified
against that exact main SHA. The human explicitly started `WS-CON-001-02A` on
2026-07-18. CON-02A is now the only active chunk and is limited to generic
PostgreSQL outbox persistence plus append/replay in a caller-owned transaction.
It introduces no route, dispatcher, delivery executor, Celery registration,
protected handler, feature authority, contribution, compensation, review, or
artifact behavior. Trusted `main` then advanced through ART PR #141 at
`a10d901` and AUTH-09C PR #146 at `0ffdabf`. CON-02A now follows ART-owned
`0025_artifact_store_v2` with linear
`0026_shared_transactional_outbox`; ART's adapter, storage, startup, and
delivery-executor changes do not add an outbox seam or change this boundary.
AUTH-09C activates only the canonical administrative
`actor.profile.read`/`actor.identity_link.read` actions; it adds no CON or
outbox identifier and does not change 02A's authorization-neutral boundary.
Trusted `main` then advanced to `b2b9016` through REV-01 PR #145. Its canonical
review specification preserves the two ordered CON flush-only operations,
accept-only FinalAcceptance source, REV-owned single commit, and same-transaction
shared outbox staging. It adds no backend runtime or migration and therefore
does not change the 02A implementation boundary.
Trusted `main` then advanced to `f18b620` through REV-02 PR #147. That
planning-only merge splits future guide activation, ReviewPolicy/task
lifecycle, and submission attribution work into explicit REV chunks. It adds no
backend runtime, migration, or shared outbox behavior and leaves CON-02A
unchanged.

`WS-CON-001-PLAN3` completed its pre-external-review exact-SHA review at
`e968430b0c3b5f1432899c9aa31ef209b774eae0` after current-main reconciliation
with merged REV PR #128 at `0302bcf`, which also contains AUTH-09A after AUTH PR
#140. The prior planning snapshot `09128ee1aed941682c7cb59ca04698de496de682`
remains historical and no longer controls publication. The reviewed refresh
corrects the AUTH catalogue baseline, replaces the obsolete omnibus nullable CON
decision input with two ordered operations, and adopts REV-12A's exact
obligation-writer/ordinal/cutoff hooks. PLAN2's human-approved v0.1
`Review(accept) -> FinalAcceptance -> accepted_submission` boundary remains
intact. Runtime code is unchanged.
CodeRabbit then opened five consolidated contract-quality threads. PLAN3's
planning-only repair added executable verification gates, restored exact AUTH
prerequisite ownership, moved optional CON-09B to a deferred proposal, aligned
the PR trust bundle, and recorded the external response/review log. All required
tracks passed exact SHA `a69fad3a32ad47e3bd60a79cd75f5867eefc52b3`.
The prior plan is superseded where it used the older policy aggregate, made ART
evidence mandatory, described service action rows as persisted assignments,
allowed partial activation-custody transfer, or let outbox dispatch imply
feature-handler authority.
CON-01 then published the canonical active specification and ADR 0016. Internal
review required explicit `NUMERIC(38, 18)` and project-scoped unit semantics,
bounded/redacted immutable provider receipt facts, plus complete conformance
rows for adapter binding, lifecycle audit, and ADR 0014. Those findings were
repaired without changing runtime, CI, tests, dependencies, or archival inputs.
CodeRabbit then identified two contract ambiguities: the adapter-binding row
could imply forbidden reverse policy/award identifiers, and the receipt wording
did not distinguish authentication tokens from bounded non-secret receipt
identifiers. Both were corrected at `c027a4b`; all eight required internal tracks
passed the exact repaired SHA with no findings.
Before the human checkpoint, trusted `main` advanced to `053242b` through merged
AUTH-09B PR #143. CON-01 now adopts its controlled service-provisioning route,
74/65/10/55 catalogue baseline, and explicit separation between provisioning
and runtime service admission without changing the contribution lifecycle.
All eight required internal tracks passed the exact reconciled SHA `a6a88fb`
with no findings. Both prior CodeRabbit threads remain resolved and outdated.

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
  exact custody and prepared-protocol contracts remain upstream gates.
- Current main has 74 PermissionIds and 65 ActionIds: 12 active and 53 planned.
  AUTH-09B activates only `actor.service.provision`; AUTH-09C activates only
  `actor.profile.read` and `actor.identity_link.read`. These administrative
  capabilities grant no fixed-service runtime admission or feature authority.
  No CON or task-claim ActionId exists, and the current fixed identities are
  ART-only.
- `task.claim` activation must follow, not precede, the CON-05A hidden
  TaskAssignment contribution-policy freeze.
- Merged REV planning requires the CON reviewer operation before the decision
  branch and the accept-only submitter operation afterward; it rejects one
  nullable omnibus participant input.
- REV-12A requires every CON fulfillment-obligation writer to fence before
  monotonic ordinal allocation and requires same-session maximum-ordinal/drain
  observation for the immutable delivery cutoff.

## Active chunk

`WS-CON-001-02A` implementation and deterministic evidence are complete after
the explicit human start. It adds one linear migration, the shared outbox
model/schema/repository/service, metadata registration, and PostgreSQL-focused
migration/append tests. The exact isolated full suite passed 1347 tests in
4:55:41 with 85.35 percent repository coverage, and the outbox subsystem
reached 95 percent focused coverage. Required exact-SHA internal review and
external PR checks remain. It stops before dispatcher mechanics and CON-02B.

| Chunk | Status | Notes |
|---|---|---|
| `WS-CON-001-PLAN` | Complete; superseded baseline | Based on PR #139 / `5d353b6`; reviewed content `c4242e0` |
| `WS-CON-001-PLAN2` | Complete; unpublished | FinalAcceptance is REV-owned; CON trigger changes only; all required internal tracks pass |
| `WS-CON-001-PLAN3` | Complete; externally repaired and internally reviewed | CodeRabbit gates/AUTH scope/09B/trust repairs pass at `a69fad3` |
| `WS-CON-001-01` | Complete; merged | PR #144 merged at `e118e33` |
| `WS-CON-001-02A` | Deterministic evidence complete; review pending | Generic persistence/append only; exact-SHA internal review and PR checks remain |
| `WS-CON-001-02B` through `08B`, `10A` through `11` | Proposed | Separate explicit start required after predecessor merge and upstream refresh |
| `WS-CON-001-09A/09B` | Deferred optional | Separate approval and fresh ART/AUTH review required |

## Open gates

| Gate | Owner | Required action |
|---|---|---|
| FinalAcceptance and decision integration | REV + CON | REV-04 runtime persistence -> CON-03C; REV-09B lineage + CON-07 two-operation participant -> REV-10 hidden single-commit composition -> AUTH activation |
| Active specification/archive handling | Complete | CON-01 merged in PR #144; archival inputs remain untouched |
| Pre-production legacy rows | Human | Choose deterministic rebuild or explicit classified migration before 05A/05B |
| D11 AdminRole candidates | Human + AUTH | Fix award-detail, delivery-recovery, and audit candidates before registration |
| Core WS-CON action registration/activation | AUTH | Add reviewed registration and later activation chunks; CON remains hidden |
| Fixed service runtime | AUTH | AUTH-09A through 09C are merged; approve/register any new CON identity/static row, then complete AUTH-09D/09E before protected service calls |
| Feature handler authority | Human + AUTH + CON | Approve exact identities/actions/static rows; no dispatcher inheritance |
| AUTH prepared protocol | AUTH | Merge AUTH-PREP after AUTH-09E; all CON-sensitive mutations consume its exact opaque handle contract |
| task.claim | AUTH + task + CON | Only PermissionId exists; after AUTH-10/PREP and stable task seam, merge CON-05A freeze and task-owned composition; AUTH-13 enumerates/registers/evaluates/activates afterward |
| review.claim/review.decision | AUTH + REV + CON | Complete REV custody transfer and AUTH-PREP; merge hidden CON participants and REV composition; AUTH-REV-06/08 activate afterward |
| Shared outbox | CON-02A/B | Land generic persistence/dispatcher after approval |
| Joint release | REV + CON + AUTH | Consume exact hidden manifest; optional evidence and ART are not prerequisites |
| Fulfillment cutoff/drain | CON + REV-12A | CON-03D ordinal; all writer/dispatch/callback hooks; CON-10B observation; CON-11 manifest -> REV-12A shared fence/controller |

## Stop condition

Implement and review only CON-02A. Stop at its specific PR human checkpoint;
do not begin CON-02B, and do not merge without explicit approval for the
specific CON-02A PR.
