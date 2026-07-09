# WS-POL-001-16 Live API Drill Evidence

## Verdict

PASS.

The final clean Terminal Benchmark drill ran through public/operator HTTP APIs
without database inspection as lifecycle proof.

This is privacy-redacted public evidence. The source fixture came from private
local operator material, so exact fixture ids, local database UUIDs,
source-material hashes, package hashes, artifact byte counts, and
source-specific task identifiers are replaced with explicit redaction
placeholders. The placeholders are not replayable API literals.

Final state:

```text
project_id: <redacted-id>
guide_id: <redacted-id>
source_snapshot_id: <redacted-id>
source_snapshot_hash: sha256:<redacted>
sufficiency_status: passed
submission_artifact_policy_hash: sha256:<redacted>
effective_policy_hash: sha256:<redacted>
pre_submit_checker_bundle_hash: sha256:<redacted>
task_id: <redacted-id>
submission_id: <redacted-id>
checker_run_id: <redacted-id>
final_task_status: review_pending
```

## Local Stack

- FastAPI: `127.0.0.1:8008`
- Postgres: local Docker Compose service, `workstream_test`
- Redis: local Docker Compose service
- Celery: `app.workers.celery_app`, queue `celery`
- Auth: local Flow-compatible HMAC tokens, values not printed or committed
- Agent runtime: OpenAI Agents SDK adapter with `gpt-5.5`
- Secrets: all bearer tokens and API keys redacted; no token value appears in
  this evidence.

Database access was used only for migration reset. Lifecycle proof below comes
from HTTP responses.

## Source Material

Fixture label:

```text
Terminal Benchmark reference fixture
```

Fixture id:

```text
<redacted-fixture-id>
```

Before the final API run, source text was sanitized so raw local filesystem
paths were not sent to Workstream. The clean request/response capture was
scanned for `/home/` and passed.

Guide body:

```text
content_markdown_hash: sha256:<redacted>
content_markdown_bytes: <redacted>
```

Source snapshot manifest:

| Label | Durable ref | Hash | Bytes |
|---|---|---:|---:|
| `PROJECT_GUIDE.md` | `import:/fixtures/<redacted-fixture-id>/PROJECT_GUIDE.md` | `sha256:<redacted>` | <redacted> |
| `REVIEWER_PROGRAM.md` | `import:/fixtures/<redacted-fixture-id>/REVIEWER_PROGRAM.md` | `sha256:<redacted>` | <redacted> |
| `task.toml` | `import:/fixtures/<redacted-fixture-id>/task.toml` | `sha256:<redacted>` | <redacted> |
| `review_packet.md` | `import:/fixtures/<redacted-fixture-id>/review_packet.md` | `sha256:<redacted>` | <redacted> |
| `static_guard.txt` | `import:/fixtures/<redacted-fixture-id>/static_guard.txt` | `sha256:<redacted>` | <redacted> |
| `docker_build.log` | `import:/fixtures/<redacted-fixture-id>/docker_build.log` | `sha256:<redacted>` | <redacted> |
| `oracle_test.log` | `import:/fixtures/<redacted-fixture-id>/oracle_test.log` | `sha256:<redacted>` | <redacted> |
| `starter_m1_test.log` | `import:/fixtures/<redacted-fixture-id>/starter_m1_test.log` | `sha256:<redacted>` | <redacted> |

## HTTP Transcript

Large guide content, exact hashes, local identifiers, and exact byte counts are
redacted as source-material fingerprints. The table below is an ordered index;
full privacy-redacted request and response bodies for every step are recorded
in the Redacted HTTP Body Appendix.

| Step | Method and path | HTTP |
|---|---|---:|
| `01_project_create` | `POST /api/v1/projects` | 201 |
| `02_guide_create` | `POST /api/v1/projects/{project_id}/guides` | 201 |
| `03_setup_poll_01..14` | `GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` | 200 |
| `04_sufficiency_report` | `GET /api/v1/projects/{project_id}/guides/{guide_id}/sufficiency-reports/{report_id}` | 200 |
| `05_submission_artifact_policy` | `GET /api/v1/projects/{project_id}/guides/{guide_id}/submission-artifact-policies/{policy_id}` | 200 |
| `06_approve_policy` | `POST /api/v1/projects/{project_id}/guides/{guide_id}/submission-artifact-policies/{policy_id}/approve` | 200 |
| `07_effective_policy` | `GET /api/v1/projects/{project_id}/guides/{guide_id}/effective-submission-artifact-policy` | 200 |
| `08_pre_submit_checker_policy` | `GET /api/v1/projects/{project_id}/guides/{guide_id}/pre-submit-checker-policy` | 200 |
| `09_activate_guide` | `POST /api/v1/projects/{project_id}/guides/{guide_id}/activate` | 200 |
| `10_task_create` | `POST /api/v1/projects/{project_id}/tasks` | 201 |
| `11_task_screen` | `POST /api/v1/tasks/{task_id}/screen` | 200 |
| `12_locked_context_after_screen` | `GET /api/v1/tasks/{task_id}/locked-context` | 200 |
| `13_task_release` | `POST /api/v1/tasks/{task_id}/release` | 200 |
| `14_worker_profile` | `POST /api/v1/workers/me/profile` | 200 |
| `15_task_claim` | `POST /api/v1/tasks/{task_id}/claim` | 200 |
| `16_task_start` | `POST /api/v1/tasks/{task_id}/start` | 200 |
| `17_locked_context_after_start` | `GET /api/v1/tasks/{task_id}/locked-context` | 200 |
| `18_work_context` | `GET /api/v1/tasks/{task_id}/work-context` | 200 |
| `19_submission_requirements` | `GET /api/v1/tasks/{task_id}/submission-requirements` | 200 |
| `20_precheck_blocked` | `POST /api/v1/tasks/{task_id}/submission-precheck` | 200 |
| `21_submission_blocked_create` | `POST /api/v1/tasks/{task_id}/submissions` | 422 |
| `22_submissions_after_blocked` | `GET /api/v1/tasks/{task_id}/submissions` | 200 |
| `23_audit_after_blocked` | `GET /api/v1/tasks/{task_id}/audit-events` | 200 |
| `24_precheck_success` | `POST /api/v1/tasks/{task_id}/submission-precheck` | 200 |
| `25_submissions_after_success_precheck` | `GET /api/v1/tasks/{task_id}/submissions` | 200 |
| `26_submission_success_create` | `POST /api/v1/tasks/{task_id}/submissions` | 201 |
| `27_submissions_after_success_create` | `GET /api/v1/tasks/{task_id}/submissions` | 200 |
| `28_submission_finalize_worker_forbidden` | `POST /api/v1/submissions/{submission_id}/finalize` | 403 |
| `29_submission_finalize_manager` | `POST /api/v1/submissions/{submission_id}/finalize` | 200 |
| `30_submission_get_after_finalize` | `GET /api/v1/submissions/{submission_id}` | 200 |
| `31_checker_runs_after_finalize` | `GET /api/v1/submissions/{submission_id}/checker-runs` | 200 |
| `32_checker_run_get` | `GET /api/v1/checker-runs/{checker_run_id}` | 200 |
| `33_audit_after_finalize` | `GET /api/v1/tasks/{task_id}/audit-events` | 200 |
| `34_task_get_after_finalize` | `GET /api/v1/tasks/{task_id}` | 200 |

## Setup Run

Setup poll statuses:

```json
[
  {"poll": 1, "status": "queued"},
  {"poll": 2, "status": "running_sufficiency_agent"},
  {"poll": 3, "status": "running_sufficiency_agent"},
  {"poll": 4, "status": "running_sufficiency_agent"},
  {"poll": 5, "status": "running_policy_derivation_agent"},
  {"poll": 6, "status": "running_policy_derivation_agent"},
  {"poll": 7, "status": "running_policy_derivation_agent"},
  {"poll": 8, "status": "running_policy_derivation_agent"},
  {"poll": 9, "status": "running_policy_derivation_agent"},
  {"poll": 10, "status": "running_policy_derivation_agent"},
  {"poll": 11, "status": "running_policy_derivation_agent"},
  {"poll": 12, "status": "running_policy_derivation_agent"},
  {"poll": 13, "status": "running_policy_derivation_agent"},
  {"poll": 14, "status": "policy_draft_ready"}
]
```

Sufficiency-agent input:

```json
{
  "input_type": "GuideSourceMaterial",
  "project_id": "<redacted-id>",
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "source_snapshot_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "guide_material": {
    "content_markdown": {
      "hash": "sha256:<redacted>",
      "bytes": "<redacted>"
    }
  },
  "source_items": [
    ["project_guide", "import:/fixtures/<redacted-fixture-id>/PROJECT_GUIDE.md", "sha256:<redacted>"],
    ["reviewer_program", "import:/fixtures/<redacted-fixture-id>/REVIEWER_PROGRAM.md", "sha256:<redacted>"],
    ["task_material", "import:/fixtures/<redacted-fixture-id>/task.toml", "sha256:<redacted>"],
    ["review_packet", "import:/fixtures/<redacted-fixture-id>/review_packet.md", "sha256:<redacted>"],
    ["static_guard", "import:/fixtures/<redacted-fixture-id>/static_guard.txt", "sha256:<redacted>"],
    ["build_log", "import:/fixtures/<redacted-fixture-id>/docker_build.log", "sha256:<redacted>"],
    ["test_log", "import:/fixtures/<redacted-fixture-id>/oracle_test.log", "sha256:<redacted>"],
    ["test_log", "import:/fixtures/<redacted-fixture-id>/starter_m1_test.log", "sha256:<redacted>"]
  ],
  "representative_task_material": {
    "items": []
  }
}
```

Sufficiency-agent output:

```text
status: passed
agent_name: ProjectGuideSufficiencyAgent
source_snapshot_hash: sha256:<redacted>
```

Submission-policy-derivation input:

```json
{
  "guide_source_material": "same GuideSourceMaterial envelope shown above",
  "sufficiency_report": {
    "status": "guide_sufficient",
    "findings": [],
    "summary_hash": "sha256:<redacted>",
    "agent_name": "ProjectGuideSufficiencyAgent",
    "agent_version": "workstream-sufficiency-agent-v0.1"
  }
}
```

Submission-policy-derivation output:

```text
derivation_source: agent_derivation
policy_hash: sha256:<redacted>
```

Final live submission requirements:

```json
{
  "required_artifacts": [
    "environment/Dockerfile",
    "environment/.dockerignore",
    "rubric.md",
    "task.toml"
  ],
  "required_evidence": [
    "dependency_pinning_review",
    "environment_hygiene_review",
    "instructions_present",
    "reward_footer_review",
    "solution_present",
    "submission_explanations",
    "test_alignment_review",
    "tests_present"
  ],
  "attestation_terms": [
    "all_or_nothing_reward",
    "confidential_data_exclusion",
    "container_bases_digest_pinned",
    "credentials_and_secret_exclusion",
    "dependencies_pinned",
    "hashes_sha256",
    "human_accountability_for_agent_assisted_work",
    "manifest_complete",
    "no_generated_caches",
    "no_reviewer_only_material",
    "no_sensitive_local_material",
    "offline_verifier_dependencies",
    "original_work",
    "task_layout_matches_metadata"
  ]
}
```

Compiled project pre-submit checker policy:

```text
compiled_bundle_hash: sha256:<redacted>
checker_names:
- check_submission_packet
- check_forbidden_files
- check_confidentiality_attestation
- check_required_files
- check_evidence_present
- check_evidence_integrity
- check_low_quality_generated_artifacts
```

## Task Context

Task creation request used the current task contract only:

```json
{
  "title": "Terminal Benchmark <redacted-fixture-id> live-api",
  "task_type": "terminal_benchmark",
  "difficulty": "medium",
  "skill_tags": ["rust", "json", "<redacted-domain-tag>", "containers", "cli"],
  "source_type": "manual",
  "source_ref": "terminal-benchmark/<redacted-fixture-id>/live-api/<redacted-run-id>",
  "external_task_id": "<redacted-fixture-id>"
}
```

Locked task context after screening included:

```text
locked_guide_version: v1
locked_guide_source_snapshot_hash: sha256:<redacted>
locked_effective_project_submission_artifact_policy_hash: sha256:<redacted>
locked_pre_submit_checker_bundle_hash: sha256:<redacted>
```

Worker work context reported:

```text
status: in_progress
assigned_to_current_actor: true
can_run_pre_submit_check: true
can_submit: true
```

## Blocked Pre-Submit Path

Blocked request intentionally omitted `environment/.dockerignore` from
`artifact_hash_manifest` while preserving the required evidence and
attestation.

Pre-submit response:

```json
{
  "authoritative": false,
  "status": "failed",
  "eligible_to_submit": false,
  "failed_checkers": ["check_required_files"]
}
```

Submission creation response:

```json
{
  "code": "pre_submission_checker_failed",
  "details": {
    "authoritative": false,
    "status": "failed",
    "eligible_to_submit": false,
    "failed_checkers": ["check_required_files"]
  }
}
```

No-side-effect proof:

```text
GET /tasks/{task_id}/submissions after blocked create: []
GET /tasks/{task_id}/audit-events after blocked create:
- pre_submission_check_failed is present
- submission_created is absent
- pre_review_gate_started is absent
```

There is no valid checker-run list endpoint before a submission id exists.
Durable checker-run visibility is submission-scoped by API design, so the
blocked create proof uses the task submission list plus task audit events. The
successful create and finalize path then proves checker-run list/get visibility
once a submission id exists.

## Successful Submission Path

Success pre-submit response:

```json
{
  "authoritative": false,
  "status": "passed",
  "eligible_to_submit": true,
  "results": [
    ["check_submission_packet", "passed"],
    ["check_forbidden_files", "passed"],
    ["check_confidentiality_attestation", "passed"],
    ["check_required_files", "passed"],
    ["check_evidence_present", "passed"],
    ["check_evidence_integrity", "passed"],
    ["check_low_quality_generated_artifacts", "passed"]
  ]
}
```

Non-authoritative proof:

```text
GET /tasks/{task_id}/submissions after success precheck: []
```

Submission create:

```text
HTTP: 201
submission_id: <redacted-id>
version: 1
```

Worker finalize attempt:

```text
HTTP: 403
detail: actor lacks required role
```

Project manager finalize:

```text
HTTP: 200
finalized_at: present
```

## Checker Runs

Checker run list and get both returned:

```json
{
  "id": "<redacted-id>",
  "status": "completed",
  "routing_recommendation": "allow_review",
  "passed_count": 8,
  "warning_count": 0,
  "failed_count": 0,
  "blocking_count": 0,
  "triggered_by": "workstream-system:pre-review-gate"
}
```

Durable checker results:

```text
check_submission_packet: passed
check_policy_context_present: passed
check_evidence_present: passed
check_evidence_integrity: passed
check_required_files: passed
check_forbidden_files: passed
check_confidentiality_attestation: passed
check_low_quality_generated_artifacts: passed
```

Final task response:

```text
status: review_pending
locked_guide_source_snapshot_hash: sha256:<redacted>
locked_effective_project_submission_artifact_policy_hash: sha256:<redacted>
locked_pre_submit_checker_bundle_hash: sha256:<redacted>
```

## Audit Events

Final task audit event sequence:

```text
task_created: null -> draft
task_status_changed: draft -> screening
task_status_changed: screening -> ready
task_status_changed: ready -> claimed
task_status_changed: claimed -> in_progress
pre_submission_check_failed: in_progress -> in_progress
submission_created: in_progress -> submitted
submission_finalized: submitted -> submitted
pre_review_gate_started: submitted -> evaluation_pending
pre_review_gate_passed: evaluation_pending -> review_pending
```

## Redacted HTTP Body Appendix

Every step below records the HTTP method/path, request body, and response body from the final clean run. `null` request body means the call had no JSON body. Large guide/source text is redacted to hash and byte count; credentials were not recorded.
### 01_project_create

`POST /api/v1/projects` -> HTTP `201`

Request body:

```json
{
  "description": "Real Terminal Benchmark fixture used as Workstream API evidence with sanitized source text.",
  "name": "Terminal Benchmark Real API <redacted-run-id>",
  "slug": "terminal-benchmark-real-api-<redacted-run-id>"
}
```

Response body:

```json
{
  "created_at": "2026-07-08T23:43:31.535968Z",
  "description": "Real Terminal Benchmark fixture used as Workstream API evidence with sanitized source text.",
  "id": "<redacted-id>",
  "name": "Terminal Benchmark Real API <redacted-run-id>",
  "slug": "terminal-benchmark-real-api-<redacted-run-id>",
  "status": "draft",
  "updated_at": "2026-07-08T23:43:31.535968Z"
}
```

### 02_guide_create

`POST /api/v1/projects/{project_id}/guides` -> HTTP `201`

Request body:

```json
{
  "change_summary": "Initial Terminal Benchmark real-world guide from sanitized imported source snapshot bundle.",
  "content_markdown": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
  "payment_policy": {
    "accepted_payment_rule": "pay_on_acceptance",
    "base_amount": "25.00",
    "currency": "USD",
    "payout_type": "fixed",
    "rejection_payment_rule": "no_payment_on_reject",
    "revision_payment_rule": "no_extra_payment_for_revisions"
  },
  "post_submit_checker_policy": {
    "blocking_severities": [
      "high",
      "medium"
    ],
    "required_checkers": [
      "check_policy_context_present",
      "check_low_quality_generated_artifacts"
    ],
    "warning_checkers": []
  },
  "review_policy": {
    "allowed_decisions": [
      "accept",
      "needs_revision",
      "reject"
    ],
    "minimum_finding_fields": [
      "issue",
      "required_fix"
    ],
    "requires_second_review": false,
    "sla_hours": 24
  },
  "revision_policy": {
    "allowed_resubmission_states": [
      "needs_revision"
    ],
    "auto_reject_after_limit": true,
    "max_revision_rounds": 7,
    "reviewer_reassignment_rule": "same_reviewer_preferred",
    "revision_deadline_hours": 48
  },
  "source_snapshot": {
    "items": [
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
        "content_hash": "sha256:<redacted>",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/PROJECT_GUIDE.md",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/markdown",
        "source_kind": "project_guide"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
        "content_hash": "sha256:<redacted>",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/REVIEWER_PROGRAM.md",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/markdown",
        "source_kind": "reviewer_program"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
        "content_hash": "sha256:<redacted>",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/task.toml",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/toml",
        "source_kind": "task_material"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
        "content_hash": "sha256:<redacted>",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/review_packet.md",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/markdown",
        "source_kind": "review_packet"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
        "content_hash": "sha256:<redacted>",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/static_guard.txt",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/plain",
        "source_kind": "checker_evidence"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
        "content_hash": "sha256:<redacted>",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/docker_build.log",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/plain",
        "source_kind": "checker_evidence"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
        "content_hash": "sha256:<redacted>",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/oracle_test.log",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/plain",
        "source_kind": "checker_evidence"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
        "content_hash": "sha256:<redacted>",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/starter_m1_test.log",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/plain",
        "source_kind": "checker_evidence"
      }
    ]
  },
  "version": "v1"
}
```

Response body:

```json
{
  "approved_by": null,
  "change_summary": "Initial Terminal Benchmark real-world guide from sanitized imported source snapshot bundle.",
  "content_markdown": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "effective_at": null,
  "id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "status": "draft",
  "superseded_at": null,
  "updated_at": "2026-07-08T23:43:31.606777Z",
  "version": "v1"
}
```

### 03_setup_poll_01

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "queued",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": null,
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": null,
  "status": "queued",
  "updated_at": "2026-07-08T23:43:31.799970Z"
}
```

### 03_setup_poll_02

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "guide_sufficiency",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": null,
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_sufficiency_agent",
  "updated_at": "2026-07-08T23:43:32.263663Z"
}
```

