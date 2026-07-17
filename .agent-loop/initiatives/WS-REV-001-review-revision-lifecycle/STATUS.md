# Status: WS-REV-001 Review And Revision Lifecycle

## Current status

`WS-REV-001-PLAN` is active on `codex/ws-rev-001-plan`; no runtime chunk is
active. On 2026-07-17 the branch rebased without conflict onto trusted main
`299363af5d9e8a68bcc9b17457188048483caeed`, merge commit for AUTH-09A PR #132.
That merge follows AUTH reconciliation PR #140 and implements migration `0023`,
the common fixed-service enum/schema, seven ART service identities, eleven
static ART memberships, and eight planned AUTH-09 route actions. It provisions
no actor, admits no service token, activates no action, and adds no REV service
identity. The earlier exact-snapshot review at `7a76da2` predates this rebase and
is historical. Refreshed normative snapshot
`12a781b2c4e8e8bb3378e3c4cb4f7c32ac9ba5be` passed all nine internal review
tracks; fresh external evidence remains required before PR #128 can merge.

The revised WS-REV Markdown/PDF pair remains byte-preserved at canonical paths
with recorded provenance. It is archival input, not authority for stale combined
roles, feature-owned action activation, provider contracts, contribution-policy
naming, or task status tokens that conflict with merged active repository
decisions.

## Reconciled dependency state

- AUTH-08 remains a historical implemented checkpoint: 74 PermissionIds and 57
  ActionIds, with 9 active and 48 planned. Current trusted main after AUTH-09A
  contains 74 PermissionIds and 65 ActionIds, with 9 active and 56 planned. Its
  rollback-only dependency teardown, typed authorization-evidence 503, and
  canonical timestamp behavior remain required regression invariants.
- The 24 REV lifecycle dependencies are registered planned `submission.create`,
  19 registered planned review actions, and four approved but unregistered REV
  lifecycle actions. None is active. The separate unregistered
  `artifact.review_evidence.binding.create` ART action is not one of the 24.
  Exact counts, custodians, availability, and SHAs are derived at each later AUTH
  registration or activation gate.
- PR #140 defines the exact AUTH sequence and ownership. AUTH-09A is now merged;
  AUTH-09B through AUTH-09E, availability-neutral
  `WS-AUTH-001-REV-CUSTODY`, `WS-AUTH-001-PREP`, and later AUTH product contracts,
  feature-gated `WS-AUTH-001-REV-REG`, per-feature `WS-AUTH-001-REV-05/06/07/08/09A/11/12`
  activation, and `WS-AUTH-001-REV-LIFECYCLE` for the four additions. Hidden REV
  schema, pure validation, resource facts, guards, and behavior may proceed when
  their exact data/participant contracts exist while actions remain unavailable.
  Each committing sensitive mutation waits for PREP; REV-13 waits for every exact
  activation and is the only product-surface release.
- AUTH-09A's fixed-service foundation is reusable, but its closed set and matrix
  contain only seven ART identities and eleven ART memberships. Each of REV's
  six service identities still needs the immutable REV-01 manifest, a separately
  reviewed AUTH enum/constraint/matrix extension, AUTH-09B provisioning, and
  AUTH-09E admission. No catch-all service authority exists.
- PR #140 also exposes one blocking AUTH graph defect: full AUTH-13/14 currently
  require prepared revision/replacement behavior owned by downstream REV-09A.
  Before REV-02 starts, AUTH must split and merge a schema-only contributor-field
  foundation. REV-09A then supplies hidden behavior; amended full AUTH-13/14
  cutovers and AUTH-14 `submission.create` activation follow before REV-13.
- Project contributor grants are independent `submitter`, `reviewer`, and
  `adjudicator`. REV consumes only reviewer authority/invalidation; adjudication
  remains unavailable.
- ART-02A2 remains preparation-only. REV waits for ART v2 submission/checker
  cutovers, narrow packet read, separately approved review-evidence
  candidate/finalize behavior, exact binding service action, projection, and
  live proof. The current merged ART plan does not schedule
  `WS-ART-001-REV-EVIDENCE`, so REV-07 is blocked until ART adds and merges that
  owner chunk. The ART plan also does not yet assign the exact active-lease
  packet-read port or server-derived `Submission.artifact_hash` persistence;
  those require approved owner amendments before REV-07/10. REV never consumes
  ArtifactStore v1, scratch, provider, or ART repository APIs.
- Merged `REV_CON_HANDOFF.md` plus the human-approved 2026-07-17 amendment
  controls contribution integration. REV owns immutable FinalAcceptance and
  creates it only for accept; CON must supply ContributionPolicyVersion freezes
  and one mandatory participant with two ordered flush-only operations. The
  reviewer operation runs before every decision branch; the submitter operation
  runs only after FinalAcceptance exists for `accept`. Submitter
  `accepted_submission` consumes FinalAcceptance rather than inferring
  `Review.decision`. REV stages shared audit and outbox rows; the request route or
  service command commits once. Core
  creation copies stabilized versioned Submission `artifact_hash` lineage,
  performs no ART call, and has no mandatory contribution-evidence projection.
