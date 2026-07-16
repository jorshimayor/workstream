# Chunk Contract: WS-AUTH-001-16 - Conformance, Observability, And Live API Proof

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Verify authority-event/idempotency completeness, finish privacy and
observability, run exhaustive permission/concurrency tests, and produce an
API-visible live authorization drill.

## Why this chunk exists

The initiative is not complete until immediate revocation, separation of
duties, resource scope, bootstrap safety, and absence of direct database edits
are proven end to end.

## Approved plan reference

- INTENT: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/INTENT.md`
- PLAN: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/PLAN.md`
- CHUNK_MAP: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/CHUNK_MAP.md`

## Risk class

L1

## SLA

P1

## Allowed files

```text
backend/app/modules/authorization/**
backend/app/modules/actors/**
backend/app/modules/audit/**
backend/app/api/**
backend/app/main.py
backend/app/workers/**
backend/app/core/config.py
backend/app/core/observability.py
backend/scripts/auth_api_e2e.py
backend/tests/**
backend/pyproject.toml
docs/operations_roles_permissions.md
docs/operations_authorization_service.md
docs/spec_authorization_service.md
docs/architecture_data_model.md
docs/roadmap_status.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
review/contribution/compensation implementation
production credentials or private keys in fixtures/evidence
direct database bootstrap or grant edits in live proof
loosening issuer, scope, permission, or resource guards
starting WS-POL-002-03 automatically
```

## Acceptance criteria

- Authority events contain version, correlation/request ID, acting/target
  actor, matched grant, project, reason, idempotency key, and bounded state.
- No authority history is backfilled to compensate for a missing earlier
  event/idempotency schema; gaps stop the initiative.
- Tokens, raw claims, JWKS bodies, secrets, and unnecessary PII are absent from
  logs, errors, audit, and committed evidence.
- Table-driven tests cover every permission role/scope allow and deny case.
- A generated conformance manifest covers every protected `/api/v1` route and
  asynchronous command with exactly one primary registered action, canonical
  resource type, and owning feature loader/composer. Unknown or missing
  permissions, resources, guards, or declarations fail closed; the manifest is
  evidence generated from the registry and surface declarations, not a second
  policy source.
- PostgreSQL tests cover provisioning, grant, final-admin, revocation/command,
  and idempotency races.
- Live drill proves bootstrap, scoped admin grants, separate submitter,
  reviewer, and adjudicator grants and independent revocation,
  admin/contributor separation, same-token revocation, suspension/reactivation,
  service handling, cross-project denial, and final-admin safety.
- Adjudicator grant behavior is visible and independently revocable while all
  adjudication actions remain unavailable until WS-REV defines the lifecycle
  and AUTH activates exact adjudication actions; admin authority alone cannot
  submit, review, or adjudicate.
- Live drill implements the complete adopted specification sequence, including
  Finance and Audit Authority capability separation, Project Manager inability
  to review by admin role alone, self-grant/self-revoke denials, full authorized
  audit export, database constraint evidence, duplicate-profile absence,
  request/correlation/error and actor/grant IDs, and proof that no direct
  database authority edit occurred.
- The verifier/JWKS/introspection metrics implemented at the adapter boundary in
  chunk 02 are verified end to end. Initiative metrics also cover first
  access/conflicts, actor/link state, authorization decisions/denials,
  admin/project grants, invalidation backlog, and bootstrap attempts with
  bounded labels.
- Alerts cover sustained verification failure, unusable JWKS cache, repeated
  bootstrap/final-admin denial attempts, unusual grant mutation rate,
  invalidation backlog, and abnormal provisioning conflicts. The runbook names
  alert owner, diagnosis, recovery, escalation, and evidence retention.
- Existing full backend suite, API contract drill, lint, docstrings, docs gates,
  and internal review evidence pass.
- No dependency, test, coverage, lint, or configuration gate is weakened. Any
  production dependency change requires separately recorded explicit human
  approval before modification.
- No obsolete token-role authorization remains in runtime code.
- Initiative memory records proof and leaves `WS-POL-002-03` inactive until an
  explicit user resume signal.

## Verification commands

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/check_internal_review_evidence.py
(cd backend && .venv/bin/python -m ruff check app tests scripts)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q \
  tests/test_authorization.py tests/test_auth.py tests/test_actors.py \
  tests/test_projects.py tests/test_tasks.py tests/test_checkers.py \
  --cov=app.modules.authorization --cov-report=term-missing --cov-fail-under=90)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python scripts/api_contract_e2e.py)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python scripts/auth_api_e2e.py)
(cd backend && .venv/bin/docstr-coverage --config .docstr.yaml)
python3 scripts/check_stale_authorization.py
git diff --check
```

## Required reviewers

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

## Human review focus

Review the live evidence chain, same-token revocation, final-admin race proof,
permission matrix completeness, privacy, and confirmation that later initiatives
were not started.

## Stop conditions

Stop if real proof requires production secrets/data, direct SQL authority edits,
test weakening, an unapproved production dependency, or starting
review/compensation/WS-POL implementation.
