# Status: WS-REV-001 Review And Revision Lifecycle

## Current status

Discovery, planning, and required internal plan review are complete on
`codex/ws-rev-001-plan`. No application implementation chunk is active.

The revised WS-REV Markdown and PDF have been read end to end and reconciled
structurally. Provenance records the current Markdown-only section 4.6 action
table rather than claiming the 52-page PDF is its generated twin. Current
backend, AUTH, ART, CON, task, checker, audit, worker,
migration, test, and documentation boundaries have been mapped.

The WS-CON planning package was reconciled and its content-reviewed state was
pinned at commit `42cf11f`; CON exact-commit publication review remains pending.
REV records the exact interleaving, canonical actor boundary,
PaymentPolicy-removal dependency, remaining digest/context and downgrade gates,
and joint REV-13 activation obligations without importing sibling code.

## Dependency state at discovery

- Current WS-REV worktree base: `f599551`, including merged AUTH-06 canonical
  actor profile. It is nine commits behind current `origin/main` during this
  planning audit; those commits establish the shared ADR-0014
  `ExternalServiceAdapter` foundation. Chunk 01 must refresh from trusted main
  without overwriting user-owned reference changes.
- WS-AUTH authorization kernel, grants, product cutovers, and final proof are
  still required before WS-REV runtime work.
- Clean AUTH-07A commit `3ab25cf` was reviewed as planning input: 74
  PermissionIds, 50 planned ActionIds, final contributor field names, and
  authority-loss revision reassignment. It remains unmerged and its 50 actions
  do not include REV's later revision-obligation-close, repair, or legacy-close
  additions.
- WS-ART provider-neutral v2, S3-compatible provider, admission/cutover,
  checker routing, recovery, and live proof are still required before review
  evidence integration.
- WS-CON policy freeze and atomic review transaction integration are not yet
  implemented. Its reviewed 05A/05B contracts remove PaymentPolicy completely;
  runtime work still waits for human approval, merged AUTH/ART dependencies,
  and the joint digest/context and downgrade gates.

These initiatives are being built in parallel. Their live merged contracts
must be re-read when each dependent WS-REV chunk is activated.

## Active chunk

`WS-REV-001-PLAN` only. After the 2026-07-15 human clarification, senior
engineering, QA/test, security/auth, product/ops, architecture, and reuse/dedup
final re-reviews pass. Documentation/spec adoption final re-review also passes.
Planning remains proposed until the remaining human decisions in
`INTENT.md` and the overall chunk sequence receive explicit approval.

## Human clarification recorded

- Keep ADR 0010 and one Project Guide context through the task pipeline.
- Same activated guide keeps the next-attempt context; any different current
  active guide, including an intentionally reactivated older guide, freezes a
  rebased next-attempt context before contributor access. The current active
  guide is authoritative.
- Reviewer uses the context stamped on the exact leased Submission and performs
  no separate guide rebase.
- LocalStorage remains the development provider, MinIO proves the S3 protocol in
  local/CI, and AWS S3 remains the production provider; Flow Node stays deferred.
- Reviewers retrieve only the active leased Submission packet through ART;
  submitters/reviewers receive bounded immutable chain history.
- Every Review creates reviewer contribution; only accept additionally creates
  the accepted Submission's submitter contribution through WS-CON.
- Human reviewer/submitter lineage uses canonical `ActorProfile.id`; service
  and system actors remain explicitly typed.
- Project Guide rebase never changes TaskAssignment or ReviewLease compensation
  freezes. Final revision context contains no legacy PaymentPolicy.

## Stop condition

Do not start `WS-REV-001-01` or any runtime implementation from this planning
turn. Present the plan, risks, and human decisions for discussion, then wait for
explicit approval.
