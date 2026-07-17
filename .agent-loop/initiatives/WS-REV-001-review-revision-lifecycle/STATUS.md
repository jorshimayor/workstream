# Status: WS-REV-001 Review And Revision Lifecycle

## Current status

`WS-REV-001-PLAN` is active on `codex/ws-rev-001-plan`; no runtime chunk is
active. On 2026-07-17 the branch rebased without conflict onto trusted main
`5d353b6d3f8a36b9b9ffdc1959487a150ac25fd1`, merge commit for WS-XINT-001 PR
#139. The REV plan is being reconciled to that merged boundary before PR #128 is
republished.

The revised WS-REV Markdown/PDF pair remains byte-preserved at canonical paths
with recorded provenance. It is archival input, not authority for stale combined
roles, feature-owned action activation, provider contracts, contribution-policy
naming, or task status tokens that conflict with merged active repository
decisions.

## Reconciled dependency state

- AUTH-08 remains the implemented baseline: 74 PermissionIds and 57 ActionIds,
  with 9 active and 48 planned at that historical snapshot. Its rollback-only
  dependency teardown, typed authorization-evidence 503, and canonical timestamp
  behavior remain required regression invariants.
- The 57 count is not a promised future total. Four REV actions remain proposed,
  and WS-XINT separately proposes
  `artifact.review_evidence.binding.create`. Exact counts, owners, availability,
  and SHAs are derived at each later AUTH registration/activation gate.
- AUTH still must merge project grants, exact reviewer evaluation, fixed service
  ActorProfiles/static rows, AUTH-09E admission, prepared mutations, resource
  evaluators, activation custody, and product cutovers before their REV consumers.
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
  and a mandatory flush-only contribution/award participant. Submitter
  `accepted_submission` consumes FinalAcceptance rather than inferring
  `Review.decision`. REV stages shared audit/outbox rows and commits once. Core
  creation copies stabilized versioned Submission `artifact_hash` lineage,
  performs no ART call, and has no mandatory contribution-evidence projection.
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
override WS-XINT.

## Human clarification retained

- Keep ADR 0010 and one Project Guide context through the task pipeline.
- Same active guide keeps context; any different active guide, including an
  older reactivated guide, causes a controlled next-attempt rebase.
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
