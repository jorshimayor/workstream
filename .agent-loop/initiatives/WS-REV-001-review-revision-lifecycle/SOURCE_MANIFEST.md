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

AUTH-07A/07B discovery was refreshed against merged AUTH-08 PR #131 at
trusted-main `aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`, whose final branch head is
`0832358a0262805f553d05b50b0d778e6e6ad995`. AUTH-08 retains the minimal
deny-by-default kernel, adds seven active administrative actions, and establishes
exactly 57 ActionIds: 9 active and 48 planned. All 20 existing revised-spec
submission/review actions stay planned. The four additive REV actions require
exact 57-to-61 typed catalogue/owner/PostgreSQL parity, producing 9 active and
52 planned. All 24 REV dependencies stay inactive until their owning REV chunks
activate them. AUTH-08 also provides the required transaction teardown,
decision-evidence `503`, and canonical verification-timestamp repairs. Later
AUTH definition-of-done chunks remain runtime gates at their owning REV chunks.

ART discovery was refreshed against merged ART-02A2 PR #129 at trusted-main
`9a04434e2f23c5dec8939dadb943bba4d85110c0`, final branch head
`32aab89262a3944f305e9e5dc4c65a2d31e2e144`. The chunk adds only inactive
committed-source/private-scratch preparation and preserves ArtifactStore v1,
provider selection, schema, product routes, and authority behavior. REV consumes
none of its scratch or source types directly. Later ART v2, S3, admission,
verification/publication, read/intake/retention/recovery, checker, projection,
and live-proof contracts remain dependency gates at their owning REV chunks.

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