- REV-12A also waits for CON-owned mandatory fence hooks on every fulfillment
  obligation writer, dispatch, and callback path; a monotonic root ordinal; and
  a same-session drain-cutoff/observation port. The exclusive cutoff transition
  waits for prior writers, and `delivery_draining` permits only completion of
  same-generation roots at or below the stored cutoff.
- The current canonical lifecycle uses `rejected` for human reject and
  `cancelled` with bounded reasons for approved administrative closure; REV will
  not introduce archival `closed/review_rejected` as a new status token.

## Reconciled plan state

The reconciliation updates intent, discovery, decisions, plan, chunk map,
conformance, CON integration, risks, source manifest, every affected chunk
contract, review log, trust bundle, and exact-SHA internal evidence. Required
changes include:

- AUTH registration -> hidden behavior -> AUTH activation -> REV product release;
- AUTH-first prepared mutation choreography;
- exact fixed-service identity rows and independent reviewer grants;
- REV-owned ReviewPacketManifest and ReviewEvidenceArtifact;
- ART v2 packet/evidence ports and exact binding action;
- first canonical Review commit only with the CON participant; and
- removal of CON router ownership and optional evidence projection from REV-13.

The first final review of snapshot `a916692` found executable-graph, external
dependency ownership, cross-project concealment, coverage, claim-order, and
artifact-error ambiguities. Those findings were repaired in `93955f1`; its
second review found a duplicated scanner workaround and one stale integration-
fence sentence. Both are repaired through literal proof commands, a narrow
tested technical-path/CLI classifier, and consistent pre-12A/released fence
wording. Immutable snapshot
`341d920496fbf7586d95a1c00bf8a6e575b9b157` then passed every required final
review track with no findings. The later human-approved FinalAcceptance
amendment reopens planning review; that older evidence remains historical and
must not be used to publish the amended snapshot. Earlier AUTH/ART dependency
review files remain dated evidence; their old future-count assumptions do not
override WS-XINT. The FinalAcceptance amendment initially failed transaction
ordering and proof-matrix review, then failed on one obsolete omnibus CON input
and one incomplete negative-source constraint. Both findings were repaired.
CodeRabbit's latest refresh then found an unreachable fulfillment-drain phase.
The repaired contract now fences every CON obligation writer before ordinal
allocation, captures an immutable cutoff after prior writers drain, permits only
pre-cutoff completion work, and retains audited same-root recovery for denied
already-claimed dispatch. Snapshot
`86ee0a5e263ac306b3bf195a9fb9043aa5439416` passed senior engineering,
QA/test, security/auth, product/ops, architecture, docs, reuse/dedup, test-delta,
and CI integrity with no findings before the PR #140 rebase. It is historical
evidence and does not approve the current snapshot.

After the PR #140 reconciliation, snapshots `777468d`, `4084cd4`, and `2146b8c`
failed internal review on dependency cycles, PREP ownership/replay semantics,
transaction ownership, and residual AUTH-13/14 cutover ownership. Every valid
finding is recorded in `REVIEW_LOG.md` and repaired. Exact snapshot
`7a76da2a79243cf61936d3bc7cf2606a82f0b5d8` passed senior engineering, QA/test,
security/auth, product/ops, architecture, docs, reuse/dedup, test-delta, and CI
integrity with no findings. No runtime chunk is active.

That approval predates merged AUTH-09A PR #132 and is historical after the
rebase onto `299363a`. Refreshed normative snapshot `12a781b` passed all nine
required tracks after the AUTH-09A, catalogue, service-identity, migration, and
guide-authority reconciliation plus the archival-provider adoption clarification.
Its evidence is bound in the PLAN review file.

## Human clarification retained

- Keep ADR 0010 and one Project Guide context through the task pipeline.
- Exact match between the prior Submission's stamped guide identity/activation
  sequence and the project's currently active guide keeps context. Any different
  internally consistent active identity/sequence pair, including an older
  reactivated guide, causes a controlled forward or backward rebase; an
  internally inconsistent pair or missing, incomplete, or unsafe active context
  blocks preparation.
- Reviewer uses the context stamped on the exact leased Submission and performs
  no separate guide rebase.
- LocalStorage is development, MinIO proves the protocol, AWS S3 is production,
  and Flow Node remains deferred.
- Artifact bytes are restricted to the exact active leased packet; bounded chain
  metadata remains available to authorized participants.
- Every decision appends an immutable Review, and every submitted finding and
  later resolution is immutable. Every Review creates reviewer contribution.
  When the decision is `accept`, REV also creates one immutable FinalAcceptance;
  only that fact creates submitter contribution. Guide rebase never changes the
  frozen ContributionPolicyVersion.

## Stop condition

PR #128 may be refreshed only from the final reviewed branch with passing gates
and exact-SHA evidence. It still requires explicit human merge approval. Do not
start `WS-REV-001-01` or any runtime implementation; merge intent requires a
separate post-merge start.
