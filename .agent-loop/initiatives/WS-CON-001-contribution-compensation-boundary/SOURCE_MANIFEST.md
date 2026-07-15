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
  `90eca12f6398f2ef168e634244d912765572c3e5`, which merges AUTH-07B through PR
  #130
- merged AUTH-07B implementation `9fd3bb4` plus CI repair `da0230c`, now
  canonical on trusted `main`: 74 PermissionIds, 50 ActionIds, exactly two
  active actor-self actions, 48 planned actions, actor-self/system runtime
  contexts only, and no WS-CON ActionIds or service-only
  delivery/fulfillment permissions
- `/home/abiorh/flow/workstream-auth-001-07/.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/`
- active sibling REV worktree `/home/abiorh/flow/workstream-rev-001/`, observed
  at branch-reachable merge head
  `e59e2bbe823bc0ee2b0e59ff35f8352349618b2e` on
  `2026-07-15T20:22:41+01:00`. It integrates trusted `main` `90eca12` and
  committed REV-12A/13 planning, while user reference-file renames remain dirty.
  Its status/evidence still cites older AUTH/CON heads and REV-12A still says
  the CON handler claims the outbox event. It remains non-consumable until that
  ownership wording and commit-bound freshness are repaired and the plan merges.
- trusted `main` at `90eca12f6398f2ef168e634244d912765572c3e5`, including merged
  ADR 0014 from PR #127, AUTH-07A catalogue/audit foundation from PR #126, and
  AUTH-07B deny-by-default actor-self kernel from PR #130.

These sibling worktrees are discovery evidence, not dependencies by path. Every
implementation chunk consumes only contracts merged into trusted `main`.

## Adoption note

The revised pair contains valuable domain invariants but is not the repository's
active runtime contract. Chunk 01 will preserve both source generations and
write the reconciled active specification/ADR after explicit human approval.
