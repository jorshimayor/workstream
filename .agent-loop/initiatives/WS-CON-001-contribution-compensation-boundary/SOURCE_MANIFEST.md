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
  `aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`, which merges AUTH-08 through PR
  #131
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
- clean trusted authorization worktree `/home/abiorh/flow/workstream-authorization-service/`
  at `aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`
- active sibling REV worktree `/home/abiorh/flow/workstream-rev-001/`, observed
  at branch-reachable head
  `a13bf352147cbb2c65742802e7c74a9478e5013b` after its parallel agent committed
  `Refresh REV plan for merged AUTH-08`; the worktree is clean. Its separate
  AUTH-08 dependency review now records correct 74/57, 9/48 and transaction/
  error/timestamp facts. Final publication evidence deliberately remains stale
  pending ART, REV-06/10 still predate the repaired CON/AUTH choreography and
  D12 custody, and REV-12A retains incorrect handler-claims-OutboxEvent wording.
  The sibling remains non-consumable until those contracts are repaired,
  commit-bound reviewed and merged.
- trusted `main` at `aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`, including merged
  ADR 0014 from PR #127, AUTH-07A/07B from PRs #126/#130, and AUTH-08 scoped
  administrative grants from PR #131. Authored loop-state/queue text in that
  merge still records pre-publication AUTH-08 state; the merge commit and code
  are authoritative while signed post-merge automation catches up.

These sibling worktrees are discovery evidence, not dependencies by path. Every
implementation chunk consumes only contracts merged into trusted `main`.

## Adoption note

The revised pair contains valuable domain invariants but is not the repository's
active runtime contract. Chunk 01 will preserve both source generations and
write the reconciled active specification/ADR after explicit human approval.
