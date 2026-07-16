# Chunk Contract: WS-CON-001-09A - Contribution Evidence Projection Write

## Goal and risk

Build minimal deterministic evidence and bind it through an ART-owned typed
capability. L1 artifact/privacy/worker risk.

## Allowed files

```text
backend/app/modules/contributions/{schemas,repository,evidence}.py
backend/app/modules/outbox/handlers.py only evidence-handler registration
backend/app/workers/contribution_evidence.py
backend/app/workers/celery_app.py only include registration
backend/tests/{test_contributions,test_artifacts,test_outbox}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-09A.json
```

## Not allowed

```text
raw ArtifactStore/provider ref, ART implementation edit
ArtifactScratchManager/PreparedArtifact/CommittedArtifactSource import or construction
scratch path/descriptor/ledger/cleanup ownership in CON
read route, semantic search, retain/pin or provider recovery invention
duplicate canonicalizer/worker/session/idempotency, dependency/CI weakening
```

## Acceptance criteria

- [ ] AUTH has registered the planned
  `artifact.contribution_evidence.binding.create` action with existing
  `artifact.binding.create` PermissionId, typed context, D10 prepared-mutation
  protocol and only the exact added assignment on the existing fixed
  `workstream.artifact.binding` ActorProfile/link; ART has merged its capability.
  A new or broader worker principal is forbidden. The real kernel remains
  fail-closed while planned and CON adds no AUTH or ART bypass.
- [ ] Merged trusted main contains the required ART chain: 02A2 committed-source
  preparation, 02A3 ArtifactStore v2, 02B1 MinIO/AWS provider, 02C1 durable
  admission, 02C2 verification/publication and 02C3 recovery; fixed AUTH-09
  verifier/scanner/put-resolver registrations, identities and assignments; ART-
  02D hidden resource/behavior composition; D12 exact AUTH custody for all eight
  ART-02D Operator and three internal actions without ActionId/PermissionId
  drift; later AUTH-owned Operator/internal evaluator integration and separate
  action activation; followed by the separately approved
  `WS-ART-001-CON-EVIDENCE` write port. Presence of PR #129 symbols alone fails.
- [ ] From a read-only canonical snapshot the handler creates versioned JSON,
  exact media type
  `application/vnd.workstream.contribution-evidence+json;version=1`, expected
  digest/size and stable identity. ART prepares the source before D10 and every database
  mutation lock and retains the raw `PreparedArtifact` behind an opaque async-
  context operation; no ART implementation type crosses into CON.
- [ ] Transaction A then asks AUTH to prepare D10 and lock authority, locks/
  reloads the CON projection/contribution rows, regenerates and compares the
  final canonical facts/digest with the server commitment, and asks ART to lock
  admission and stage the AuthorizationDecision plus durable attempt. ART
  flushes but does not commit; no first-pass filesystem or provider I/O occurs
  while AUTH/CON/ART rows are locked.
- [ ] After the caller explicitly commits, an opaque same-process ART
  continuation uses a fresh transaction to prove/claim the committed attempt
  before consuming the sealed stream once and calling the provider outside all
  database transactions. Commit failure, rollback, drift, cancellation and
  replay close/release or retain explicit ART cleanup custody until retry.
  Process loss persists no handle/path; stale cleanup and deterministic outbox
  replay regenerate identical bytes against the durable attempt. Observation
  precedes any absent-object replay after ambiguous provider completion.
- [ ] While planned, success-path evidence tests use only an explicit fake below
  that seam and real-kernel/worker tests fail closed. Transaction tests cover
  prepare denial, CON/ART final-fact drift, handle misuse, ART Transaction-A
  rollback, unsupported/wrong media or digest/size mismatch with zero admission/
  provider calls, no DB locks during first pass, locked-fact drift, post-commit
  durable-attempt proof, prepared-source close/cancellation/quota custody,
  process loss/replay without handle serialization, single-use second pass, and
  AUTH -> CON -> ART lock races in both relevant orders. Provider I/O is
  impossible before Transaction A commits.
- [ ] Versioned minimal schema/disclosure matrix excludes reviewer-private,
  compensation/provider, credential, external-receipt and unnecessary actor data.
- [ ] Versioned `ContributionEvidenceProjectionRequested` reuses shared hashing,
  outbox, worker, idempotency and session utilities; replay is byte-stable.
- [ ] ART owns admission/I/O/verification/binding/receipt/recovery; WS-CON stores
  only projection state and verified binding reference.
- [ ] Before marking the projection `projected`, CON validates returned binding/
  receipt digest, byte count, exact media type, owner, project, logical role,
  schema version and operation/idempotency identity against its immutable
  projection. Any mismatch is an artifact integrity failure, never success.
- [ ] LocalStorage/MinIO capability conformance passes; new-schema rebuild
  retains prior immutable bundles.
- [ ] A later AUTH-owned activation gate, after the ART capability and CON
  composer are merged, integrates the evaluator against the merged seams
  without editing CON feature code and alone changes availability; CON-11
  waits.

## Verification and reviewers

Execute CON-09A in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/privacy, product/ops,
architecture, docs, reuse/dedup, test-delta and CI integrity are required. Stop
if ART capability/action is not merged.
