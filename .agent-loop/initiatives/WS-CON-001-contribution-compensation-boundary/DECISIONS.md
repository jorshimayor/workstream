# Decisions: WS-CON-001 Contribution Record And Compensation Boundary

## D1 - Preserve Reference Generations; Reconcile Active Contract

**Status:** recommended; human approval required.

Preserve supplied PDFs as immutable source generations. Treat the Markdown as
an explicitly editable reconciled working transcription derived from the
generation-2 PDF, record its current hash after every reviewed reconciliation,
and never claim it is byte-identical to the PDF. CON-01 creates
`docs/spec_contribution_compensation.md` plus an ADR as the active normative
repository contract.

Rejected: silently replacing a PDF generation, claiming the reconciled
Markdown is archival, or treating a candidate as executable merely because it
says “locked.”

## D2 - One Executable Compensation Authority

**Status:** approved by the human on 2026-07-15.

`CompensationPolicyVersion` supersedes and completely replaces `PaymentPolicy`.
The `PaymentPolicy` model/table, project-guide request/response fields,
repository/service methods, task/submission/checker locked-version fields,
copied amount/currency/payout fields, constraints, imports, tests, active docs,
templates, diagrams and operations language are removed. No compatibility
alias, dormant historical model, dual write/read, automatic conversion, or
fallback is retained.

CON-05A atomically cuts every semantic consumer to the replacement: project
guide activation stops requiring PaymentPolicy, Finance-published
CompensationPolicyVersion becomes the only task-claim economic prerequisite,
and TaskAssignment freezes it. Old columns/table may remain physically present
but are unreachable and write-blocked only until CON-05B drops them. CON-05B
owns physical schema/model removal and a zero-consumer scanner. Ambiguous legacy
rows fail migration; the exact reset-versus-classified-backfill rule remains a
separate human gate before CON-05A.

Rejected: advisory retention, historical quote APIs, dual execution, silent
unpaid behavior, or rewriting legacy values into compensation terms by guess.

## D3 - Existing Submission Is The Versioned Identity

**Status:** accepted by repository evidence and parallel WS-REV plan.

Use `backend/app/modules/tasks/models.py::Submission` and its `version`/
`supersedes_submission_id` chain. WS-CON creates no `SubmissionVersion` table.

## D4 - ActionIds Do Not Replace PermissionIds

**Status:** separation accepted; all WS-CON actions and service permissions are
proposed dependencies requiring human approval and AUTH registration.

WS-CON declares granular proposed ActionIds mapped to existing stable
PermissionIds when semantically safe. AUTH owns registration, audit migration,
grants/service actors, and kernel behavior; the named feature chunk owns
resource composition, behavioral proof, and activation after registration.
Shared outbox dispatch and the external fulfillment callback require the
proposed service-only PermissionIds `outbox.dispatch` and
`compensation.fulfillment.report`; neither can borrow human authority. CON-08A
is a handler of the claimed shared-outbox command, not a separately authorized
delivery command. Keeping dispatch separate from human reconciliation or retry
authority prevents a Finance or Operator grant from authorizing an external
side effect.

No WS-CON code edits the AUTH catalogue. `AUTHORIZATION_HANDOFF.md` is the exact
proposal, and every mapping is re-read from merged trusted `main` before its
implementation chunk.

## D5 - Derived Contribution/Award Writes Are Review Participants

**Status:** accepted by the parallel WS-REV plan and candidate invariant.

The authorized `review.decision` transaction invokes mandatory task and WS-CON
participants using the same `AsyncSession`. Contribution/award creation has no
separate human API and no invented `materialize` permission. The participant
flushes but does not commit.

## D6 - Artifact Ownership Follows ADR 0013/0014

**Status:** accepted repository decision.

WS-CON owns the deterministic contribution evidence schema and projection
status. ART owns prepared-byte admission, raw provider operations, verification,
content/binding/receipt persistence, and recovery through a narrow typed
capability. LocalStorage is development/focused-test only; MinIO proves the
S3-compatible protocol locally/in CI; AWS S3 is v0.1 production. Flow Node and
R2 are deferred.

## D7 - Shared Outbox Is A Prerequisite

**Status:** recommended; human approval required with the chunk sequence.

One generic shared outbox owns delivery state and retry/dead-letter mechanics.
Review and WS-CON append events through a caller-transaction participant. No
review-private or compensation-private outbox is allowed.

## D8 - Coherent Public Activation

**Status:** recommended; human approval required.

Policy, contribution, award, callback, evidence, read, and review lifecycle
routes remain behind unregistered production composition until AUTH, ART, REV,
outbox, audit, migrations, operations, and live preflight are complete. The
final chunk activates one coherent `/api/v1` surface and no `/v1` alias.

## D9 - No Provider Payment Or Points Ledger In Workstream

**Status:** accepted from the human scope and candidate boundary.

Workstream persists awards, exact outbound instructions, adapter delivery
evidence, immutable fulfillment receipts, and rebuildable status. External
adapters own payment requests/attempts, approvals, provider reconciliation,
beneficiary accounts, balances, and project-points ledger entries.
