# Status: WS-REV-001 Review And Revision Lifecycle

## Current status

Discovery, planning, and fresh internal plan review are complete on
`codex/ws-rev-001-plan`. No application implementation chunk is active.

The revised WS-REV Markdown and PDF have been read end to end and reconciled
structurally. Provenance records the current Markdown-only section 4.6 action
table rather than claiming the 52-page PDF is its generated twin. Current
backend, AUTH, ART, CON, task, checker, audit, worker,
migration, test, and documentation boundaries have been mapped.

The WS-CON planning package was reconciled at rebased committed head `c965f9b`;
its content-review lineage comes from `42cf11f`. Later uncommitted sibling
fence-handoff edits were read as discovery evidence but are not treated as
merged contracts. REV records the
exact interleaving, canonical actor boundary,
PaymentPolicy-removal dependency, remaining digest/context and downgrade gates,
and joint REV-13 activation obligations without importing sibling code.

## Dependency state at discovery

- Current WS-REV HEAD `3e09e99` contains trusted main `e9d72a1`; the pull was a
  clean merge and retained every user-owned reference change. Main now includes
  merged AUTH-07A plus the shared ADR-0014 `ExternalServiceAdapter` foundation.
- WS-AUTH authorization kernel, grants, product cutovers, and final proof are
  still required before WS-REV runtime work.
- Merged AUTH-07A commit `3ab25cf` was reviewed as planning input: 74
  PermissionIds, 50 registered planned ActionIds, final contributor field names, and
  authority-loss revision reassignment. Its 50 actions
  do not include REV's later revision-obligation-close, repair, legacy-close, or
  lifecycle-activation additions; AUTH must migrate exact audit parity to 54.
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

`WS-REV-001-PLAN` only. Earlier post-clarification reviewer passes remain
historical evidence. After the main pull, the AUTH/CON reconciliation and new
12A joint release-control contract received fresh senior engineering, QA/test,
security/auth, product/ops, architecture, docs, and reuse/dedup review. Every
track passes after fixes with no residual blocking finding. Planning is
human-approved for PR publication. D6, reviewer-current precedence, coherent
joint activation, and the overall chunk sequence were approved on 2026-07-15.

The internal-review evidence file is complete at the reviewer/content level.
Publication binds that evidence to the approved planning commit and verifies
SHA freshness before the branch is pushed. User-owned reference-file changes
remain outside this chunk and outside its publication commits.

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

Publish only `WS-REV-001-PLAN`. Do not start `WS-REV-001-01` or runtime
implementation in this PR; the merge intent requires a separate post-merge
start gate.
