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
  repository decision, including WS-XINT-001 and ADR 0015, without claiming the
  supplied PDF is a generated twin.
- README, reference README, checksum manifest, architecture lockdown, and ADR
  precedence point to the active contract while retaining all archival hashes.
- ADR 0010 remains explicitly additive to revised submissions and is reconciled
  to the confirmed one-Project-Guide task pipeline: assignment binds to the
  task's initial lock, same guide keeps the prior context, any different
  currently active guide prepares the next attempt's complete context including
  an intentional backward rebase, and the reviewer consumes
  the context stamped on the leased Submission without a separate guide/rebase.
- The active contract supersedes archival combined-role wording with independent
  `submitter`, `reviewer`, and `adjudicator` grants; review requires exact active
  reviewer authority, and adjudication remains unavailable.
- AUTH alone registers, owns activation custody, integrates evaluators, and
  changes availability. REV chunks produce hidden behavior, canonical typed
  facts/guards, and feature-manifest evidence before AUTH activation; REV-13 is
  a separate product release.
- The active contract names merged PR #140's exact gates:
  `WS-AUTH-001-REV-CUSTODY`, `WS-AUTH-001-PREP`,
  `WS-AUTH-001-REV-REG`, `WS-AUTH-001-REV-05/06/07/08/09A/11/12`, and
  `WS-AUTH-001-REV-LIFECYCLE`. It distinguishes the availability-neutral
  19-row custody transfer from later registration and activation.
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
- The active action table contains 24 non-executable review-lifecycle
  dependencies: registered planned `submission.create`, 19 registered planned
  review actions, and four approved but unregistered additions. The four
  proposed additions are
  `review.revision_obligation.close -> project.task.manage` for a covered
  Project Manager, `review.revision_context.repair -> project.task.manage` for a covered Project
  Manager and `review.revision_context.legacy_close -> operations.reconcile.run`
  for an Operator, plus
  `review.lifecycle.activation.manage -> operations.reconcile.run` for an
  Operator. Chunk 01 documents their typed resource/guard contract. Separately,
  ART/REV evidence finalization requires proposed service action
  `artifact.review_evidence.binding.create -> artifact.binding.create` for
  `workstream.artifact.binding`. Exact future counts are derived from the merged
  catalogue at each AUTH gate; 57/9/48 remains only the AUTH-08 snapshot. The
  four REV additions and ART service action are independently inventoried and
  cannot be silently collapsed into 61. No new REV PermissionId is introduced.
- The merged REV-01 active contract and its immutable SHA are the feature
  registration manifest for `WS-AUTH-001-REV-REG`. For each of the four additions
  it names principal class, typed resource and canonical facts, candidates,
  guards, surface, transaction owner, revalidation, and exact hidden-behavior
  dependency. Registration may then add four planned rows before REV-11/12A
  implementation; it activates nothing and does not claim hidden behavior exists.
- The same active contract publishes six separate service identity-to-ActionId
  manifests for preference expiry, lease expiry, authority-invalidation
  reconciliation, general reconciliation, artifact-reference reconciliation,
  and projection. AUTH may create separately reviewed identity-specific extension
  contracts from that immutable manifest before the consuming REV chunk. Generic
  AUTH-09E admission never creates a catch-all identity.
- A stale-contract scanner rejects active Flow Node production, the archival
  noncanonical API prefix, full
  reviewer backlog, legacy severity, synthetic reject, direct
  payment/reputation, and bypass wording without scanning archival bytes as
  active policy.
- Active reviewer/revision/queue/contribution flow docs and templates are reconciled
  now as contract/status documentation, clearly distinguishing planned
  unavailable endpoints from implemented behavior; the scanner has no temporary
  allowlist or exception that can outlive this chunk.
- Principles, lifecycle-state, and project-operating docs state the same
  deterministic one-guide rebase rule and the WS-CON creation matrix. Every
  valid decision appends an immutable Review; every submitted finding and later
  resolution is immutable; every committed Review creates reviewer contribution.
  When the decision is `accept`, REV also creates one immutable FinalAcceptance,
  and the submitter contribution is sourced from that fact rather than inferred
  from `Review.decision`.
- The active contract defines every human lifecycle identity as canonical
  `ActorProfile.id`, defines distinct AUTH-09E fixed-service identities/static
  rows for protected jobs, removes retired compensation context from revision context,
  and records exact AUTH-first mutation choreography and REV/CON interleaving.
  It requires the opaque single-use prepared handle to match exact session,
  ActionId, actor-reference kind and ID, idempotency key, and canonical request
  digest before first feature mutation. Protocol misuse stages no decision or
  evidence, does not consume the original valid handle, and permits later exact
  first use. Evaluated authority/policy denial uses dirty-transaction rollback,
  clean unchanged AUTH denial-evidence restaging, and one route/service-command
  evidence commit with no feature/shared audit/outbox effects.
- The active contract defines REV-owned `ReviewPacketManifest` and
  `ReviewEvidenceArtifact`, ART v2 packet-read/candidate-finalize boundaries,
  exact binding service action, and no raw ArtifactStore version-1/provider access.
- The active contract maps XINT's conceptual `SubmissionVersion.artifact_hash`
  to a server-derived verified `artifact_hash` on the existing versioned
  `Submission`, copied to `ContributionRecord.artifact_hash`; caller
  `package_hash` is not trusted or silently renamed.
- Core contribution creation uses frozen `ContributionPolicyVersion`, a CON
  participant with ordered flush-only reviewer and submitter operations, no ART
  call, and no mandatory contribution-evidence projection. REV stages shared
  audit and outbox records and owns the single
  decision commit; CON owns its contribution/award behavior, public routes, and
  fulfillment transitions.
- Active contracts define FinalAcceptance as an internal immutable REV fact
  created only when a new Review has decision `accept`. It has unique
  task/source-Review/Submission lineage, exact ReviewPolicy and canonical actor
  links, no manual/public create API, and no separate AUTH action. The existing
  Submission is the version identity.
- Human reject uses canonical task `rejected`; approved administrative
  revision-obligation closure uses `cancelled` with a bounded reason. No active
  `closed/review_rejected` status token is introduced.

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