### 03_setup_poll_03

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "guide_sufficiency",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": null,
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_sufficiency_agent",
  "updated_at": "2026-07-08T23:43:32.263663Z"
}
```

### 03_setup_poll_04

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "guide_sufficiency",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": null,
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_sufficiency_agent",
  "updated_at": "2026-07-08T23:43:32.263663Z"
}
```

### 03_setup_poll_05

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_policy_derivation_agent",
  "updated_at": "2026-07-08T23:43:40.681014Z"
}
```

### 03_setup_poll_06

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_policy_derivation_agent",
  "updated_at": "2026-07-08T23:43:40.681014Z"
}
```

### 03_setup_poll_07

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_policy_derivation_agent",
  "updated_at": "2026-07-08T23:43:40.681014Z"
}
```

### 03_setup_poll_08

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_policy_derivation_agent",
  "updated_at": "2026-07-08T23:43:40.681014Z"
}
```

### 03_setup_poll_09

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_policy_derivation_agent",
  "updated_at": "2026-07-08T23:43:40.681014Z"
}
```

### 03_setup_poll_10

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_policy_derivation_agent",
  "updated_at": "2026-07-08T23:43:40.681014Z"
}
```

### 03_setup_poll_11

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_policy_derivation_agent",
  "updated_at": "2026-07-08T23:43:40.681014Z"
}
```

### 03_setup_poll_12

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_policy_derivation_agent",
  "updated_at": "2026-07-08T23:43:40.681014Z"
}
```

### 03_setup_poll_13

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "running_policy_derivation_agent",
  "updated_at": "2026-07-08T23:43:40.681014Z"
}
```

### 03_setup_poll_14

`GET /api/v1/projects/{project_id}/guides/{guide_id}/setup-runs/latest` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "celery_task_id": "<redacted-id>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "<redacted-id>",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": "2026-07-08T23:44:00.380059Z",
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "output_submission_artifact_policy_id": "<redacted-id>",
  "output_sufficiency_report_id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "started_at": "2026-07-08T23:43:32.307172Z",
  "status": "policy_draft_ready",
  "updated_at": "2026-07-08T23:44:00.332149Z"
}
```

### 04_sufficiency_report

`GET /api/v1/projects/{project_id}/guides/{guide_id}/sufficiency-reports/{report_id}` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "acknowledgement_note": null,
  "agent_name": "ProjectGuideSufficiencyAgent",
  "agent_version": "workstream-sufficiency-agent-v0.1",
  "created_at": "2026-07-08T23:43:40.523990Z",
  "created_by": "workstream-system:project-setup-pipeline",
  "findings": [],
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "status": "passed",
  "summary": "The guide provides sufficient reviewer criteria and workflow direction for this Terminal Benchmark task review, including milestone structure, static guard handling, dependency pinning, Dockerfile requirements, test alignment, rubric rules, reward behavior, and category mapping.",
  "warnings_acknowledged_at": null,
  "warnings_acknowledged_by_actor": null,
  "warnings_acknowledged_by_role": null
}
```

### 05_submission_artifact_policy

`GET /api/v1/projects/{project_id}/guides/{guide_id}/submission-artifact-policies/{policy_id}` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "approved_at": null,
  "approved_by_actor": null,
  "approved_by_role": null,
  "change_summary": null,
  "created_at": "2026-07-08T23:44:00.095072Z",
  "created_by": "workstream-system:project-setup-pipeline",
  "derivation_agent_name": "SubmissionArtifactPolicyDerivationAgent",
  "derivation_agent_version": "workstream-policy-derivation-agent-v0.1",
  "derivation_source": "agent_derivation",
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "lifecycle_status": "draft",
  "policy_body": {
    "allowed_storage_schemes": [
      "local",
      "r2",
      "s3"
    ],
    "artifact_hash_algorithm": "sha256",
    "artifact_hash_required": true,
    "attestation_terms": [
      "all_or_nothing_reward",
      "container_bases_digest_pinned",
      "dependencies_pinned",
      "hashes_sha256",
      "manifest_complete",
      "no_generated_caches",
      "no_reviewer_only_material",
      "no_sensitive_local_material",
      "offline_verifier_dependencies",
      "task_layout_matches_metadata"
    ],
    "forbidden_artifacts": [
      {
        "pattern": "**/*.key",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
      },
      {
        "pattern": "**/*.pem",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
      },
      {
        "pattern": "**/*.pyc",
        "reason": "compiled Python bytecode is a generated artifact",
        "worker_facing_fix": "delete bytecode files before packaging"
      },
      {
        "pattern": "**/.DS_Store",
        "reason": "operating system metadata is not part of the task submission",
        "worker_facing_fix": "remove operating system metadata files"
      },
      {
        "pattern": "**/.env",
        "reason": "local configuration files may expose sensitive local settings",
        "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
      },
      {
        "pattern": "**/.env.*",
        "reason": "local configuration variants may expose sensitive local settings",
        "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
      },
      {
        "pattern": "**/.pytest_cache/**",
        "reason": "generated test cache files are stale package artifacts",
        "worker_facing_fix": "delete cache directories before packaging"
      },
      {
        "pattern": "**/__pycache__/**",
        "reason": "generated Python cache files are stale package artifacts",
        "worker_facing_fix": "delete cache directories before packaging"
      },
      {
        "pattern": "**/build/**",
        "reason": "compiled or generated build outputs are not part of source intake by default",
        "worker_facing_fix": "remove generated build directories unless explicitly required by the task"
      },
      {
        "pattern": "**/dist/**",
        "reason": "compiled or generated distribution outputs are not part of source intake by default",
        "worker_facing_fix": "remove generated distribution directories unless explicitly required by the task"
      },
      {
        "pattern": "**/docker_build.log",
        "reason": "build logs are not source submission artifacts",
        "worker_facing_fix": "remove local logs before packaging"
      },
      {
        "pattern": "**/id_ed25519",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file from the package"
      },
      {
        "pattern": "**/id_rsa",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file from the package"
      },
      {
        "pattern": "**/node_modules/**",
        "reason": "local dependency folders bloat submissions and reduce reproducibility",
        "worker_facing_fix": "remove local dependency folders and rely on pinned manifests or lockfiles"
      },
      {
        "pattern": "**/oracle_test.log",
        "reason": "test logs are not source submission artifacts",
        "worker_facing_fix": "remove local logs before packaging"
      },
      {
        "pattern": "**/platform_review.md",
        "reason": "review-only material must not be included in worker submissions",
        "worker_facing_fix": "remove reviewer-only notes before packaging"
      },
      {
        "pattern": "**/platfrom_review.md",
        "reason": "review-only material must not be included in worker submissions",
        "worker_facing_fix": "remove reviewer-only notes before packaging"
      },
      {
        "pattern": "**/review_packet.md",
        "reason": "review-only material must not be included in worker submissions",
        "worker_facing_fix": "remove reviewer-only packets before packaging"
      },
      {
        "pattern": "**/rubrics.txt",
        "reason": "rubrics must be supplied through the expected rubric artifact, not as this legacy packaged file",
        "worker_facing_fix": "remove rubrics.txt and provide rubric.md"
      },
      {
        "pattern": "**/static_guard.txt",
        "reason": "local checker output is not a worker submission artifact",
        "worker_facing_fix": "remove checker logs before packaging"
      },
      {
        "pattern": "**/target/**",
        "reason": "compiled Rust build outputs should not be submitted",
        "worker_facing_fix": "remove build output directories before packaging"
      }
    ],
    "manifest_required": true,
    "maximum_file_size_bytes": null,
    "maximum_package_size_bytes": null,
    "packaging": {
      "allowed_package_formats": [
        "zip"
      ],
      "package_required": true
    },
    "required_artifacts": [
      {
        "description": "container build definition for the task environment",
        "hash_required": true,
        "key": "environment_dockerfile",
        "path": "environment/Dockerfile",
        "required": true
      },
      {
        "description": "build context hygiene exclusions",
        "hash_required": true,
        "key": "environment_dockerignore",
        "path": "environment/.dockerignore",
        "required": true
      },
      {
        "description": "task scoring criteria for agent traces",
        "hash_required": true,
        "key": "rubric",
        "path": "rubric.md",
        "required": true
      },
      {
        "description": "project task metadata and runtime configuration",
        "hash_required": true,
        "key": "task_config",
        "path": "task.toml",
        "required": true
      }
    ],
    "required_evidence": [
      {
        "description": "confirms language packages and container bases are pinned as required",
        "hash_required": true,
        "key": "dependency_pinning_review",
        "label": "Dependency pinning review",
        "required": true
      },
      {
        "description": "confirms build context, size limits, and runtime setup are acceptable",
        "hash_required": true,
        "key": "environment_hygiene_review",
        "label": "Environment hygiene review",
        "required": true
      },
      {
        "description": "root or milestone instruction files are included for the task layout",
        "hash_required": true,
        "key": "instructions_present",
        "label": "Task instructions included",
        "required": true
      },
      {
        "description": "confirms verifier runner writes only all-or-nothing reward output",
        "hash_required": true,
        "key": "reward_footer_review",
        "label": "Reward footer review",
        "required": true
      },
      {
        "description": "root or milestone solution scripts are included for validation",
        "hash_required": true,
        "key": "solution_present",
        "label": "Reference solution included",
        "required": true
      },
      {
        "description": "difficulty, solution, and verification explanations are provided",
        "hash_required": true,
        "key": "submission_explanations",
        "label": "Submission explanations",
        "required": true
      },
      {
        "description": "maps stated behavior to verifier coverage and strict assertions",
        "hash_required": true,
        "key": "test_alignment_review",
        "label": "Test alignment review",
        "required": true
      },
      {
        "description": "root or milestone verifier runner and test files are included for the task layout",
        "hash_required": true,
        "key": "tests_present",
        "label": "Verifier files included",
        "required": true
      }
    ],
    "schema_version": "project_submission_artifact_policy.v1"
  },
  "policy_hash": "sha256:<redacted>",
  "policy_version": "agent-9843f69ef5b7f7631f98a61d",
  "project_id": "<redacted-id>",
  "source_material_refs": [
    "import:/fixtures/<redacted-fixture-id>/docker_build.log",
    "import:/fixtures/<redacted-fixture-id>/oracle_test.log",
    "import:/fixtures/<redacted-fixture-id>/starter_m1_test.log",
    "import:/fixtures/<redacted-fixture-id>/static_guard.txt",
    "import:/fixtures/<redacted-fixture-id>/PROJECT_GUIDE.md",
    "inline:/guides/<redacted-id>/v1",
    "import:/fixtures/<redacted-fixture-id>/review_packet.md",
    "import:/fixtures/<redacted-fixture-id>/REVIEWER_PROGRAM.md",
    "import:/fixtures/<redacted-fixture-id>/task.toml"
  ],
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "superseded_at": null,
  "supersedes_policy_id": null,
  "updated_at": "2026-07-08T23:44:00.095072Z"
}
```

### 06_approve_policy

`POST /api/v1/projects/{project_id}/guides/{guide_id}/submission-artifact-policies/{policy_id}/approve` -> HTTP `200`

Request body:

```json
{
  "approval_note": "Approved agent-derived Terminal Benchmark intake contract for final clean live API drill."
}
```

Response body:

```json
{
  "created_at": "2026-07-08T23:44:02.228409Z",
  "created_by": "<redacted-id>",
  "effective_policy": {
    "allowed_storage_schemes": [
      "local",
      "r2",
      "s3"
    ],
    "artifact_hash_algorithm": "sha256",
    "artifact_hash_required": true,
    "attestation_terms": [
      "all_or_nothing_reward",
      "confidential_data_exclusion",
      "container_bases_digest_pinned",
      "credentials_and_secret_exclusion",
      "dependencies_pinned",
      "hashes_sha256",
      "human_accountability_for_agent_assisted_work",
      "manifest_complete",
      "no_generated_caches",
      "no_reviewer_only_material",
      "no_sensitive_local_material",
      "offline_verifier_dependencies",
      "original_work",
      "task_layout_matches_metadata"
    ],
    "forbidden_artifacts": [
      {
        "pattern": "**/*.key",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
      },
      {
        "pattern": "**/*.pem",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
      },
      {
        "pattern": "**/*.pyc",
        "reason": "compiled Python bytecode is a generated artifact",
        "worker_facing_fix": "delete bytecode files before packaging"
      },
      {
        "pattern": "**/.DS_Store",
        "reason": "operating system metadata is not part of the task submission",
        "worker_facing_fix": "remove operating system metadata files"
      },
      {
        "pattern": "**/.env",
        "reason": "local configuration files may expose sensitive local settings",
        "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
      },
      {
        "pattern": "**/.env.*",
        "reason": "local configuration variants may expose sensitive local settings",
        "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
      },
      {
        "pattern": "**/.pytest_cache/**",
        "reason": "generated test cache files are stale package artifacts",
        "worker_facing_fix": "delete cache directories before packaging"
      },
      {
        "pattern": "**/__pycache__/**",
        "reason": "generated Python cache files are stale package artifacts",
        "worker_facing_fix": "delete cache directories before packaging"
      },
      {
        "pattern": "**/build/**",
        "reason": "compiled or generated build outputs are not part of source intake by default",
        "worker_facing_fix": "remove generated build directories unless explicitly required by the task"
      },
      {
        "pattern": "**/dist/**",
        "reason": "compiled or generated distribution outputs are not part of source intake by default",
        "worker_facing_fix": "remove generated distribution directories unless explicitly required by the task"
      },
      {
        "pattern": "**/docker_build.log",
        "reason": "build logs are not source submission artifacts",
        "worker_facing_fix": "remove local logs before packaging"
      },
      {
        "pattern": "**/id_ed25519",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file from the package"
      },
      {
        "pattern": "**/id_rsa",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file from the package"
      },
      {
        "pattern": "**/node_modules/**",
        "reason": "local dependency folders bloat submissions and reduce reproducibility",
        "worker_facing_fix": "remove local dependency folders and rely on pinned manifests or lockfiles"
      },
      {
        "pattern": "**/oracle_test.log",
        "reason": "test logs are not source submission artifacts",
        "worker_facing_fix": "remove local logs before packaging"
      },
      {
        "pattern": "**/platform_review.md",
        "reason": "review-only material must not be included in worker submissions",
        "worker_facing_fix": "remove reviewer-only notes before packaging"
      },
      {
        "pattern": "**/platfrom_review.md",
        "reason": "review-only material must not be included in worker submissions",
        "worker_facing_fix": "remove reviewer-only notes before packaging"
      },
      {
        "pattern": "**/review_packet.md",
        "reason": "review-only material must not be included in worker submissions",
        "worker_facing_fix": "remove reviewer-only packets before packaging"
      },
      {
        "pattern": "**/rubrics.txt",
        "reason": "rubrics must be supplied through the expected rubric artifact, not as this legacy packaged file",
        "worker_facing_fix": "remove rubrics.txt and provide rubric.md"
      },
      {
        "pattern": "**/static_guard.txt",
        "reason": "local checker output is not a worker submission artifact",
        "worker_facing_fix": "remove checker logs before packaging"
      },
      {
        "pattern": "**/target/**",
        "reason": "compiled Rust build outputs should not be submitted",
        "worker_facing_fix": "remove build output directories before packaging"
      },
      {
        "pattern": "*.env",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "*.env.*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "*.key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "*.pem",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".env",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".env*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".git",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".npmrc",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".pypirc",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "access-key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "access-key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "access_key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "access_key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "api-key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "api-key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "api_key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "api_key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "credential*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "credentials",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_dsa",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_dsa*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_ecdsa",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_ecdsa*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_ed25519",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_ed25519*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_rsa",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_rsa*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "node_modules",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "private-key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "private-key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "private_key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "private_key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "secret*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "secrets",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "service-account",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "service-account*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "service_account",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "service_account*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "token",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "token*",
        "severity": "blocking",
        "source": "workstream_default"
      }
    ],
    "manifest_required": true,
    "maximum_file_size_bytes": null,
    "maximum_package_size_bytes": null,
    "merge_algorithm_version": "workstream_default_merge.v1",
    "packaging": {
      "allowed_package_formats": [
        "zip"
      ],
      "package_required": true
    },
    "project_policy": {
      "allowed_storage_schemes": [
        "local",
        "r2",
        "s3"
      ],
      "artifact_hash_algorithm": "sha256",
      "artifact_hash_required": true,
      "attestation_terms": [
        "all_or_nothing_reward",
        "container_bases_digest_pinned",
        "dependencies_pinned",
        "hashes_sha256",
        "manifest_complete",
        "no_generated_caches",
        "no_reviewer_only_material",
        "no_sensitive_local_material",
        "offline_verifier_dependencies",
        "task_layout_matches_metadata"
      ],
      "forbidden_artifacts": [
        {
          "pattern": "**/*.key",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
        },
        {
          "pattern": "**/*.pem",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
        },
        {
          "pattern": "**/*.pyc",
          "reason": "compiled Python bytecode is a generated artifact",
          "worker_facing_fix": "delete bytecode files before packaging"
        },
        {
          "pattern": "**/.DS_Store",
          "reason": "operating system metadata is not part of the task submission",
          "worker_facing_fix": "remove operating system metadata files"
        },
        {
          "pattern": "**/.env",
          "reason": "local configuration files may expose sensitive local settings",
          "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
        },
        {
          "pattern": "**/.env.*",
          "reason": "local configuration variants may expose sensitive local settings",
          "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
        },
        {
          "pattern": "**/.pytest_cache/**",
          "reason": "generated test cache files are stale package artifacts",
          "worker_facing_fix": "delete cache directories before packaging"
        },
        {
          "pattern": "**/__pycache__/**",
          "reason": "generated Python cache files are stale package artifacts",
          "worker_facing_fix": "delete cache directories before packaging"
        },
        {
          "pattern": "**/build/**",
          "reason": "compiled or generated build outputs are not part of source intake by default",
          "worker_facing_fix": "remove generated build directories unless explicitly required by the task"
        },
        {
          "pattern": "**/dist/**",
          "reason": "compiled or generated distribution outputs are not part of source intake by default",
          "worker_facing_fix": "remove generated distribution directories unless explicitly required by the task"
        },
        {
          "pattern": "**/docker_build.log",
          "reason": "build logs are not source submission artifacts",
          "worker_facing_fix": "remove local logs before packaging"
        },
        {
          "pattern": "**/id_ed25519",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file from the package"
        },
        {
          "pattern": "**/id_rsa",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file from the package"
        },
        {
          "pattern": "**/node_modules/**",
          "reason": "local dependency folders bloat submissions and reduce reproducibility",
          "worker_facing_fix": "remove local dependency folders and rely on pinned manifests or lockfiles"
        },
        {
          "pattern": "**/oracle_test.log",
          "reason": "test logs are not source submission artifacts",
          "worker_facing_fix": "remove local logs before packaging"
        },
        {
          "pattern": "**/platform_review.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only notes before packaging"
        },
        {
          "pattern": "**/platfrom_review.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only notes before packaging"
        },
        {
          "pattern": "**/review_packet.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only packets before packaging"
        },
        {
          "pattern": "**/rubrics.txt",
          "reason": "rubrics must be supplied through the expected rubric artifact, not as this legacy packaged file",
          "worker_facing_fix": "remove rubrics.txt and provide rubric.md"
        },
        {
          "pattern": "**/static_guard.txt",
          "reason": "local checker output is not a worker submission artifact",
          "worker_facing_fix": "remove checker logs before packaging"
        },
        {
          "pattern": "**/target/**",
          "reason": "compiled Rust build outputs should not be submitted",
          "worker_facing_fix": "remove build output directories before packaging"
        }
      ],
      "manifest_required": true,
      "maximum_file_size_bytes": null,
      "maximum_package_size_bytes": null,
      "packaging": {
        "allowed_package_formats": [
          "zip"
        ],
        "package_required": true
      },
      "required_artifacts": [
        {
          "description": "container build definition for the task environment",
          "hash_required": true,
          "key": "environment_dockerfile",
          "path": "environment/Dockerfile",
          "required": true
        },
        {
          "description": "build context hygiene exclusions",
          "hash_required": true,
          "key": "environment_dockerignore",
          "path": "environment/.dockerignore",
          "required": true
        },
        {
          "description": "task scoring criteria for agent traces",
          "hash_required": true,
          "key": "rubric",
          "path": "rubric.md",
          "required": true
        },
        {
          "description": "project task metadata and runtime configuration",
          "hash_required": true,
          "key": "task_config",
          "path": "task.toml",
          "required": true
        }
      ],
      "required_evidence": [
        {
          "description": "confirms language packages and container bases are pinned as required",
          "hash_required": true,
          "key": "dependency_pinning_review",
          "label": "Dependency pinning review",
          "required": true
        },
        {
          "description": "confirms build context, size limits, and runtime setup are acceptable",
          "hash_required": true,
          "key": "environment_hygiene_review",
          "label": "Environment hygiene review",
          "required": true
        },
        {
          "description": "root or milestone instruction files are included for the task layout",
          "hash_required": true,
          "key": "instructions_present",
          "label": "Task instructions included",
          "required": true
        },
        {
          "description": "confirms verifier runner writes only all-or-nothing reward output",
          "hash_required": true,
          "key": "reward_footer_review",
          "label": "Reward footer review",
          "required": true
        },
        {
          "description": "root or milestone solution scripts are included for validation",
          "hash_required": true,
          "key": "solution_present",
          "label": "Reference solution included",
          "required": true
        },
        {
          "description": "difficulty, solution, and verification explanations are provided",
          "hash_required": true,
          "key": "submission_explanations",
          "label": "Submission explanations",
          "required": true
        },
        {
          "description": "maps stated behavior to verifier coverage and strict assertions",
          "hash_required": true,
          "key": "test_alignment_review",
          "label": "Test alignment review",
          "required": true
        },
        {
          "description": "root or milestone verifier runner and test files are included for the task layout",
          "hash_required": true,
          "key": "tests_present",
          "label": "Verifier files included",
          "required": true
        }
      ],
      "schema_version": "project_submission_artifact_policy.v1"
    },
    "required_artifacts": [
      {
        "description": "container build definition for the task environment",
        "hash_required": true,
        "key": "environment_dockerfile",
        "path": "environment/Dockerfile",
        "required": true
      },
      {
        "description": "build context hygiene exclusions",
        "hash_required": true,
        "key": "environment_dockerignore",
        "path": "environment/.dockerignore",
        "required": true
      },
      {
        "description": "task scoring criteria for agent traces",
        "hash_required": true,
        "key": "rubric",
        "path": "rubric.md",
        "required": true
      },
      {
        "description": "project task metadata and runtime configuration",
        "hash_required": true,
        "key": "task_config",
        "path": "task.toml",
        "required": true
      }
    ],
    "required_evidence": [
      {
        "description": "confirms language packages and container bases are pinned as required",
        "hash_required": true,
        "key": "dependency_pinning_review",
        "label": "Dependency pinning review",
        "required": true
      },
      {
        "description": "confirms build context, size limits, and runtime setup are acceptable",
        "hash_required": true,
        "key": "environment_hygiene_review",
        "label": "Environment hygiene review",
        "required": true
      },
      {
        "description": "root or milestone instruction files are included for the task layout",
        "hash_required": true,
        "key": "instructions_present",
        "label": "Task instructions included",
        "required": true
      },
      {
        "description": "confirms verifier runner writes only all-or-nothing reward output",
        "hash_required": true,
        "key": "reward_footer_review",
        "label": "Reward footer review",
        "required": true
      },
      {
        "description": "root or milestone solution scripts are included for validation",
        "hash_required": true,
        "key": "solution_present",
        "label": "Reference solution included",
        "required": true
      },
      {
        "description": "difficulty, solution, and verification explanations are provided",
        "hash_required": true,
        "key": "submission_explanations",
        "label": "Submission explanations",
        "required": true
      },
      {
        "description": "maps stated behavior to verifier coverage and strict assertions",
        "hash_required": true,
        "key": "test_alignment_review",
        "label": "Test alignment review",
        "required": true
      },
      {
        "description": "root or milestone verifier runner and test files are included for the task layout",
        "hash_required": true,
        "key": "tests_present",
        "label": "Verifier files included",
        "required": true
      }
    ],
    "required_packet_fields": [
      "artifact_hash_manifest",
      "summary",
      "worker_attestation"
    ],
    "schema_version": "effective_project_submission_artifact_policy.v1",
    "workstream_default_policy": {
      "allowed_storage_schemes": [
        "local",
        "s3",
        "r2"
      ],
      "artifact_hash_algorithm": "sha256",
      "artifact_hash_required": true,
      "attestation_terms": [
        "original_work",
        "confidential_data_exclusion",
        "credentials_and_secret_exclusion",
        "human_accountability_for_agent_assisted_work"
      ],
      "forbidden_artifacts": [
        {
          "pattern": ".env",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".env*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.env",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.env.*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".git",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "credentials",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "credential*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "secrets",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "secret*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".npmrc",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".pypirc",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api_key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api-key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api_key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api-key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access_key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access-key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access_key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access-key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private_key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private-key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private_key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private-key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_rsa",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_rsa*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_dsa",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_dsa*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ecdsa",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ecdsa*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ed25519",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ed25519*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service_account",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service-account",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service_account*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service-account*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "token",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "token*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.pem",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "node_modules",
          "severity": "blocking",
          "source": "workstream_default"
        }
      ],
      "manifest_required": true,
      "maximum_file_size_bytes": null,
      "maximum_package_size_bytes": null,
      "packaging": {},
      "required_artifacts": [],
      "required_evidence": [],
      "required_packet_fields": [
        "summary",
        "artifact_hash_manifest",
        "worker_attestation"
      ],
      "schema_version": "workstream_default_submission_artifact_policy.v1"
    }
  },
  "effective_policy_hash": "sha256:<redacted>",
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "lifecycle_status": "approved",
  "merge_algorithm_version": "workstream_default_merge.v1",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "submission_artifact_policy_hash": "sha256:<redacted>",
  "submission_artifact_policy_id": "<redacted-id>",
  "superseded_at": null,
  "supersedes_effective_policy_id": null
}
```

