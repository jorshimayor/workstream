# PR Trust Bundle: WS-REV-001-PLAN

## Chunk

`WS-REV-001-PLAN` - Review And Revision Lifecycle Planning

## Goal

Reconcile the review/revision lifecycle plan with trusted main after merged AUTH
reconciliation PR #140, preserve the WS-XINT handoffs, and incorporate the
human-approved FinalAcceptance boundary without changing runtime behavior or
starting a successor.

## Trusted Baseline

- Trusted main: `d541521790a0441cfd2193f466e00ef81248ec31`.
- AUTH reconciliation final head: `b80e89837d5204bb2ba59bb1ee0cbc3fe59b1ad5`.
- WS-XINT branch head: `f315ffacf09db433af54e84f081c5425167d0a9a`.
- Current authority: ADR 0015 plus the merged AUTH/REV, AUTH role/service,
  ART/REV, and REV/CON handoffs.
- The WS-REV reference Markdown/PDF pair remains immutable archival input.

## What Changed

- Assigned all action registration, evaluator integration, activation custody,
  `ActionOwner`, and availability changes to AUTH. REV builds hidden behavior
  and releases product surfaces only after exact AUTH activation.
- Replaced fixed future action totals with current-main-derived accounting. The
  24 REV dependencies are one registered planned submission action, 19
  registered planned review actions, and four approved but unregistered REV
  actions; ART's evidence-binding proposal is separate.
- Adopted PR #140's exact `REV-CUSTODY`, `PREP`, `REV-REG`, per-feature REV
  activation, and `REV-LIFECYCLE` gates without treating planning as runtime.
- Bound every sensitive mutation consumer to AUTH's opaque single-use handle by
  exact session, action, actor-reference kind/ID, idempotency key, and request
  digest, with misuse, authority-loss, and clean-denial-evidence proof.
- Made the request route or service command the sole committer; REV remains the
  lifecycle orchestrator and stages shared audit/outbox rows.
- Required AUTH-13/14 contributor-field clean cuts before REV-02 to prevent
  parallel schema and migration ownership collisions.
- Required exact independent `reviewer` grants, role-specific invalidation, six
  fixed review service identities through AUTH-09E, request-scoped AUTH reads,
  and AUTH-first prepared mutations.
- Restricted REV to ART v2 packet-read and evidence candidate/finalize ports.
  REV owns `ReviewPacketManifest` and `ReviewEvidenceArtifact`; ART owns bytes,
  bindings, candidates, providers, and finalization mechanics.
- Made unscheduled `WS-ART-001-REV-EVIDENCE` an explicit hard blocker for
  REV-07 instead of assuming the capability exists.
- Reordered decision work so REV-08 cannot commit a canonical Review and REV-10
  creates the first such transaction only with CON's mandatory flush-only
  participant.
- Replaced stale compensation-policy and mandatory evidence assumptions with
  `ContributionPolicyVersion`, server-derived versioned Submission
  `artifact_hash`, explicit unpaid/payable award behavior, and optional
  post-commit contribution evidence.
- Preserved canonical task states: human reject uses `rejected`; approved
  administrative closure uses `cancelled` plus a bounded reason.
- Removed REV ownership of CON routes and separated AUTH activation from the
  REV-12A/13 product release controller.
- Made every Review, submitted finding, and later resolution immutable for all
  three decisions; later rounds append rather than rewrite.
- Added REV-owned FinalAcceptance only for `accept`, with submitter
  `accepted_submission` sourced only from that fact and no separate create API
  or authorization action.
- Split the mandatory CON interface into a reviewer operation for every decision
  and an accept-only submitter operation after FinalAcceptance, each with its own
  frozen actor-policy lineage and mutually exclusive source fields.
- Fixed the atomic write order: common Review history, lease and queue closure,
  reviewer contribution, decision branch, accept-only FinalAcceptance and
  submitter contribution, REV audit and outbox staging, then one commit.
- Updated the shared REV/CON handoff to the accept-only FinalAcceptance source,
  two operation-specific CON inputs, and corrected audit/outbox ownership.
- Made `delivery_draining` a reachable completion-only phase for fulfillment
  obligations committed before the immutable generation cutoff. Every CON root
  writer must acquire the shared fence before ordinal allocation, and the
  exclusive transition captures the server-derived maximum only after prior
  writers drain.
- Required same-generation, pre-cutoff dispatch and callbacks, complete
  zero-obligation proof before `disabled`, denial before provider or successor
  I/O, bounded audit, and dispatcher-owned same-root claim recovery.

