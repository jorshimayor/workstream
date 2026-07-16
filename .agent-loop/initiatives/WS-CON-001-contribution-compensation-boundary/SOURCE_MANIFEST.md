# Source Manifest: WS-CON-001 Contribution Record And Compensation Boundary

## Primary revised inputs under review

| File | SHA-256 | Status |
|---|---|---|
| `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.md` | `cddbe20f4fadf5307f68519347bdd9520ef49b23fb0b92cad24c31fc9b34c640` | Editable reconciled working transcription derived from generation-2 PDF; not archival and not canonically adopted |
| `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification(2).pdf` | `ce65e208076769f0bafb09779d60ab6f5fc0c596514d4e8f4cc03690c6e6d457` | Revised archival companion; text extracted and structurally inspected; not a reproducible Markdown build contract |

## Original immutable input

| File | SHA-256 | Status |
|---|---|---|
| `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.pdf` | `34c4337f27e42a5b0ed5e153fe8ccd492ecede202c2764506a930d109aef66c1` | First archival generation supplied 2026-07-11; currently deleted in the pre-existing user worktree and not modified/restored by this audit |

## Normative repository constraints

- `AGENTS.md`
- `README.md`
- `docs/architecture_lockdown.md`
- `docs/decision_0005_postgres_is_the_record_database.md`
- `docs/decision_0007_async_first_execution.md`
- `docs/decision_0009_review_decisions_are_canonical.md`
- `docs/decision_0010_revision_context_rebase.md`
- `docs/decision_0012_workstream_authorization_service.md`
- `docs/decision_0013_immutable_artifact_storage_boundary.md`
- `docs/decision_0014_external_service_adapter_convention.md`
- `docs/spec_authorization_service.md`
- `docs/spec_artifact_storage_service.md`
- `.agent-loop/policies/*`

## Parallel dependency sources inspected

- trusted authorization worktree and `origin/main` at
  `9a04434e2f23c5dec8939dadb943bba4d85110c0`, which merges ART-02A2 through PR
  #129 and includes AUTH-08 merge `aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`
- merged AUTH-08 implementation lineage through `0832358`, now canonical on
  trusted `main`: 74 PermissionIds, 57 ActionIds, exactly nine active self/admin
  actions, 48 planned actions, eight closed resource-context variants,
  actor-self/AdminRoleGrant matched authority, complete resource-context digest
  and matched grant/scope decision evidence, explicit feature-route commit
  ownership, and no WS-CON ActionIds or service-only dispatch/fulfillment
  permissions
- merged `backend/app/modules/authorization/policy.py`, whose exact role matrix
  confirms Finance Authority has `compensation.delivery.reconcile`, Operator
  does not, and Project Manager has the broader `compensation.award.read`
  candidate. These facts create the unresolved D11 human decision and only its
  chosen AUTH amendment/evaluator or CON-01 matrix-update gates; they are not
  copied into CON runtime.
- merged ART-02A2 final branch head
  `32aab89262a3944f305e9e5dc4c65a2d31e2e144`: inactive
  `ArtifactPreparationService`, `ArtifactScratchManager`, `PreparedArtifact`
  and `CommittedArtifactSource`; no ArtifactStore v2 cutover, S3/MinIO,
  admission, verification, contribution capability, action or permission
- merged AUTH catalogue assigns eight Operator-facing and three internal
  artifact actions to `ActionOwner.ART_02D`; their existing PermissionId
  mappings are unchanged. Because `ActionOwner` currently owns activation,
  contribution-evidence readiness now extends D12 with exact proposed
  `AUTH_ART_02D_OPERATOR` and `AUTH_ART_02D_INTERNAL` custody rather than
  allowing ART/CON to write availability.
- clean trusted authorization worktree `/home/abiorh/flow/workstream-authorization-service/`
  at `9a04434e2f23c5dec8939dadb943bba4d85110c0`
- active sibling REV worktree `/home/abiorh/flow/workstream-rev-001/`: reviewed
  evidence-bound baseline `6faccc04e9dbad7c746b081e55a47750f678d37c`
  was inspected, then later same-turn uncommitted external-review repairs were
  observed. Its ART-02A2 classification is accurate, but no sibling path/head/
  dirty state is a durable dependency. Only a reviewed merge on trusted `main`
  may be consumed, and it must repair REV-06/08 prepared authorization, REV-10
  final CON composition, D12 custody and dispatcher-owned outbox transitions.
- trusted `main` at `9a04434e2f23c5dec8939dadb943bba4d85110c0`, including merged
  ADR 0014 from PR #127, AUTH-07A/07B from PRs #126/#130, and AUTH-08 scoped
  administrative grants from PR #131 plus ART-02A2 from PR #129. The merge
  commits and code are authoritative where authored initiative status still
  describes its pre-merge branch state.

These sibling worktrees are discovery evidence, not dependencies by path. Every
implementation chunk consumes only contracts merged into trusted `main`.
The verification contract deliberately does not pin a live sibling head or
cleanliness because its authorized owner is working concurrently.

## Adoption note

The revised pair contains valuable domain invariants but is not the repository's
active runtime contract. Chunk 01 will preserve both source generations and
write the reconciled active specification/ADR after explicit human approval.
