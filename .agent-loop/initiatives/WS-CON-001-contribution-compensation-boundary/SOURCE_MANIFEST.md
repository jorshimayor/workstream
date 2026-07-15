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
  `e9d72a16d95e704f2af514a97d37623940854d95`, which merges AUTH-07A through
  PR #126
- merged AUTH-07A catalogue implementation `3ab25cf`, now canonical on trusted
  `main` with 74 PermissionIds, 50 planned ActionIds, and no WS-CON ActionIds or
  service-only delivery/fulfillment permissions
- `/home/abiorh/flow/workstream-auth-001-07/.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/`
- active sibling REV worktree `/home/abiorh/flow/workstream-rev-001/`, observed
  at branch-reachable head `3e09e994d500cd45916b449d7bc4f13b7623cdcc`
  on `2026-07-15T17:48:19+01:00`, plus an uncommitted initiative delta. The
  branch head integrates trusted `main` `e9d72a1`. The
  delta introduces REV-12A hidden joint release control, preserves REV-13 as
  sole production activation, consumes the proposed CON-owned dispatch and
  callback fences plus fulfillment-drain observation only through composition,
  and retains the complete PaymentPolicy removal/CON-11 gates. All required
  content-review tracks pass in the sibling evidence, but the reviewed snapshot
  and reference changes remain dirty. No dependency SHA is claimed. The exact
  reviewed delta must become a branch-reachable commit, pass commit-bound
  freshness review, refresh against trusted main, and merge before it is
  consumable. The sibling's revised reference Markdown/PDF remain separate
  worktree-only discovery inputs alongside pre-existing original-reference
  deletions.
- trusted `main` at `e9d72a16d95e704f2af514a97d37623940854d95`, including the
  merged ADR 0014 `ExternalServiceAdapterFactory[TAdapter]` foundation from PR
  #127 and the AUTH-07A catalogue/audit foundation from PR #126.

These sibling worktrees are discovery evidence, not dependencies by path. Every
implementation chunk consumes only contracts merged into trusted `main`.

## Adoption note

The revised pair contains valuable domain invariants but is not the repository's
active runtime contract. Chunk 01 will preserve both source generations and
write the reconciled active specification/ADR after explicit human approval.
