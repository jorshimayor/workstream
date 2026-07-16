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
proposed dependencies requiring human approval and AUTH-owned executable
integration.

WS-CON declares granular proposed ActionIds mapped to existing stable
PermissionIds when semantically safe. AUTH owns registration, audit migration,
availability, evaluator dispatch, grants/service actors, authority
revalidation, and kernel behavior; the named feature chunk owns product-row
loading, approved typed resource composition and hidden behavioral proof below
an explicit test seam while the action remains planned. AUTH later integrates
the evaluator against that exact merged seam, proves real-kernel behavior and
alone activates the action.
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

Current trusted `main` proves why registration and activation cannot be
collapsed: AUTH-08 has 57 registered actions but only nine active self/admin
actions; all planned and unsupported actions fail closed. Its complete
resource-context digest, matched grant/scope evidence and route-owned commit
boundary become mandatory inputs to later WS-CON evaluators rather than a
feature-local replacement.

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

## D10 - AUTH Owns Prepared Cross-Domain Mutation Authorization

**Status:** required architecture correction after merged AUTH-07B/AUTH-08 review;
human/AUTH approval required before any `T` action implementation.

The current actor-self kernel can revalidate entirely inside AUTH-owned rows.
WS-CON mutations cross AUTH and product rows, so one `require()` call against an
unlocked product snapshot is insufficient, while locking product rows before
AUTH rows violates the canonical lock order.

AUTH must provide one caller-session-bound prepared authorization protocol. It
locks actor/link/grant or service-assignment authority first from a
server-resolved preliminary target, returns an opaque single-use handle, and
evaluates that handle exactly once against the final typed context recomposed
from locked product rows. The handle is bound to request, session, actor,
action, target and authority snapshot; it cannot be serialized, cached, reused,
or substituted. AUTH stages one decision and never commits. WS-CON supplies
facts and product guards but cannot implement the handle or query AUTH state.

Rejected: product-row locks before AUTH locks, evaluating an unlocked snapshot,
calling AUTH twice and emitting competing decisions, or letting feature code
flip catalogue availability.

## D11 - Reconcile AUTH-08 Role Candidates Per Action

**Status:** unresolved human cross-spec decision before CON-10A/10B
authorization registration; any resulting AUTH correction remains AUTH-owned.

Merged AUTH-08 is the canonical five-role permission-candidate matrix. It gives
Finance Authority the existing `compensation.delivery.reconcile` PermissionId
but omits it from Operator, while the reconciled candidate WS-CON human matrix
proposes a reason-bound system Operator for delivery reconciliation. Only D2 is
human-approved. The recommended D11 resolution is to preserve that candidate
behavior: a reviewed AUTH successor adds the existing PermissionId to Operator
and updates its closed definition/API/kernel tests. The human may instead
reject Operator delivery reconciliation; then CON-01 removes it from the active
matrix before AUTH registration. WS-CON adds no PermissionId, role query or
local exception under either resolution.

The human must also resolve the inverse mismatches. Project Manager has the
merged `compensation.award.read` permission while the candidate WS-CON matrix
excludes it from monetary award/fulfillment detail; candidate audit read/export
sets are narrower than every merged role containing `audit.read` or
`audit.export`. D11 chooses whether to preserve each merged candidate or adopt
the narrower WS-CON action set. Any approved narrowing is implemented only by
AUTH through an evaluator-owned closed role intersection before grant query.
The role set is never request- or CON-supplied; an actor with both excluded and
eligible grants must match only the eligible grant. If the merged set is kept,
CON-01 updates the active product matrix before registration. No generic
"permission present means action allowed" branch or silent narrowing is
accepted.

Rejected: silently choosing either side of a role-matrix conflict, changing a
candidate set after registration without review, or reproducing role policy in
CON.

## D12 - ActionOwner And Activation Custody Have One Meaning

**Status:** unresolved AUTH/human contract decision before any WS-CON action
registration or review-action activation amendment.

The merged enum defines ActionOwner as the implementation chunk allowed to
activate an action. The user requires AUTH to own authorization activation, so
the recommended resolution keeps that meaning and adds the exact eight
AUTH-owned WS-CON activation owners plus two review activation owners listed in
`AUTHORIZATION_HANDOFF.md`. Every proposed action maps to one owner; CON/ART/REV
remain feature resource owners but never change availability.

The alternative is a reviewed global semantic change: ActionOwner becomes the
feature/resource owner and AUTH adds a separate closed activation-custody type.
That change must update catalogue docs, typed/PostgreSQL parity where
applicable, startup checks and every existing owner test before use. It cannot
be inferred locally. Under either choice there is exactly one activation
authority and the handoff table keeps feature ownership separate.

Rejected: leaving current REV owners while saying AUTH activates, assigning an
evidence action jointly to AUTH/ART, using a registration PR as a second owner,
or letting two chunks flip one action.