### 07_effective_policy

`GET /api/v1/projects/{project_id}/guides/{guide_id}/effective-submission-artifact-policy` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "created_at": "2026-07-08T23:44:02.228409Z",
  "created_by": "<redacted-id>",
  "effective_policy": {
    "allowed_storage_schemes": [
      "local",
      "r2",
      "s3"
    ],
    "artifact_hash_algorithm": "sha256",
    "artifact_hash_required": true,
    "attestation_terms": [
      "all_or_nothing_reward",
      "confidential_data_exclusion",
      "container_bases_digest_pinned",
      "credentials_and_secret_exclusion",
      "dependencies_pinned",
      "hashes_sha256",
      "human_accountability_for_agent_assisted_work",
      "manifest_complete",
      "no_generated_caches",
      "no_reviewer_only_material",
      "no_sensitive_local_material",
      "offline_verifier_dependencies",
      "original_work",
      "task_layout_matches_metadata"
    ],
    "forbidden_artifacts": [
      {
        "pattern": "**/*.key",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
      },
      {
        "pattern": "**/*.pem",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
      },
      {
        "pattern": "**/*.pyc",
        "reason": "compiled Python bytecode is a generated artifact",
        "worker_facing_fix": "delete bytecode files before packaging"
      },
      {
        "pattern": "**/.DS_Store",
        "reason": "operating system metadata is not part of the task submission",
        "worker_facing_fix": "remove operating system metadata files"
      },
      {
        "pattern": "**/.env",
        "reason": "local configuration files may expose sensitive local settings",
        "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
      },
      {
        "pattern": "**/.env.*",
        "reason": "local configuration variants may expose sensitive local settings",
        "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
      },
      {
        "pattern": "**/.pytest_cache/**",
        "reason": "generated test cache files are stale package artifacts",
        "worker_facing_fix": "delete cache directories before packaging"
      },
      {
        "pattern": "**/__pycache__/**",
        "reason": "generated Python cache files are stale package artifacts",
        "worker_facing_fix": "delete cache directories before packaging"
      },
      {
        "pattern": "**/build/**",
        "reason": "compiled or generated build outputs are not part of source intake by default",
        "worker_facing_fix": "remove generated build directories unless explicitly required by the task"
      },
      {
        "pattern": "**/dist/**",
        "reason": "compiled or generated distribution outputs are not part of source intake by default",
        "worker_facing_fix": "remove generated distribution directories unless explicitly required by the task"
      },
      {
        "pattern": "**/docker_build.log",
        "reason": "build logs are not source submission artifacts",
        "worker_facing_fix": "remove local logs before packaging"
      },
      {
        "pattern": "**/id_ed25519",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file from the package"
      },
      {
        "pattern": "**/id_rsa",
        "reason": "private authentication material must not be submitted",
        "worker_facing_fix": "remove the file from the package"
      },
      {
        "pattern": "**/node_modules/**",
        "reason": "local dependency folders bloat submissions and reduce reproducibility",
        "worker_facing_fix": "remove local dependency folders and rely on pinned manifests or lockfiles"
      },
      {
        "pattern": "**/oracle_test.log",
        "reason": "test logs are not source submission artifacts",
        "worker_facing_fix": "remove local logs before packaging"
      },
      {
        "pattern": "**/platform_review.md",
        "reason": "review-only material must not be included in worker submissions",
        "worker_facing_fix": "remove reviewer-only notes before packaging"
      },
      {
        "pattern": "**/platfrom_review.md",
        "reason": "review-only material must not be included in worker submissions",
        "worker_facing_fix": "remove reviewer-only notes before packaging"
      },
      {
        "pattern": "**/review_packet.md",
        "reason": "review-only material must not be included in worker submissions",
        "worker_facing_fix": "remove reviewer-only packets before packaging"
      },
      {
        "pattern": "**/rubrics.txt",
        "reason": "rubrics must be supplied through the expected rubric artifact, not as this legacy packaged file",
        "worker_facing_fix": "remove rubrics.txt and provide rubric.md"
      },
      {
        "pattern": "**/static_guard.txt",
        "reason": "local checker output is not a worker submission artifact",
        "worker_facing_fix": "remove checker logs before packaging"
      },
      {
        "pattern": "**/target/**",
        "reason": "compiled Rust build outputs should not be submitted",
        "worker_facing_fix": "remove build output directories before packaging"
      },
      {
        "pattern": "*.env",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "*.env.*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "*.key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "*.pem",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".env",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".env*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".git",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".npmrc",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": ".pypirc",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "access-key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "access-key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "access_key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "access_key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "api-key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "api-key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "api_key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "api_key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "credential*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "credentials",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_dsa",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_dsa*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_ecdsa",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_ecdsa*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_ed25519",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_ed25519*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_rsa",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "id_rsa*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "node_modules",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "private-key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "private-key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "private_key",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "private_key*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "secret*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "secrets",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "service-account",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "service-account*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "service_account",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "service_account*",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "token",
        "severity": "blocking",
        "source": "workstream_default"
      },
      {
        "pattern": "token*",
        "severity": "blocking",
        "source": "workstream_default"
      }
    ],
    "manifest_required": true,
    "maximum_file_size_bytes": null,
    "maximum_package_size_bytes": null,
    "merge_algorithm_version": "workstream_default_merge.v1",
    "packaging": {
      "allowed_package_formats": [
        "zip"
      ],
      "package_required": true
    },
    "project_policy": {
      "allowed_storage_schemes": [
        "local",
        "r2",
        "s3"
      ],
      "artifact_hash_algorithm": "sha256",
      "artifact_hash_required": true,
      "attestation_terms": [
        "all_or_nothing_reward",
        "container_bases_digest_pinned",
        "dependencies_pinned",
        "hashes_sha256",
        "manifest_complete",
        "no_generated_caches",
        "no_reviewer_only_material",
        "no_sensitive_local_material",
        "offline_verifier_dependencies",
        "task_layout_matches_metadata"
      ],
      "forbidden_artifacts": [
        {
          "pattern": "**/*.key",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
        },
        {
          "pattern": "**/*.pem",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
        },
        {
          "pattern": "**/*.pyc",
          "reason": "compiled Python bytecode is a generated artifact",
          "worker_facing_fix": "delete bytecode files before packaging"
        },
        {
          "pattern": "**/.DS_Store",
          "reason": "operating system metadata is not part of the task submission",
          "worker_facing_fix": "remove operating system metadata files"
        },
        {
          "pattern": "**/.env",
          "reason": "local configuration files may expose sensitive local settings",
          "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
        },
        {
          "pattern": "**/.env.*",
          "reason": "local configuration variants may expose sensitive local settings",
          "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
        },
        {
          "pattern": "**/.pytest_cache/**",
          "reason": "generated test cache files are stale package artifacts",
          "worker_facing_fix": "delete cache directories before packaging"
        },
        {
          "pattern": "**/__pycache__/**",
          "reason": "generated Python cache files are stale package artifacts",
          "worker_facing_fix": "delete cache directories before packaging"
        },
        {
          "pattern": "**/build/**",
          "reason": "compiled or generated build outputs are not part of source intake by default",
          "worker_facing_fix": "remove generated build directories unless explicitly required by the task"
        },
        {
          "pattern": "**/dist/**",
          "reason": "compiled or generated distribution outputs are not part of source intake by default",
          "worker_facing_fix": "remove generated distribution directories unless explicitly required by the task"
        },
        {
          "pattern": "**/docker_build.log",
          "reason": "build logs are not source submission artifacts",
          "worker_facing_fix": "remove local logs before packaging"
        },
        {
          "pattern": "**/id_ed25519",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file from the package"
        },
        {
          "pattern": "**/id_rsa",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file from the package"
        },
        {
          "pattern": "**/node_modules/**",
          "reason": "local dependency folders bloat submissions and reduce reproducibility",
          "worker_facing_fix": "remove local dependency folders and rely on pinned manifests or lockfiles"
        },
        {
          "pattern": "**/oracle_test.log",
          "reason": "test logs are not source submission artifacts",
          "worker_facing_fix": "remove local logs before packaging"
        },
        {
          "pattern": "**/platform_review.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only notes before packaging"
        },
        {
          "pattern": "**/platfrom_review.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only notes before packaging"
        },
        {
          "pattern": "**/review_packet.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only packets before packaging"
        },
        {
          "pattern": "**/rubrics.txt",
          "reason": "rubrics must be supplied through the expected rubric artifact, not as this legacy packaged file",
          "worker_facing_fix": "remove rubrics.txt and provide rubric.md"
        },
        {
          "pattern": "**/static_guard.txt",
          "reason": "local checker output is not a worker submission artifact",
          "worker_facing_fix": "remove checker logs before packaging"
        },
        {
          "pattern": "**/target/**",
          "reason": "compiled Rust build outputs should not be submitted",
          "worker_facing_fix": "remove build output directories before packaging"
        }
      ],
      "manifest_required": true,
      "maximum_file_size_bytes": null,
      "maximum_package_size_bytes": null,
      "packaging": {
        "allowed_package_formats": [
          "zip"
        ],
        "package_required": true
      },
      "required_artifacts": [
        {
          "description": "container build definition for the task environment",
          "hash_required": true,
          "key": "environment_dockerfile",
          "path": "environment/Dockerfile",
          "required": true
        },
        {
          "description": "build context hygiene exclusions",
          "hash_required": true,
          "key": "environment_dockerignore",
          "path": "environment/.dockerignore",
          "required": true
        },
        {
          "description": "task scoring criteria for agent traces",
          "hash_required": true,
          "key": "rubric",
          "path": "rubric.md",
          "required": true
        },
        {
          "description": "project task metadata and runtime configuration",
          "hash_required": true,
          "key": "task_config",
          "path": "task.toml",
          "required": true
        }
      ],
      "required_evidence": [
        {
          "description": "confirms language packages and container bases are pinned as required",
          "hash_required": true,
          "key": "dependency_pinning_review",
          "label": "Dependency pinning review",
          "required": true
        },
        {
          "description": "confirms build context, size limits, and runtime setup are acceptable",
          "hash_required": true,
          "key": "environment_hygiene_review",
          "label": "Environment hygiene review",
          "required": true
        },
        {
          "description": "root or milestone instruction files are included for the task layout",
          "hash_required": true,
          "key": "instructions_present",
          "label": "Task instructions included",
          "required": true
        },
        {
          "description": "confirms verifier runner writes only all-or-nothing reward output",
          "hash_required": true,
          "key": "reward_footer_review",
          "label": "Reward footer review",
          "required": true
        },
        {
          "description": "root or milestone solution scripts are included for validation",
          "hash_required": true,
          "key": "solution_present",
          "label": "Reference solution included",
          "required": true
        },
        {
          "description": "difficulty, solution, and verification explanations are provided",
          "hash_required": true,
          "key": "submission_explanations",
          "label": "Submission explanations",
          "required": true
        },
        {
          "description": "maps stated behavior to verifier coverage and strict assertions",
          "hash_required": true,
          "key": "test_alignment_review",
          "label": "Test alignment review",
          "required": true
        },
        {
          "description": "root or milestone verifier runner and test files are included for the task layout",
          "hash_required": true,
          "key": "tests_present",
          "label": "Verifier files included",
          "required": true
        }
      ],
      "schema_version": "project_submission_artifact_policy.v1"
    },
    "required_artifacts": [
      {
        "description": "container build definition for the task environment",
        "hash_required": true,
        "key": "environment_dockerfile",
        "path": "environment/Dockerfile",
        "required": true
      },
      {
        "description": "build context hygiene exclusions",
        "hash_required": true,
        "key": "environment_dockerignore",
        "path": "environment/.dockerignore",
        "required": true
      },
      {
        "description": "task scoring criteria for agent traces",
        "hash_required": true,
        "key": "rubric",
        "path": "rubric.md",
        "required": true
      },
      {
        "description": "project task metadata and runtime configuration",
        "hash_required": true,
        "key": "task_config",
        "path": "task.toml",
        "required": true
      }
    ],
    "required_evidence": [
      {
        "description": "confirms language packages and container bases are pinned as required",
        "hash_required": true,
        "key": "dependency_pinning_review",
        "label": "Dependency pinning review",
        "required": true
      },
      {
        "description": "confirms build context, size limits, and runtime setup are acceptable",
        "hash_required": true,
        "key": "environment_hygiene_review",
        "label": "Environment hygiene review",
        "required": true
      },
      {
        "description": "root or milestone instruction files are included for the task layout",
        "hash_required": true,
        "key": "instructions_present",
        "label": "Task instructions included",
        "required": true
      },
      {
        "description": "confirms verifier runner writes only all-or-nothing reward output",
        "hash_required": true,
        "key": "reward_footer_review",
        "label": "Reward footer review",
        "required": true
      },
      {
        "description": "root or milestone solution scripts are included for validation",
        "hash_required": true,
        "key": "solution_present",
        "label": "Reference solution included",
        "required": true
      },
      {
        "description": "difficulty, solution, and verification explanations are provided",
        "hash_required": true,
        "key": "submission_explanations",
        "label": "Submission explanations",
        "required": true
      },
      {
        "description": "maps stated behavior to verifier coverage and strict assertions",
        "hash_required": true,
        "key": "test_alignment_review",
        "label": "Test alignment review",
        "required": true
      },
      {
        "description": "root or milestone verifier runner and test files are included for the task layout",
        "hash_required": true,
        "key": "tests_present",
        "label": "Verifier files included",
        "required": true
      }
    ],
    "required_packet_fields": [
      "artifact_hash_manifest",
      "summary",
      "worker_attestation"
    ],
    "schema_version": "effective_project_submission_artifact_policy.v1",
    "workstream_default_policy": {
      "allowed_storage_schemes": [
        "local",
        "s3",
        "r2"
      ],
      "artifact_hash_algorithm": "sha256",
      "artifact_hash_required": true,
      "attestation_terms": [
        "original_work",
        "confidential_data_exclusion",
        "credentials_and_secret_exclusion",
        "human_accountability_for_agent_assisted_work"
      ],
      "forbidden_artifacts": [
        {
          "pattern": ".env",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".env*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.env",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.env.*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".git",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "credentials",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "credential*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "secrets",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "secret*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".npmrc",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".pypirc",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api_key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api-key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api_key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api-key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access_key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access-key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access_key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access-key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private_key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private-key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private_key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private-key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_rsa",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_rsa*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_dsa",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_dsa*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ecdsa",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ecdsa*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ed25519",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ed25519*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service_account",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service-account",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service_account*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service-account*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "token",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "token*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.pem",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "node_modules",
          "severity": "blocking",
          "source": "workstream_default"
        }
      ],
      "manifest_required": true,
      "maximum_file_size_bytes": null,
      "maximum_package_size_bytes": null,
      "packaging": {},
      "required_artifacts": [],
      "required_evidence": [],
      "required_packet_fields": [
        "summary",
        "artifact_hash_manifest",
        "worker_attestation"
      ],
      "schema_version": "workstream_default_submission_artifact_policy.v1"
    }
  },
  "effective_policy_hash": "sha256:<redacted>",
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "lifecycle_status": "approved",
  "merge_algorithm_version": "workstream_default_merge.v1",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "submission_artifact_policy_hash": "sha256:<redacted>",
  "submission_artifact_policy_id": "<redacted-id>",
  "superseded_at": null,
  "supersedes_effective_policy_id": null
}
```

### 08_pre_submit_checker_policy

`GET /api/v1/projects/{project_id}/guides/{guide_id}/pre-submit-checker-policy` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "checker_names": [
    "check_submission_packet",
    "check_forbidden_files",
    "check_confidentiality_attestation",
    "check_required_files",
    "check_evidence_present",
    "check_evidence_integrity",
    "check_low_quality_generated_artifacts"
  ],
  "compiled_bundle_hash": "sha256:<redacted>",
  "compiler_version": "workstream-pre-submit-compiler-v0.1",
  "created_at": "2026-07-08T23:44:02.228409Z",
  "created_by": "<redacted-id>",
  "effective_policy_hash": "sha256:<redacted>",
  "effective_policy_id": "<redacted-id>",
  "guide_id": "<redacted-id>",
  "guide_version": "v1",
  "id": "<redacted-id>",
  "lifecycle_status": "compiled",
  "project_id": "<redacted-id>",
  "source_snapshot_hash": "sha256:<redacted>",
  "source_snapshot_id": "<redacted-id>",
  "superseded_at": null,
  "supersedes_pre_submit_checker_policy_id": null
}
```

