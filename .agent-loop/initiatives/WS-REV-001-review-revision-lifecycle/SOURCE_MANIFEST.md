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
- `.agent-loop/policies/repository-engineering-policy.md`

## Dependency specifications and plans

- `docs/reference_specs/WS-AUTH-001-actor-profile-role-and-authorization-service-specification.md`
- `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.pdf`
- `docs/reference_specs/WS-IMP-001-workstream-v0.1-coding-agent-implementation-specification.md`
- `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/`
- `.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/`

AUTH-07A discovery from `3ab25cf3b1e99336c635a318101375bb4bebdf91`
was refreshed against merged AUTH-07B at trusted-main
`90eca12f6398f2ef168e634244d912765572c3e5`. AUTH-07B installs the minimal
deny-by-default kernel and makes 2 of 50 ActionIds active; the remaining 48,
including all 20 existing revised-spec submission/review actions, stay planned.
The amended but unmerged AUTH-08 contract projects 57 actions after AUTH-08: 9
active and 48 planned. The four additive REV actions then require exact 57-to-61
typed catalogue/owner/PostgreSQL parity, producing 9 active and 52 planned. All
24 REV dependencies stay inactive until their owning REV chunks activate them.
AUTH-08 runtime/merge, later AUTH definition-of-done chunks, and AUTH-owned
kernel transaction/error/timestamp repairs remain runtime gates.

## Cross-worktree discovery evidence

The following sibling planning paths were read-only discovery inputs on
2026-07-15, pinned for this review to rebased CON planning head `c965f9b`. They are
not runtime dependencies by path and no file in that worktree was edited by
WS-REV:

- `/home/abiorh/flow/workstream-con-001/.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/`
- `/home/abiorh/flow/workstream-con-001/.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/JOINT_RELEASE_HANDOFF.md`
- `/home/abiorh/flow/workstream-con-001/docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.md`

The reconciled CON content passed security/auth, product/QA, and
architecture/docs delta review on predecessor commit `42cf11f`; exact-head
publication review of `c965f9b` remains pending. Later uncommitted sibling
fence-handoff edits are discovery evidence only. Its contracts must still be reread from the merged
trusted-main SHA named by each runtime gate; the planning commit does not
substitute for that merge.

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
