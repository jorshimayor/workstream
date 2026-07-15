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

- [ ] Versioned minimal schema/disclosure matrix excludes reviewer-private,
  compensation/provider, credential, external-receipt and unnecessary actor data.
- [ ] Versioned `ContributionEvidenceProjectionRequested` reuses shared hashing,
  outbox, worker, idempotency and session utilities; replay is byte-stable.
- [ ] ART owns admission/I/O/verification/binding/receipt/recovery; WS-CON stores
  only projection state and verified binding reference.
- [ ] LocalStorage/MinIO capability conformance passes; new-schema rebuild
  retains prior immutable bundles.

## Verification and reviewers

Execute CON-09A in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/privacy, product/ops,
architecture, docs, reuse/dedup, test-delta and CI integrity are required. Stop
if ART capability/action is not merged.
