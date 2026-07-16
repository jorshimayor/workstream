# Chunk Contract: WS-CON-001-09B - Authorized Contribution Evidence Read

## Goal and risk

Expose safe self/project evidence reads behind unregistered routes through ART's
typed read capability. L1 auth/privacy risk.

## Allowed files

```text
backend/app/modules/contributions/{schemas,repository,service}.py
backend/app/api/internal_contributions.py
backend/app/composition/contributions.py
backend/tests/{test_contributions,test_authorization,test_api_contract_e2e}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-09B.json
```

## Not allowed

```text
write projection, raw ArtifactStore/provider ref, AUTH/ART implementation edit
production router registration or broad artifact disclosure
dependency, test, coverage or CI weakening
```

## Acceptance criteria

- [ ] Trusted main contains the separately approved
  `WS-ART-001-CON-EVIDENCE` `ContributionEvidenceReadPort`; 09A's merged write
  port does not imply read readiness unless the same ART chunk explicitly
  delivers and proves both.
- [ ] AUTH has registered the exact planned contribution self/project read
  actions, typed contexts and applicable actor-self/AdminRoleGrant definitions.
  CON composes canonical facts; pre-filter pagination and cross-project
  concealment are required. The real kernel remains fail-closed while planned;
  a later AUTH gate owns evaluator integration and availability before CON-10A.
- [ ] Matrix proves self, Project Manager, Finance, Operator/Audit views and
  Reviewer project-wide denial/self-only behavior without private/provider data.
- [ ] Grant-backed reads validate the allowed decision's complete resource-
  context digest, matched AdminRoleGrant ID and matched project against the
  canonical collection facts. CON tests disclosure with explicit allowed/
  denied decision seams only; the later AUTH activation gate proves exact role,
  revoked-grant, mixed-grant and foreign-project candidate selection.
- [ ] ART result matches immutable projection binding, digest, byte count,
  exact media type
  `application/vnd.workstream.contribution-evidence+json;version=1`, owner/
  project/logical role and schema identity; evidence failure never changes
  ContributionRecord truth.
- [ ] All product-fact/project mismatch cases map to CONFORMANCE_MATRIX;
  AUTH-owned role cases map to the activation gate; OpenAPI is hidden.

## Verification and reviewers

Execute CON-09B in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/privacy, product/ops,
architecture, docs, reuse/dedup and test-delta are required. Stop before public
registration.