## Boundary Decisions

REV never imports AUTH, ART, or CON repositories and never commits their
authority independently. Evidence finalization is provider-I/O-free inside the
database transaction and follows AUTH authority lock -> REV lineage locks ->
ART candidate/admission/binding locks -> final fact recomposition -> one AUTH
evaluation -> participant flush -> one caller commit.

The repository's existing versioned `Submission` is the concrete form of the
XINT handoff's conceptual `SubmissionVersion`. The future ART submission/checker
cutover must persist verified server-derived `Submission.artifact_hash`; CON
copies that exact value and does not rederive it or trust caller `package_hash`.

The reviewer contribution operation receives Review and ReviewLease lineage and
the lease-frozen reviewer policy. It never receives FinalAcceptance or submitter
policy facts. Only the `accept` branch creates FinalAcceptance and then invokes
the submitter contribution operation with FinalAcceptance, TaskAssignment, and
the assignment-frozen submitter policy. `needs_revision` and `reject` never
create FinalAcceptance or a submitter contribution.

CON owns fulfillment-obligation roots and their monotonic ordinals. REV owns the
single release controller and stores only the cutoff returned through CON's
typed same-session port. CON obligation creation, requeue, successor, repair,
dispatch, and callback paths all consume the shared fence through mandatory
composition; REV imports no CON repository and creates no second dispatcher.

## Scope Control

This PR changes WS-REV initiative planning, the exact shared REV/CON handoff,
review evidence, its one merge intent, the human-supplied canonical archival Markdown/PDF replacement,
reference provenance/checksums, the exact `.gitattributes` rule required to
preserve that Markdown's bytes, and a narrowly tested AUTH documentation-scanner
correction for literal technical paths/CLI flags. It changes no backend,
migration, workflow, package script, test threshold, active product route,
authorization catalogue, artifact provider, or contribution runtime.

## Verification

The rebased planning snapshot requires fresh deterministic gates and exact-SHA
internal evidence before publication. The REV contract scanner is
created only by successor chunk REV-01 and is not claimed as current proof. The
repository loop-memory check will be rerun against PR #140's repaired main state.
No product tests are expected because runtime code is unchanged.

## Review State

The pre-amendment reviews repaired material WS-XINT drift, executable ordering,
coverage, concealment, external owner gates, and scanner integrity. The
FinalAcceptance amendment then received two repair cycles: reviewers corrected
the contribution order, full decision matrix, an obsolete nullable omnibus
input, and an incomplete reviewer negative-source constraint. Pre-rebase snapshot
`86ee0a5e263ac306b3bf195a9fb9043aa5439416` passed every required track. It is
historical after PR #140; the current snapshot requires fresh exact-SHA review.

The latest CodeRabbit pass found one unreachable fulfillment-drain contract.
The repaired state machine and its cutoff/writer-fence hardening passed every
required internal track; the external response records each repair cycle and
the exact thread disposition.

## Remaining Gates

- AUTH must implement and merge the exact per-consumer gates defined by PR #140,
  including REV-CUSTODY, PREP, reviewer grants, contributor-field cutovers,
  exact service identity extensions, registrations, evaluators, and activations.
- ART must schedule, approve, and merge `WS-ART-001-REV-EVIDENCE`; REV-07 is
  blocked until then.
- The ART owner must publish approved amendments for the currently unassigned
  v2 packet-read port and server-derived `Submission.artifact_hash`; exact
  packet bindings and lineage remain hard REV-07/10 gates.
- CON must merge its frozen policy lineage, mutually exclusive source schema,
  and exact two-operation flush-only participant before REV-10. Before REV-12A,
  it must merge every obligation-writer, dispatch, and callback fence hook, its
  monotonic root ordinal, and the drain-cutoff/observation port.
- Every runtime chunk requires a fresh main-SHA dependency audit, explicit
  human start, its own evidence, reviewer fanout, and merge approval.

## Human Review Focus

Check AUTH activation custody, the exact reviewer/service authority model, ART
v2 ownership and missing ART gate, all-decision Review immutability, accept-only
FinalAcceptance, the two ordered CON operations, mutually exclusive contribution
sources, canonical task states, fulfillment cutoff ownership, universal CON
writer fencing, completion-only drain, and the absence of runtime implementation.

## Human Merge Ownership

Only the human may approve and merge PR #128. Its merge intent names
`WS-REV-001-01` with `next_requires_explicit_start: true`; this PR does not
start that successor.
