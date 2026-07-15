# Chunk Contract: WS-REV-001-13

## Goal

Perform fail-closed public lifecycle activation, run privacy-safe HTTP-visible
conformance drills, close active documentation, and prove the complete backend
review/revision lifecycle.

## Risk class

L1 release proof and documentation closure.

## Allowed files

```text
backend/scripts/review_lifecycle_{stack_preflight,live_drill,validate_evidence}.py
backend/tests/test_{reviews,contributions,compensation,authorization,api_contract_e2e,review_lifecycle_live_drill}.py only for final conformance gaps
backend/app/api/router.py only for one joint review/contribution/compensation registration
backend/app/modules/reviews/router.py only for final activation conformance
backend/app/modules/contributions/router.py only for final activation conformance
backend/app/modules/compensation/router.py only for final activation conformance
backend/app/modules/lifecycle_control/router.py only for final Operator control activation conformance
backend/app/modules/tasks/{schemas,service,router}.py only for Task Context/preparation acknowledgment and strict canonical revision cutover
backend/app/composition/review_lifecycle.py only for final fail-closed participant activation
backend/app/composition/joint_lifecycle_control.py only for final active command-class/binding activation
backend/alembic/versions/<activation-next>_strict_revision_cutover.py
backend/tests/test_alembic.py only for final revision-cutover migration proof
docs/architecture_*.md
docs/architecture_brief/**
docs/diagrams/**
docs/operations_*.md
docs/product_brief.md
docs/product_principles.md
docs/principles.md
docs/product_first_user_flows.md
docs/glossary.md
docs/roles_permissions.md
docs/template_review_packet.md
docs/template_revision_replay.md
docs/template_prior_feedback_checklist.md
docs/template_task_status.md
docs/template_project_guide.md
docs/template_task.md
docs/current_system_data_flow.html
README.md
.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/**
.agent-loop/merge-intents/WS-REV-001-13.json
```

## Not allowed

```text
new lifecycle behavior hidden inside proof scripts
frontend implementation
real secrets, private artifact content, local absolute paths, or personal IDs
provider or authorization bypass for the drill
reputation formula or deferred product scope
```

## Acceptance criteria

- HTTP drill proves first submission, needs revision, revision preparation,
  response evidence, preferred return, preference expiry/takeover, and accept.
- Separate drills prove reject, lease expiry, grant revocation during lease,
  finding evidence, artifact unavailable/integrity failure/recovery, projection
  retry, and WS-CON atomicity.
- Separate drills prove reason-bound preparation repair after guide correction,
  stale-head/concurrent repair behavior, and audited legacy unrecoverable closure
  without a fabricated Review or contribution.
- Reconciliation proof runs duplicate/concurrent scans, closure, and a controlled
  post-resolution recurrence and verifies one unresolved fingerprint generation,
  one resolution, stable alert/outbox effects, and generation N+1 only after the
  prior finding is resolved.
- Database and API audit evidence agree; no direct database mutation creates
  the claimed lifecycle result.
- Before registration, stack preflight proves merged AUTH/ART/CON, shared
  outbox, workers/schedules, MinIO protocol, migrations, and reconciliation are
  live. Production composition fails closed when any mandatory participant is
  absent.
- The exact merged WS-REV-12A release-control schema, phase history, advisory
  lock, command-class matrix, Operator action, and mandatory fence bindings are
  preflight inputs. REV-13 registers and exercises that foundation; it does not
  implement an alternate controller or store phase in a proof script.
- Preflight consumes WS-CON-11's exact merged SHA, migration head, ActionId and
  service-actor assignment, ART capability, outbox/worker, and handler manifest.
  Missing, extra, stale, or mismatched entries block startup and activation.
- A separate REV-owned activation manifest covers every human endpoint and
  asynchronous command with exact ActionId, PermissionId mapping, resource
  composer owner, allowed principal kind, service ActorProfile/system-principal
  assignment, transaction-revalidation rule, exact
  `JointLifecycleCommandClass`, and generation-aware phase policy. Internal
  checker admission, AUTH-13 replacement, and every operation-specific
  `review.reconcile.run` mode are manifest entries even when they share an
  ActionId. The shared-outbox review snapshot projection handler is a separate
  manifest entry under fixed `outbox.dispatch` authority. It includes at least
  `review.preference_expiry.run`, `review.lease_expiry.run`,
  `review.reconcile.run`, `review.artifact_reference.reconcile`, and
  `review.projection.rebuild`; missing, extra, ambiguous, caller-selected, stale,
  or mismatched mappings fail preflight and startup. The CON-11 manifest supplies
  the same fields for every joint contribution/compensation command.