### 09_activate_guide

`POST /api/v1/projects/{project_id}/guides/{guide_id}/activate` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "effective_submission_artifact_policy": {
    "created_at": "2026-07-08T23:44:02.228409Z",
    "created_by": "<redacted-id>",
    "effective_policy": {
      "allowed_storage_schemes": [
        "local",
        "r2",
        "s3"
      ],
      "artifact_hash_algorithm": "sha256",
      "artifact_hash_required": true,
      "attestation_terms": [
        "all_or_nothing_reward",
        "confidential_data_exclusion",
        "container_bases_digest_pinned",
        "credentials_and_secret_exclusion",
        "dependencies_pinned",
        "hashes_sha256",
        "human_accountability_for_agent_assisted_work",
        "manifest_complete",
        "no_generated_caches",
        "no_reviewer_only_material",
        "no_sensitive_local_material",
        "offline_verifier_dependencies",
        "original_work",
        "task_layout_matches_metadata"
      ],
      "forbidden_artifacts": [
        {
          "pattern": "**/*.key",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
        },
        {
          "pattern": "**/*.pem",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
        },
        {
          "pattern": "**/*.pyc",
          "reason": "compiled Python bytecode is a generated artifact",
          "worker_facing_fix": "delete bytecode files before packaging"
        },
        {
          "pattern": "**/.DS_Store",
          "reason": "operating system metadata is not part of the task submission",
          "worker_facing_fix": "remove operating system metadata files"
        },
        {
          "pattern": "**/.env",
          "reason": "local configuration files may expose sensitive local settings",
          "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
        },
        {
          "pattern": "**/.env.*",
          "reason": "local configuration variants may expose sensitive local settings",
          "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
        },
        {
          "pattern": "**/.pytest_cache/**",
          "reason": "generated test cache files are stale package artifacts",
          "worker_facing_fix": "delete cache directories before packaging"
        },
        {
          "pattern": "**/__pycache__/**",
          "reason": "generated Python cache files are stale package artifacts",
          "worker_facing_fix": "delete cache directories before packaging"
        },
        {
          "pattern": "**/build/**",
          "reason": "compiled or generated build outputs are not part of source intake by default",
          "worker_facing_fix": "remove generated build directories unless explicitly required by the task"
        },
        {
          "pattern": "**/dist/**",
          "reason": "compiled or generated distribution outputs are not part of source intake by default",
          "worker_facing_fix": "remove generated distribution directories unless explicitly required by the task"
        },
        {
          "pattern": "**/docker_build.log",
          "reason": "build logs are not source submission artifacts",
          "worker_facing_fix": "remove local logs before packaging"
        },
        {
          "pattern": "**/id_ed25519",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file from the package"
        },
        {
          "pattern": "**/id_rsa",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file from the package"
        },
        {
          "pattern": "**/node_modules/**",
          "reason": "local dependency folders bloat submissions and reduce reproducibility",
          "worker_facing_fix": "remove local dependency folders and rely on pinned manifests or lockfiles"
        },
        {
          "pattern": "**/oracle_test.log",
          "reason": "test logs are not source submission artifacts",
          "worker_facing_fix": "remove local logs before packaging"
        },
        {
          "pattern": "**/platform_review.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only notes before packaging"
        },
        {
          "pattern": "**/platfrom_review.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only notes before packaging"
        },
        {
          "pattern": "**/review_packet.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only packets before packaging"
        },
        {
          "pattern": "**/rubrics.txt",
          "reason": "rubrics must be supplied through the expected rubric artifact, not as this legacy packaged file",
          "worker_facing_fix": "remove rubrics.txt and provide rubric.md"
        },
        {
          "pattern": "**/static_guard.txt",
          "reason": "local checker output is not a worker submission artifact",
          "worker_facing_fix": "remove checker logs before packaging"
        },
        {
          "pattern": "**/target/**",
          "reason": "compiled Rust build outputs should not be submitted",
          "worker_facing_fix": "remove build output directories before packaging"
        },
        {
          "pattern": "*.env",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.env.*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "*.pem",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".env",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".env*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".git",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".npmrc",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": ".pypirc",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access-key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access-key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access_key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "access_key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api-key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api-key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api_key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "api_key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "credential*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "credentials",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_dsa",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_dsa*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ecdsa",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ecdsa*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ed25519",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_ed25519*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_rsa",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "id_rsa*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "node_modules",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private-key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private-key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private_key",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "private_key*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "secret*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "secrets",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service-account",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service-account*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service_account",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "service_account*",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "token",
          "severity": "blocking",
          "source": "workstream_default"
        },
        {
          "pattern": "token*",
          "severity": "blocking",
          "source": "workstream_default"
        }
      ],
      "manifest_required": true,
      "maximum_file_size_bytes": null,
      "maximum_package_size_bytes": null,
      "merge_algorithm_version": "workstream_default_merge.v1",
      "packaging": {
        "allowed_package_formats": [
          "zip"
        ],
        "package_required": true
      },
      "project_policy": {
        "allowed_storage_schemes": [
          "local",
          "r2",
          "s3"
        ],
        "artifact_hash_algorithm": "sha256",
        "artifact_hash_required": true,
        "attestation_terms": [
          "all_or_nothing_reward",
          "container_bases_digest_pinned",
          "dependencies_pinned",
          "hashes_sha256",
          "manifest_complete",
          "no_generated_caches",
          "no_reviewer_only_material",
          "no_sensitive_local_material",
          "offline_verifier_dependencies",
          "task_layout_matches_metadata"
        ],
        "forbidden_artifacts": [
          {
            "pattern": "**/*.key",
            "reason": "private authentication material must not be submitted",
            "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
          },
          {
            "pattern": "**/*.pem",
            "reason": "private authentication material must not be submitted",
            "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
          },
          {
            "pattern": "**/*.pyc",
            "reason": "compiled Python bytecode is a generated artifact",
            "worker_facing_fix": "delete bytecode files before packaging"
          },
          {
            "pattern": "**/.DS_Store",
            "reason": "operating system metadata is not part of the task submission",
            "worker_facing_fix": "remove operating system metadata files"
          },
          {
            "pattern": "**/.env",
            "reason": "local configuration files may expose sensitive local settings",
            "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
          },
          {
            "pattern": "**/.env.*",
            "reason": "local configuration variants may expose sensitive local settings",
            "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
          },
          {
            "pattern": "**/.pytest_cache/**",
            "reason": "generated test cache files are stale package artifacts",
            "worker_facing_fix": "delete cache directories before packaging"
          },
          {
            "pattern": "**/__pycache__/**",
            "reason": "generated Python cache files are stale package artifacts",
            "worker_facing_fix": "delete cache directories before packaging"
          },
          {
            "pattern": "**/build/**",
            "reason": "compiled or generated build outputs are not part of source intake by default",
            "worker_facing_fix": "remove generated build directories unless explicitly required by the task"
          },
          {
            "pattern": "**/dist/**",
            "reason": "compiled or generated distribution outputs are not part of source intake by default",
            "worker_facing_fix": "remove generated distribution directories unless explicitly required by the task"
          },
          {
            "pattern": "**/docker_build.log",
            "reason": "build logs are not source submission artifacts",
            "worker_facing_fix": "remove local logs before packaging"
          },
          {
            "pattern": "**/id_ed25519",
            "reason": "private authentication material must not be submitted",
            "worker_facing_fix": "remove the file from the package"
          },
          {
            "pattern": "**/id_rsa",
            "reason": "private authentication material must not be submitted",
            "worker_facing_fix": "remove the file from the package"
          },
          {
            "pattern": "**/node_modules/**",
            "reason": "local dependency folders bloat submissions and reduce reproducibility",
            "worker_facing_fix": "remove local dependency folders and rely on pinned manifests or lockfiles"
          },
          {
            "pattern": "**/oracle_test.log",
            "reason": "test logs are not source submission artifacts",
            "worker_facing_fix": "remove local logs before packaging"
          },
          {
            "pattern": "**/platform_review.md",
            "reason": "review-only material must not be included in worker submissions",
            "worker_facing_fix": "remove reviewer-only notes before packaging"
          },
          {
            "pattern": "**/platfrom_review.md",
            "reason": "review-only material must not be included in worker submissions",
            "worker_facing_fix": "remove reviewer-only notes before packaging"
          },
          {
            "pattern": "**/review_packet.md",
            "reason": "review-only material must not be included in worker submissions",
            "worker_facing_fix": "remove reviewer-only packets before packaging"
          },
          {
            "pattern": "**/rubrics.txt",
            "reason": "rubrics must be supplied through the expected rubric artifact, not as this legacy packaged file",
            "worker_facing_fix": "remove rubrics.txt and provide rubric.md"
          },
          {
            "pattern": "**/static_guard.txt",
            "reason": "local checker output is not a worker submission artifact",
            "worker_facing_fix": "remove checker logs before packaging"
          },
          {
            "pattern": "**/target/**",
            "reason": "compiled Rust build outputs should not be submitted",
            "worker_facing_fix": "remove build output directories before packaging"
          }
        ],
        "manifest_required": true,
        "maximum_file_size_bytes": null,
        "maximum_package_size_bytes": null,
        "packaging": {
          "allowed_package_formats": [
            "zip"
          ],
          "package_required": true
        },
        "required_artifacts": [
          {
            "description": "container build definition for the task environment",
            "hash_required": true,
            "key": "environment_dockerfile",
            "path": "environment/Dockerfile",
            "required": true
          },
          {
            "description": "build context hygiene exclusions",
            "hash_required": true,
            "key": "environment_dockerignore",
            "path": "environment/.dockerignore",
            "required": true
          },
          {
            "description": "task scoring criteria for agent traces",
            "hash_required": true,
            "key": "rubric",
            "path": "rubric.md",
            "required": true
          },
          {
            "description": "project task metadata and runtime configuration",
            "hash_required": true,
            "key": "task_config",
            "path": "task.toml",
            "required": true
          }
        ],
        "required_evidence": [
          {
            "description": "confirms language packages and container bases are pinned as required",
            "hash_required": true,
            "key": "dependency_pinning_review",
            "label": "Dependency pinning review",
            "required": true
          },
          {
            "description": "confirms build context, size limits, and runtime setup are acceptable",
            "hash_required": true,
            "key": "environment_hygiene_review",
            "label": "Environment hygiene review",
            "required": true
          },
          {
            "description": "root or milestone instruction files are included for the task layout",
            "hash_required": true,
            "key": "instructions_present",
            "label": "Task instructions included",
            "required": true
          },
          {
            "description": "confirms verifier runner writes only all-or-nothing reward output",
            "hash_required": true,
            "key": "reward_footer_review",
            "label": "Reward footer review",
            "required": true
          },
          {
            "description": "root or milestone solution scripts are included for validation",
            "hash_required": true,
            "key": "solution_present",
            "label": "Reference solution included",
            "required": true
          },
          {
            "description": "difficulty, solution, and verification explanations are provided",
            "hash_required": true,
            "key": "submission_explanations",
            "label": "Submission explanations",
            "required": true
          },
          {
            "description": "maps stated behavior to verifier coverage and strict assertions",
            "hash_required": true,
            "key": "test_alignment_review",
            "label": "Test alignment review",
            "required": true
          },
          {
            "description": "root or milestone verifier runner and test files are included for the task layout",
            "hash_required": true,
            "key": "tests_present",
            "label": "Verifier files included",
            "required": true
          }
        ],
        "schema_version": "project_submission_artifact_policy.v1"
      },
      "required_artifacts": [
        {
          "description": "container build definition for the task environment",
          "hash_required": true,
          "key": "environment_dockerfile",
          "path": "environment/Dockerfile",
          "required": true
        },
        {
          "description": "build context hygiene exclusions",
          "hash_required": true,
          "key": "environment_dockerignore",
          "path": "environment/.dockerignore",
          "required": true
        },
        {
          "description": "task scoring criteria for agent traces",
          "hash_required": true,
          "key": "rubric",
          "path": "rubric.md",
          "required": true
        },
        {
          "description": "project task metadata and runtime configuration",
          "hash_required": true,
          "key": "task_config",
          "path": "task.toml",
          "required": true
        }
      ],
      "required_evidence": [
        {
          "description": "confirms language packages and container bases are pinned as required",
          "hash_required": true,
          "key": "dependency_pinning_review",
          "label": "Dependency pinning review",
          "required": true
        },
        {
          "description": "confirms build context, size limits, and runtime setup are acceptable",
          "hash_required": true,
          "key": "environment_hygiene_review",
          "label": "Environment hygiene review",
          "required": true
        },
        {
          "description": "root or milestone instruction files are included for the task layout",
          "hash_required": true,
          "key": "instructions_present",
          "label": "Task instructions included",
          "required": true
        },
        {
          "description": "confirms verifier runner writes only all-or-nothing reward output",
          "hash_required": true,
          "key": "reward_footer_review",
          "label": "Reward footer review",
          "required": true
        },
        {
          "description": "root or milestone solution scripts are included for validation",
          "hash_required": true,
          "key": "solution_present",
          "label": "Reference solution included",
          "required": true
        },
        {
          "description": "difficulty, solution, and verification explanations are provided",
          "hash_required": true,
          "key": "submission_explanations",
          "label": "Submission explanations",
          "required": true
        },
        {
          "description": "maps stated behavior to verifier coverage and strict assertions",
          "hash_required": true,
          "key": "test_alignment_review",
          "label": "Test alignment review",
          "required": true
        },
        {
          "description": "root or milestone verifier runner and test files are included for the task layout",
          "hash_required": true,
          "key": "tests_present",
          "label": "Verifier files included",
          "required": true
        }
      ],
      "required_packet_fields": [
        "artifact_hash_manifest",
        "summary",
        "worker_attestation"
      ],
      "schema_version": "effective_project_submission_artifact_policy.v1",
      "workstream_default_policy": {
        "allowed_storage_schemes": [
          "local",
          "s3",
          "r2"
        ],
        "artifact_hash_algorithm": "sha256",
        "artifact_hash_required": true,
        "attestation_terms": [
          "original_work",
          "confidential_data_exclusion",
          "credentials_and_secret_exclusion",
          "human_accountability_for_agent_assisted_work"
        ],
        "forbidden_artifacts": [
          {
            "pattern": ".env",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": ".env*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "*.env",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "*.env.*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": ".git",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "credentials",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "credential*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "secrets",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "secret*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": ".npmrc",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": ".pypirc",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "api_key",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "api-key",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "api_key*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "api-key*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "access_key",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "access-key",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "access_key*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "access-key*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "private_key",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "private-key",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "private_key*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "private-key*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "id_rsa",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "id_rsa*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "id_dsa",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "id_dsa*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "id_ecdsa",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "id_ecdsa*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "id_ed25519",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "id_ed25519*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "service_account",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "service-account",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "service_account*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "service-account*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "token",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "token*",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "*.pem",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "*.key",
            "severity": "blocking",
            "source": "workstream_default"
          },
          {
            "pattern": "node_modules",
            "severity": "blocking",
            "source": "workstream_default"
          }
        ],
        "manifest_required": true,
        "maximum_file_size_bytes": null,
        "maximum_package_size_bytes": null,
        "packaging": {},
        "required_artifacts": [],
        "required_evidence": [],
        "required_packet_fields": [
          "summary",
          "artifact_hash_manifest",
          "worker_attestation"
        ],
        "schema_version": "workstream_default_submission_artifact_policy.v1"
      }
    },
    "effective_policy_hash": "sha256:<redacted>",
    "guide_id": "<redacted-id>",
    "guide_version": "v1",
    "id": "<redacted-id>",
    "lifecycle_status": "approved",
    "merge_algorithm_version": "workstream_default_merge.v1",
    "project_id": "<redacted-id>",
    "source_snapshot_hash": "sha256:<redacted>",
    "source_snapshot_id": "<redacted-id>",
    "submission_artifact_policy_hash": "sha256:<redacted>",
    "submission_artifact_policy_id": "<redacted-id>",
    "superseded_at": null,
    "supersedes_effective_policy_id": null
  },
  "guide": {
    "approved_by": "<redacted-id>",
    "change_summary": "Initial Terminal Benchmark real-world guide from sanitized imported source snapshot bundle.",
    "content_markdown": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
    "created_at": "2026-07-08T23:43:31.606777Z",
    "created_by": "<redacted-id>",
    "effective_at": "2026-07-08T23:44:03.147622Z",
    "id": "<redacted-id>",
    "project_id": "<redacted-id>",
    "status": "active",
    "superseded_at": null,
    "updated_at": "2026-07-08T23:44:02.875444Z",
    "version": "v1"
  },
  "guide_source_snapshot": {
    "bundle_hash": "sha256:<redacted>",
    "captured_at": "2026-07-08T23:43:31.606777Z",
    "captured_by": "<redacted-id>",
    "guide_id": "<redacted-id>",
    "guide_version": "v1",
    "id": "<redacted-id>",
    "items": [
      {
        "content_cid": null,
        "content_hash": "sha256:<redacted>",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/docker_build.log",
        "id": "<redacted-id>",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 0,
        "media_type": "text/plain",
        "source_kind": "checker_evidence",
        "source_snapshot_id": "<redacted-id>"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:<redacted>",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/oracle_test.log",
        "id": "<redacted-id>",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 1,
        "media_type": "text/plain",
        "source_kind": "checker_evidence",
        "source_snapshot_id": "<redacted-id>"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:<redacted>",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/starter_m1_test.log",
        "id": "<redacted-id>",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 2,
        "media_type": "text/plain",
        "source_kind": "checker_evidence",
        "source_snapshot_id": "<redacted-id>"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:<redacted>",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/static_guard.txt",
        "id": "<redacted-id>",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 3,
        "media_type": "text/plain",
        "source_kind": "checker_evidence",
        "source_snapshot_id": "<redacted-id>"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:<redacted>",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/PROJECT_GUIDE.md",
        "id": "<redacted-id>",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 4,
        "media_type": "text/markdown",
        "source_kind": "project_guide",
        "source_snapshot_id": "<redacted-id>"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:<redacted>",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "inline:/guides/<redacted-id>/v1",
        "id": "<redacted-id>",
        "ingestion_adapter": "workstream_project_guide",
        "item_order": 5,
        "media_type": "application/json",
        "source_kind": "project_guide",
        "source_snapshot_id": "<redacted-id>"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:<redacted>",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/review_packet.md",
        "id": "<redacted-id>",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 6,
        "media_type": "text/markdown",
        "source_kind": "review_packet",
        "source_snapshot_id": "<redacted-id>"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:<redacted>",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/REVIEWER_PROGRAM.md",
        "id": "<redacted-id>",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 7,
        "media_type": "text/markdown",
        "source_kind": "reviewer_program",
        "source_snapshot_id": "<redacted-id>"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:<redacted>",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/<redacted-fixture-id>/task.toml",
        "id": "<redacted-id>",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 8,
        "media_type": "text/toml",
        "source_kind": "task_material",
        "source_snapshot_id": "<redacted-id>"
      }
    ],
    "manifest_json": {
      "items": [
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
          "content_hash": "sha256:<redacted>",
          "durable_ref": "import:/fixtures/<redacted-fixture-id>/docker_build.log",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/plain",
          "source_kind": "checker_evidence"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
          "content_hash": "sha256:<redacted>",
          "durable_ref": "import:/fixtures/<redacted-fixture-id>/oracle_test.log",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/plain",
          "source_kind": "checker_evidence"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
          "content_hash": "sha256:<redacted>",
          "durable_ref": "import:/fixtures/<redacted-fixture-id>/starter_m1_test.log",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/plain",
          "source_kind": "checker_evidence"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
          "content_hash": "sha256:<redacted>",
          "durable_ref": "import:/fixtures/<redacted-fixture-id>/static_guard.txt",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/plain",
          "source_kind": "checker_evidence"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
          "content_hash": "sha256:<redacted>",
          "durable_ref": "import:/fixtures/<redacted-fixture-id>/PROJECT_GUIDE.md",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/markdown",
          "source_kind": "project_guide"
        },
        {
          "content_cid": null,
          "content_excerpt": null,
          "content_hash": "sha256:<redacted>",
          "durable_ref": "inline:/guides/<redacted-id>/v1",
          "ingestion_adapter": "workstream_project_guide",
          "media_type": "application/json",
          "source_kind": "project_guide"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
          "content_hash": "sha256:<redacted>",
          "durable_ref": "import:/fixtures/<redacted-fixture-id>/review_packet.md",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/markdown",
          "source_kind": "review_packet"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
          "content_hash": "sha256:<redacted>",
          "durable_ref": "import:/fixtures/<redacted-fixture-id>/REVIEWER_PROGRAM.md",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/markdown",
          "source_kind": "reviewer_program"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
          "content_hash": "sha256:<redacted>",
          "durable_ref": "import:/fixtures/<redacted-fixture-id>/task.toml",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/toml",
          "source_kind": "task_material"
        }
      ],
      "schema_version": "guide_source_snapshot.v1"
    },
    "manifest_schema_version": "guide_source_snapshot.v1",
    "project_id": "<redacted-id>"
  },
  "guide_sufficiency_report": {
    "acknowledgement_note": null,
    "agent_name": "ProjectGuideSufficiencyAgent",
    "agent_version": "workstream-sufficiency-agent-v0.1",
    "created_at": "2026-07-08T23:43:40.523990Z",
    "created_by": "workstream-system:project-setup-pipeline",
    "findings": [],
    "guide_id": "<redacted-id>",
    "guide_version": "v1",
    "id": "<redacted-id>",
    "project_id": "<redacted-id>",
    "source_snapshot_hash": "sha256:<redacted>",
    "source_snapshot_id": "<redacted-id>",
    "status": "passed",
    "summary": "The guide provides sufficient reviewer criteria and workflow direction for this Terminal Benchmark task review, including milestone structure, static guard handling, dependency pinning, Dockerfile requirements, test alignment, rubric rules, reward behavior, and category mapping.",
    "warnings_acknowledged_at": null,
    "warnings_acknowledged_by_actor": null,
    "warnings_acknowledged_by_role": null
  },
  "payment_policy": {
    "accepted_payment_rule": "pay_on_acceptance",
    "base_amount": "25.00",
    "created_at": "2026-07-08T23:43:31.606777Z",
    "currency": "USD",
    "guide_version": "v1",
    "id": "<redacted-id>",
    "payout_type": "fixed",
    "project_id": "<redacted-id>",
    "rejection_payment_rule": "no_payment_on_reject",
    "revision_payment_rule": "no_extra_payment_for_revisions"
  },
  "post_submit_checker_policy": {
    "blocking_severities": [
      "high",
      "medium"
    ],
    "created_at": "2026-07-08T23:43:31.606777Z",
    "guide_version": "v1",
    "id": "<redacted-id>",
    "policy_hash": "sha256:<redacted>",
    "project_id": "<redacted-id>",
    "required_checkers": [
      "check_policy_context_present",
      "check_low_quality_generated_artifacts"
    ],
    "warning_checkers": []
  },
  "pre_submit_checker_policy": {
    "checker_configs": {
      "enforce_storage_scheme": {
        "schemes": [
          "local",
          "r2",
          "s3"
        ]
      },
      "forbid_artifact": {
        "patterns": [
          "**/*.key",
          "**/*.pem",
          "**/*.pyc",
          "**/.DS_Store",
          "**/.env",
          "**/.env.*",
          "**/.pytest_cache/**",
          "**/__pycache__/**",
          "**/build/**",
          "**/dist/**",
          "**/docker_build.log",
          "**/id_ed25519",
          "**/id_rsa",
          "**/node_modules/**",
          "**/oracle_test.log",
          "**/platform_review.md",
          "**/platfrom_review.md",
          "**/review_packet.md",
          "**/rubrics.txt",
          "**/static_guard.txt",
          "**/target/**",
          "*.env",
          "*.env.*",
          "*.key",
          "*.pem",
          ".env",
          ".env*",
          ".git",
          ".npmrc",
          ".pypirc",
          "access-key",
          "access-key*",
          "access_key",
          "access_key*",
          "api-key",
          "api-key*",
          "api_key",
          "api_key*",
          "credential*",
          "credentials",
          "id_dsa",
          "id_dsa*",
          "id_ecdsa",
          "id_ecdsa*",
          "id_ed25519",
          "id_ed25519*",
          "id_rsa",
          "id_rsa*",
          "node_modules",
          "private-key",
          "private-key*",
          "private_key",
          "private_key*",
          "secret*",
          "secrets",
          "service-account",
          "service-account*",
          "service_account",
          "service_account*",
          "token",
          "token*"
        ]
      },
      "require_attestation": {
        "terms": [
          "all_or_nothing_reward",
          "confidential_data_exclusion",
          "container_bases_digest_pinned",
          "credentials_and_secret_exclusion",
          "dependencies_pinned",
          "hashes_sha256",
          "human_accountability_for_agent_assisted_work",
          "manifest_complete",
          "no_generated_caches",
          "no_reviewer_only_material",
          "no_sensitive_local_material",
          "offline_verifier_dependencies",
          "original_work",
          "task_layout_matches_metadata"
        ]
      },
      "require_file": {
        "artifact_keys": [
          "environment_dockerfile",
          "environment_dockerignore",
          "rubric",
          "task_config"
        ]
      },
      "require_manifest_field": {},
      "require_minimum_evidence": {
        "evidence_keys": [
          "dependency_pinning_review",
          "environment_hygiene_review",
          "instructions_present",
          "reward_footer_review",
          "solution_present",
          "submission_explanations",
          "test_alignment_review",
          "tests_present"
        ]
      },
      "require_packaging": {
        "allowed_package_formats": [
          "zip"
        ],
        "package_required": true
      },
      "validate_submission_packet": {
        "fields": [
          "artifact_hash_manifest",
          "summary",
          "worker_attestation"
        ]
      },
      "verify_hash": {
        "algorithm": "sha256"
      },
      "warn_low_quality_generated_artifact": {}
    },
    "checker_names": [
      "check_submission_packet",
      "check_forbidden_files",
      "check_confidentiality_attestation",
      "check_required_files",
      "check_evidence_present",
      "check_evidence_integrity",
      "check_low_quality_generated_artifacts"
    ],
    "compiled_bundle_hash": "sha256:<redacted>",
    "compiler_version": "workstream-pre-submit-compiler-v0.1",
    "created_at": "2026-07-08T23:44:02.228409Z",
    "created_by": "<redacted-id>",
    "effective_policy_hash": "sha256:<redacted>",
    "effective_policy_id": "<redacted-id>",
    "guide_id": "<redacted-id>",
    "guide_version": "v1",
    "id": "<redacted-id>",
    "lifecycle_status": "compiled",
    "project_id": "<redacted-id>",
    "source_snapshot_hash": "sha256:<redacted>",
    "source_snapshot_id": "<redacted-id>",
    "superseded_at": null,
    "supersedes_pre_submit_checker_policy_id": null
  },
  "review_policy": {
    "allowed_decisions": [
      "accept",
      "needs_revision",
      "reject"
    ],
    "created_at": "2026-07-08T23:43:31.606777Z",
    "guide_version": "v1",
    "id": "<redacted-id>",
    "minimum_finding_fields": [
      "issue",
      "required_fix"
    ],
    "project_id": "<redacted-id>",
    "requires_second_review": false,
    "sla_hours": 24
  },
  "revision_policy": {
    "allowed_resubmission_states": [
      "needs_revision"
    ],
    "auto_reject_after_limit": true,
    "created_at": "2026-07-08T23:43:31.606777Z",
    "guide_version": "v1",
    "id": "<redacted-id>",
    "max_revision_rounds": 7,
    "project_id": "<redacted-id>",
    "reviewer_reassignment_rule": "same_reviewer_preferred",
    "revision_deadline_hours": 48
  },
  "submission_artifact_policy": {
    "approved_at": "2026-07-08T23:44:02.420104Z",
    "approved_by_actor": "<redacted-id>",
    "approved_by_role": "project_manager",
    "change_summary": null,
    "created_at": "2026-07-08T23:44:00.095072Z",
    "created_by": "workstream-system:project-setup-pipeline",
    "derivation_agent_name": "SubmissionArtifactPolicyDerivationAgent",
    "derivation_agent_version": "workstream-policy-derivation-agent-v0.1",
    "derivation_source": "agent_derivation",
    "guide_id": "<redacted-id>",
    "guide_version": "v1",
    "id": "<redacted-id>",
    "lifecycle_status": "approved",
    "policy_body": {
      "allowed_storage_schemes": [
        "local",
        "r2",
        "s3"
      ],
      "artifact_hash_algorithm": "sha256",
      "artifact_hash_required": true,
      "attestation_terms": [
        "all_or_nothing_reward",
        "container_bases_digest_pinned",
        "dependencies_pinned",
        "hashes_sha256",
        "manifest_complete",
        "no_generated_caches",
        "no_reviewer_only_material",
        "no_sensitive_local_material",
        "offline_verifier_dependencies",
        "task_layout_matches_metadata"
      ],
      "forbidden_artifacts": [
        {
          "pattern": "**/*.key",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
        },
        {
          "pattern": "**/*.pem",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
        },
        {
          "pattern": "**/*.pyc",
          "reason": "compiled Python bytecode is a generated artifact",
          "worker_facing_fix": "delete bytecode files before packaging"
        },
        {
          "pattern": "**/.DS_Store",
          "reason": "operating system metadata is not part of the task submission",
          "worker_facing_fix": "remove operating system metadata files"
        },
        {
          "pattern": "**/.env",
          "reason": "local configuration files may expose sensitive local settings",
          "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
        },
        {
          "pattern": "**/.env.*",
          "reason": "local configuration variants may expose sensitive local settings",
          "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
        },
        {
          "pattern": "**/.pytest_cache/**",
          "reason": "generated test cache files are stale package artifacts",
          "worker_facing_fix": "delete cache directories before packaging"
        },
        {
          "pattern": "**/__pycache__/**",
          "reason": "generated Python cache files are stale package artifacts",
          "worker_facing_fix": "delete cache directories before packaging"
        },
        {
          "pattern": "**/build/**",
          "reason": "compiled or generated build outputs are not part of source intake by default",
          "worker_facing_fix": "remove generated build directories unless explicitly required by the task"
        },
        {
          "pattern": "**/dist/**",
          "reason": "compiled or generated distribution outputs are not part of source intake by default",
          "worker_facing_fix": "remove generated distribution directories unless explicitly required by the task"
        },
        {
          "pattern": "**/docker_build.log",
          "reason": "build logs are not source submission artifacts",
          "worker_facing_fix": "remove local logs before packaging"
        },
        {
          "pattern": "**/id_ed25519",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file from the package"
        },
        {
          "pattern": "**/id_rsa",
          "reason": "private authentication material must not be submitted",
          "worker_facing_fix": "remove the file from the package"
        },
        {
          "pattern": "**/node_modules/**",
          "reason": "local dependency folders bloat submissions and reduce reproducibility",
          "worker_facing_fix": "remove local dependency folders and rely on pinned manifests or lockfiles"
        },
        {
          "pattern": "**/oracle_test.log",
          "reason": "test logs are not source submission artifacts",
          "worker_facing_fix": "remove local logs before packaging"
        },
        {
          "pattern": "**/platform_review.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only notes before packaging"
        },
        {
          "pattern": "**/platfrom_review.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only notes before packaging"
        },
        {
          "pattern": "**/review_packet.md",
          "reason": "review-only material must not be included in worker submissions",
          "worker_facing_fix": "remove reviewer-only packets before packaging"
        },
        {
          "pattern": "**/rubrics.txt",
          "reason": "rubrics must be supplied through the expected rubric artifact, not as this legacy packaged file",
          "worker_facing_fix": "remove rubrics.txt and provide rubric.md"
        },
        {
          "pattern": "**/static_guard.txt",
          "reason": "local checker output is not a worker submission artifact",
          "worker_facing_fix": "remove checker logs before packaging"
        },
        {
          "pattern": "**/target/**",
          "reason": "compiled Rust build outputs should not be submitted",
          "worker_facing_fix": "remove build output directories before packaging"
        }
      ],
      "manifest_required": true,
      "maximum_file_size_bytes": null,
      "maximum_package_size_bytes": null,
      "packaging": {
        "allowed_package_formats": [
          "zip"
        ],
        "package_required": true
      },
      "required_artifacts": [
        {
          "description": "container build definition for the task environment",
          "hash_required": true,
          "key": "environment_dockerfile",
          "path": "environment/Dockerfile",
          "required": true
        },
        {
          "description": "build context hygiene exclusions",
          "hash_required": true,
          "key": "environment_dockerignore",
          "path": "environment/.dockerignore",
          "required": true
        },
        {
          "description": "task scoring criteria for agent traces",
          "hash_required": true,
          "key": "rubric",
          "path": "rubric.md",
          "required": true
        },
        {
          "description": "project task metadata and runtime configuration",
          "hash_required": true,
          "key": "task_config",
          "path": "task.toml",
          "required": true
        }
      ],
      "required_evidence": [
        {
          "description": "confirms language packages and container bases are pinned as required",
          "hash_required": true,
          "key": "dependency_pinning_review",
          "label": "Dependency pinning review",
          "required": true
        },
        {
          "description": "confirms build context, size limits, and runtime setup are acceptable",
          "hash_required": true,
          "key": "environment_hygiene_review",
          "label": "Environment hygiene review",
          "required": true
        },
        {
          "description": "root or milestone instruction files are included for the task layout",
          "hash_required": true,
          "key": "instructions_present",
          "label": "Task instructions included",
          "required": true
        },
        {
          "description": "confirms verifier runner writes only all-or-nothing reward output",
          "hash_required": true,
          "key": "reward_footer_review",
          "label": "Reward footer review",
          "required": true
        },
        {
          "description": "root or milestone solution scripts are included for validation",
          "hash_required": true,
          "key": "solution_present",
          "label": "Reference solution included",
          "required": true
        },
        {
          "description": "difficulty, solution, and verification explanations are provided",
          "hash_required": true,
          "key": "submission_explanations",
          "label": "Submission explanations",
          "required": true
        },
        {
          "description": "maps stated behavior to verifier coverage and strict assertions",
          "hash_required": true,
          "key": "test_alignment_review",
          "label": "Test alignment review",
          "required": true
        },
        {
          "description": "root or milestone verifier runner and test files are included for the task layout",
          "hash_required": true,
          "key": "tests_present",
          "label": "Verifier files included",
          "required": true
        }
      ],
      "schema_version": "project_submission_artifact_policy.v1"
    },
    "policy_hash": "sha256:<redacted>",
    "policy_version": "agent-9843f69ef5b7f7631f98a61d",
    "project_id": "<redacted-id>",
    "source_material_refs": [
      "import:/fixtures/<redacted-fixture-id>/docker_build.log",
      "import:/fixtures/<redacted-fixture-id>/oracle_test.log",
      "import:/fixtures/<redacted-fixture-id>/starter_m1_test.log",
      "import:/fixtures/<redacted-fixture-id>/static_guard.txt",
      "import:/fixtures/<redacted-fixture-id>/PROJECT_GUIDE.md",
      "inline:/guides/<redacted-id>/v1",
      "import:/fixtures/<redacted-fixture-id>/review_packet.md",
      "import:/fixtures/<redacted-fixture-id>/REVIEWER_PROGRAM.md",
      "import:/fixtures/<redacted-fixture-id>/task.toml"
    ],
    "source_snapshot_hash": "sha256:<redacted>",
    "source_snapshot_id": "<redacted-id>",
    "superseded_at": null,
    "supersedes_policy_id": null,
    "updated_at": "2026-07-08T23:44:02.228409Z"
  }
}
```

### 10_task_create

`POST /api/v1/projects/{project_id}/tasks` -> HTTP `201`

Request body:

```json
{
  "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
  "description": "Real Terminal Benchmark reference fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "<redacted-fixture-id>",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "<redacted-domain-tag>",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:<redacted>",
  "source_ref": "terminal-benchmark/<redacted-fixture-id>/live-api/<redacted-run-id>",
  "source_type": "manual",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark <redacted-fixture-id> live-api"
}
```

Response body:

```json
{
  "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
  "created_at": "2026-07-08T23:44:03.452947Z",
  "created_by": "<redacted-id>",
  "description": "Real Terminal Benchmark reference fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "<redacted-fixture-id>",
  "id": "<redacted-id>",
  "project_id": "<redacted-id>",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "<redacted-domain-tag>",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:<redacted>",
  "source_ref": "terminal-benchmark/<redacted-fixture-id>/live-api/<redacted-run-id>",
  "source_type": "manual",
  "status": "draft",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark <redacted-fixture-id> live-api",
  "updated_at": "2026-07-08T23:44:03.452947Z"
}
```

### 11_task_screen

`POST /api/v1/tasks/{task_id}/screen` -> HTTP `200`

Request body:

```json
{
  "reason": "Terminal Benchmark final clean live API screening; lock active guide and policy context."
}
```

Response body:

```json
{
  "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
  "base_amount": "25.00",
  "created_at": "2026-07-08T23:44:03.452947Z",
  "created_by": "<redacted-id>",
  "currency": "USD",
  "description": "Real Terminal Benchmark reference fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "<redacted-fixture-id>",
  "id": "<redacted-id>",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
  "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
  "locked_guide_source_snapshot_hash": "sha256:<redacted>",
  "locked_guide_source_snapshot_id": "<redacted-id>",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
  "locked_pre_submit_checker_policy_id": "<redacted-id>",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "payout_type": "fixed",
  "project_id": "<redacted-id>",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "<redacted-domain-tag>",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:<redacted>",
  "source_ref": "terminal-benchmark/<redacted-fixture-id>/live-api/<redacted-run-id>",
  "source_type": "manual",
  "status": "screening",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark <redacted-fixture-id> live-api",
  "updated_at": "2026-07-08T23:44:03.630101Z"
}
```

### 12_locked_context_after_screen

`GET /api/v1/tasks/{task_id}/locked-context` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
  "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
  "locked_guide_source_snapshot_hash": "sha256:<redacted>",
  "locked_guide_source_snapshot_id": "<redacted-id>",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_post_submit_checker_policy_body_summary": {
    "blocking_severities": [
      "high",
      "medium"
    ],
    "default_checkers": [
      "check_submission_packet",
      "check_policy_context_present",
      "check_evidence_present",
      "check_evidence_integrity",
      "check_required_files",
      "check_forbidden_files",
      "check_confidentiality_attestation",
      "check_low_quality_generated_artifacts"
    ],
    "execution_checkers": [
      "check_submission_packet",
      "check_policy_context_present",
      "check_evidence_present",
      "check_evidence_integrity",
      "check_required_files",
      "check_forbidden_files",
      "check_confidentiality_attestation",
      "check_low_quality_generated_artifacts"
    ],
    "required_checkers": [
      "check_policy_context_present",
      "check_low_quality_generated_artifacts"
    ],
    "schema_version": "post_submit_checker_policy.v1",
    "warning_checkers": []
  },
  "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
  "locked_post_submit_checker_policy_id": "<redacted-id>",
  "locked_post_submit_checker_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
  "locked_pre_submit_checker_policy_id": "<redacted-id>",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "project_id": "<redacted-id>",
  "task_id": "<redacted-id>"
}
```

