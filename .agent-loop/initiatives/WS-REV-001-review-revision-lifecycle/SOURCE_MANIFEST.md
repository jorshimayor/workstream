# Source Manifest: WS-REV-001 Review And Revision Lifecycle

## Primary revised input under review

| File | SHA-256 | Status |
|---|---|---|
| `docs/reference_specs/WS-REV-001-review-lifecycle-specification(2).md` | `fffadc271c267801250b044edc570e515a250eff48afdc64f9c1f8753e6ab058` | Newest revised candidate; includes Markdown-only section 4.6 action mapping; not yet canonically adopted |
| `docs/reference_specs/WS-REV-001-review-lifecycle-specification(2).pdf` | `8c053bc752a7b0c64e04b3eda1873bb5dbc02bbdfef84bd17d07cbbf01bce2fd` | Revised archival companion; does not contain Markdown section 4.6 and is not a generated twin |

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

AUTH-07A discovery was refreshed from clean commit
`3ab25cf3b1e99336c635a318101375bb4bebdf91` in
`/home/abiorh/flow/workstream-auth-001-07`. Pull merge `3e09e99` now contains
trusted-main merge `e9d72a1`, which includes that reviewed catalogue/audit
foundation. Later AUTH definition-of-done chunks and the four additive REV
actions remain future runtime gates.

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

The tracked WS-REV filenames refer to the first archival pair and their hashes
remain in `docs/reference_specs/README.md` and `docs/reference_specs/SHA256SUMS`.
The revised pair is a second supplied archival generation, not a replacement or
a reproducible Markdown/PDF build. Within that generation, the current Markdown
is newer than the PDF because its section 4.6 closed action table is absent from
PDF text extraction. Chunk 01 preserves and hashes both files unchanged, records
their provenance/status differences, and creates
`docs/spec_review_lifecycle.md` as the reconciled active normative contract.
Neither WS-REV generation nor either WS-IMP archival file is edited to express
active repository policy.