- AUTH preflight also proves the four additive actions migrated typed catalogue,
  owner mapping, and PostgreSQL audit parity together from 50 to exactly 54,
  with no missing or extra action.
- Final registration exposes coherent current-work, claim, release, decline,
  context, decision, revision preparation/evidence, chain, and authorized admin
  operations alongside the existing canonical task resubmission endpoint.
  Shutdown advances the persisted 12A controller through every adjacent phase:
  `admission_fenced` blocks new submissions, queue admission, claims, and
  replacement while leased completion may finish; `commands_draining` blocks
  new completion commands and fresh Operator calls release remaining leases;
  `leases_released` lets already committed fulfillment dispatch drain;
  `delivery_draining` blocks new dispatch only after its pending/in-flight count
  is zero while authenticated callbacks finish; and `disabled` requires zero
  callback obligations. Routes, workers, and service assignments are then
  disabled in manifest order without deleting pending immutable work. The
  authenticated lifecycle-control transition/status route and its AUTH mapping
  remain available while disabled; all product routes, product workers, and
  product service assignments remain off. Queued review work remains durable
  for forward reactivation. REV-13 does not invent a second coordinator or
  attempt schema downgrade after protected rows exist.
- The same PR registers the reviewed contribution/compensation binding and
  policy operations, contribution/award/evidence reads, fulfillment callback,
  and bounded Finance/Operator operations under `/api/v1`. No review-only,
  contribution-only, `/v1` alias, or optional-participant activation occurs
  earlier.
- API proof includes the exact Project Manager D6 obligation-close and repair
  routes plus Operator legacy-close, their registered AUTH mappings/resource
  composers, PM cross-project/not-reached denial, Operator D6 denial,
  non-Operator legacy-close denial, stale/crossed head or finding denial, exact
  replay, and changed-replay conflict.
- Activation registers only the review-owned evidence-intake routes and installs
  frozen-preparation acknowledgment as an internal lifecycle guard of the
  existing canonical task submission command. The same commit unlocks that
  command's prepared, structured-response branch, removes the legacy
  direct-revision path, and adds neither a contributor/reviewer preparation
  route nor a second reviews resubmission route. The only preparation mutation
  route is the privileged chunk-11 successor-repair command. First submissions
  remain behaviorally unchanged.
- The same composition cutover makes the AUTH-13 replacement-assignment command
  depend on the typed review preparation-transfer participant whenever a
  Review-rooted revision obligation exists. The binding is non-optional: startup
  and the command fail closed if it is absent, and assignment plus preparation
  successor commit or roll back together. Tests cover absent binding, injected
  failure after each participant, replay, stale head, and concurrent
  replacement/repair/submission. Rollback first fences replacement assignment
  and drains in-flight commands; it never removes the participant while the
  AUTH-13 command can create a target assignment.
- The same atomic cutover migration adds the named PostgreSQL `NOT VALID` check
  requiring version 1 or a non-null preparation reference. Existing version>1
  rows remain immutable/readable, while every new or updated post-cutover row is
  checked. The service maps missing/stale preparation to a stable domain error;
  no `IntegrityError` escapes. Migration/API tests prove the pre-cutover legacy
  branch works before upgrade, the route and database guard switch together,
  new unprepared revisions fail, prepared revisions succeed, direct SQL cannot
  forge a legacy exemption, and downgrade is refused once post-cutover rows
  depend on the rule.
- Deployment does not pretend Alembic and process replacement are simultaneous.
  The Operator advances `pre_activation -> revision_cutover_fenced`, whose exact
  matrix allows initial submissions and checker admission but denies legacy and
  prepared revisions plus both replacement classes. The runbook drains and
  verifies no old writer remains, applies the migration, starts and verifies the
  prepared branch plus mandatory replacement-transfer binding, then advances to
  `active` to open prepared revision/replacement admission. A live ordering test
  holds an old writer at the fence and proves it cannot cross the migration/
  activation boundary or leak an IntegrityError.
- Existing Task Context responses expose the frozen current preparation ID,
  digest, guide/policy versions, and change summary during `needs_revision`.
  The canonical submission request acknowledges preparation ID/digest; neither
  request mutates preparation state.
