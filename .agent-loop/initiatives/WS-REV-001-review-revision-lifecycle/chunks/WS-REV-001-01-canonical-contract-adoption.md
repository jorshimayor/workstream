# Chunk Contract: WS-REV-001-01 - Canonical Contract Adoption And Dependency Conformance

## Goal

Preserve the supplied revised WS-REV Markdown/PDF pair at its canonical
filenames as byte-immutable archival input, create one reconciled active
review-lifecycle contract, and align precedence material before runtime
implementation.

## Risk class

L1 specification and architecture boundary.

## Allowed files

```text
docs/reference_specs/WS-REV-001-review-lifecycle-specification.md only to preserve recorded revised archival bytes
docs/reference_specs/WS-REV-001-review-lifecycle-specification.pdf only to preserve recorded revised archival bytes
docs/reference_specs/WS-IMP-001-workstream-v0.1-coding-agent-implementation-specification.md only to preserve recorded archival bytes
docs/reference_specs/WS-IMP-001-workstream-v0.1-coding-agent-implementation-specification.pdf only to preserve recorded archival bytes
docs/reference_specs/README.md
docs/reference_specs/SHA256SUMS
docs/spec_review_lifecycle.md
docs/architecture_lockdown.md
docs/architecture_lifecycle_state_machine.md
docs/decision_*.md only when an approved decision requires it
docs/glossary.md
docs/principles.md
docs/product_principles.md
docs/operations_reviewer_workflow.md
docs/operations_revision_replay.md
docs/operations_queue_policy.md
docs/operations_payment_reputation.md
docs/operations_operator_workflow.md
docs/operations_project_operating_manual.md
docs/product_first_user_flows.md
docs/risk_register.md
docs/template_review_packet.md
docs/template_revision_replay.md
docs/template_prior_feedback_checklist.md
docs/template_task_status.md
docs/architecture_brief/task_lifecycle_sequence.puml
docs/architecture_brief/workstream_architecture_brief.md
docs/architecture_brief/workstream_architecture_brief.pdf
docs/architecture_brief/images/task_lifecycle_sequence.png
docs/diagrams/task_lifecycle_sequence.md
README.md
scripts/check_stale_review_contracts.py
scripts/check_stale_artifact_contracts.py
scripts/check_stale_authorization_docs.py
scripts/test_agent_gates.py
.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/**
.agent-loop/merge-intents/WS-REV-001-01.json
```

## Not allowed

```text
backend/app/**
backend/alembic/**
backend/tests/**
AUTH, ART, or CON runtime implementation
modification or replacement of any supplied archival reference byte
new provider choice
frontend work
```

## Acceptance criteria

- The supplied revised WS-REV Markdown/PDF pair and the WS-IMP pair remain
  byte-for-byte unchanged, separately hashed, and provenance-labelled as
  archival inputs. No `(2)` duplicate filename or one-sided pair edit remains.
- Provenance explicitly records that the newest revised Markdown contains
  section 4.6's closed action/permission table while its PDF companion does not;
  adoption reconciles that difference without editing either archival file.
- `docs/spec_review_lifecycle.md` is the active normative implementation
  contract. It reconciles `/api/v1`, server-selected current work, artifact
  evidence, AUTH/CON ownership, LocalStorage/MinIO/AWS S3, and every approved
  repository decision without claiming the supplied PDF is a generated twin.
- README, reference README, checksum manifest, architecture lockdown, and ADR
  precedence point to the active contract while retaining all archival hashes.
- ADR 0010 remains explicitly additive to revised submissions and is reconciled
  to the confirmed one-Project-Guide task pipeline: assignment binds to the
  task's initial lock, same guide keeps the prior context, any different
  currently active guide prepares the next attempt's complete context including
  an intentional backward rebase, and the reviewer consumes
  the context stamped on the leased Submission without a separate guide/rebase.
- Permission additions are assigned to WS-AUTH ownership, not implemented here.
- The active contract records merged AUTH-08 as 74 PermissionIds and 57
  ActionIds split into 9 active actions and 48 planned actions. It
  does not describe the authorization kernel as absent and does not treat any
  of the 24 REV dependencies as active.
- The active contract records AUTH-08's rollback-only dependency teardown,
  typed authorization-evidence `503` mapping, and route-owned canonical
  verification timestamps as required regression invariants. Chunk 01 changes
  no AUTH implementation.
- The active contract records merged ART-02A2 as inactive committed-source and
  private scratch preparation only. Review code never consumes
  `ArtifactScratchManager`, `PreparedArtifact`, or `CommittedArtifactSource`,
  persists scratch state, or treats ART-02A2 as reviewer read/intake readiness.
  Chunk 01 changes no ART implementation.
- The active action table contains 24 dependencies. The four additions are
  `review.revision_obligation.close -> project.task.manage` for a covered
  Project Manager, `review.revision_context.repair -> project.task.manage` for a covered Project
  Manager and `review.revision_context.legacy_close -> operations.reconcile.run`
  for an Operator, plus
  `review.lifecycle.activation.manage -> operations.reconcile.run` for an
  Operator. Chunk 01 documents their typed resource/guard contract, while
  AUTH owns typed catalogue/owner and PostgreSQL audit-parity migration from 57
  to exactly 61 actions from AUTH-08's merged 57 actions (9 active, 48
  planned). The resulting 61 contains 9 active and 52 planned; all 24 REV
  dependencies stay inactive until their owning REV chunks. The three
  closure/repair actions gate chunk 11 and the lifecycle-control action gates
  12A; no new PermissionId is introduced.
- A stale-contract scanner rejects active Flow Node production, `/v1`, full
  reviewer backlog, legacy severity, synthetic reject, direct
  payment/reputation, and bypass wording without scanning archival bytes as
  active policy.
- Active reviewer/revision/queue/payment flow docs and templates are reconciled
  now as contract/status documentation, clearly distinguishing planned
  unavailable endpoints from implemented behavior; the scanner has no temporary
  allowlist or exception that can outlive this chunk.
- Principles, lifecycle-state, and project-operating docs state the same
  deterministic one-guide rebase rule and the WS-CON creation matrix: every
  committed Review creates reviewer contribution, while only accept additionally
  creates the accepted Submission's submitter contribution.
- The active contract defines every human lifecycle identity as canonical
  `ActorProfile.id`, preserves explicit service/system actor kinds, removes
  legacy PaymentPolicy from final revision context, and records the exact
  WS-CON interleaving and sole REV-13 joint activation boundary.
- Active contract adoption does not guess the unresolved Submission packet
  digest. It records that CON-01/03C, ART, and REV-10 must adopt one verified
  immutable digest field, representation, derivation, and binding before
  contribution integration.

## Verification

```text
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_review_contracts.py
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
sha256sum -c docs/reference_specs/SHA256SUMS
git check-attr diff merge text -- docs/reference_specs/*.pdf | awk '$3 != "unset" {bad=1} END {exit bad}'
./docs/architecture_brief/render_pdf.sh
git diff --exit-code -- docs/architecture_brief/workstream_architecture_brief.pdf docs/architecture_brief/images/task_lifecycle_sequence.png
python3 scripts/test_agent_gates.py
git diff --check
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
reuse/dedup, and CI integrity if scanners change.

## Human review focus

Archival provenance, active-contract precedence, no semantic drift beyond the
approved planning decisions, and clear Markdown-over-archival-PDF authority.

## Stop condition

Merge, record automated memory, and stop. Do not start 02.
