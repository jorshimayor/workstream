# PR Trust Bundle: WS-REV-001-PLAN

## Chunk

`WS-REV-001-PLAN` - Review And Revision Lifecycle Planning

## Goal

Reconcile the review/revision lifecycle plan with trusted main after merged
WS-XINT-001 PR #139, without changing runtime behavior or starting a successor.

## Trusted Baseline

- Trusted main: `5d353b6d3f8a36b9b9ffdc1959487a150ac25fd1`.
- WS-XINT branch head: `f315ffacf09db433af54e84f081c5425167d0a9a`.
- Current authority: ADR 0015 plus the merged AUTH/REV, AUTH role/service,
  ART/REV, and REV/CON handoffs.
- The WS-REV reference Markdown/PDF pair remains immutable archival input.

## What Changed

- Assigned all action registration, evaluator integration, activation custody,
  `ActionOwner`, and availability changes to AUTH. REV builds hidden behavior
  and releases product surfaces only after exact AUTH activation.
- Replaced fixed future action totals with current-main-derived accounting. The
  four proposed REV actions and ART's proposed evidence-binding action are
  separately inventoried.
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

## Scope Control

This PR changes WS-REV initiative planning, review evidence, its one merge
intent, the human-supplied canonical archival Markdown/PDF replacement,
reference provenance/checksums, the exact `.gitattributes` rule required to
preserve that Markdown's bytes, and a narrowly tested AUTH documentation-scanner
correction for literal technical paths/CLI flags. It changes no backend,
migration, workflow, package script, test threshold, active product route,
authorization catalogue, artifact provider, or contribution runtime.

## Verification

The planning snapshot passes diff integrity, Markdown links, the implemented
stale Workstream/AUTH/ART scanners, reference checksums, 80 agent-gate tests,
and exact internal-review evidence validation. The REV contract scanner is
created only by successor chunk REV-01 and is not claimed as current proof. The
repository loop-memory check reports a trusted-main AUTH status that still names
a pre-merge human checkpoint; this REV PR records but does not edit that
AUTH-owned issue. No product tests are expected because runtime code is
unchanged.

## Review State

The pre-repair reviews failed on material WS-XINT drift, executable ordering,
coverage, concealment, external owner gates, and scanner integrity. Every valid
finding was repaired through four immutable review cycles. Final snapshot
`341d920496fbf7586d95a1c00bf8a6e575b9b157` passes senior engineering,
QA/test, security/auth, product/ops, architecture, docs, reuse/dedup,
test-delta, and CI integrity with no findings. Exact reviewer IDs and results
are recorded in the internal-review evidence.

## Remaining Gates

- AUTH must merge the exact registration, grants, prepared mutation,
  AUTH-09E, evaluator, activation, and cutover chunks required by each REV
  consumer.
- ART must schedule, approve, and merge `WS-ART-001-REV-EVIDENCE`; REV-07 is
  blocked until then.
- The ART owner must publish approved amendments for the currently unassigned
  v2 packet-read port and server-derived `Submission.artifact_hash`; exact
  packet bindings and lineage remain hard REV-07/10 gates.
- CON must merge its frozen policy lineage and flush-only Review decision
  participant before REV-10.
- Every runtime chunk requires a fresh main-SHA dependency audit, explicit
  human start, its own evidence, reviewer fanout, and merge approval.

## Human Review Focus

Check AUTH activation custody, the exact reviewer/service authority model, ART
v2 ownership and missing ART gate, first canonical Review placement, CON atomic
effects, canonical task states, and the absence of runtime implementation.

## Human Merge Ownership

Only the human may approve and merge PR #128. Its merge intent names
`WS-REV-001-01` with `next_requires_explicit_start: true`; this PR does not
start that successor.
