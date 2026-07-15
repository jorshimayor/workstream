# Chunk Contract: WS-REV-001-12

## Goal

Deliver deterministic review snapshot projection, notification events,
artifact-reference reconciliation, and bounded operational observability.

## Risk class

L1 asynchronous delivery, privacy, and operations.

## Allowed files

```text
backend/app/modules/reviews/{ports,repository,schemas,service,projection}.py
backend/app/workers/{celery_app,reviews}.py
backend/app/core/config.py only for bounded worker settings
backend/tests/test_{reviews,artifacts,audit,config}.py
docs/operations_reviewer_workflow.md
docs/operations_operator_workflow.md
docs/operations_queue_policy.md
.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/**
.agent-loop/merge-intents/WS-REV-001-12.json
```

## Not allowed

```text
remote storage call in decision transaction
projection as canonical Review truth
unbounded reviewer IDs or finding text in public metric labels/logs
notification provider implementation beyond existing adapter convention
review decision changes on projection failure
production `/api/v1` review-router registration
```

## Acceptance criteria

- Projection bytes are deterministic for Review ID and schema version.
- Same operation/bytes replay one logical receipt; changed bytes conflict.
- Worker retry/dead-letter/reconciliation changes only delivery status.
- The shared outbox dispatcher remains the sole event claimant and owner of
  attempt, retry, dead-letter, and delivery status. Reviews registers only a
  typed deterministic projection handler and relies on ART receipts; no review
  polling loop, attempt table, or dead-letter ledger is created.
- Search/projection reads are reauthorized through Workstream.
- Artifact-reference reconciliation declares
  `review.artifact_reference.reconcile`; an authorized projection rebuild
  declares `review.projection.rebuild`. Both call the centralized
  `AuthorizationService.require` boundary with system or Operator context as
  defined by their activation guards.
- Artifact relation reconciliation covers verification, project/task scope,
  retention, missing projection, receipt mismatch, uncertainty, and unavailable
  retained content without editing canonical history.
- Required queue, lease, decision, authorization, evidence, projection, and lag
  metrics exist with bounded cardinality.
- Reviews exposes a typed, same-session `ReviewLifecycleDrainObservationPort`
  that returns server-derived active-lease and review-maintenance counts under
  canonical review locks. It is read-only, never commits, advances no lifecycle
  phase, imports no lifecycle-control type, and is named in chunk 12 evidence so
  12A can consume it through composition.
- Administrative read models include open/preferred depth, oldest preferred
  age, approaching-expiry leases, expired/released/invalidation counts, and
  bounded turnaround distributions.
- Notification events explicitly cover preference nearing expiry, lease nearing
  expiry, lease expired, preferred routing, decisions, and every authority
  invalidation cause without coupling lifecycle to a delivery provider.
- Audit, shared outbox, dead-letter, alerts, errors, logs, and metrics retain
  only bounded typed identifiers/reasons and never finding text, private
  artifact metadata, signed access, provider paths, or secrets.
- Production OpenAPI remains free of lifecycle routes.
- Operator docs enumerate every projection/notification worker variable,
  bounded default, schedule/worker command, retry/dead-letter alert, rollout,
  drain, and rollback behavior in the same chunk.
- Projection handlers reuse `run_async_task`, fresh worker engine/session
  disposal, stable task IDs, and `sync_task_settings`; no second async bridge,
  session factory, or queue helper is introduced.

## Verification

```text
cd backend && pytest -q tests/test_reviews.py tests/test_artifacts.py tests/test_audit.py tests/test_config.py
cd backend && ruff check app/modules/reviews app/workers/reviews.py tests/test_reviews.py
(metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78))
cd backend && coverage report --include='app/modules/reviews/*,app/workers/reviews.py' --precision=2 --fail-under=90
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
reuse/dedup, and test-delta.

## Human review focus

Canonical/projection separation, deterministic bytes, privacy, dead-letter
operations, and metric usefulness.

## Stop condition

Merge, record automated memory, and stop. Do not start 12A.
