# Source Manifest: WS-REV-001 Review And Revision Lifecycle

## Primary revised input under review

| File | SHA-256 | Status |
|---|---|---|
| `docs/reference_specs/WS-REV-001-review-lifecycle-specification.md` | `fffadc271c267801250b044edc570e515a250eff48afdc64f9c1f8753e6ab058` | Canonical revised archival input; includes Markdown-only section 4.6 action mapping; not yet actively adopted |
| `docs/reference_specs/WS-REV-001-review-lifecycle-specification.pdf` | `8c053bc752a7b0c64e04b3eda1873bb5dbc02bbdfef84bd17d07cbbf01bce2fd` | Canonical revised archival companion; does not contain Markdown section 4.6 and is not a generated twin |

## Normative repository constraints

- `AGENTS.md`
- `docs/architecture_lockdown.md`
- `docs/decision_0009_review_decisions_are_canonical.md`
- `docs/decision_0010_revision_context_rebase.md`
- `docs/decision_0012_workstream_authorization_service.md`
- `docs/decision_0013_immutable_artifact_storage_boundary.md`
- `docs/decision_0014_external_service_adapter_convention.md`
- `docs/decision_0015_project_contributor_roles_are_independent.md`
- `.agent-loop/policies/repository-engineering-policy.md`

## Merged cross-initiative authority

WS-XINT-001 PR #139 merged to trusted main
`5d353b6d3f8a36b9b9ffdc1959487a150ac25fd1` from reviewed head
`f315ffacf09db433af54e84f081c5425167d0a9a`. REV adopts:

- `.agent-loop/initiatives/WS-XINT-001-lifecycle-boundary-reconciliation/PLAN.md`
- `.agent-loop/initiatives/WS-XINT-001-lifecycle-boundary-reconciliation/DECISIONS.md`
- `.agent-loop/initiatives/WS-XINT-001-lifecycle-boundary-reconciliation/AUTH_REV_HANDOFF.md`
- `.agent-loop/initiatives/WS-XINT-001-lifecycle-boundary-reconciliation/AUTH_ROLE_SERVICE_HANDOFF.md`
- `.agent-loop/initiatives/WS-XINT-001-lifecycle-boundary-reconciliation/ART_REV_HANDOFF.md`
- `.agent-loop/initiatives/WS-XINT-001-lifecycle-boundary-reconciliation/REV_CON_HANDOFF.md`

## Later human-approved boundary amendment

On 2026-07-17 the human explicitly amended the merged REV/CON handoff for v0.1:

- every valid reviewer decision, submitted finding, and later resolution is
  immutable; later rounds append new history;
- `Review(accept)` additionally creates one immutable REV-owned
  `FinalAcceptance`;
- submitter `accepted_submission` consumes FinalAcceptance rather than inferring
  acceptance directly from `Review.decision`;
- the REV request owns one transaction; one CON participant first creates the
  reviewer contribution and evaluates the reviewer policy; REV applies the
  decision branch; the CON submitter operation runs only after FinalAcceptance
  exists for `accept`; REV stages shared audit and outbox rows; and REV commits
  once; and
- adjudication remains disabled and unimplemented in v0.1 while existing
  boundary/interface compatibility is retained for separately approved future
  work.

This explicit amendment supersedes conflicting contribution-trigger and
audit/outbox-staging wording in the merged handoff. It changes planning only;
the corresponding CON/handoff/shared-doc owner changes must merge before any
runtime REV consumer starts.

## Dependency specifications and plans

- `docs/reference_specs/WS-AUTH-001-actor-profile-role-and-authorization-service-specification.md`
- `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.pdf`
- `docs/reference_specs/WS-IMP-001-workstream-v0.1-coding-agent-implementation-specification.md`
- `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/`
- `.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/`

AUTH-07A/07B discovery was refreshed against merged AUTH-08 PR #131 at
trusted-main `aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`, whose final branch head is
`0832358a0262805f553d05b50b0d778e6e6ad995`. AUTH-08 retains the minimal
deny-by-default kernel, adds seven active administrative actions, and establishes
exactly 57 ActionIds: 9 active and 48 planned. All 20 existing revised-spec
submission/review actions stay planned. The four additive REV actions require
separate AUTH registration and later activation contracts. The 57 count is a
historical snapshot, not a future fixed total: WS-XINT-001 also proposes the
separate ART service action `artifact.review_evidence.binding.create`. Every
gate derives exact counts from current trusted main and inventories both deltas.
REV chunks never activate actions. AUTH-08 also provides the required transaction teardown,
decision-evidence `503`, and canonical verification-timestamp repairs. Later
AUTH registration, evaluator, service-admission, and activation chunks remain
independent runtime gates before their corresponding REV behavior is released.

ART discovery was refreshed against merged ART-02A2 PR #129 at trusted-main
`9a04434e2f23c5dec8939dadb943bba4d85110c0`, final branch head
`32aab89262a3944f305e9e5dc4c65a2d31e2e144`. The chunk adds only inactive
committed-source/private-scratch preparation. Its current ArtifactStore v1 state
is not a REV interface. REV consumes none of its scratch/source types or raw
store methods. Later ART v2, S3, submission/checker binding cutovers, packet
read, review-evidence candidate/finalize, projection, and live-proof contracts,
including a separately approved `WS-ART-001-REV-EVIDENCE` owner chunk, remain
dependency gates.

The merged ART plan also leaves the narrow active-lease packet-read port and
server-derived `Submission.artifact_hash` field unassigned to an approved chunk.
REV-07/10 require exact merged ART/task-owner amendments for those capabilities;
existing artifact-set context is not treated as either contract.

## Historical cross-worktree discovery evidence

The following sibling planning paths were read-only discovery inputs on
2026-07-15, pinned for this review to rebased CON planning head `c965f9b`. They are
not runtime dependencies by path and no file in that worktree was edited by
WS-REV:

- `/home/abiorh/flow/workstream-con-001/.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/`
- `/home/abiorh/flow/workstream-con-001/.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/JOINT_RELEASE_HANDOFF.md`
- `/home/abiorh/flow/workstream-con-001/docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.md`

These paths are dated discovery only. Merged WS-XINT
`REV_CON_HANDOFF.md` supersedes their conflicting mandatory evidence-projection,
policy naming, activation, and core ART-dependency assumptions. Owning WS-CON
runtime contracts must still merge before a REV gate consumes them.

## Adoption note

The revised supplied WS-REV pair now occupies the canonical filenames and its
hashes are recorded in `docs/reference_specs/README.md` and
`docs/reference_specs/SHA256SUMS`; no duplicate `(2)` path remains. The Markdown
is newer than the PDF because its section 4.6 closed action table is absent from
PDF text extraction. Chunk 01 preserves and hashes both canonical files
unchanged, records their provenance/status differences, and creates
`docs/spec_review_lifecycle.md` as the reconciled active normative contract.
Neither WS-REV archival file nor either WS-IMP archival file is edited to
express active repository policy.