- Full conformance suite, lint, docs, coverage, stale scans, and link checks pass.
- The live drill calls the authenticated Operator lifecycle-control route for
  every legal edge, proves every illegal/skipped edge, full phase/command matrix,
  N-to-N+1 reactivation with a new manifest and proof that no retired legacy
  revision/replacement writer revives, exact and changed replay, and crash
  after each durable-write boundary. It also proves timeout leaves phase
  unchanged, fresh retry, bounded lease release, dispatch denial before adapter
  I/O, callback in flight during delivery drain, and disable denial while any
  delivery/callback obligation remains.
- The drill runs fulfillment dispatch and ART-backed review projection against
  disable in both orderings: durable in-flight state precedes fence release,
  a disable attempt observes it, returns blocked with phase unchanged, and
  releases the exclusive lock. Provider I/O observes no lifecycle advisory lock
  or database transaction; crash returns work to retryable state; fenced
  finalization clears the observation; and a fresh Operator command advances
  without changing canonical Review/award truth.
- The joint drill also proves compensation binding/policy setup, TaskAssignment
  and ReviewLease freezes, reviewer contribution for all three decisions,
  accept-only submitter contribution, a second revision Review, paid and
  explicit-unpaid awards, outbound delivery/callback ordering, suspended or
  retired binding behavior, contribution-evidence privacy/rebuild,
  Finance-versus-Operator denials, atomic rollback, adapter/storage outage,
  replay, and reconciliation.
- Forward and backward Project Guide rebase leave the TaskAssignment
  compensation freeze unchanged; each new ReviewLease freezes reviewer terms
  independently and decision-neutral reviewer awards agree across
  `accept`/`needs_revision`/`reject` for the same frozen terms.
- Active docs use blocking/advisory findings, server-selected offer semantics,
  controlled rebase, canonical decisions, WS-CON boundaries, AWS S3/MinIO, and
  deferred reputation consistently.
- Evidence report contains only placeholder paths/IDs and approved bounded
  excerpts.
- A terminology/retirement matrix covers every review object and removes active
  high/medium/low, full-backlog, direct payment/reputation, and checker-as-human-
  decision wording. PlantUML, architecture brief PDF, and linked generated
  derivatives are regenerated and diff-verified.
- Initiative status, risks, decisions, review evidence, and trust bundle record
  what is proven and any explicitly deferred residual work.

## Verification

```text
cd backend && alembic upgrade head
cd backend && pytest -q tests/test_alembic.py tests/test_reviews.py tests/test_contributions.py tests/test_compensation.py tests/test_authorization.py tests/test_api_contract_e2e.py tests/test_review_lifecycle_live_drill.py
cd backend && ruff check app tests scripts
cd backend && docstr-coverage --config .docstr.yaml
docker compose up -d --wait postgres redis minio
cd backend && python scripts/review_lifecycle_live_drill.py --start-api-worker-beat --run-live-preflight --require-postgres --require-workers --require-minio --require-auth --require-con --require-outbox --base-url http://127.0.0.1:8000 --require-real-http --artifact-backend s3_compatible --evidence-out ../.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/evidence/live-drill.json
cd backend && python scripts/review_lifecycle_validate_evidence.py ../.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/evidence/live-drill.json
(metadata_dir="$(mktemp -d)" && trap 'rm -rf "$metadata_dir"' EXIT && (cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json "$metadata_dir/result.json" --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78))
cd backend && coverage report --include='app/modules/reviews/*,app/workers/reviews.py' --precision=2 --fail-under=90
cd backend && for path in app/api/router.py app/modules/contributions/router.py app/modules/compensation/router.py app/modules/lifecycle_control/router.py app/modules/tasks/schemas.py app/modules/tasks/service.py app/modules/tasks/router.py app/composition/review_lifecycle.py app/composition/joint_lifecycle_control.py; do coverage report --include="$path" --precision=2 --fail-under=90 || exit 1; done
./docs/diagrams/render_plantuml.sh
./docs/architecture_brief/render_pdf.sh
git diff --exit-code -- docs/diagrams docs/architecture_brief
sha256sum -c docs/reference_specs/SHA256SUMS
git check-attr diff merge text -- docs/reference_specs/*.pdf | awk '$3 != "unset" {bad=1} END {exit bad}'
python3 scripts/check_internal_review_evidence.py
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_review_contracts.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_authorization_docs.py
git diff --check
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
reuse/dedup, test-delta, and CI integrity if proof or coverage tooling changes.

## Human review focus

Evidence authenticity, no bypass, complete failure coverage, privacy scrub, and
clear distinction between proven lifecycle and deferred frontend/reputation.

## Stop condition

After merge and automated memory, mark the initiative complete only if every
definition-of-done item is proven. Do not start a frontend successor
automatically.
