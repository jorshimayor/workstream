# Chunk Contract: WS-CON-001-04B - Hidden Contribution-Policy Service

## Goal and risk

Implement hidden read/draft/update/publish/retire ContributionPolicy behavior
and canonical resource composition while routes remain absent and AUTH actions
remain planned. L1 economic/auth risk.

## Allowed files

```text
backend/app/modules/contributions/{schemas,repository,service}.py
backend/app/modules/projects/repository.py only policy relationship locking
backend/app/composition/contributions.py
backend/tests/{test_contributions,test_projects,test_authorization,test_api_contract_e2e}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-04B.json
```

## Not allowed

```text
production router registration, task/review claim integration, award results
AUTH catalogue/grant/kernel/static-matrix edits, adapter/provider calls
legacy fallback, dependency or CI weakening
```

## Acceptance criteria

- [ ] AUTH registration is merged for planned `contribution.policy.*` actions,
  each mapped to stable `compensation.policy.manage`, with typed contexts,
  Finance candidates, AUTH ActionOwner, and prepared T protocol.
- [ ] Publish locks project, active policy, version, rules, definitions, and
  bindings; evaluates one prepared handle against recomposed final facts; and
  atomically updates current_published_version_id with audit/outbox.
- [ ] Allowed decision evidence matches complete resource digest, grant ID,
  project scope, request, and correlation. Service flushes and never commits.
- [ ] Explicit unpaid is valid. Missing/incomplete/contradictory setup is a
  stable failure. No legacy authority executes.
- [ ] Concurrent draft/publish/retire/selector/binding changes are
  deterministic. Production OpenAPI remains unchanged.
- [ ] AUTH later integrates exact evaluators and alone activates the actions;
  CON-05A waits for activation.

## Verification and reviewers

Execute CON-04B in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Required tracks: senior, QA, security, product, architecture, docs,
reuse, and test-delta. Stop after hidden behavior.
