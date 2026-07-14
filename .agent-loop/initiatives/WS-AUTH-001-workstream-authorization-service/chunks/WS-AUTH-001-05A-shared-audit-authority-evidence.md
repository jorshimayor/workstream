# Chunk Contract: WS-AUTH-001-05A - Shared Audit Ownership And Append-Only Authority Evidence

## Status

Active for contract repair and required preimplementation review. Runtime edits
remain prohibited until that review passes.

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Evolve the existing `audit_events` path into one privacy-safe, append-only,
versioned authority-evidence envelope while preserving every legacy lifecycle
event and existing task/checker behavior.

## Risk and circuit breaker

- Risk: L1 / SLA P1.
- Inspect scope at 350 changed non-comment production lines.
- Hard stop at 500 changed non-comment production lines, counting
  `backend/app/**` plus migration code; tests and evidence do not justify
  exceeding the production limit.

## Allowed files

```text
backend/app/modules/audit/**
backend/app/db/models.py
backend/app/modules/tasks/models.py
backend/app/modules/tasks/repository.py
backend/alembic/versions/0018_authority_audit_evidence.py
backend/tests/test_audit.py
backend/tests/test_alembic.py
backend/tests/test_tasks.py
docs/architecture_data_model.md
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

`backend/tests/test_tasks.py` may receive only bounded delegation/regression
proof; the existing full task suite remains an unchanged regression target.

## Not allowed

```text
authorization idempotency records or replay orchestration
routes, dependencies, middleware, or generic core helpers
actor/profile migration or first-access behavior
permission definitions/evaluation or admin/project grants
project/task/submission/checker authorization cutover
invalidation consumers, caches, queues, or external delivery
token-role or IdentityIssuerVerifier/factory changes
workflow, dependency, coverage-threshold, skip, or exclusion changes
backfilled or fabricated authority history
repository or service commit/rollback/session creation
```

## Authority event envelope

Migration `0018_authority_audit_evidence` revises `0017_api_controls` and
extends the existing `audit_events` table. It does not create a parallel event
table. Existing rows and legacy writers retain their current values and public
behavior; no legacy row is reclassified as authority evidence.

New rows use `event_domain = authority`, `event_version = 1`, and a typed event
token from the adopted specification. Authority rows require:

- database-owned `occurred_at`;
- `request_id` and `correlation_id` UUIDs;
- namespaced acting reference kind (`legacy_actor`, `actor_profile`, or
  `system_principal`) plus stable opaque reference;
- optional target actor reference with all-or-none kind/reference presence;
- optional matched-grant, permission, project, resource type/id, and target
  grant/link reference;
- optional bounded reason and denial code;
- optional idempotency-record reference;
- optional invalidation cause event and invalidation target kind/id;
- typed shallow before/after fact objects.

Authority rows never persist external issuer, external subject, token roles,
claim snapshots, request bodies, raw tokens, JWKS documents, secrets, emails,
or URLs. Legacy claim fields are nullable only to permit authority rows and
must be `NULL`, `[]`, or `{}` as appropriate for the authority domain.
Conditional database constraints reject mixed legacy/authority shapes.

Reference/type/reason tokens have explicit length and character bounds.
Before/after facts are JSON objects with at most 16 allowlisted scalar keys,
no nested containers, and at most 4096 encoded bytes per object. The typed
writer applies per-event allowed-key sets; database checks enforce object type
and byte bounds.

## Shared writer and append-only custody

- `AuditRepository` is the only supported insert/read implementation.
- `TaskRepository.add_audit_event` and `list_audit_events` remain temporary
  compatibility methods but delegate the same session/event/query to
  `AuditRepository`; task/checker call sites and responses do not change.
- Supported application APIs expose insert/read only.
- Named PostgreSQL triggers reject every `audit_events` UPDATE, DELETE, and
  TRUNCATE, regardless of event domain or session flag. Failed attempts leave
  both legacy and authority rows unchanged.
- No application-settable GUC or current-user bypass exists.
- The protection is a normal-DML custody boundary, not a defense against the
  table owner or DDL credentials. Production rollout requires a distinct
  non-owner runtime role without trigger/DDL privileges. The runbook documents
  that deployment gate and a separately controlled DB-owner maintenance
  procedure using an exclusive lock, explicit trigger disable/re-enable,
  transaction, change record, and post-check. Migration teardown is the only
  ordinary trigger-removal path.

## Migration custody

- Upgrade `0017 -> 0018` preserves representative populated prior-head domain
  and legacy audit rows without fabricating authority fields.
- Tests assert exact columns, nullability, defaults, constraints, indexes,
  trigger/function names, invalid direct inserts, and database time.
- Downgrade takes writer-blocking locks before inspection and refuses without
  mutation when any authority-domain audit row exists.
- Privileged test cleanup may delete only explicit fixture authority rows after
  deliberately disabling/re-enabling the trigger under lock; legacy rows are
  never deleted by downgrade.
- Empty authority evidence permits `0018 -> 0017 -> 0018`; re-upgrade recreates
  all triggers. Destructive migration tests restore Alembic `head` in `finally`.

## Acceptance criteria

- Legacy audit writers/readers and task/checker response projections remain
  behaviorally unchanged.
- Typed allowed, denied, and invalidation authority event shapes persist only
  bounded non-sensitive evidence and reject malformed/mixed shapes.
- Application-role normal DML cannot update, delete, or truncate any audit row.
- Shared-writer tests instrument `AuditRepository` and prove TaskRepository
  compatibility methods pass the same session/event and return the shared
  result; row-count-only proof is insufficient.
- No new route, dependency, middleware, permission, grant, actor, product
  authority behavior, or invalidation consumer exists.

## Verification

```bash
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && isolated PostgreSQL: pytest -q tests/test_alembic.py::<0018-proof> tests/test_audit.py tests/test_tasks.py::<delegation-proof>)
(cd backend && focused AUTH-05A coverage >= 90 percent)
(cd backend && isolated full suite --cov=app --cov-fail-under=78)
(cd backend && .venv/bin/docstr-coverage --config .docstr.yaml)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_markdown_links.py
python3 scripts/check_internal_review_evidence.py
git diff --check
```

Run the exact migration node before audit/delegation tests on the same isolated
database. Test delta must be additive: no assertion, raises, skip, xfail,
threshold, workflow, or exclusion weakening.

## Required reviewers

- senior engineering
- QA/test
- security/auth and privacy
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

## Human review focus

Review legacy audit compatibility, sole writer ownership, authority-envelope
privacy, unconditional normal-DML immutability, migration custody, and the
documented non-owner production role requirement.

## Stop conditions

Stop if legacy event behavior changes, authority evidence needs a canonical
ActorProfile FK, normal application DML can mutate history, production scope
exceeds the circuit breaker, or tests/CI must be weakened.
