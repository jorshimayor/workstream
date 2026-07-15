# Chunk Contract: WS-CON-001-04B - Hidden Compensation-Policy Service

## Goal and risk

Implement authorization-ready draft/read/update/publish/retire domain behavior
and canonical resource composition while routes remain unregistered and AUTH
actions remain planned. L1 payment/auth risk.

## Allowed files

```text
backend/app/modules/compensation/{schemas,repository,service}.py
backend/app/modules/projects/repository.py only active-selector locking
backend/app/composition/compensation.py
backend/tests/{test_compensation,test_projects,test_authorization,test_api_contract_e2e}.py
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-04B.json
```

## Not allowed

```text
production router registration, task/review claim integration or awards
AUTH catalogue/grant/kernel edits, adapter/provider calls
PaymentPolicy fallback, dependency or CI weakening
```

## Acceptance criteria

- [ ] AUTH's registration checkpoint is merged: exact planned policy actions,
  typed context contracts, Finance Authority grant definitions and prepared
  `T` protocol. Read maps to `compensation.policy.manage`, never broad
  `project.read`. This chunk changes no AUTH file, keeps the real kernel
  fail-closed while planned, and uses only an explicit test decision/fake below
  the authorization boundary for domain-success tests.
- [ ] Publish locks project/selector/version/bindings, revalidates authority,
  validates closed rules/active bindings, and atomically changes selector with
  audit/outbox. It evaluates one AUTH-prepared handle against facts recomposed
  from those locked rows.
- [ ] Explicit unpaid is valid; absent/incomplete/contradictory setup is stable
  remediation failure; removed PaymentPolicy never executes or acts as fallback.
- [ ] Own-state concurrent draft/publish/retire/selector/binding changes are
  deterministic. Claim races remain 05/06; delivery/callback races remain 08.
- [ ] Production OpenAPI remains unchanged.
- [ ] A later AUTH-owned gate integrates the central evaluators against this
  merged composer and alone changes availability. CON-05A remains blocked until
  that activation passes.

## Verification and reviewers

Execute CON-04B in `../RUNTIME_VERIFICATION.md`; changed code is at least 90
percent. Senior engineering, QA/test, security/auth, product/ops, architecture,
docs, reuse/dedup and test-delta are required. Stop after hidden behavior.