### 13_task_release

`POST /api/v1/tasks/{task_id}/release` -> HTTP `200`

Request body:

```json
{
  "reason": "Terminal Benchmark final clean live API ready for worker claim."
}
```

Response body:

```json
{
  "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
  "base_amount": "25.00",
  "created_at": "2026-07-08T23:44:03.452947Z",
  "created_by": "<redacted-id>",
  "currency": "USD",
  "description": "Real Terminal Benchmark reference fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "<redacted-fixture-id>",
  "id": "<redacted-id>",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
  "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
  "locked_guide_source_snapshot_hash": "sha256:<redacted>",
  "locked_guide_source_snapshot_id": "<redacted-id>",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
  "locked_pre_submit_checker_policy_id": "<redacted-id>",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "payout_type": "fixed",
  "project_id": "<redacted-id>",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "<redacted-domain-tag>",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:<redacted>",
  "source_ref": "terminal-benchmark/<redacted-fixture-id>/live-api/<redacted-run-id>",
  "source_type": "manual",
  "status": "ready",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark <redacted-fixture-id> live-api",
  "updated_at": "2026-07-08T23:44:04.041939Z"
}
```

### 14_worker_profile

`POST /api/v1/workers/me/profile` -> HTTP `200`

Request body:

```json
{
  "skill_tags": [
    "rust",
    "json",
    "<redacted-domain-tag>",
    "containers",
    "cli"
  ]
}
```

