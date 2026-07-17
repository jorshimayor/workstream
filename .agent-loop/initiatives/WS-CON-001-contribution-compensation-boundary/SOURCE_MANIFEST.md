# Source Manifest: WS-CON-001 Contribution Record And Compensation Boundary

## Reference inputs

| File | SHA-256 | Status |
|---|---|---|
| `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.md` | `cddbe20f4fadf5307f68519347bdd9520ef49b23fb0b92cad24c31fc9b34c640` | Working transcription; not canonical |
| `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification(2).pdf` | `ce65e208076769f0bafb09779d60ab6f5fc0c596514d4e8f4cc03690c6e6d457` | Revised archival input; not runtime authority |
| `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.pdf` | `34c4337f27e42a5b0ed5e153fe8ccd492ecede202c2764506a930d109aef66c1` | Original archival input; pre-existing user deletion remains untouched |

## Trusted baseline

- `origin/main` / merged PR #139 at
  `5d353b6d3f8a36b9b9ffdc1959487a150ac25fd1`.
- PR #139 title: `ws-xint-001-boundary-reconciliation` / AUTH, ART, REV, and
  CON lifecycle boundary reconciliation.
- Runtime AUTH remains 74 PermissionIds, 57 ActionIds, nine active, 48 planned.
- PR #139 changed planning/canonical docs/scanners, not runtime CON behavior or
  action availability.

## Normative repository sources

- `AGENTS.md`
- `README.md`
- `docs/glossary.md`
- `docs/architecture_lockdown.md`
- `docs/architecture_data_model.md`
- `docs/architecture_lifecycle_state_machine.md`
- `docs/decision_0005_postgres_is_the_record_database.md`
- `docs/decision_0007_async_first_execution.md`
- `docs/decision_0009_review_decisions_are_canonical.md`
- `docs/decision_0010_revision_context_rebase.md`
- `docs/decision_0012_workstream_authorization_service.md`
- `docs/decision_0013_immutable_artifact_storage_boundary.md`
- `docs/decision_0014_external_service_adapter_convention.md`
- `docs/decision_0015_project_contributor_roles_are_independent.md`
- `docs/spec_authorization_service.md`
- `docs/spec_artifact_storage_service.md`
- `.agent-loop/policies/*`

## Normative WS-XINT handoffs

- `WS-XINT-001/REV_CON_HANDOFF.md`: core contribution participant, frozen
  ContributionPolicyVersion, no core ART dependency.
- `WS-XINT-001/AUTH_ROLE_SERVICE_HANDOFF.md`: independent project grants,
  fixed-service static matrix, AUTH-09E admission.
- `WS-XINT-001/AUTH_REV_HANDOFF.md`: complete REV activation-custody and hidden
  behavior choreography.
- `WS-XINT-001/AUTH_ART_HANDOFF.md`: complete 25-action ART custody transfer;
  referenced only, not a core CON dependency.
- `WS-XINT-001/DECISIONS.md`: D1-D13 ownership and transaction rules.

## Runtime observations

- Current code still contains the retired guide-bound economic schema; CON-05A
  and 05B own semantic then physical removal after a human migration decision.
- No ContributionPolicy, ContributionRecord, CompensationAward, fulfillment, or
  WS-CON action runtime exists yet.
- Existing `Submission` is the versioned identity; no new SubmissionVersion is
  required.
- ART preparation from PR #129 is inactive foundation only and does not approve
  optional contribution-evidence projection.
- Sibling worktrees are discovery evidence only. Implementation consumes only
  reviewed contracts merged to trusted `main`.

## Adoption note

The reference inputs contain useful invariants but do not override merged
repository decisions. CON-01 writes the active specification after explicit
approval and leaves archival inputs unchanged.
