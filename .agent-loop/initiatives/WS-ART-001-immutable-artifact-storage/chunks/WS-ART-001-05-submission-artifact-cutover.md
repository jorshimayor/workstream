# WS-ART-001-05: Submission Artifact Cutover

Parent: `WS-ART-001` | Repository: Workstream | Risk: L1 | SLA: P0

Dependency: `WS-ART-001-04` and merged WS-AUTH task/submission cutovers.

## Goal

Atomically consume one valid admission/session into an immutable submission and
remove all legacy URI/caller-authoritative hash contracts.

## Allowed Files

- `backend/app/modules/tasks/**`, artifact integration, audit schemas
- `backend/app/modules/checkers/models.py`
- `backend/app/modules/checkers/compiler.py`
- `backend/app/modules/checkers/runner.py`
- `backend/app/modules/checkers/schemas.py`
- `backend/app/modules/checkers/service.py`
- `backend/app/modules/checkers/repository.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/adapters/project_agents/openai_agent_sdk.py`
- `backend/app/interfaces/project_agents.py`
- `backend/tests/test_checkers.py`
- `backend/tests/test_projects.py`
- `backend/tests/test_agent_runtime.py`
- one destructive submission-owned migration
- task/artifact/alembic/API contract tests
- `docs/spec_chunk_5_submission_packet_foundation.md`
- `docs/decision_0011_submission_artifact_policy_drives_pre_submit.md`
- `docs/architecture_data_model.md`, `docs/architecture_checker_framework.md`
- `docs/spec_chunk_8_submission_artifact_policy_checkers.md`
- `docs/template_submission_artifact_policy.md`
- `docs/template_submission_packet.md`, `docs/template_checker_policy.md`
- `docs/glossary.md`, `docs/current_system_data_flow.html`
- `scripts/check_stale_artifact_contracts.py`

## Not Allowed

No compatibility alias/read, post-submit checker retrieval, review lifecycle,
or backfill of declarations as verified evidence.

## Acceptance Criteria

- One transaction revalidates actor/grant, assignment/task/context, admission
  expiry/hash, verified retained replicas, and locks/CAS-consumes every row.
- Submission/binding audit evidence continues through the shared
  `AuditRepository`; legacy artifact-manifest hashing helpers are removed and
  canonical input/artifact-set hashes use the shared central helper.
- Exactly one concurrent submission wins; loser creates no submission/binding
  changes. Replay, expiry, revocation, policy drift, cross-task/actor all fail.
- Deterministic pre-submit policy failure still creates no submission.
- Request becomes `summary`, `contributor_attestation`, `upload_session_id`; server
  owns artifact set/hash and evidence IDs.
- Canonical `required_packet_fields` becomes exactly `summary`,
  `contributor_attestation`, and `upload_session_id` for both precheck and
  submission creation; the passing admission binds their exact canonical input
  hash and changed input requires a new precheck.
- `package_uri`, `package_hash`, `artifact_hash_manifest`, and evidence
  URI/hash/size fields are removed from schemas/models/audits/tests/docs.
- `worker_attestation` is replaced by canonical `contributor_attestation` with
  no compatibility alias.
- Project policy removes `manifest_required`, `artifact_hash_required`,
  `artifact_hash_algorithm`, and `allowed_storage_schemes`; sealed manifests,
  server SHA-256, and the configured storage provider are unconditional
  Workstream invariants, not project choices.
- The trusted compiler/runner removes URI/hash/manifest declaration primitives
  and uses `validate_sealed_artifact_set` plus the retained project semantic
  artifact/evidence, forbidden, attestation, limit, and packaging rules.
- The project-agent output schema and prompt stop generating every removed
  policy field. ADR 0011, policy templates/specs, and checker architecture are
  updated in the same chunk to mark ADR 0013's storage/hash provisions as the
  superseding contract; no accepted document continues to require the rejected
  primitives.
- Existing approved/effective policies, compiled pre-submit bundles, and
  locked/active tasks carrying the rejected contract cause a fail-closed
  preflight with pre-production rebuild/regeneration guidance. No old bundle is
  executed against the new submission API.
- Checker-run declaration columns that copy package/hash input are removed in
  this same destructive migration and replaced by the canonical
  `artifact_set_id`/`artifact_set_hash` bridge. WS-ART-001-06 owns retrieval,
  `CheckerInputSnapshot`, logs, and outputs, not this schema cleanup.
- Populated legacy submission/evidence/checker data refuses migration with
  rebuild guidance; fresh/downgrade-empty/re-upgrade tests pass.

## Verification

```bash
(cd backend && .venv/bin/ruff check app tests scripts)
(cd backend && .venv/bin/docstr-coverage --config .docstr.yaml)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q tests/test_tasks.py tests/test_artifacts.py tests/test_checkers.py tests/test_projects.py tests/test_alembic.py)
(cd backend && WORKSTREAM_TEST_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/pytest -q)
(cd backend && WORKSTREAM_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/workstream_test .venv/bin/python scripts/api_contract_e2e.py)
python3 scripts/test_agent_gates.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/check_loop_memory_state.py
python3 scripts/check_internal_review_evidence.py
git diff --check
```

Reviewers: all required tracks.

Human focus: transaction/concurrency proof, complete legacy removal, API shape,
and no changed lifecycle meaning. Stop after this PR.