Response body:

```json
{
  "actor_id": "<redacted-id>",
  "created_at": "2026-07-08T23:44:04.145081Z",
  "display_name": "Terminal Benchmark Worker Ws16 Clean Cb1540Ba",
  "email": "terminal-benchmark-worker-<redacted-run-id>@flow.local",
  "external_issuer": "https://auth.flow.local/e2e",
  "external_subject": "terminal-benchmark-worker-<redacted-run-id>",
  "id": "<redacted-id>",
  "profile_metadata": {
    "source": "worker_profile_api"
  },
  "profile_type": "worker",
  "scope_id": "global",
  "scope_type": "global",
  "skill_tags": [
    "rust",
    "json",
    "<redacted-domain-tag>",
    "containers",
    "cli"
  ],
  "status": "active",
  "updated_at": "2026-07-08T23:44:04.240478Z"
}
```

### 15_task_claim

`POST /api/v1/tasks/{task_id}/claim` -> HTTP `200`

Request body:

```json
{
  "reason": "Terminal Benchmark final clean live API worker claim."
}
```

Response body:

```json
{
  "assignment": {
    "accepted_at": "2026-07-08T23:44:04.575130Z",
    "assigned_at": "2026-07-08T23:44:04.503583Z",
    "assigned_by": "<redacted-id>",
    "id": "<redacted-id>",
    "status": "active",
    "task_id": "<redacted-id>",
    "worker_id": "<redacted-id>"
  },
  "task": {
    "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
    "base_amount": "25.00",
    "created_at": "2026-07-08T23:44:03.452947Z",
    "currency": "USD",
    "description": "Real Terminal Benchmark reference fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
    "difficulty": "medium",
    "estimated_time_minutes": 75,
    "id": "<redacted-id>",
    "locked_guide_version": "v1",
    "locked_payment_policy_version": "v1",
    "locked_review_policy_version": "v1",
    "locked_revision_policy_version": "v1",
    "payout_type": "fixed",
    "project_id": "<redacted-id>",
    "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
    "skill_tags": [
      "rust",
      "json",
      "<redacted-domain-tag>",
      "containers",
      "cli"
    ],
    "source_type": "manual",
    "status": "claimed",
    "task_type": "terminal_benchmark",
    "title": "Terminal Benchmark <redacted-fixture-id> live-api",
    "updated_at": "2026-07-08T23:44:04.503583Z"
  }
}
```

### 16_task_start

`POST /api/v1/tasks/{task_id}/start` -> HTTP `200`

Request body:

```json
{
  "reason": "Terminal Benchmark final clean live API worker started work."
}
```

Response body:

```json
{
  "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
  "base_amount": "25.00",
  "created_at": "2026-07-08T23:44:03.452947Z",
  "currency": "USD",
  "description": "Real Terminal Benchmark reference fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "id": "<redacted-id>",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "payout_type": "fixed",
  "project_id": "<redacted-id>",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "<redacted-domain-tag>",
    "containers",
    "cli"
  ],
  "source_type": "manual",
  "status": "in_progress",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark <redacted-fixture-id> live-api",
  "updated_at": "2026-07-08T23:44:04.727342Z"
}
```

### 17_locked_context_after_start

`GET /api/v1/tasks/{task_id}/locked-context` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
  "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
  "locked_guide_source_snapshot_hash": "sha256:<redacted>",
  "locked_guide_source_snapshot_id": "<redacted-id>",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_post_submit_checker_policy_body_summary": {
    "blocking_severities": [
      "high",
      "medium"
    ],
    "default_checkers": [
      "check_submission_packet",
      "check_policy_context_present",
      "check_evidence_present",
      "check_evidence_integrity",
      "check_required_files",
      "check_forbidden_files",
      "check_confidentiality_attestation",
      "check_low_quality_generated_artifacts"
    ],
    "execution_checkers": [
      "check_submission_packet",
      "check_policy_context_present",
      "check_evidence_present",
      "check_evidence_integrity",
      "check_required_files",
      "check_forbidden_files",
      "check_confidentiality_attestation",
      "check_low_quality_generated_artifacts"
    ],
    "required_checkers": [
      "check_policy_context_present",
      "check_low_quality_generated_artifacts"
    ],
    "schema_version": "post_submit_checker_policy.v1",
    "warning_checkers": []
  },
  "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
  "locked_post_submit_checker_policy_id": "<redacted-id>",
  "locked_post_submit_checker_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
  "locked_pre_submit_checker_policy_id": "<redacted-id>",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "project_id": "<redacted-id>",
  "task_id": "<redacted-id>"
}
```

### 18_work_context

`GET /api/v1/tasks/{task_id}/work-context` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "guide": {
    "change_summary": "Initial Terminal Benchmark real-world guide from sanitized imported source snapshot bundle.",
    "content_markdown": "<redacted-large-text sha256:<redacted> bytes:<redacted>>",
    "effective_at": "2026-07-08T23:44:03.147622Z",
    "id": "<redacted-id>",
    "version": "v1"
  },
  "lifecycle": {
    "assigned_to_current_actor": true,
    "can_run_pre_submit_check": true,
    "can_submit": true,
    "next_actions": [
      "run_pre_submit_check",
      "submit"
    ],
    "status": "in_progress"
  },
  "payment_policy": {
    "base_amount": "25.00",
    "currency": "USD",
    "guide_version": "v1",
    "payout_type": "fixed"
  },
  "project": {
    "description": "Real Terminal Benchmark fixture used as Workstream API evidence with sanitized source text.",
    "id": "<redacted-id>",
    "name": "Terminal Benchmark Real API <redacted-run-id>",
    "slug": "terminal-benchmark-real-api-<redacted-run-id>"
  },
  "review_policy": {
    "guide_version": "v1"
  },
  "revision_policy": {
    "guide_version": "v1"
  },
  "task": {
    "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
    "base_amount": "25.00",
    "created_at": "2026-07-08T23:44:03.452947Z",
    "currency": "USD",
    "description": "Real Terminal Benchmark reference fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
    "difficulty": "medium",
    "estimated_time_minutes": 75,
    "id": "<redacted-id>",
    "locked_guide_version": "v1",
    "payout_type": "fixed",
    "project_id": "<redacted-id>",
    "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
    "skill_tags": [
      "rust",
      "json",
      "<redacted-domain-tag>",
      "containers",
      "cli"
    ],
    "status": "in_progress",
    "task_type": "terminal_benchmark",
    "title": "Terminal Benchmark <redacted-fixture-id> live-api",
    "updated_at": "2026-07-08T23:44:04.727342Z"
  }
}
```

### 19_submission_requirements

