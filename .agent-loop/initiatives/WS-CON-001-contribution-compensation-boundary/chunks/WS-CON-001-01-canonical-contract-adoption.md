# Chunk Contract: WS-CON-001-01 - Canonical Contract Adoption And Architecture Decision

## Parent initiative

`WS-CON-001` - Contribution Record And Compensation Boundary

## Goal

Preserve both WS-CON archival generations and adopt one ADR-backed active
repository specification reconciled with AUTH, ART, REV, `/api/v1`, existing
Submission identity, and payment-policy reality.

## Why this chunk exists

The revised candidate contains correct domain intent and incorrect executable
contracts. Runtime chunks need one active source of truth before schema work.

## Approved plan reference

- `../INTENT.md`
- `../PLAN.md`
- `../CHUNK_MAP.md`

## Risk class

L0 architecture direction executed as an L1 specification chunk; SLA P1.

## Allowed files

```text
docs/reference_specs/README.md
docs/reference_specs/SHA256SUMS
docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.pdf
docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.md only for a byte-preserving rename
docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification(2).md
docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification(2).pdf
docs/spec_contribution_compensation.md
docs/decision_0015_contribution_compensation_boundary.md
README.md only for one active-spec link/precedence note
scripts/check_stale_authorization_docs.py only for the exact generation-2
  archival Markdown classification
scripts/test_agent_gates.py only for the exact archival-classification
  fail-closed regression and the existing cross-scanner history-set assertion
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-01.json
```

The original and second-generation reference bytes are allowed only for
restoration/filename normalization that preserves their recorded hashes; their
contents are not editable.

## Not allowed

```text
backend runtime, migrations, backend tests, workflows, dependencies
AUTH/ART/REV owned specifications or catalogues
permission/action activation
roadmap or broad operational-doc rewrite
```

## Acceptance criteria

- [ ] Original PDF is restored at exact hash `34c433...66c1`.
- [ ] Revised candidate pair has distinct generation-2 names and exact recorded
  hashes; the original eight checksum entries remain unchanged and additive
  generation-2 provenance/checksums describe the pair without calling it
  executable. The current Markdown path may only be deleted as one side of a
  byte-preserving Git rename.
- [ ] Only after the byte-preserving rename and hash proof, the exact renamed
  path
  `docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification(2).md`
  is added to `HISTORICAL_PATHS` with an explicit immutable/reconciled archival
  candidate rationale. The active `docs/spec_contribution_compensation.md`
  remains scanned; the deleted unsuffixed working path is not allowlisted; and
  arbitrary new documents or near-miss sibling filenames continue to fail
  closed under gate regression tests.
- [ ] The existing authorization/artifact historical-set regression subtracts
  only that named authorization-only path before comparing exact sets, then
  separately proves the artifact scanner already classifies the renamed path as
  historical through its `docs/reference_specs/` prefix. Do not edit the
  artifact scanner or duplicate this path in its exact-path set.
- [ ] ADR 0015 resolves immutable contribution/award/receipt meaning,
  PaymentPolicy versus CompensationPolicyVersion authority, external
  fulfillment, shared outbox, review atomicity, and artifact ownership.
- [ ] ADR/spec defines the exact project setup handoff: Project Manager records
  guide/business terms; Finance Authority creates a canonical adapter binding
  and publishes the executable policy; new assignment/lease fails with stable
  remediation when setup is absent, suspended, retired, contradictory, or
  incomplete. Missing setup is never silently unpaid.
- [ ] ADR adopts complete PaymentPolicy removal: CON-05A atomically removes all
  semantic consumers while cutting task claims to the frozen replacement;
  CON-05B physically removes dead schema after the zero-consumer and approved
  legacy-data gates pass. No advisory runtime/API fallback survives.
- [ ] Active spec uses `/api/v1`, existing `Submission`, AWS/MinIO/LocalStorage
  roles, typed ART capabilities, and exact ActionId -> PermissionId language.
- [ ] Active spec contains no `WS-AUTH-001-A`, `review.decision.record`,
  `artifact.recovery.request`, `artifact.recovery.execute`, `artifact.retrieve`,
  `ArtifactStorePort`, production Flow Node/R2, or broad-permission removal.
- [ ] Active spec declares AUTH/ART/REV/outbox prerequisites and no local auth
  implementation.
- [ ] Active spec reflects merged AUTH-08: 74 PermissionIds, 57 ActionIds, nine
  active self/admin actions and 48 planned actions on reviewed main; every
  WS-CON action remains absent until an AUTH-owned registration plus typed
  evaluator/principal/transaction/availability gate merges. It defines D10's
  prepared `T` protocol and the absent upstream `task.claim` ActionId gate
  without authorizing CON to edit AUTH. It also records D11's human-approved
  delivery/award/audit role outcomes and any required AUTH amendment without
  treating broad permission candidacy or candidate narrowing as executable.
- [ ] D12 is human/AUTH-approved and the active spec lists one exact owner for
  all 23 proposed actions plus the review claim/decision and eleven required
  ART-02D custody amendments; it preserves exact ActionId/PermissionId mappings
  and never conflates feature resource ownership with catalogue activation. In
  the recommended transfer model the contract requires atomic removal of unused
  `REV_08`/`ART_02D`; the global alternative keeps them only as feature owners
  under a separate closed custody type.
- [ ] Required specification reviewers pass.
- [ ] `CONFORMANCE_MATRIX.md` maps every retained normative invariant to its
  owning chunk, concrete behavioral case, and final evidence owner; no blanket
  or unowned requirement remains.
- [ ] Every README-linked active document and generated companion containing
  mutable PaymentRecord, accept-only/voidable contribution, automatic
  reputation, or PaymentPolicy execution language is inventoried in the
  conformance matrix. The scan also covers active templates and operations docs
  even when not README-linked, and emits the exact REV-13 allowed-file inventory.
  Historical review/reference evidence stays untouched.

## Verification commands

```bash
sha256sum -c docs/reference_specs/SHA256SUMS
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/test_agent_gates.py
python3 -m py_compile scripts/check_stale_authorization_docs.py scripts/test_agent_gates.py
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
rg -n '(^|[^[:alnum:]_/])/v1|WS-AUTH-001-A|review\.decision\.record|artifact\.recovery\.(request|execute)|artifact\.retrieve|ArtifactStorePort|production Flow Node' docs/spec_contribution_compensation.md
git diff --check
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
reuse/dedup, test-delta, and CI integrity.

## Human review focus

ADR load-bearing decisions, archive provenance, the exact and fail-closed
historical-path classification, sole compensation authority,
ActionId/PermissionId mapping, and strict ownership exclusions.

## Stop conditions

Stop if active adoption requires editing archival bytes, implementing AUTH/ART
behavior, or choosing a legacy-data migration not approved by the human.
Stop after merge/memory; do not start 02 automatically.
