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
- [ ] The handler prepares authority from a server-resolved contribution and
  evidence-role target before locking its CON-owned projection/contribution
  rows, then passes the opaque handle, deterministic bytes and canonical
  project/contribution/role/schema/digest facts into the ART-owned caller-
  transaction capability. ART locks/composes ART-owned admission facts after
  those rows, completes the handle's one final evaluation, stages the one
  AuthorizationDecision plus admission/put-attempt continuation, and never
  commits or performs provider I/O in that transaction. CON never imports ART
  persistence, evaluates ART facts or invokes the final evaluator itself.
- [ ] While planned, success-path evidence tests use only an explicit fake below
  that seam and real-kernel/worker tests fail closed. Transaction tests cover
  prepare denial, CON/ART final-fact drift, handle misuse, ART Transaction-A
  rollback, post-commit provider continuation, and AUTH -> CON -> ART lock races
  in both relevant orders. Provider I/O is impossible before Transaction A
  commits.
- [ ] Versioned minimal schema/disclosure matrix excludes reviewer-private,
  compensation/provider, credential, external-receipt and unnecessary actor data.
- [ ] Versioned `ContributionEvidenceProjectionRequested` reuses shared hashing,
  outbox, worker, idempotency and session utilities; replay is byte-stable.
- [ ] ART owns admission/I/O/verification/binding/receipt/recovery; WS-CON stores
  only projection state and verified binding reference.
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