`GET /api/v1/tasks/{task_id}/submission-requirements` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "allowed_storage_schemes": [
    "local",
    "r2",
    "s3"
  ],
  "artifact_hash_algorithm": "sha256",
  "artifact_hash_required": true,
  "attestation_terms": [
    "all_or_nothing_reward",
    "confidential_data_exclusion",
    "container_bases_digest_pinned",
    "credentials_and_secret_exclusion",
    "dependencies_pinned",
    "hashes_sha256",
    "human_accountability_for_agent_assisted_work",
    "manifest_complete",
    "no_generated_caches",
    "no_reviewer_only_material",
    "no_sensitive_local_material",
    "offline_verifier_dependencies",
    "original_work",
    "task_layout_matches_metadata"
  ],
  "forbidden_artifacts": [
    {
      "pattern": "**/*.key",
      "reason": "private authentication material must not be submitted",
      "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
    },
    {
      "pattern": "**/*.pem",
      "reason": "private authentication material must not be submitted",
      "worker_facing_fix": "remove the file unless it is a non-sensitive public test fixture explicitly required by the task"
    },
    {
      "pattern": "**/*.pyc",
      "reason": "compiled Python bytecode is a generated artifact",
      "worker_facing_fix": "delete bytecode files before packaging"
    },
    {
      "pattern": "**/.DS_Store",
      "reason": "operating system metadata is not part of the task submission",
      "worker_facing_fix": "remove operating system metadata files"
    },
    {
      "pattern": "**/.env",
      "reason": "local configuration files may expose sensitive local settings",
      "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
    },
    {
      "pattern": "**/.env.*",
      "reason": "local configuration variants may expose sensitive local settings",
      "worker_facing_fix": "remove the file and submit only safe example configuration if needed"
    },
    {
      "pattern": "**/.pytest_cache/**",
      "reason": "generated test cache files are stale package artifacts",
      "worker_facing_fix": "delete cache directories before packaging"
    },
    {
      "pattern": "**/__pycache__/**",
      "reason": "generated Python cache files are stale package artifacts",
      "worker_facing_fix": "delete cache directories before packaging"
    },
    {
      "pattern": "**/build/**",
      "reason": "compiled or generated build outputs are not part of source intake by default",
      "worker_facing_fix": "remove generated build directories unless explicitly required by the task"
    },
    {
      "pattern": "**/dist/**",
      "reason": "compiled or generated distribution outputs are not part of source intake by default",
      "worker_facing_fix": "remove generated distribution directories unless explicitly required by the task"
    },
    {
      "pattern": "**/docker_build.log",
      "reason": "build logs are not source submission artifacts",
      "worker_facing_fix": "remove local logs before packaging"
    },
    {
      "pattern": "**/id_ed25519",
      "reason": "private authentication material must not be submitted",
      "worker_facing_fix": "remove the file from the package"
    },
    {
      "pattern": "**/id_rsa",
      "reason": "private authentication material must not be submitted",
      "worker_facing_fix": "remove the file from the package"
    },
    {
      "pattern": "**/node_modules/**",
      "reason": "local dependency folders bloat submissions and reduce reproducibility",
      "worker_facing_fix": "remove local dependency folders and rely on pinned manifests or lockfiles"
    },
    {
      "pattern": "**/oracle_test.log",
      "reason": "test logs are not source submission artifacts",
      "worker_facing_fix": "remove local logs before packaging"
    },
    {
      "pattern": "**/platform_review.md",
      "reason": "review-only material must not be included in worker submissions",
      "worker_facing_fix": "remove reviewer-only notes before packaging"
    },
    {
      "pattern": "**/platfrom_review.md",
      "reason": "review-only material must not be included in worker submissions",
      "worker_facing_fix": "remove reviewer-only notes before packaging"
    },
    {
      "pattern": "**/review_packet.md",
      "reason": "review-only material must not be included in worker submissions",
      "worker_facing_fix": "remove reviewer-only packets before packaging"
    },
    {
      "pattern": "**/rubrics.txt",
      "reason": "rubrics must be supplied through the expected rubric artifact, not as this legacy packaged file",
      "worker_facing_fix": "remove rubrics.txt and provide rubric.md"
    },
    {
      "pattern": "**/static_guard.txt",
      "reason": "local checker output is not a worker submission artifact",
      "worker_facing_fix": "remove checker logs before packaging"
    },
    {
      "pattern": "**/target/**",
      "reason": "compiled Rust build outputs should not be submitted",
      "worker_facing_fix": "remove build output directories before packaging"
    },
    {
      "pattern": "*.env",
      "severity": "blocking"
    },
    {
      "pattern": "*.env.*",
      "severity": "blocking"
    },
    {
      "pattern": "*.key",
      "severity": "blocking"
    },
    {
      "pattern": "*.pem",
      "severity": "blocking"
    },
    {
      "pattern": ".env",
      "severity": "blocking"
    },
    {
      "pattern": ".env*",
      "severity": "blocking"
    },
    {
      "pattern": ".git",
      "severity": "blocking"
    },
    {
      "pattern": ".npmrc",
      "severity": "blocking"
    },
    {
      "pattern": ".pypirc",
      "severity": "blocking"
    },
    {
      "pattern": "access-key",
      "severity": "blocking"
    },
    {
      "pattern": "access-key*",
      "severity": "blocking"
    },
    {
      "pattern": "access_key",
      "severity": "blocking"
    },
    {
      "pattern": "access_key*",
      "severity": "blocking"
    },
    {
      "pattern": "api-key",
      "severity": "blocking"
    },
    {
      "pattern": "api-key*",
      "severity": "blocking"
    },
    {
      "pattern": "api_key",
      "severity": "blocking"
    },
    {
      "pattern": "api_key*",
      "severity": "blocking"
    },
    {
      "pattern": "credential*",
      "severity": "blocking"
    },
    {
      "pattern": "credentials",
      "severity": "blocking"
    },
    {
      "pattern": "id_dsa",
      "severity": "blocking"
    },
    {
      "pattern": "id_dsa*",
      "severity": "blocking"
    },
    {
      "pattern": "id_ecdsa",
      "severity": "blocking"
    },
    {
      "pattern": "id_ecdsa*",
      "severity": "blocking"
    },
    {
      "pattern": "id_ed25519",
      "severity": "blocking"
    },
    {
      "pattern": "id_ed25519*",
      "severity": "blocking"
    },
    {
      "pattern": "id_rsa",
      "severity": "blocking"
    },
    {
      "pattern": "id_rsa*",
      "severity": "blocking"
    },
    {
      "pattern": "node_modules",
      "severity": "blocking"
    },
    {
      "pattern": "private-key",
      "severity": "blocking"
    },
    {
      "pattern": "private-key*",
      "severity": "blocking"
    },
    {
      "pattern": "private_key",
      "severity": "blocking"
    },
    {
      "pattern": "private_key*",
      "severity": "blocking"
    },
    {
      "pattern": "secret*",
      "severity": "blocking"
    },
    {
      "pattern": "secrets",
      "severity": "blocking"
    },
    {
      "pattern": "service-account",
      "severity": "blocking"
    },
    {
      "pattern": "service-account*",
      "severity": "blocking"
    },
    {
      "pattern": "service_account",
      "severity": "blocking"
    },
    {
      "pattern": "service_account*",
      "severity": "blocking"
    },
    {
      "pattern": "token",
      "severity": "blocking"
    },
    {
      "pattern": "token*",
      "severity": "blocking"
    }
  ],
  "guide_version": "v1",
  "manifest_required": true,
  "merge_algorithm_version": "workstream_default_merge.v1",
  "packaging": {
    "allowed_package_formats": [
      "zip"
    ],
    "package_required": true
  },
  "policy_schema_version": "effective_project_submission_artifact_policy.v1",
  "project_id": "<redacted-id>",
  "required_artifacts": [
    {
      "description": "container build definition for the task environment",
      "hash_required": true,
      "key": "environment_dockerfile",
      "path": "environment/Dockerfile",
      "required": true
    },
    {
      "description": "build context hygiene exclusions",
      "hash_required": true,
      "key": "environment_dockerignore",
      "path": "environment/.dockerignore",
      "required": true
    },
    {
      "description": "task scoring criteria for agent traces",
      "hash_required": true,
      "key": "rubric",
      "path": "rubric.md",
      "required": true
    },
    {
      "description": "project task metadata and runtime configuration",
      "hash_required": true,
      "key": "task_config",
      "path": "task.toml",
      "required": true
    }
  ],
  "required_evidence": [
    {
      "description": "confirms language packages and container bases are pinned as required",
      "hash_required": true,
      "key": "dependency_pinning_review",
      "label": "Dependency pinning review",
      "required": true
    },
    {
      "description": "confirms build context, size limits, and runtime setup are acceptable",
      "hash_required": true,
      "key": "environment_hygiene_review",
      "label": "Environment hygiene review",
      "required": true
    },
    {
      "description": "root or milestone instruction files are included for the task layout",
      "hash_required": true,
      "key": "instructions_present",
      "label": "Task instructions included",
      "required": true
    },
    {
      "description": "confirms verifier runner writes only all-or-nothing reward output",
      "hash_required": true,
      "key": "reward_footer_review",
      "label": "Reward footer review",
      "required": true
    },
    {
      "description": "root or milestone solution scripts are included for validation",
      "hash_required": true,
      "key": "solution_present",
      "label": "Reference solution included",
      "required": true
    },
    {
      "description": "difficulty, solution, and verification explanations are provided",
      "hash_required": true,
      "key": "submission_explanations",
      "label": "Submission explanations",
      "required": true
    },
    {
      "description": "maps stated behavior to verifier coverage and strict assertions",
      "hash_required": true,
      "key": "test_alignment_review",
      "label": "Test alignment review",
      "required": true
    },
    {
      "description": "root or milestone verifier runner and test files are included for the task layout",
      "hash_required": true,
      "key": "tests_present",
      "label": "Verifier files included",
      "required": true
    }
  ],
  "required_packet_fields": [
    "summary",
    "package_hash",
    "artifact_hash_manifest",
    "worker_attestation"
  ],
  "storage_reference_rules": {
    "allowed_storage_schemes": [
      "local",
      "r2",
      "s3"
    ],
    "allowed_uri_prefixes": [
      "local://",
      "r2://",
      "s3://"
    ],
    "credentials_allowed": false,
    "fragments_allowed": false,
    "path_traversal_allowed": false,
    "query_strings_allowed": false
  },
  "task_id": "<redacted-id>"
}
```

### 20_precheck_blocked

`POST /api/v1/tasks/{task_id}/submission-precheck` -> HTTP `200`

Request body:

```json
{
  "submission": {
    "artifact_hash_manifest": [
      {
        "artifact": "environment/Dockerfile",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      },
      {
        "artifact": "rubric.md",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      },
      {
        "artifact": "task.toml",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      }
    ],
    "evidence_items": [
      {
        "hash": "sha256:<redacted>",
        "label": "Dependency pinning review",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "dependency_pinning_review"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/dependency_pinning_review.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Environment hygiene review",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "environment_hygiene_review"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/environment_hygiene_review.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Task instructions included",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "instructions_present"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/instructions_present.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Reward footer review",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "reward_footer_review"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/reward_footer_review.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Reference solution included",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "solution_present"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/solution_present.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Submission explanations",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "submission_explanations"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/submission_explanations.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Test alignment review",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "test_alignment_review"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/test_alignment_review.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Verifier files included",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "tests_present"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/tests_present.txt"
      }
    ],
    "package_hash": "sha256:<redacted>",
    "package_uri": "local://terminal-benchmark/<redacted-fixture-id>/submission.zip",
    "summary": "Blocked-path packet built from live requirements, missing environment/.dockerignore.",
    "worker_attestation": "<redacted-large-string sha256:<redacted> bytes:<redacted> prefix:'I attest this submission is original_work, produced under human_accountability_f'>"
  }
}
```

Response body:

```json
{
  "authoritative": false,
  "eligible_to_submit": false,
  "results": [
    {
      "checker_name": "check_submission_packet",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission packet satisfies locked project packet policy.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_forbidden_files",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission does not include default forbidden paths.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_confidentiality_attestation",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes the required confidentiality attestation.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_required_files",
      "severity": "high",
      "status": "failed",
      "worker_evidence_refs": [],
      "worker_message": "Submission is missing required artifact files.",
      "worker_suggested_fix": "Add every file required by the task to the artifact hash manifest.",
      "would_block_if_submitted": true
    },
    {
      "checker_name": "check_evidence_present",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes required evidence references.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_evidence_integrity",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Artifact manifest and evidence references are structurally valid.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_low_quality_generated_artifacts",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission does not contain obvious generated-output placeholder signals.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    }
  ],
  "status": "failed",
  "task_id": "<redacted-id>"
}
```

### 21_submission_blocked_create

`POST /api/v1/tasks/{task_id}/submissions` -> HTTP `422`

Request body:

```json
{
  "artifact_hash_manifest": [
    {
      "artifact": "environment/Dockerfile",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    }
  ],
  "evidence_items": [
    {
      "hash": "sha256:<redacted>",
      "label": "Dependency pinning review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "dependency_pinning_review"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/dependency_pinning_review.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Environment hygiene review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "environment_hygiene_review"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/environment_hygiene_review.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Task instructions included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "instructions_present"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/instructions_present.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Reward footer review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "reward_footer_review"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/reward_footer_review.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Reference solution included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "solution_present"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/solution_present.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Submission explanations",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "submission_explanations"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/submission_explanations.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Test alignment review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "test_alignment_review"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/test_alignment_review.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Verifier files included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "tests_present"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/tests_present.txt"
    }
  ],
  "package_hash": "sha256:<redacted>",
  "package_uri": "local://terminal-benchmark/<redacted-fixture-id>/submission.zip",
  "summary": "Blocked-path packet built from live requirements, missing environment/.dockerignore.",
  "worker_attestation": "<redacted-large-string sha256:<redacted> bytes:<redacted> prefix:'I attest this submission is original_work, produced under human_accountability_f'>"
}
```

Response body:

```json
{
  "code": "pre_submission_checker_failed",
  "details": {
    "authoritative": false,
    "eligible_to_submit": false,
    "results": [
      {
        "checker_name": "check_submission_packet",
        "severity": "info",
        "status": "passed",
        "worker_evidence_refs": [],
        "worker_message": "Submission packet satisfies locked project packet policy.",
        "worker_suggested_fix": null,
        "would_block_if_submitted": false
      },
      {
        "checker_name": "check_forbidden_files",
        "severity": "info",
        "status": "passed",
        "worker_evidence_refs": [],
        "worker_message": "Submission does not include default forbidden paths.",
        "worker_suggested_fix": null,
        "would_block_if_submitted": false
      },
      {
        "checker_name": "check_confidentiality_attestation",
        "severity": "info",
        "status": "passed",
        "worker_evidence_refs": [],
        "worker_message": "Submission includes the required confidentiality attestation.",
        "worker_suggested_fix": null,
        "would_block_if_submitted": false
      },
      {
        "checker_name": "check_required_files",
        "severity": "high",
        "status": "failed",
        "worker_evidence_refs": [],
        "worker_message": "Submission is missing required artifact files.",
        "worker_suggested_fix": "Add every file required by the task to the artifact hash manifest.",
        "would_block_if_submitted": true
      },
      {
        "checker_name": "check_evidence_present",
        "severity": "info",
        "status": "passed",
        "worker_evidence_refs": [],
        "worker_message": "Submission includes required evidence references.",
        "worker_suggested_fix": null,
        "would_block_if_submitted": false
      },
      {
        "checker_name": "check_evidence_integrity",
        "severity": "info",
        "status": "passed",
        "worker_evidence_refs": [],
        "worker_message": "Artifact manifest and evidence references are structurally valid.",
        "worker_suggested_fix": null,
        "would_block_if_submitted": false
      },
      {
        "checker_name": "check_low_quality_generated_artifacts",
        "severity": "info",
        "status": "passed",
        "worker_evidence_refs": [],
        "worker_message": "Submission does not contain obvious generated-output placeholder signals.",
        "worker_suggested_fix": null,
        "would_block_if_submitted": false
      }
    ],
    "status": "failed",
    "task_id": "<redacted-id>"
  }
}
```

### 22_submissions_after_blocked

`GET /api/v1/tasks/{task_id}/submissions` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
[]
```

### 23_audit_after_blocked

`GET /api/v1/tasks/{task_id}/audit-events` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
[
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:03.452947Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": null,
      "locked_effective_project_submission_artifact_policy_id": null,
      "locked_guide_source_snapshot_hash": null,
      "locked_guide_source_snapshot_id": null,
      "locked_guide_version": null,
      "locked_payment_policy_version": null,
      "locked_post_submit_checker_policy_hash": null,
      "locked_post_submit_checker_policy_id": null,
      "locked_post_submit_checker_policy_version": null,
      "locked_pre_submit_checker_bundle_hash": null,
      "locked_pre_submit_checker_policy_id": null,
      "locked_review_policy_version": null,
      "locked_revision_policy_version": null,
      "source_type": "manual"
    },
    "event_type": "task_created",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-<redacted-run-id>",
    "from_status": null,
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "draft"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:03.630101Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-<redacted-run-id>",
    "from_status": "draft",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API screening; lock active guide and policy context.",
    "to_status": "screening"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.041939Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-<redacted-run-id>",
    "from_status": "screening",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API ready for worker claim.",
    "to_status": "ready"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.503583Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "<redacted-id>",
      "assignment_id": "<redacted-id>",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "worker_id": "<redacted-id>"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-<redacted-run-id>",
    "from_status": "ready",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API worker claim.",
    "to_status": "claimed"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.727342Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "<redacted-id>",
      "assignment_id": "<redacted-id>",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "operator_override": false,
      "worker_id": "<redacted-id>"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-<redacted-run-id>",
    "from_status": "claimed",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API worker started work.",
    "to_status": "in_progress"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:17.452515Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "<redacted-id>",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "pre_submit_check": {
        "authoritative": false,
        "eligible_to_submit": false,
        "results": [
          {
            "checker_name": "check_submission_packet",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission packet satisfies locked project packet policy.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_forbidden_files",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission does not include default forbidden paths.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_confidentiality_attestation",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission includes the required confidentiality attestation.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_required_files",
            "severity": "high",
            "status": "failed",
            "worker_evidence_refs": [],
            "worker_message": "Submission is missing required artifact files.",
            "worker_suggested_fix": "Add every file required by the task to the artifact hash manifest.",
            "would_block_if_submitted": true
          },
          {
            "checker_name": "check_evidence_present",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission includes required evidence references.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_evidence_integrity",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Artifact manifest and evidence references are structurally valid.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_low_quality_generated_artifacts",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission does not contain obvious generated-output placeholder signals.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          }
        ],
        "status": "failed",
        "task_id": "<redacted-id>"
      }
    },
    "event_type": "pre_submission_check_failed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-<redacted-run-id>",
    "from_status": "in_progress",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "in_progress"
  }
]
```

### 24_precheck_success

`POST /api/v1/tasks/{task_id}/submission-precheck` -> HTTP `200`

Request body:

```json
{
  "submission": {
    "artifact_hash_manifest": [
      {
        "artifact": "environment/Dockerfile",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      },
      {
        "artifact": "environment/.dockerignore",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      },
      {
        "artifact": "rubric.md",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      },
      {
        "artifact": "task.toml",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      }
    ],
    "evidence_items": [
      {
        "hash": "sha256:<redacted>",
        "label": "Dependency pinning review",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "dependency_pinning_review"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/dependency_pinning_review.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Environment hygiene review",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "environment_hygiene_review"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/environment_hygiene_review.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Task instructions included",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "instructions_present"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/instructions_present.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Reward footer review",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "reward_footer_review"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/reward_footer_review.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Reference solution included",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "solution_present"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/solution_present.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Submission explanations",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "submission_explanations"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/submission_explanations.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Test alignment review",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "test_alignment_review"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/test_alignment_review.txt"
      },
      {
        "hash": "sha256:<redacted>",
        "label": "Verifier files included",
        "metadata": {
          "fixture_id": "<redacted-fixture-id>",
          "required_evidence_key": "tests_present"
        },
        "size_bytes": "<redacted>",
        "type": "log",
        "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/tests_present.txt"
      }
    ],
    "package_hash": "sha256:<redacted>",
    "package_uri": "local://terminal-benchmark/<redacted-fixture-id>/submission.zip",
    "summary": "Terminal Benchmark <redacted-fixture-id> packet built from live submission requirements.",
    "worker_attestation": "<redacted-large-string sha256:<redacted> bytes:<redacted> prefix:'I attest this submission is original_work, produced under human_accountability_f'>"
  }
}
```

Response body:

```json
{
  "authoritative": false,
  "eligible_to_submit": true,
  "results": [
    {
      "checker_name": "check_submission_packet",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission packet satisfies locked project packet policy.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_forbidden_files",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission does not include default forbidden paths.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_confidentiality_attestation",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes the required confidentiality attestation.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_required_files",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes required artifact files.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_evidence_present",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes required evidence references.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_evidence_integrity",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Artifact manifest and evidence references are structurally valid.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    },
    {
      "checker_name": "check_low_quality_generated_artifacts",
      "severity": "info",
      "status": "passed",
      "worker_evidence_refs": [],
      "worker_message": "Submission does not contain obvious generated-output placeholder signals.",
      "worker_suggested_fix": null,
      "would_block_if_submitted": false
    }
  ],
  "status": "passed",
  "task_id": "<redacted-id>"
}
```

### 25_submissions_after_success_precheck

`GET /api/v1/tasks/{task_id}/submissions` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
[]
```

### 26_submission_success_create

`POST /api/v1/tasks/{task_id}/submissions` -> HTTP `201`

Request body:

```json
{
  "artifact_hash_manifest": [
    {
      "artifact": "environment/Dockerfile",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "environment/.dockerignore",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    }
  ],
  "evidence_items": [
    {
      "hash": "sha256:<redacted>",
      "label": "Dependency pinning review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "dependency_pinning_review"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/dependency_pinning_review.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Environment hygiene review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "environment_hygiene_review"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/environment_hygiene_review.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Task instructions included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "instructions_present"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/instructions_present.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Reward footer review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "reward_footer_review"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/reward_footer_review.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Reference solution included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "solution_present"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/solution_present.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Submission explanations",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "submission_explanations"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/submission_explanations.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Test alignment review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "test_alignment_review"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/test_alignment_review.txt"
    },
    {
      "hash": "sha256:<redacted>",
      "label": "Verifier files included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "tests_present"
      },
      "size_bytes": "<redacted>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/tests_present.txt"
    }
  ],
  "package_hash": "sha256:<redacted>",
  "package_uri": "local://terminal-benchmark/<redacted-fixture-id>/submission.zip",
  "summary": "Terminal Benchmark <redacted-fixture-id> packet built from live submission requirements.",
  "worker_attestation": "<redacted-large-string sha256:<redacted> bytes:<redacted> prefix:'I attest this submission is original_work, produced under human_accountability_f'>"
}
```

Response body:

```json
{
  "evidence_items": [
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "<redacted-id>",
      "label": "Dependency pinning review",
      "metadata": {},
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "<redacted-id>",
      "label": "Environment hygiene review",
      "metadata": {},
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "<redacted-id>",
      "label": "Task instructions included",
      "metadata": {},
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "<redacted-id>",
      "label": "Reward footer review",
      "metadata": {},
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "<redacted-id>",
      "label": "Reference solution included",
      "metadata": {},
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "<redacted-id>",
      "label": "Submission explanations",
      "metadata": {},
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "<redacted-id>",
      "label": "Test alignment review",
      "metadata": {},
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "<redacted-id>",
      "label": "Verifier files included",
      "metadata": {},
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log"
    }
  ],
  "id": "<redacted-id>",
  "status": "submitted",
  "submitted_at": "2026-07-08T23:45:18.127472Z",
  "summary": "Terminal Benchmark <redacted-fixture-id> packet built from live submission requirements.",
  "task_id": "<redacted-id>",
  "version": 1,
  "worker_id": "<redacted-id>"
}
```

### 27_submissions_after_success_create

`GET /api/v1/tasks/{task_id}/submissions` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
[
  {
    "evidence_items": [
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "<redacted-id>",
        "label": "Dependency pinning review",
        "metadata": {},
        "size_bytes": "<redacted>",
        "submission_id": "<redacted-id>",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "<redacted-id>",
        "label": "Environment hygiene review",
        "metadata": {},
        "size_bytes": "<redacted>",
        "submission_id": "<redacted-id>",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "<redacted-id>",
        "label": "Task instructions included",
        "metadata": {},
        "size_bytes": "<redacted>",
        "submission_id": "<redacted-id>",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "<redacted-id>",
        "label": "Reward footer review",
        "metadata": {},
        "size_bytes": "<redacted>",
        "submission_id": "<redacted-id>",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "<redacted-id>",
        "label": "Reference solution included",
        "metadata": {},
        "size_bytes": "<redacted>",
        "submission_id": "<redacted-id>",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "<redacted-id>",
        "label": "Submission explanations",
        "metadata": {},
        "size_bytes": "<redacted>",
        "submission_id": "<redacted-id>",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "<redacted-id>",
        "label": "Test alignment review",
        "metadata": {},
        "size_bytes": "<redacted>",
        "submission_id": "<redacted-id>",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "<redacted-id>",
        "label": "Verifier files included",
        "metadata": {},
        "size_bytes": "<redacted>",
        "submission_id": "<redacted-id>",
        "type": "log"
      }
    ],
    "id": "<redacted-id>",
    "status": "submitted",
    "submitted_at": "2026-07-08T23:45:18.127472Z",
    "summary": "Terminal Benchmark <redacted-fixture-id> packet built from live submission requirements.",
    "task_id": "<redacted-id>",
    "version": 1,
    "worker_id": "<redacted-id>"
  }
]
```

### 28_submission_finalize_worker_forbidden

`POST /api/v1/submissions/{submission_id}/finalize` -> HTTP `403`

Request body:

```json
null
```

Response body:

```json
{
  "detail": "actor lacks required role"
}
```

### 29_submission_finalize_manager

`POST /api/v1/submissions/{submission_id}/finalize` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "artifact_hash_manifest": [
    {
      "artifact": "environment/Dockerfile",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "environment/.dockerignore",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    }
  ],
  "evidence_items": [
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Dependency pinning review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "dependency_pinning_review"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/dependency_pinning_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Environment hygiene review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "environment_hygiene_review"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/environment_hygiene_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Task instructions included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "instructions_present"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/instructions_present.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Reward footer review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "reward_footer_review"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/reward_footer_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Reference solution included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "solution_present"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/solution_present.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Submission explanations",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "submission_explanations"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/submission_explanations.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Test alignment review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "test_alignment_review"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/test_alignment_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Verifier files included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "tests_present"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/tests_present.txt"
    }
  ],
  "finalized_at": "2026-07-08T23:45:18.750577Z",
  "id": "<redacted-id>",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
  "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
  "locked_guide_source_snapshot_hash": "sha256:<redacted>",
  "locked_guide_source_snapshot_id": "<redacted-id>",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
  "locked_pre_submit_checker_policy_id": "<redacted-id>",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "package_hash": "sha256:<redacted>",
  "package_uri": "local://terminal-benchmark/<redacted-fixture-id>/submission.zip",
  "status": "submitted",
  "submitted_at": "2026-07-08T23:45:18.127472Z",
  "summary": "Terminal Benchmark <redacted-fixture-id> packet built from live submission requirements.",
  "task_id": "<redacted-id>",
  "version": 1,
  "worker_attestation": "<redacted-large-string sha256:<redacted> bytes:<redacted> prefix:'I attest this submission is original_work, produced under human_accountability_f'>",
  "worker_id": "<redacted-id>"
}
```

