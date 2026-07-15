# Status: WS-REV-001 Review And Revision Lifecycle

## Current status

Discovery and planning are complete on `codex/ws-rev-001-plan`. An AUTH-07B
dependency refresh is complete; the final planning publication refresh remains
parked while ART PR #129 is conflict-blocked and until it refreshes from main
and merges. No application implementation chunk is active.

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

## Dependency state at latest refresh

- Local pull merge `e59e2bb` contains trusted main `90eca12`, including merged
  AUTH-07B and the shared ADR-0014 `ExternalServiceAdapter` foundation. The pull
  was conflict-free and retained every user-owned reference change.
- AUTH-07B installs the request-scoped deny-by-default kernel and activates only
  `actor.profile.read_self` and `actor.profile.update_self`. The merged catalogue
  remains 74 PermissionIds and 50 ActionIds: 2 active and 48 planned. All 20
  existing revised-spec submission/review actions remain planned, and the four
  later REV additions remain absent, so all 24 REV dependencies are inactive.
- WS-AUTH grants, actor/service administration, product cutovers, the four-action
  57-to-61 parity migration, and final proof are still required before WS-REV
  runtime work. AUTH-08 is amended but unmerged; after its expected 57-action
  state (9 active, 48 planned), the four REV additions produce 61 actions (9
  active, 52 planned) while all 24 REV dependencies remain inactive.
- AUTH-07B cannot yet be consumed by REV: its generic dependency teardown can
  commit any open shared-session transaction, authorization-evidence SQL errors
  are not consistently mapped to retryable 503 responses, and the cut-over
  actor-self routes no longer advance canonical verification timestamps. AUTH
  owns those repairs and their PostgreSQL/API regression proof.
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
historical evidence. After the first main pull, the AUTH/CON reconciliation and new
12A joint release-control contract received fresh senior engineering, QA/test,
security/auth, product/ops, architecture, docs, and reuse/dedup review. Every
track passes after fixes with no residual blocking finding. Planning is
human-approved for PR publication. D6, reviewer-current precedence, coherent
joint activation, and the overall chunk sequence were approved on 2026-07-15.

The previous internal-review evidence is bound to approved planning commit
`706158d8078da508eb022749fb011db5725a45ef`. The later AUTH-07B/main merge and
dependency repair deliberately make that publication binding stale. Evidence
will be re-reviewed and rebound only after ART PR #129 merges and the final
dependency refresh is complete. The supplied revised reference contents are now
restored to the canonical Markdown/PDF filenames with matching checksum
metadata; the accidental `(2)` paths are removed.

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

Do not push a refreshed `WS-REV-001-PLAN` while ART PR #129 remains
conflict-blocked or until its merged contracts are reconciled. Do not start
`WS-REV-001-01` or runtime implementation; the merge intent requires a separate
post-merge start gate.