### 30_submission_get_after_finalize

`GET /api/v1/submissions/{submission_id}` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "artifact_hash_manifest": [
    {
      "artifact": "environment/Dockerfile",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "environment/.dockerignore",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    }
  ],
  "evidence_items": [
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Dependency pinning review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "dependency_pinning_review"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/dependency_pinning_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Environment hygiene review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "environment_hygiene_review"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/environment_hygiene_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Task instructions included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "instructions_present"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/instructions_present.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Reward footer review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "reward_footer_review"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/reward_footer_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Reference solution included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "solution_present"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/solution_present.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Submission explanations",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "submission_explanations"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/submission_explanations.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Test alignment review",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "test_alignment_review"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/test_alignment_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:<redacted>",
      "id": "<redacted-id>",
      "label": "Verifier files included",
      "metadata": {
        "fixture_id": "<redacted-fixture-id>",
        "required_evidence_key": "tests_present"
      },
      "size_bytes": "<redacted>",
      "submission_id": "<redacted-id>",
      "type": "log",
      "uri": "local://terminal-benchmark/<redacted-fixture-id>/evidence/tests_present.txt"
    }
  ],
  "finalized_at": "2026-07-08T23:45:18.750577Z",
  "id": "<redacted-id>",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
  "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
  "locked_guide_source_snapshot_hash": "sha256:<redacted>",
  "locked_guide_source_snapshot_id": "<redacted-id>",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
  "locked_pre_submit_checker_policy_id": "<redacted-id>",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "package_hash": "sha256:<redacted>",
  "package_uri": "local://terminal-benchmark/<redacted-fixture-id>/submission.zip",
  "status": "submitted",
  "submitted_at": "2026-07-08T23:45:18.127472Z",
  "summary": "Terminal Benchmark <redacted-fixture-id> packet built from live submission requirements.",
  "task_id": "<redacted-id>",
  "version": 1,
  "worker_attestation": "<redacted-large-string sha256:<redacted> bytes:<redacted> prefix:'I attest this submission is original_work, produced under human_accountability_f'>",
  "worker_id": "<redacted-id>"
}
```

### 31_checker_runs_after_finalize

`GET /api/v1/submissions/{submission_id}/checker-runs` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
[
  {
    "artifact_hash_manifest": [
      {
        "artifact": "environment/Dockerfile",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      },
      {
        "artifact": "environment/.dockerignore",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      },
      {
        "artifact": "rubric.md",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      },
      {
        "artifact": "task.toml",
        "hash": "sha256:<redacted>",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": "<redacted>"
      }
    ],
    "artifact_manifest_hash": "sha256:<redacted>",
    "attempt_number": 1,
    "audit_event_id": "<redacted-id>",
    "blocking_count": 0,
    "completed_at": "2026-07-08T23:45:18.864215Z",
    "created_at": "2026-07-08T23:45:18.592353Z",
    "failed_count": 0,
    "id": "<redacted-id>",
    "is_current_for_submission": true,
    "locked_guide_version": "v1",
    "locked_payment_policy_version": "v1",
    "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
    "locked_post_submit_checker_policy_id": "<redacted-id>",
    "locked_post_submit_checker_policy_version": "v1",
    "locked_review_policy_version": "v1",
    "locked_revision_policy_version": "v1",
    "outcome_source": "none",
    "package_hash": "sha256:<redacted>",
    "passed_count": 8,
    "queued_at": "2026-07-08T23:45:18.592353Z",
    "results": [
      {
        "blocks_review": false,
        "checker_name": "check_submission_packet",
        "checker_run_id": "<redacted-id>",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "<redacted-id>",
        "message": "Submission packet contains required fields.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "<redacted-id>",
        "task_id": "<redacted-id>",
        "worker_evidence_refs": [],
        "worker_message": "Submission packet contains required fields.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_policy_context_present",
        "checker_run_id": "<redacted-id>",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "<redacted-id>",
        "message": "Submission has locked guide and policy context.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "<redacted-id>",
        "task_id": "<redacted-id>",
        "worker_evidence_refs": [],
        "worker_message": "Submission has locked guide and policy context.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_evidence_present",
        "checker_run_id": "<redacted-id>",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "<redacted-id>",
        "message": "Submission includes required evidence references.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "<redacted-id>",
        "task_id": "<redacted-id>",
        "worker_evidence_refs": [],
        "worker_message": "Submission includes required evidence references.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_evidence_integrity",
        "checker_run_id": "<redacted-id>",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "<redacted-id>",
        "message": "Artifact manifest and evidence references are structurally valid.",
        "metadata": {
          "artifact_count": 4,
          "artifact_manifest_hash": "sha256:<redacted>"
        },
        "severity": "info",
        "status": "passed",
        "submission_id": "<redacted-id>",
        "task_id": "<redacted-id>",
        "worker_evidence_refs": [],
        "worker_message": "Artifact manifest and evidence references are structurally valid.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_required_files",
        "checker_run_id": "<redacted-id>",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "<redacted-id>",
        "message": "Submission includes required artifact files.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "<redacted-id>",
        "task_id": "<redacted-id>",
        "worker_evidence_refs": [],
        "worker_message": "Submission includes required artifact files.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_forbidden_files",
        "checker_run_id": "<redacted-id>",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "<redacted-id>",
        "message": "Submission does not include default forbidden paths.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "<redacted-id>",
        "task_id": "<redacted-id>",
        "worker_evidence_refs": [],
        "worker_message": "Submission does not include default forbidden paths.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_confidentiality_attestation",
        "checker_run_id": "<redacted-id>",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "<redacted-id>",
        "message": "Submission includes the required confidentiality attestation.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "<redacted-id>",
        "task_id": "<redacted-id>",
        "worker_evidence_refs": [],
        "worker_message": "Submission includes the required confidentiality attestation.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_low_quality_generated_artifacts",
        "checker_run_id": "<redacted-id>",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "<redacted-id>",
        "message": "Submission does not contain obvious generated-output placeholder signals.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "<redacted-id>",
        "task_id": "<redacted-id>",
        "worker_evidence_refs": [],
        "worker_message": "Submission does not contain obvious generated-output placeholder signals.",
        "worker_visible": true
      }
    ],
    "routing_recommendation": "allow_review",
    "started_at": "2026-07-08T23:45:18.864215Z",
    "status": "completed",
    "submission_id": "<redacted-id>",
    "submission_version": 1,
    "task_id": "<redacted-id>",
    "trigger_auth_source": "workstream_system",
    "trigger_reason": "submission finalized pre-review gate",
    "trigger_source": "submission_finalized",
    "triggered_by": "workstream-system:pre-review-gate",
    "triggered_by_issuer": "workstream",
    "triggered_by_subject": "workstream-system:pre-review-gate",
    "warning_count": 0
  }
]
```

### 32_checker_run_get

`GET /api/v1/checker-runs/{checker_run_id}` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "artifact_hash_manifest": [
    {
      "artifact": "environment/Dockerfile",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "environment/.dockerignore",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:<redacted>",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": "<redacted>"
    }
  ],
  "artifact_manifest_hash": "sha256:<redacted>",
  "attempt_number": 1,
  "audit_event_id": "<redacted-id>",
  "blocking_count": 0,
  "completed_at": "2026-07-08T23:45:18.864215Z",
  "created_at": "2026-07-08T23:45:18.592353Z",
  "failed_count": 0,
  "id": "<redacted-id>",
  "is_current_for_submission": true,
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
  "locked_post_submit_checker_policy_id": "<redacted-id>",
  "locked_post_submit_checker_policy_version": "v1",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "outcome_source": "none",
  "package_hash": "sha256:<redacted>",
  "passed_count": 8,
  "queued_at": "2026-07-08T23:45:18.592353Z",
  "results": [
    {
      "blocks_review": false,
      "checker_name": "check_submission_packet",
      "checker_run_id": "<redacted-id>",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "<redacted-id>",
      "message": "Submission packet contains required fields.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "<redacted-id>",
      "task_id": "<redacted-id>",
      "worker_evidence_refs": [],
      "worker_message": "Submission packet contains required fields.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_policy_context_present",
      "checker_run_id": "<redacted-id>",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "<redacted-id>",
      "message": "Submission has locked guide and policy context.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "<redacted-id>",
      "task_id": "<redacted-id>",
      "worker_evidence_refs": [],
      "worker_message": "Submission has locked guide and policy context.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_evidence_present",
      "checker_run_id": "<redacted-id>",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "<redacted-id>",
      "message": "Submission includes required evidence references.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "<redacted-id>",
      "task_id": "<redacted-id>",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes required evidence references.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_evidence_integrity",
      "checker_run_id": "<redacted-id>",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "<redacted-id>",
      "message": "Artifact manifest and evidence references are structurally valid.",
      "metadata": {
        "artifact_count": 4,
        "artifact_manifest_hash": "sha256:<redacted>"
      },
      "severity": "info",
      "status": "passed",
      "submission_id": "<redacted-id>",
      "task_id": "<redacted-id>",
      "worker_evidence_refs": [],
      "worker_message": "Artifact manifest and evidence references are structurally valid.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_required_files",
      "checker_run_id": "<redacted-id>",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "<redacted-id>",
      "message": "Submission includes required artifact files.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "<redacted-id>",
      "task_id": "<redacted-id>",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes required artifact files.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_forbidden_files",
      "checker_run_id": "<redacted-id>",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "<redacted-id>",
      "message": "Submission does not include default forbidden paths.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "<redacted-id>",
      "task_id": "<redacted-id>",
      "worker_evidence_refs": [],
      "worker_message": "Submission does not include default forbidden paths.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_confidentiality_attestation",
      "checker_run_id": "<redacted-id>",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "<redacted-id>",
      "message": "Submission includes the required confidentiality attestation.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "<redacted-id>",
      "task_id": "<redacted-id>",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes the required confidentiality attestation.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_low_quality_generated_artifacts",
      "checker_run_id": "<redacted-id>",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "<redacted-id>",
      "message": "Submission does not contain obvious generated-output placeholder signals.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "<redacted-id>",
      "task_id": "<redacted-id>",
      "worker_evidence_refs": [],
      "worker_message": "Submission does not contain obvious generated-output placeholder signals.",
      "worker_visible": true
    }
  ],
  "routing_recommendation": "allow_review",
  "started_at": "2026-07-08T23:45:18.864215Z",
  "status": "completed",
  "submission_id": "<redacted-id>",
  "submission_version": 1,
  "task_id": "<redacted-id>",
  "trigger_auth_source": "workstream_system",
  "trigger_reason": "submission finalized pre-review gate",
  "trigger_source": "submission_finalized",
  "triggered_by": "workstream-system:pre-review-gate",
  "triggered_by_issuer": "workstream",
  "triggered_by_subject": "workstream-system:pre-review-gate",
  "warning_count": 0
}
```

### 33_audit_after_finalize

`GET /api/v1/tasks/{task_id}/audit-events` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
[
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:03.452947Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": null,
      "locked_effective_project_submission_artifact_policy_id": null,
      "locked_guide_source_snapshot_hash": null,
      "locked_guide_source_snapshot_id": null,
      "locked_guide_version": null,
      "locked_payment_policy_version": null,
      "locked_post_submit_checker_policy_hash": null,
      "locked_post_submit_checker_policy_id": null,
      "locked_post_submit_checker_policy_version": null,
      "locked_pre_submit_checker_bundle_hash": null,
      "locked_pre_submit_checker_policy_id": null,
      "locked_review_policy_version": null,
      "locked_revision_policy_version": null,
      "source_type": "manual"
    },
    "event_type": "task_created",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-<redacted-run-id>",
    "from_status": null,
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "draft"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:03.630101Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-<redacted-run-id>",
    "from_status": "draft",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API screening; lock active guide and policy context.",
    "to_status": "screening"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.041939Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-<redacted-run-id>",
    "from_status": "screening",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API ready for worker claim.",
    "to_status": "ready"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.503583Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "<redacted-id>",
      "assignment_id": "<redacted-id>",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "worker_id": "<redacted-id>"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-<redacted-run-id>",
    "from_status": "ready",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API worker claim.",
    "to_status": "claimed"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.727342Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "<redacted-id>",
      "assignment_id": "<redacted-id>",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "operator_override": false,
      "worker_id": "<redacted-id>"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-<redacted-run-id>",
    "from_status": "claimed",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API worker started work.",
    "to_status": "in_progress"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:17.452515Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "<redacted-id>",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "pre_submit_check": {
        "authoritative": false,
        "eligible_to_submit": false,
        "results": [
          {
            "checker_name": "check_submission_packet",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission packet satisfies locked project packet policy.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_forbidden_files",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission does not include default forbidden paths.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_confidentiality_attestation",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission includes the required confidentiality attestation.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_required_files",
            "severity": "high",
            "status": "failed",
            "worker_evidence_refs": [],
            "worker_message": "Submission is missing required artifact files.",
            "worker_suggested_fix": "Add every file required by the task to the artifact hash manifest.",
            "would_block_if_submitted": true
          },
          {
            "checker_name": "check_evidence_present",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission includes required evidence references.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_evidence_integrity",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Artifact manifest and evidence references are structurally valid.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          },
          {
            "checker_name": "check_low_quality_generated_artifacts",
            "severity": "info",
            "status": "passed",
            "worker_evidence_refs": [],
            "worker_message": "Submission does not contain obvious generated-output placeholder signals.",
            "worker_suggested_fix": null,
            "would_block_if_submitted": false
          }
        ],
        "status": "failed",
        "task_id": "<redacted-id>"
      }
    },
    "event_type": "pre_submission_check_failed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-<redacted-run-id>",
    "from_status": "in_progress",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "in_progress"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:18.127472Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "artifact_hash_manifest": [
        {
          "artifact": "environment/Dockerfile",
          "hash": "sha256:<redacted>",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": "<redacted>"
        },
        {
          "artifact": "environment/.dockerignore",
          "hash": "sha256:<redacted>",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": "<redacted>"
        },
        {
          "artifact": "rubric.md",
          "hash": "sha256:<redacted>",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": "<redacted>"
        },
        {
          "artifact": "task.toml",
          "hash": "sha256:<redacted>",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": "<redacted>"
        }
      ],
      "assigned_to": "<redacted-id>",
      "finalized_at": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "package_hash": "sha256:<redacted>",
      "submission_id": "<redacted-id>",
      "submission_version": 1,
      "supersedes_submission_id": null,
      "worker_id": "<redacted-id>"
    },
    "event_type": "submission_created",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-<redacted-run-id>",
    "from_status": "in_progress",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "submitted"
  },
  {
    "actor_id": "<redacted-id>",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:18.592353Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "artifact_hash_manifest": [
        {
          "artifact": "environment/Dockerfile",
          "hash": "sha256:<redacted>",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": "<redacted>"
        },
        {
          "artifact": "environment/.dockerignore",
          "hash": "sha256:<redacted>",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": "<redacted>"
        },
        {
          "artifact": "rubric.md",
          "hash": "sha256:<redacted>",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": "<redacted>"
        },
        {
          "artifact": "task.toml",
          "hash": "sha256:<redacted>",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": "<redacted>"
        }
      ],
      "assigned_to": "<redacted-id>",
      "finalized_at": "2026-07-08T23:45:18.750577+00:00",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
      "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
      "locked_guide_source_snapshot_hash": "sha256:<redacted>",
      "locked_guide_source_snapshot_id": "<redacted-id>",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
      "locked_pre_submit_checker_policy_id": "<redacted-id>",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "package_hash": "sha256:<redacted>",
      "submission_id": "<redacted-id>",
      "submission_version": 1,
      "supersedes_submission_id": null,
      "worker_id": "<redacted-id>"
    },
    "event_type": "submission_finalized",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-<redacted-run-id>",
    "from_status": "submitted",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "submitted"
  },
  {
    "actor_id": "workstream-system:pre-review-gate",
    "actor_roles": [
      "workstream_system"
    ],
    "auth_source": "workstream_system",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:18.592353Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "requester_actor_id": "<redacted-id>",
      "requester_auth_source": "flow",
      "requester_external_issuer": "https://auth.flow.local/e2e",
      "requester_external_subject": "terminal-benchmark-manager-<redacted-run-id>",
      "submission_id": "<redacted-id>",
      "submission_version": 1,
      "task_id": "<redacted-id>",
      "trigger_source": "submission_finalized"
    },
    "event_type": "pre_review_gate_started",
    "external_issuer": "workstream",
    "external_subject": "workstream-system:pre-review-gate",
    "from_status": "submitted",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "submission finalized pre-review gate",
    "to_status": "evaluation_pending"
  },
  {
    "actor_id": "workstream-system:pre-review-gate",
    "actor_roles": [
      "workstream_system"
    ],
    "auth_source": "workstream_system",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:18.592353Z",
    "entity_id": "<redacted-id>",
    "entity_type": "task",
    "event_payload": {
      "blocking_count": 0,
      "checker_run_id": "<redacted-id>",
      "failed_count": 0,
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:<redacted>",
      "locked_post_submit_checker_policy_id": "<redacted-id>",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "outcome_source": "none",
      "requester_actor_id": "<redacted-id>",
      "requester_auth_source": "flow",
      "requester_external_issuer": "https://auth.flow.local/e2e",
      "requester_external_subject": "terminal-benchmark-manager-<redacted-run-id>",
      "review_decision_id": null,
      "routing_recommendation": "allow_review",
      "submission_id": "<redacted-id>",
      "submission_version": 1,
      "task_id": "<redacted-id>",
      "trigger_source": "submission_finalized",
      "warning_count": 0
    },
    "event_type": "pre_review_gate_passed",
    "external_issuer": "workstream",
    "external_subject": "workstream-system:pre-review-gate",
    "from_status": "evaluation_pending",
    "id": "<redacted-id>",
    "is_dev_auth": false,
    "reason": "submission finalized pre-review gate",
    "to_status": "review_pending"
  }
]
```

### 34_task_get_after_finalize

`GET /api/v1/tasks/{task_id}` -> HTTP `200`

Request body:

```json
null
```

Response body:

```json
{
  "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
  "assigned_to": "<redacted-id>",
  "base_amount": "25.00",
  "created_at": "2026-07-08T23:44:03.452947Z",
  "created_by": "<redacted-id>",
  "currency": "USD",
  "description": "Real Terminal Benchmark reference fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "<redacted-fixture-id>",
  "id": "<redacted-id>",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:<redacted>",
  "locked_effective_project_submission_artifact_policy_id": "<redacted-id>",
  "locked_guide_source_snapshot_hash": "sha256:<redacted>",
  "locked_guide_source_snapshot_id": "<redacted-id>",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:<redacted>",
  "locked_pre_submit_checker_policy_id": "<redacted-id>",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "payout_type": "fixed",
  "project_id": "<redacted-id>",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "<redacted-domain-tag>",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:<redacted>",
  "source_ref": "terminal-benchmark/<redacted-fixture-id>/live-api/<redacted-run-id>",
  "source_type": "manual",
  "status": "review_pending",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark <redacted-fixture-id> live-api",
  "updated_at": "2026-07-08T23:45:18.592353Z"
}
```


## Notes

- The first construction pass was discarded because the imported reviewer
  material contained raw local path text. The final run sanitized source text
  before guide creation and passed a request/response scan for `/home/`.
- A later construction pass was discarded because the worker packet was built
  before reading the live `submission-requirements` response. The final run
  built the packet from the live requirements before pre-submit calls.
- No Workstream default checker was weakened.
- No task-specific checker generation was introduced.
- No product review decision token leaked into pre-submit output.
- No database inspection was used as lifecycle proof.
