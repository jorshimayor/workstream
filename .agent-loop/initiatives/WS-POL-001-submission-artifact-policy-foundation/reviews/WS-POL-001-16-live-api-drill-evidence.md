# WS-POL-001-16 Live API Drill Evidence

## Verdict

PASS.

The final clean Terminal Benchmark drill ran through public/operator HTTP APIs
without database inspection as lifecycle proof.

Final state:

```text
project_id: 36331e8e-c849-484d-9e9e-c8ebc2f70130
guide_id: fbe0b2ab-2793-4619-a414-ed083d9cc117
source_snapshot_id: 2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b
source_snapshot_hash: sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb
sufficiency_status: passed
submission_artifact_policy_hash: sha256:aa0cf8add77b6d193e5f3ffa1bf22f0fd21f27e484e4aa027e693d77b3624136
effective_policy_hash: sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850
pre_submit_checker_bundle_hash: sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63
task_id: d8cfda33-6c7e-461a-bdcd-036a6cefeda3
submission_id: ba25f15a-e36a-4925-9891-09d394eae2ec
checker_run_id: d7885348-fd08-4820-b209-36a704765a2b
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
termius_reviewer/reviews/build-seccomp-profile-reducer-rust-json
```

Fixture id:

```text
terminal-benchmark-1c027e78be41
```

Before the final API run, source text was sanitized so raw local filesystem
paths were not sent to Workstream. The clean request/response capture was
scanned for `/home/` and passed.

Guide body:

```text
content_markdown_hash: sha256:586b0e702b8fe201185ffab41d9ec4b4b862fea134deb010c2cc93c3b7412c1c
content_markdown_bytes: 138427
```

Source snapshot manifest:

| Label | Durable ref | Hash | Bytes |
|---|---|---:|---:|
| `PROJECT_GUIDE.md` | `import:/fixtures/terminal-benchmark-1c027e78be41/PROJECT_GUIDE.md` | `sha256:a2b2d57cc56cddc4a8049e9df00da02577fcd729043aad065e2a47f84ca4372e` | 27143 |
| `REVIEWER_PROGRAM.md` | `import:/fixtures/terminal-benchmark-1c027e78be41/REVIEWER_PROGRAM.md` | `sha256:297415ca932fd7109c63c03232afd0d73a0ce0b1237cd460a6b0cbec81e8995d` | 45121 |
| `task.toml` | `import:/fixtures/terminal-benchmark-1c027e78be41/task.toml` | `sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811` | 1562 |
| `review_packet.md` | `import:/fixtures/terminal-benchmark-1c027e78be41/review_packet.md` | `sha256:42eb6fead00923488b1212d23ef756926849dd51087aa0490ca656e829e8b8ea` | 36295 |
| `static_guard.txt` | `import:/fixtures/terminal-benchmark-1c027e78be41/static_guard.txt` | `sha256:73840f643300f873de7bfff017cfe00ed01659208800fd1c572362fc8a300b62` | 612 |
| `docker_build.log` | `import:/fixtures/terminal-benchmark-1c027e78be41/docker_build.log` | `sha256:793b9c193beb4f7b4bad4aacf66f5a74a6007e420c3232039d96cfa8cf6fbf42` | 31676 |
| `oracle_test.log` | `import:/fixtures/terminal-benchmark-1c027e78be41/oracle_test.log` | `sha256:33e5d68026c8e84b7558e2389293edc9d8b9f366a37e40b449397cd1b5b6fd97` | 3926 |
| `starter_m1_test.log` | `import:/fixtures/terminal-benchmark-1c027e78be41/starter_m1_test.log` | `sha256:fb06dbd479c6a782297fde0f83414ff3f9bc456ece2c7e7098362f783730bbc2` | 11284 |

## HTTP Transcript

Large guide content is represented by stable hashes and source manifest rows
above. The table below is an ordered index; full redacted request and response
bodies for every step are recorded in the Redacted HTTP Body Appendix.

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
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "guide_material": {
    "content_markdown": {
      "hash": "sha256:586b0e702b8fe201185ffab41d9ec4b4b862fea134deb010c2cc93c3b7412c1c",
      "bytes": 138427
    }
  },
  "source_items": [
    ["project_guide", "import:/fixtures/terminal-benchmark-1c027e78be41/PROJECT_GUIDE.md", "sha256:a2b2d57cc56cddc4a8049e9df00da02577fcd729043aad065e2a47f84ca4372e"],
    ["reviewer_program", "import:/fixtures/terminal-benchmark-1c027e78be41/REVIEWER_PROGRAM.md", "sha256:297415ca932fd7109c63c03232afd0d73a0ce0b1237cd460a6b0cbec81e8995d"],
    ["task_material", "import:/fixtures/terminal-benchmark-1c027e78be41/task.toml", "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811"],
    ["review_packet", "import:/fixtures/terminal-benchmark-1c027e78be41/review_packet.md", "sha256:42eb6fead00923488b1212d23ef756926849dd51087aa0490ca656e829e8b8ea"],
    ["static_guard", "import:/fixtures/terminal-benchmark-1c027e78be41/static_guard.txt", "sha256:73840f643300f873de7bfff017cfe00ed01659208800fd1c572362fc8a300b62"],
    ["build_log", "import:/fixtures/terminal-benchmark-1c027e78be41/docker_build.log", "sha256:793b9c193beb4f7b4bad4aacf66f5a74a6007e420c3232039d96cfa8cf6fbf42"],
    ["test_log", "import:/fixtures/terminal-benchmark-1c027e78be41/oracle_test.log", "sha256:33e5d68026c8e84b7558e2389293edc9d8b9f366a37e40b449397cd1b5b6fd97"],
    ["test_log", "import:/fixtures/terminal-benchmark-1c027e78be41/starter_m1_test.log", "sha256:fb06dbd479c6a782297fde0f83414ff3f9bc456ece2c7e7098362f783730bbc2"]
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
source_snapshot_hash: sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb
```

Submission-policy-derivation input:

```json
{
  "guide_source_material": "same GuideSourceMaterial envelope shown above",
  "sufficiency_report": {
    "status": "guide_sufficient",
    "findings": [],
    "summary_hash": "sha256:2cfc87c9362a379ea96b21e57d2bc054abd5a523b939fe7c85c38428c844ab21",
    "agent_name": "ProjectGuideSufficiencyAgent",
    "agent_version": "workstream-sufficiency-agent-v0.1"
  }
}
```

Submission-policy-derivation output:

```text
derivation_source: agent_derivation
policy_hash: sha256:aa0cf8add77b6d193e5f3ffa1bf22f0fd21f27e484e4aa027e693d77b3624136
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
compiled_bundle_hash: sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63
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
  "title": "Terminal Benchmark terminal-benchmark-1c027e78be41 live-api",
  "task_type": "terminal_benchmark",
  "difficulty": "medium",
  "skill_tags": ["rust", "json", "seccomp", "containers", "cli"],
  "source_type": "manual",
  "source_ref": "terminal-benchmark/terminal-benchmark-1c027e78be41/live-api/ws16-clean-cb1540ba",
  "external_task_id": "terminal-benchmark-1c027e78be41"
}
```

Locked task context after screening included:

```text
locked_guide_version: v1
locked_guide_source_snapshot_hash: sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb
locked_effective_project_submission_artifact_policy_hash: sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850
locked_pre_submit_checker_bundle_hash: sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63
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
submission_id: ba25f15a-e36a-4925-9891-09d394eae2ec
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
  "id": "d7885348-fd08-4820-b209-36a704765a2b",
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
locked_guide_source_snapshot_hash: sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb
locked_effective_project_submission_artifact_policy_hash: sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850
locked_pre_submit_checker_bundle_hash: sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63
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
  "name": "Terminal Benchmark Real API ws16-clean-cb1540ba",
  "slug": "terminal-benchmark-real-api-ws16-clean-cb1540ba"
}
```

Response body:

```json
{
  "created_at": "2026-07-08T23:43:31.535968Z",
  "description": "Real Terminal Benchmark fixture used as Workstream API evidence with sanitized source text.",
  "id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "name": "Terminal Benchmark Real API ws16-clean-cb1540ba",
  "slug": "terminal-benchmark-real-api-ws16-clean-cb1540ba",
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
  "content_markdown": "<redacted-large-text sha256:586b0e702b8fe201185ffab41d9ec4b4b862fea134deb010c2cc93c3b7412c1c bytes:138427>",
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
        "content_excerpt": "<redacted-large-text sha256:83e622313af9475491018b62eaf7e04994d21cb37e2477243429f898915d42c3 bytes:6112>",
        "content_hash": "sha256:a2b2d57cc56cddc4a8049e9df00da02577fcd729043aad065e2a47f84ca4372e",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/PROJECT_GUIDE.md",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/markdown",
        "source_kind": "project_guide"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:d9f7d7d3e8c6a2f34e8a66a3a16b59debe5288698ab47816decc46783abdc55c bytes:6000>",
        "content_hash": "sha256:297415ca932fd7109c63c03232afd0d73a0ce0b1237cd460a6b0cbec81e8995d",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/REVIEWER_PROGRAM.md",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/markdown",
        "source_kind": "reviewer_program"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811 bytes:1562>",
        "content_hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/task.toml",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/toml",
        "source_kind": "task_material"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:ad79f0f6e01c996dad51584e8e94613a7a90c7926dbea45d42f6403c3ab269de bytes:6184>",
        "content_hash": "sha256:42eb6fead00923488b1212d23ef756926849dd51087aa0490ca656e829e8b8ea",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/review_packet.md",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/markdown",
        "source_kind": "review_packet"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:73840f643300f873de7bfff017cfe00ed01659208800fd1c572362fc8a300b62 bytes:612>",
        "content_hash": "sha256:73840f643300f873de7bfff017cfe00ed01659208800fd1c572362fc8a300b62",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/static_guard.txt",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/plain",
        "source_kind": "checker_evidence"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:6063a751026695b21e58992629eb5051890e424baece1163de3f5e8491e89bc2 bytes:6000>",
        "content_hash": "sha256:793b9c193beb4f7b4bad4aacf66f5a74a6007e420c3232039d96cfa8cf6fbf42",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/docker_build.log",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/plain",
        "source_kind": "checker_evidence"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:33e5d68026c8e84b7558e2389293edc9d8b9f366a37e40b449397cd1b5b6fd97 bytes:3926>",
        "content_hash": "sha256:33e5d68026c8e84b7558e2389293edc9d8b9f366a37e40b449397cd1b5b6fd97",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/oracle_test.log",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "media_type": "text/plain",
        "source_kind": "checker_evidence"
      },
      {
        "content_cid": null,
        "content_excerpt": "<redacted-large-text sha256:49d77e52862014442ee09cb884fa89856bdd06a26c10131411b23bf641aeca1c bytes:6000>",
        "content_hash": "sha256:fb06dbd479c6a782297fde0f83414ff3f9bc456ece2c7e7098362f783730bbc2",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/starter_m1_test.log",
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
  "content_markdown": "<redacted-large-text sha256:586b0e702b8fe201185ffab41d9ec4b4b862fea134deb010c2cc93c3b7412c1c bytes:138427>",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "effective_at": null,
  "id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "queued",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": null,
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "guide_sufficiency",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": null,
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "guide_sufficiency",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": null,
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "guide_sufficiency",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": null,
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": null,
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": null,
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "celery_task_id": "3ef70bda-0261-4008-9255-d6b4a0fd2351",
  "created_at": "2026-07-08T23:43:31.606777Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "current_step": "submission_artifact_policy_derivation",
  "error_code": null,
  "error_summary": null,
  "finished_at": "2026-07-08T23:44:00.380059Z",
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "54b56346-0562-47b9-b2b1-1f7ec10f8805",
  "output_submission_artifact_policy_id": "f81d05aa-8f7d-4498-b3da-1de9b453d450",
  "output_sufficiency_report_id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
  "status": "passed",
  "summary": "The guide provides sufficient reviewer criteria and workflow direction for this Terminus task review, including milestone structure, static guard handling, dependency pinning, Dockerfile requirements, test alignment, rubric rules, reward behavior, and category mapping.",
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
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "f81d05aa-8f7d-4498-b3da-1de9b453d450",
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
  "policy_hash": "sha256:aa0cf8add77b6d193e5f3ffa1bf22f0fd21f27e484e4aa027e693d77b3624136",
  "policy_version": "agent-9843f69ef5b7f7631f98a61d",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_material_refs": [
    "import:/fixtures/terminal-benchmark-1c027e78be41/docker_build.log",
    "import:/fixtures/terminal-benchmark-1c027e78be41/oracle_test.log",
    "import:/fixtures/terminal-benchmark-1c027e78be41/starter_m1_test.log",
    "import:/fixtures/terminal-benchmark-1c027e78be41/static_guard.txt",
    "import:/fixtures/terminal-benchmark-1c027e78be41/PROJECT_GUIDE.md",
    "inline:/guides/fbe0b2ab-2793-4619-a414-ed083d9cc117/v1",
    "import:/fixtures/terminal-benchmark-1c027e78be41/review_packet.md",
    "import:/fixtures/terminal-benchmark-1c027e78be41/REVIEWER_PROGRAM.md",
    "import:/fixtures/terminal-benchmark-1c027e78be41/task.toml"
  ],
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
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
  "effective_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "lifecycle_status": "approved",
  "merge_algorithm_version": "workstream_default_merge.v1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
  "submission_artifact_policy_hash": "sha256:aa0cf8add77b6d193e5f3ffa1bf22f0fd21f27e484e4aa027e693d77b3624136",
  "submission_artifact_policy_id": "f81d05aa-8f7d-4498-b3da-1de9b453d450",
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
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
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
  "effective_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "lifecycle_status": "approved",
  "merge_algorithm_version": "workstream_default_merge.v1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
  "submission_artifact_policy_hash": "sha256:aa0cf8add77b6d193e5f3ffa1bf22f0fd21f27e484e4aa027e693d77b3624136",
  "submission_artifact_policy_id": "f81d05aa-8f7d-4498-b3da-1de9b453d450",
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
  "compiled_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
  "compiler_version": "workstream-pre-submit-compiler-v0.1",
  "created_at": "2026-07-08T23:44:02.228409Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "effective_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "effective_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
  "guide_version": "v1",
  "id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
  "lifecycle_status": "compiled",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
    "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
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
    "effective_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
    "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
    "guide_version": "v1",
    "id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
    "lifecycle_status": "approved",
    "merge_algorithm_version": "workstream_default_merge.v1",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
    "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
    "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
    "submission_artifact_policy_hash": "sha256:aa0cf8add77b6d193e5f3ffa1bf22f0fd21f27e484e4aa027e693d77b3624136",
    "submission_artifact_policy_id": "f81d05aa-8f7d-4498-b3da-1de9b453d450",
    "superseded_at": null,
    "supersedes_effective_policy_id": null
  },
  "guide": {
    "approved_by": "5080787a-cb3b-591d-9948-6b38354788ab",
    "change_summary": "Initial Terminal Benchmark real-world guide from sanitized imported source snapshot bundle.",
    "content_markdown": "<redacted-large-text sha256:586b0e702b8fe201185ffab41d9ec4b4b862fea134deb010c2cc93c3b7412c1c bytes:138427>",
    "created_at": "2026-07-08T23:43:31.606777Z",
    "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
    "effective_at": "2026-07-08T23:44:03.147622Z",
    "id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
    "status": "active",
    "superseded_at": null,
    "updated_at": "2026-07-08T23:44:02.875444Z",
    "version": "v1"
  },
  "guide_source_snapshot": {
    "bundle_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
    "captured_at": "2026-07-08T23:43:31.606777Z",
    "captured_by": "5080787a-cb3b-591d-9948-6b38354788ab",
    "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
    "guide_version": "v1",
    "id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
    "items": [
      {
        "content_cid": null,
        "content_hash": "sha256:793b9c193beb4f7b4bad4aacf66f5a74a6007e420c3232039d96cfa8cf6fbf42",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/docker_build.log",
        "id": "c408d25e-6276-426f-a99e-ac6114db773b",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 0,
        "media_type": "text/plain",
        "source_kind": "checker_evidence",
        "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:33e5d68026c8e84b7558e2389293edc9d8b9f366a37e40b449397cd1b5b6fd97",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/oracle_test.log",
        "id": "8531f065-4575-43c1-bf39-e51e0ae3cd07",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 1,
        "media_type": "text/plain",
        "source_kind": "checker_evidence",
        "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:fb06dbd479c6a782297fde0f83414ff3f9bc456ece2c7e7098362f783730bbc2",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/starter_m1_test.log",
        "id": "45961844-d3cb-4418-b03f-3a3eeca32615",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 2,
        "media_type": "text/plain",
        "source_kind": "checker_evidence",
        "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:73840f643300f873de7bfff017cfe00ed01659208800fd1c572362fc8a300b62",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/static_guard.txt",
        "id": "49d53b1d-1a81-45e1-9d37-7f519478c654",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 3,
        "media_type": "text/plain",
        "source_kind": "checker_evidence",
        "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:a2b2d57cc56cddc4a8049e9df00da02577fcd729043aad065e2a47f84ca4372e",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/PROJECT_GUIDE.md",
        "id": "a23f68aa-b4d0-4dd5-aeba-d0d9a716f96c",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 4,
        "media_type": "text/markdown",
        "source_kind": "project_guide",
        "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:4b88e4bb333b1ff2d207ffedfde94c8350a814e3c89db8789a2d0a851397a042",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "inline:/guides/fbe0b2ab-2793-4619-a414-ed083d9cc117/v1",
        "id": "f1b51900-4dac-47fd-9d93-97d975877cd8",
        "ingestion_adapter": "workstream_project_guide",
        "item_order": 5,
        "media_type": "application/json",
        "source_kind": "project_guide",
        "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:42eb6fead00923488b1212d23ef756926849dd51087aa0490ca656e829e8b8ea",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/review_packet.md",
        "id": "61db2ff4-3495-49d4-80b3-78cc023f2e51",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 6,
        "media_type": "text/markdown",
        "source_kind": "review_packet",
        "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:297415ca932fd7109c63c03232afd0d73a0ce0b1237cd460a6b0cbec81e8995d",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/REVIEWER_PROGRAM.md",
        "id": "87c64c15-33d9-48f2-85a6-cb0ee5ddd932",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 7,
        "media_type": "text/markdown",
        "source_kind": "reviewer_program",
        "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b"
      },
      {
        "content_cid": null,
        "content_hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
        "created_at": "2026-07-08T23:43:31.606777Z",
        "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/task.toml",
        "id": "316c8374-322d-4e49-a6d9-a581803cb32a",
        "ingestion_adapter": "manual_fixture_import_sanitized",
        "item_order": 8,
        "media_type": "text/toml",
        "source_kind": "task_material",
        "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b"
      }
    ],
    "manifest_json": {
      "items": [
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:6063a751026695b21e58992629eb5051890e424baece1163de3f5e8491e89bc2 bytes:6000>",
          "content_hash": "sha256:793b9c193beb4f7b4bad4aacf66f5a74a6007e420c3232039d96cfa8cf6fbf42",
          "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/docker_build.log",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/plain",
          "source_kind": "checker_evidence"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:33e5d68026c8e84b7558e2389293edc9d8b9f366a37e40b449397cd1b5b6fd97 bytes:3926>",
          "content_hash": "sha256:33e5d68026c8e84b7558e2389293edc9d8b9f366a37e40b449397cd1b5b6fd97",
          "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/oracle_test.log",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/plain",
          "source_kind": "checker_evidence"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:49d77e52862014442ee09cb884fa89856bdd06a26c10131411b23bf641aeca1c bytes:6000>",
          "content_hash": "sha256:fb06dbd479c6a782297fde0f83414ff3f9bc456ece2c7e7098362f783730bbc2",
          "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/starter_m1_test.log",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/plain",
          "source_kind": "checker_evidence"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:73840f643300f873de7bfff017cfe00ed01659208800fd1c572362fc8a300b62 bytes:612>",
          "content_hash": "sha256:73840f643300f873de7bfff017cfe00ed01659208800fd1c572362fc8a300b62",
          "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/static_guard.txt",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/plain",
          "source_kind": "checker_evidence"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:83e622313af9475491018b62eaf7e04994d21cb37e2477243429f898915d42c3 bytes:6112>",
          "content_hash": "sha256:a2b2d57cc56cddc4a8049e9df00da02577fcd729043aad065e2a47f84ca4372e",
          "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/PROJECT_GUIDE.md",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/markdown",
          "source_kind": "project_guide"
        },
        {
          "content_cid": null,
          "content_excerpt": null,
          "content_hash": "sha256:4b88e4bb333b1ff2d207ffedfde94c8350a814e3c89db8789a2d0a851397a042",
          "durable_ref": "inline:/guides/fbe0b2ab-2793-4619-a414-ed083d9cc117/v1",
          "ingestion_adapter": "workstream_project_guide",
          "media_type": "application/json",
          "source_kind": "project_guide"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:ad79f0f6e01c996dad51584e8e94613a7a90c7926dbea45d42f6403c3ab269de bytes:6184>",
          "content_hash": "sha256:42eb6fead00923488b1212d23ef756926849dd51087aa0490ca656e829e8b8ea",
          "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/review_packet.md",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/markdown",
          "source_kind": "review_packet"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:d9f7d7d3e8c6a2f34e8a66a3a16b59debe5288698ab47816decc46783abdc55c bytes:6000>",
          "content_hash": "sha256:297415ca932fd7109c63c03232afd0d73a0ce0b1237cd460a6b0cbec81e8995d",
          "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/REVIEWER_PROGRAM.md",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/markdown",
          "source_kind": "reviewer_program"
        },
        {
          "content_cid": null,
          "content_excerpt": "<redacted-large-text sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811 bytes:1562>",
          "content_hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
          "durable_ref": "import:/fixtures/terminal-benchmark-1c027e78be41/task.toml",
          "ingestion_adapter": "manual_fixture_import_sanitized",
          "media_type": "text/toml",
          "source_kind": "task_material"
        }
      ],
      "schema_version": "guide_source_snapshot.v1"
    },
    "manifest_schema_version": "guide_source_snapshot.v1",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130"
  },
  "guide_sufficiency_report": {
    "acknowledgement_note": null,
    "agent_name": "ProjectGuideSufficiencyAgent",
    "agent_version": "workstream-sufficiency-agent-v0.1",
    "created_at": "2026-07-08T23:43:40.523990Z",
    "created_by": "workstream-system:project-setup-pipeline",
    "findings": [],
    "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
    "guide_version": "v1",
    "id": "27cd37ac-638f-445a-8637-b8ced01d3ae1",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
    "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
    "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
    "status": "passed",
    "summary": "The guide provides sufficient reviewer criteria and workflow direction for this Terminus task review, including milestone structure, static guard handling, dependency pinning, Dockerfile requirements, test alignment, rubric rules, reward behavior, and category mapping.",
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
    "id": "9219d8bc-153c-4492-8884-571ec92a8264",
    "payout_type": "fixed",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
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
    "id": "30095d84-e5c5-46e3-a292-3788bd34699f",
    "policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
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
    "compiled_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
    "compiler_version": "workstream-pre-submit-compiler-v0.1",
    "created_at": "2026-07-08T23:44:02.228409Z",
    "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
    "effective_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
    "effective_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
    "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
    "guide_version": "v1",
    "id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
    "lifecycle_status": "compiled",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
    "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
    "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
    "id": "ff2e72ce-efff-461a-9491-e88f3e61e259",
    "minimum_finding_fields": [
      "issue",
      "required_fix"
    ],
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
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
    "id": "17ddcb94-16e0-420d-8507-a8faba12fa8c",
    "max_revision_rounds": 7,
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
    "reviewer_reassignment_rule": "same_reviewer_preferred",
    "revision_deadline_hours": 48
  },
  "submission_artifact_policy": {
    "approved_at": "2026-07-08T23:44:02.420104Z",
    "approved_by_actor": "5080787a-cb3b-591d-9948-6b38354788ab",
    "approved_by_role": "project_manager",
    "change_summary": null,
    "created_at": "2026-07-08T23:44:00.095072Z",
    "created_by": "workstream-system:project-setup-pipeline",
    "derivation_agent_name": "SubmissionArtifactPolicyDerivationAgent",
    "derivation_agent_version": "workstream-policy-derivation-agent-v0.1",
    "derivation_source": "agent_derivation",
    "guide_id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
    "guide_version": "v1",
    "id": "f81d05aa-8f7d-4498-b3da-1de9b453d450",
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
    "policy_hash": "sha256:aa0cf8add77b6d193e5f3ffa1bf22f0fd21f27e484e4aa027e693d77b3624136",
    "policy_version": "agent-9843f69ef5b7f7631f98a61d",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
    "source_material_refs": [
      "import:/fixtures/terminal-benchmark-1c027e78be41/docker_build.log",
      "import:/fixtures/terminal-benchmark-1c027e78be41/oracle_test.log",
      "import:/fixtures/terminal-benchmark-1c027e78be41/starter_m1_test.log",
      "import:/fixtures/terminal-benchmark-1c027e78be41/static_guard.txt",
      "import:/fixtures/terminal-benchmark-1c027e78be41/PROJECT_GUIDE.md",
      "inline:/guides/fbe0b2ab-2793-4619-a414-ed083d9cc117/v1",
      "import:/fixtures/terminal-benchmark-1c027e78be41/review_packet.md",
      "import:/fixtures/terminal-benchmark-1c027e78be41/REVIEWER_PROGRAM.md",
      "import:/fixtures/terminal-benchmark-1c027e78be41/task.toml"
    ],
    "source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
    "source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "description": "Real Terminal Benchmark reviewer fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "terminal-benchmark-1c027e78be41",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "seccomp",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
  "source_ref": "terminal-benchmark/terminal-benchmark-1c027e78be41/live-api/ws16-clean-cb1540ba",
  "source_type": "manual",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark terminal-benchmark-1c027e78be41 live-api"
}
```

Response body:

```json
{
  "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
  "created_at": "2026-07-08T23:44:03.452947Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "description": "Real Terminal Benchmark reviewer fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "terminal-benchmark-1c027e78be41",
  "id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "seccomp",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
  "source_ref": "terminal-benchmark/terminal-benchmark-1c027e78be41/live-api/ws16-clean-cb1540ba",
  "source_type": "manual",
  "status": "draft",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark terminal-benchmark-1c027e78be41 live-api",
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
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "currency": "USD",
  "description": "Real Terminal Benchmark reviewer fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "terminal-benchmark-1c027e78be41",
  "id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
  "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "payout_type": "fixed",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "seccomp",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
  "source_ref": "terminal-benchmark/terminal-benchmark-1c027e78be41/live-api/ws16-clean-cb1540ba",
  "source_type": "manual",
  "status": "screening",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark terminal-benchmark-1c027e78be41 live-api",
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
  "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
  "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
  "locked_post_submit_checker_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
  "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3"
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
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "currency": "USD",
  "description": "Real Terminal Benchmark reviewer fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "terminal-benchmark-1c027e78be41",
  "id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
  "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "payout_type": "fixed",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "seccomp",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
  "source_ref": "terminal-benchmark/terminal-benchmark-1c027e78be41/live-api/ws16-clean-cb1540ba",
  "source_type": "manual",
  "status": "ready",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark terminal-benchmark-1c027e78be41 live-api",
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
    "seccomp",
    "containers",
    "cli"
  ]
}
```

Response body:

```json
{
  "actor_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
  "created_at": "2026-07-08T23:44:04.145081Z",
  "display_name": "Terminal Benchmark Worker Ws16 Clean Cb1540Ba",
  "email": "terminal-benchmark-worker-ws16-clean-cb1540ba@flow.local",
  "external_issuer": "https://auth.flow.local/e2e",
  "external_subject": "terminal-benchmark-worker-ws16-clean-cb1540ba",
  "id": "f67a061a-ff59-4416-bd5a-3fa8461e8b25",
  "profile_metadata": {
    "source": "worker_profile_api"
  },
  "profile_type": "worker",
  "scope_id": "global",
  "scope_type": "global",
  "skill_tags": [
    "rust",
    "json",
    "seccomp",
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
    "assigned_by": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
    "id": "47f47a44-cd98-41e6-859e-86ac232cd83b",
    "status": "active",
    "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
  },
  "task": {
    "acceptance_criteria": "Submission packet must satisfy the locked project submission requirements and pre-submit checker policy.",
    "base_amount": "25.00",
    "created_at": "2026-07-08T23:44:03.452947Z",
    "currency": "USD",
    "description": "Real Terminal Benchmark reviewer fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
    "difficulty": "medium",
    "estimated_time_minutes": 75,
    "id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "locked_guide_version": "v1",
    "locked_payment_policy_version": "v1",
    "locked_review_policy_version": "v1",
    "locked_revision_policy_version": "v1",
    "payout_type": "fixed",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
    "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
    "skill_tags": [
      "rust",
      "json",
      "seccomp",
      "containers",
      "cli"
    ],
    "source_type": "manual",
    "status": "claimed",
    "task_type": "terminal_benchmark",
    "title": "Terminal Benchmark terminal-benchmark-1c027e78be41 live-api",
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
  "description": "Real Terminal Benchmark reviewer fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "payout_type": "fixed",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "seccomp",
    "containers",
    "cli"
  ],
  "source_type": "manual",
  "status": "in_progress",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark terminal-benchmark-1c027e78be41 live-api",
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
  "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
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
  "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
  "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
  "locked_post_submit_checker_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
  "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3"
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
    "content_markdown": "<redacted-large-text sha256:586b0e702b8fe201185ffab41d9ec4b4b862fea134deb010c2cc93c3b7412c1c bytes:138427>",
    "effective_at": "2026-07-08T23:44:03.147622Z",
    "id": "fbe0b2ab-2793-4619-a414-ed083d9cc117",
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
    "id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
    "name": "Terminal Benchmark Real API ws16-clean-cb1540ba",
    "slug": "terminal-benchmark-real-api-ws16-clean-cb1540ba"
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
    "description": "Real Terminal Benchmark reviewer fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
    "difficulty": "medium",
    "estimated_time_minutes": 75,
    "id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "locked_guide_version": "v1",
    "payout_type": "fixed",
    "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
    "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
    "skill_tags": [
      "rust",
      "json",
      "seccomp",
      "containers",
      "cli"
    ],
    "status": "in_progress",
    "task_type": "terminal_benchmark",
    "title": "Terminal Benchmark terminal-benchmark-1c027e78be41 live-api",
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
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
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
  "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3"
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
        "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 1327
      },
      {
        "artifact": "rubric.md",
        "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 34
      },
      {
        "artifact": "task.toml",
        "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 1562
      }
    ],
    "evidence_items": [
      {
        "hash": "sha256:054bfe7027e1d80dbbcc44e9ccb077714e482d7bdef7abbdf9cee10dea17966a",
        "label": "Dependency pinning review",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "dependency_pinning_review"
        },
        "size_bytes": 40,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/dependency_pinning_review.txt"
      },
      {
        "hash": "sha256:693734646cdc384030f735f2cf8b74da1fcf5fe1f12e0e53237ecf13016de751",
        "label": "Environment hygiene review",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "environment_hygiene_review"
        },
        "size_bytes": 41,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/environment_hygiene_review.txt"
      },
      {
        "hash": "sha256:37f31815061bdb7ad0d0c0c1e46ad7382b77df61c36583e3a704c87c763d99ca",
        "label": "Task instructions included",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "instructions_present"
        },
        "size_bytes": 35,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/instructions_present.txt"
      },
      {
        "hash": "sha256:a88f98916343d1e1aac53d6fd09b9d3be01c322bce792a06074d0a2d46b27659",
        "label": "Reward footer review",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "reward_footer_review"
        },
        "size_bytes": 35,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/reward_footer_review.txt"
      },
      {
        "hash": "sha256:71feef897c3a79358318bf8b2634fce6c928ddd5303b57293b93be063bd8d20a",
        "label": "Reference solution included",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "solution_present"
        },
        "size_bytes": 31,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/solution_present.txt"
      },
      {
        "hash": "sha256:c82ac87b125cad1ca6928d1fed6b9190fda594c239a84c34dc9a2f77b2d10021",
        "label": "Submission explanations",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "submission_explanations"
        },
        "size_bytes": 38,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/submission_explanations.txt"
      },
      {
        "hash": "sha256:d4390376e1a3875eb88b7b404f0c02cc5cfb5aa123d087ce5890ad13dd6accc1",
        "label": "Test alignment review",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "test_alignment_review"
        },
        "size_bytes": 36,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/test_alignment_review.txt"
      },
      {
        "hash": "sha256:a89843ff6d20f721ed2b958b37046e740c53dad7c0e7fdd928b97e3e16e885ce",
        "label": "Verifier files included",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "tests_present"
        },
        "size_bytes": 28,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/tests_present.txt"
      }
    ],
    "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
    "package_uri": "local://termius/terminal-benchmark-1c027e78be41/submission.zip",
    "summary": "Blocked-path packet built from live requirements, missing environment/.dockerignore.",
    "worker_attestation": "<redacted-large-string sha256:cc6f114774078918553f5b2f5c3cddc2c0d9a8cb997837becba1ea330e51a82c bytes:752 prefix:'I attest this submission is original_work, produced under human_accountability_f'>"
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
  "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3"
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
      "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1327
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 34
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1562
    }
  ],
  "evidence_items": [
    {
      "hash": "sha256:054bfe7027e1d80dbbcc44e9ccb077714e482d7bdef7abbdf9cee10dea17966a",
      "label": "Dependency pinning review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "dependency_pinning_review"
      },
      "size_bytes": 40,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/dependency_pinning_review.txt"
    },
    {
      "hash": "sha256:693734646cdc384030f735f2cf8b74da1fcf5fe1f12e0e53237ecf13016de751",
      "label": "Environment hygiene review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "environment_hygiene_review"
      },
      "size_bytes": 41,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/environment_hygiene_review.txt"
    },
    {
      "hash": "sha256:37f31815061bdb7ad0d0c0c1e46ad7382b77df61c36583e3a704c87c763d99ca",
      "label": "Task instructions included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "instructions_present"
      },
      "size_bytes": 35,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/instructions_present.txt"
    },
    {
      "hash": "sha256:a88f98916343d1e1aac53d6fd09b9d3be01c322bce792a06074d0a2d46b27659",
      "label": "Reward footer review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "reward_footer_review"
      },
      "size_bytes": 35,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/reward_footer_review.txt"
    },
    {
      "hash": "sha256:71feef897c3a79358318bf8b2634fce6c928ddd5303b57293b93be063bd8d20a",
      "label": "Reference solution included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "solution_present"
      },
      "size_bytes": 31,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/solution_present.txt"
    },
    {
      "hash": "sha256:c82ac87b125cad1ca6928d1fed6b9190fda594c239a84c34dc9a2f77b2d10021",
      "label": "Submission explanations",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "submission_explanations"
      },
      "size_bytes": 38,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/submission_explanations.txt"
    },
    {
      "hash": "sha256:d4390376e1a3875eb88b7b404f0c02cc5cfb5aa123d087ce5890ad13dd6accc1",
      "label": "Test alignment review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "test_alignment_review"
      },
      "size_bytes": 36,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/test_alignment_review.txt"
    },
    {
      "hash": "sha256:a89843ff6d20f721ed2b958b37046e740c53dad7c0e7fdd928b97e3e16e885ce",
      "label": "Verifier files included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "tests_present"
      },
      "size_bytes": 28,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/tests_present.txt"
    }
  ],
  "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
  "package_uri": "local://termius/terminal-benchmark-1c027e78be41/submission.zip",
  "summary": "Blocked-path packet built from live requirements, missing environment/.dockerignore.",
  "worker_attestation": "<redacted-large-string sha256:cc6f114774078918553f5b2f5c3cddc2c0d9a8cb997837becba1ea330e51a82c bytes:752 prefix:'I attest this submission is original_work, produced under human_accountability_f'>"
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
    "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3"
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
    "actor_id": "5080787a-cb3b-591d-9948-6b38354788ab",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:03.452947Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
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
    "external_subject": "terminal-benchmark-manager-ws16-clean-cb1540ba",
    "from_status": null,
    "id": "3c645ce6-9cf1-498c-bff2-b5a53e481c3d",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "draft"
  },
  {
    "actor_id": "5080787a-cb3b-591d-9948-6b38354788ab",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:03.630101Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-ws16-clean-cb1540ba",
    "from_status": "draft",
    "id": "43563128-a38c-41ef-baad-f4a5ea77e153",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API screening; lock active guide and policy context.",
    "to_status": "screening"
  },
  {
    "actor_id": "5080787a-cb3b-591d-9948-6b38354788ab",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.041939Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-ws16-clean-cb1540ba",
    "from_status": "screening",
    "id": "b8264b10-3383-4138-ab3b-6071850aaff9",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API ready for worker claim.",
    "to_status": "ready"
  },
  {
    "actor_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.503583Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
      "assignment_id": "47f47a44-cd98-41e6-859e-86ac232cd83b",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-ws16-clean-cb1540ba",
    "from_status": "ready",
    "id": "b5a3091c-8506-41fe-800c-58dd1aadfb8a",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API worker claim.",
    "to_status": "claimed"
  },
  {
    "actor_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.727342Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
      "assignment_id": "47f47a44-cd98-41e6-859e-86ac232cd83b",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "operator_override": false,
      "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-ws16-clean-cb1540ba",
    "from_status": "claimed",
    "id": "3f3f1439-662a-4c42-b2bf-6e5543489d46",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API worker started work.",
    "to_status": "in_progress"
  },
  {
    "actor_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:17.452515Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
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
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3"
      }
    },
    "event_type": "pre_submission_check_failed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-ws16-clean-cb1540ba",
    "from_status": "in_progress",
    "id": "aaeaf9c7-4482-4bdf-956f-075f539175eb",
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
        "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 1327
      },
      {
        "artifact": "environment/.dockerignore",
        "hash": "sha256:cb2d67a46a111652f3bb388ee15d455eed7542905bdc61cd2a3c6d2fc23cc709",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 185
      },
      {
        "artifact": "rubric.md",
        "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 34
      },
      {
        "artifact": "task.toml",
        "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 1562
      }
    ],
    "evidence_items": [
      {
        "hash": "sha256:054bfe7027e1d80dbbcc44e9ccb077714e482d7bdef7abbdf9cee10dea17966a",
        "label": "Dependency pinning review",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "dependency_pinning_review"
        },
        "size_bytes": 40,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/dependency_pinning_review.txt"
      },
      {
        "hash": "sha256:693734646cdc384030f735f2cf8b74da1fcf5fe1f12e0e53237ecf13016de751",
        "label": "Environment hygiene review",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "environment_hygiene_review"
        },
        "size_bytes": 41,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/environment_hygiene_review.txt"
      },
      {
        "hash": "sha256:37f31815061bdb7ad0d0c0c1e46ad7382b77df61c36583e3a704c87c763d99ca",
        "label": "Task instructions included",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "instructions_present"
        },
        "size_bytes": 35,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/instructions_present.txt"
      },
      {
        "hash": "sha256:a88f98916343d1e1aac53d6fd09b9d3be01c322bce792a06074d0a2d46b27659",
        "label": "Reward footer review",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "reward_footer_review"
        },
        "size_bytes": 35,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/reward_footer_review.txt"
      },
      {
        "hash": "sha256:71feef897c3a79358318bf8b2634fce6c928ddd5303b57293b93be063bd8d20a",
        "label": "Reference solution included",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "solution_present"
        },
        "size_bytes": 31,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/solution_present.txt"
      },
      {
        "hash": "sha256:c82ac87b125cad1ca6928d1fed6b9190fda594c239a84c34dc9a2f77b2d10021",
        "label": "Submission explanations",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "submission_explanations"
        },
        "size_bytes": 38,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/submission_explanations.txt"
      },
      {
        "hash": "sha256:d4390376e1a3875eb88b7b404f0c02cc5cfb5aa123d087ce5890ad13dd6accc1",
        "label": "Test alignment review",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "test_alignment_review"
        },
        "size_bytes": 36,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/test_alignment_review.txt"
      },
      {
        "hash": "sha256:a89843ff6d20f721ed2b958b37046e740c53dad7c0e7fdd928b97e3e16e885ce",
        "label": "Verifier files included",
        "metadata": {
          "fixture_id": "terminal-benchmark-1c027e78be41",
          "required_evidence_key": "tests_present"
        },
        "size_bytes": 28,
        "type": "log",
        "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/tests_present.txt"
      }
    ],
    "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
    "package_uri": "local://termius/terminal-benchmark-1c027e78be41/submission.zip",
    "summary": "Terminal Benchmark terminal-benchmark-1c027e78be41 packet built from live submission requirements.",
    "worker_attestation": "<redacted-large-string sha256:cc6f114774078918553f5b2f5c3cddc2c0d9a8cb997837becba1ea330e51a82c bytes:752 prefix:'I attest this submission is original_work, produced under human_accountability_f'>"
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
  "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3"
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
      "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1327
    },
    {
      "artifact": "environment/.dockerignore",
      "hash": "sha256:cb2d67a46a111652f3bb388ee15d455eed7542905bdc61cd2a3c6d2fc23cc709",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 185
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 34
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1562
    }
  ],
  "evidence_items": [
    {
      "hash": "sha256:054bfe7027e1d80dbbcc44e9ccb077714e482d7bdef7abbdf9cee10dea17966a",
      "label": "Dependency pinning review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "dependency_pinning_review"
      },
      "size_bytes": 40,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/dependency_pinning_review.txt"
    },
    {
      "hash": "sha256:693734646cdc384030f735f2cf8b74da1fcf5fe1f12e0e53237ecf13016de751",
      "label": "Environment hygiene review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "environment_hygiene_review"
      },
      "size_bytes": 41,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/environment_hygiene_review.txt"
    },
    {
      "hash": "sha256:37f31815061bdb7ad0d0c0c1e46ad7382b77df61c36583e3a704c87c763d99ca",
      "label": "Task instructions included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "instructions_present"
      },
      "size_bytes": 35,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/instructions_present.txt"
    },
    {
      "hash": "sha256:a88f98916343d1e1aac53d6fd09b9d3be01c322bce792a06074d0a2d46b27659",
      "label": "Reward footer review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "reward_footer_review"
      },
      "size_bytes": 35,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/reward_footer_review.txt"
    },
    {
      "hash": "sha256:71feef897c3a79358318bf8b2634fce6c928ddd5303b57293b93be063bd8d20a",
      "label": "Reference solution included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "solution_present"
      },
      "size_bytes": 31,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/solution_present.txt"
    },
    {
      "hash": "sha256:c82ac87b125cad1ca6928d1fed6b9190fda594c239a84c34dc9a2f77b2d10021",
      "label": "Submission explanations",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "submission_explanations"
      },
      "size_bytes": 38,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/submission_explanations.txt"
    },
    {
      "hash": "sha256:d4390376e1a3875eb88b7b404f0c02cc5cfb5aa123d087ce5890ad13dd6accc1",
      "label": "Test alignment review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "test_alignment_review"
      },
      "size_bytes": 36,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/test_alignment_review.txt"
    },
    {
      "hash": "sha256:a89843ff6d20f721ed2b958b37046e740c53dad7c0e7fdd928b97e3e16e885ce",
      "label": "Verifier files included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "tests_present"
      },
      "size_bytes": 28,
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/tests_present.txt"
    }
  ],
  "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
  "package_uri": "local://termius/terminal-benchmark-1c027e78be41/submission.zip",
  "summary": "Terminal Benchmark terminal-benchmark-1c027e78be41 packet built from live submission requirements.",
  "worker_attestation": "<redacted-large-string sha256:cc6f114774078918553f5b2f5c3cddc2c0d9a8cb997837becba1ea330e51a82c bytes:752 prefix:'I attest this submission is original_work, produced under human_accountability_f'>"
}
```

Response body:

```json
{
  "evidence_items": [
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "0807ade0-2c5a-4128-a253-e3f6307c6e69",
      "label": "Dependency pinning review",
      "metadata": {},
      "size_bytes": 40,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "21e8b24f-51d8-4934-96dd-6608b9d54082",
      "label": "Environment hygiene review",
      "metadata": {},
      "size_bytes": 41,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "06f50e90-b055-485e-bda4-289ffa822025",
      "label": "Task instructions included",
      "metadata": {},
      "size_bytes": 35,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "f21c9ab2-cc6d-466b-a2fb-817ae8741918",
      "label": "Reward footer review",
      "metadata": {},
      "size_bytes": 35,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "40eb6111-adeb-48ba-9333-ddaa8340a768",
      "label": "Reference solution included",
      "metadata": {},
      "size_bytes": 31,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "d94c5f46-a286-44cc-a19b-2e4890be3ef8",
      "label": "Submission explanations",
      "metadata": {},
      "size_bytes": 38,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "f0d58929-efa4-446f-bb72-04c7a2c14a77",
      "label": "Test alignment review",
      "metadata": {},
      "size_bytes": 36,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "id": "afdb97ca-4a8d-46de-9d7f-34f4c7468242",
      "label": "Verifier files included",
      "metadata": {},
      "size_bytes": 28,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log"
    }
  ],
  "id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
  "status": "submitted",
  "submitted_at": "2026-07-08T23:45:18.127472Z",
  "summary": "Terminal Benchmark terminal-benchmark-1c027e78be41 packet built from live submission requirements.",
  "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
  "version": 1,
  "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
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
        "id": "0807ade0-2c5a-4128-a253-e3f6307c6e69",
        "label": "Dependency pinning review",
        "metadata": {},
        "size_bytes": 40,
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "21e8b24f-51d8-4934-96dd-6608b9d54082",
        "label": "Environment hygiene review",
        "metadata": {},
        "size_bytes": 41,
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "06f50e90-b055-485e-bda4-289ffa822025",
        "label": "Task instructions included",
        "metadata": {},
        "size_bytes": 35,
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "f21c9ab2-cc6d-466b-a2fb-817ae8741918",
        "label": "Reward footer review",
        "metadata": {},
        "size_bytes": 35,
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "40eb6111-adeb-48ba-9333-ddaa8340a768",
        "label": "Reference solution included",
        "metadata": {},
        "size_bytes": 31,
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "d94c5f46-a286-44cc-a19b-2e4890be3ef8",
        "label": "Submission explanations",
        "metadata": {},
        "size_bytes": 38,
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "f0d58929-efa4-446f-bb72-04c7a2c14a77",
        "label": "Test alignment review",
        "metadata": {},
        "size_bytes": 36,
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "type": "log"
      },
      {
        "created_at": "2026-07-08T23:45:18.127472Z",
        "id": "afdb97ca-4a8d-46de-9d7f-34f4c7468242",
        "label": "Verifier files included",
        "metadata": {},
        "size_bytes": 28,
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "type": "log"
      }
    ],
    "id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
    "status": "submitted",
    "submitted_at": "2026-07-08T23:45:18.127472Z",
    "summary": "Terminal Benchmark terminal-benchmark-1c027e78be41 packet built from live submission requirements.",
    "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "version": 1,
    "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
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
      "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1327
    },
    {
      "artifact": "environment/.dockerignore",
      "hash": "sha256:cb2d67a46a111652f3bb388ee15d455eed7542905bdc61cd2a3c6d2fc23cc709",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 185
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 34
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1562
    }
  ],
  "evidence_items": [
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:054bfe7027e1d80dbbcc44e9ccb077714e482d7bdef7abbdf9cee10dea17966a",
      "id": "0807ade0-2c5a-4128-a253-e3f6307c6e69",
      "label": "Dependency pinning review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "dependency_pinning_review"
      },
      "size_bytes": 40,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/dependency_pinning_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:693734646cdc384030f735f2cf8b74da1fcf5fe1f12e0e53237ecf13016de751",
      "id": "21e8b24f-51d8-4934-96dd-6608b9d54082",
      "label": "Environment hygiene review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "environment_hygiene_review"
      },
      "size_bytes": 41,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/environment_hygiene_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:37f31815061bdb7ad0d0c0c1e46ad7382b77df61c36583e3a704c87c763d99ca",
      "id": "06f50e90-b055-485e-bda4-289ffa822025",
      "label": "Task instructions included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "instructions_present"
      },
      "size_bytes": 35,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/instructions_present.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:a88f98916343d1e1aac53d6fd09b9d3be01c322bce792a06074d0a2d46b27659",
      "id": "f21c9ab2-cc6d-466b-a2fb-817ae8741918",
      "label": "Reward footer review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "reward_footer_review"
      },
      "size_bytes": 35,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/reward_footer_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:71feef897c3a79358318bf8b2634fce6c928ddd5303b57293b93be063bd8d20a",
      "id": "40eb6111-adeb-48ba-9333-ddaa8340a768",
      "label": "Reference solution included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "solution_present"
      },
      "size_bytes": 31,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/solution_present.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:c82ac87b125cad1ca6928d1fed6b9190fda594c239a84c34dc9a2f77b2d10021",
      "id": "d94c5f46-a286-44cc-a19b-2e4890be3ef8",
      "label": "Submission explanations",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "submission_explanations"
      },
      "size_bytes": 38,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/submission_explanations.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:d4390376e1a3875eb88b7b404f0c02cc5cfb5aa123d087ce5890ad13dd6accc1",
      "id": "f0d58929-efa4-446f-bb72-04c7a2c14a77",
      "label": "Test alignment review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "test_alignment_review"
      },
      "size_bytes": 36,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/test_alignment_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:a89843ff6d20f721ed2b958b37046e740c53dad7c0e7fdd928b97e3e16e885ce",
      "id": "afdb97ca-4a8d-46de-9d7f-34f4c7468242",
      "label": "Verifier files included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "tests_present"
      },
      "size_bytes": 28,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/tests_present.txt"
    }
  ],
  "finalized_at": "2026-07-08T23:45:18.750577Z",
  "id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
  "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
  "package_uri": "local://termius/terminal-benchmark-1c027e78be41/submission.zip",
  "status": "submitted",
  "submitted_at": "2026-07-08T23:45:18.127472Z",
  "summary": "Terminal Benchmark terminal-benchmark-1c027e78be41 packet built from live submission requirements.",
  "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
  "version": 1,
  "worker_attestation": "<redacted-large-string sha256:cc6f114774078918553f5b2f5c3cddc2c0d9a8cb997837becba1ea330e51a82c bytes:752 prefix:'I attest this submission is original_work, produced under human_accountability_f'>",
  "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
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
      "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1327
    },
    {
      "artifact": "environment/.dockerignore",
      "hash": "sha256:cb2d67a46a111652f3bb388ee15d455eed7542905bdc61cd2a3c6d2fc23cc709",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 185
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 34
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1562
    }
  ],
  "evidence_items": [
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:054bfe7027e1d80dbbcc44e9ccb077714e482d7bdef7abbdf9cee10dea17966a",
      "id": "0807ade0-2c5a-4128-a253-e3f6307c6e69",
      "label": "Dependency pinning review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "dependency_pinning_review"
      },
      "size_bytes": 40,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/dependency_pinning_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:693734646cdc384030f735f2cf8b74da1fcf5fe1f12e0e53237ecf13016de751",
      "id": "21e8b24f-51d8-4934-96dd-6608b9d54082",
      "label": "Environment hygiene review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "environment_hygiene_review"
      },
      "size_bytes": 41,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/environment_hygiene_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:37f31815061bdb7ad0d0c0c1e46ad7382b77df61c36583e3a704c87c763d99ca",
      "id": "06f50e90-b055-485e-bda4-289ffa822025",
      "label": "Task instructions included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "instructions_present"
      },
      "size_bytes": 35,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/instructions_present.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:a88f98916343d1e1aac53d6fd09b9d3be01c322bce792a06074d0a2d46b27659",
      "id": "f21c9ab2-cc6d-466b-a2fb-817ae8741918",
      "label": "Reward footer review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "reward_footer_review"
      },
      "size_bytes": 35,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/reward_footer_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:71feef897c3a79358318bf8b2634fce6c928ddd5303b57293b93be063bd8d20a",
      "id": "40eb6111-adeb-48ba-9333-ddaa8340a768",
      "label": "Reference solution included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "solution_present"
      },
      "size_bytes": 31,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/solution_present.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:c82ac87b125cad1ca6928d1fed6b9190fda594c239a84c34dc9a2f77b2d10021",
      "id": "d94c5f46-a286-44cc-a19b-2e4890be3ef8",
      "label": "Submission explanations",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "submission_explanations"
      },
      "size_bytes": 38,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/submission_explanations.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:d4390376e1a3875eb88b7b404f0c02cc5cfb5aa123d087ce5890ad13dd6accc1",
      "id": "f0d58929-efa4-446f-bb72-04c7a2c14a77",
      "label": "Test alignment review",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "test_alignment_review"
      },
      "size_bytes": 36,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/test_alignment_review.txt"
    },
    {
      "created_at": "2026-07-08T23:45:18.127472Z",
      "finalized_at": "2026-07-08T23:45:18.750577Z",
      "hash": "sha256:a89843ff6d20f721ed2b958b37046e740c53dad7c0e7fdd928b97e3e16e885ce",
      "id": "afdb97ca-4a8d-46de-9d7f-34f4c7468242",
      "label": "Verifier files included",
      "metadata": {
        "fixture_id": "terminal-benchmark-1c027e78be41",
        "required_evidence_key": "tests_present"
      },
      "size_bytes": 28,
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "type": "log",
      "uri": "local://termius/terminal-benchmark-1c027e78be41/evidence/tests_present.txt"
    }
  ],
  "finalized_at": "2026-07-08T23:45:18.750577Z",
  "id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
  "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
  "package_uri": "local://termius/terminal-benchmark-1c027e78be41/submission.zip",
  "status": "submitted",
  "submitted_at": "2026-07-08T23:45:18.127472Z",
  "summary": "Terminal Benchmark terminal-benchmark-1c027e78be41 packet built from live submission requirements.",
  "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
  "version": 1,
  "worker_attestation": "<redacted-large-string sha256:cc6f114774078918553f5b2f5c3cddc2c0d9a8cb997837becba1ea330e51a82c bytes:752 prefix:'I attest this submission is original_work, produced under human_accountability_f'>",
  "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
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
        "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 1327
      },
      {
        "artifact": "environment/.dockerignore",
        "hash": "sha256:cb2d67a46a111652f3bb388ee15d455eed7542905bdc61cd2a3c6d2fc23cc709",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 185
      },
      {
        "artifact": "rubric.md",
        "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 34
      },
      {
        "artifact": "task.toml",
        "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
        "notes": "Required by locked Terminal Benchmark project policy.",
        "size_bytes": 1562
      }
    ],
    "artifact_manifest_hash": "sha256:69c050a6f5042e96d4775d666722bc5f5f231a64052e4e37ebee8c978df36eb6",
    "attempt_number": 1,
    "audit_event_id": "b79137c1-398e-4826-9147-9179aa07eb00",
    "blocking_count": 0,
    "completed_at": "2026-07-08T23:45:18.864215Z",
    "created_at": "2026-07-08T23:45:18.592353Z",
    "failed_count": 0,
    "id": "d7885348-fd08-4820-b209-36a704765a2b",
    "is_current_for_submission": true,
    "locked_guide_version": "v1",
    "locked_payment_policy_version": "v1",
    "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
    "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
    "locked_post_submit_checker_policy_version": "v1",
    "locked_review_policy_version": "v1",
    "locked_revision_policy_version": "v1",
    "outcome_source": "none",
    "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
    "passed_count": 8,
    "queued_at": "2026-07-08T23:45:18.592353Z",
    "results": [
      {
        "blocks_review": false,
        "checker_name": "check_submission_packet",
        "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "881d313f-729e-442b-9d2a-9e7b41ced497",
        "message": "Submission packet contains required fields.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
        "worker_evidence_refs": [],
        "worker_message": "Submission packet contains required fields.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_policy_context_present",
        "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "5e9e4ea6-b300-4860-b543-4539c227f755",
        "message": "Submission has locked guide and policy context.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
        "worker_evidence_refs": [],
        "worker_message": "Submission has locked guide and policy context.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_evidence_present",
        "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "981f41b2-59b3-4a4d-b9b3-a368719de2a5",
        "message": "Submission includes required evidence references.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
        "worker_evidence_refs": [],
        "worker_message": "Submission includes required evidence references.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_evidence_integrity",
        "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "95dda22a-9486-4e2f-9ada-1ff6def7c0cc",
        "message": "Artifact manifest and evidence references are structurally valid.",
        "metadata": {
          "artifact_count": 4,
          "artifact_manifest_hash": "sha256:69c050a6f5042e96d4775d666722bc5f5f231a64052e4e37ebee8c978df36eb6"
        },
        "severity": "info",
        "status": "passed",
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
        "worker_evidence_refs": [],
        "worker_message": "Artifact manifest and evidence references are structurally valid.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_required_files",
        "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "e5d0538a-79c2-40a7-90c5-56ef67538dd2",
        "message": "Submission includes required artifact files.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
        "worker_evidence_refs": [],
        "worker_message": "Submission includes required artifact files.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_forbidden_files",
        "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "183eeb53-03f2-4c7d-8f9c-9b4544241bd2",
        "message": "Submission does not include default forbidden paths.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
        "worker_evidence_refs": [],
        "worker_message": "Submission does not include default forbidden paths.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_confidentiality_attestation",
        "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "ec9e8111-1128-4a34-a576-27afb8d5f664",
        "message": "Submission includes the required confidentiality attestation.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
        "worker_evidence_refs": [],
        "worker_message": "Submission includes the required confidentiality attestation.",
        "worker_visible": true
      },
      {
        "blocks_review": false,
        "checker_name": "check_low_quality_generated_artifacts",
        "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
        "created_at": "2026-07-08T23:45:18.592353Z",
        "id": "024d7ea5-69f8-4c68-a457-b0c24c8c4eca",
        "message": "Submission does not contain obvious generated-output placeholder signals.",
        "metadata": {},
        "severity": "info",
        "status": "passed",
        "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
        "worker_evidence_refs": [],
        "worker_message": "Submission does not contain obvious generated-output placeholder signals.",
        "worker_visible": true
      }
    ],
    "routing_recommendation": "allow_review",
    "started_at": "2026-07-08T23:45:18.864215Z",
    "status": "completed",
    "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
    "submission_version": 1,
    "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
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
      "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1327
    },
    {
      "artifact": "environment/.dockerignore",
      "hash": "sha256:cb2d67a46a111652f3bb388ee15d455eed7542905bdc61cd2a3c6d2fc23cc709",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 185
    },
    {
      "artifact": "rubric.md",
      "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 34
    },
    {
      "artifact": "task.toml",
      "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
      "notes": "Required by locked Terminal Benchmark project policy.",
      "size_bytes": 1562
    }
  ],
  "artifact_manifest_hash": "sha256:69c050a6f5042e96d4775d666722bc5f5f231a64052e4e37ebee8c978df36eb6",
  "attempt_number": 1,
  "audit_event_id": "b79137c1-398e-4826-9147-9179aa07eb00",
  "blocking_count": 0,
  "completed_at": "2026-07-08T23:45:18.864215Z",
  "created_at": "2026-07-08T23:45:18.592353Z",
  "failed_count": 0,
  "id": "d7885348-fd08-4820-b209-36a704765a2b",
  "is_current_for_submission": true,
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
  "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
  "locked_post_submit_checker_policy_version": "v1",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "outcome_source": "none",
  "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
  "passed_count": 8,
  "queued_at": "2026-07-08T23:45:18.592353Z",
  "results": [
    {
      "blocks_review": false,
      "checker_name": "check_submission_packet",
      "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "881d313f-729e-442b-9d2a-9e7b41ced497",
      "message": "Submission packet contains required fields.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "worker_evidence_refs": [],
      "worker_message": "Submission packet contains required fields.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_policy_context_present",
      "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "5e9e4ea6-b300-4860-b543-4539c227f755",
      "message": "Submission has locked guide and policy context.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "worker_evidence_refs": [],
      "worker_message": "Submission has locked guide and policy context.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_evidence_present",
      "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "981f41b2-59b3-4a4d-b9b3-a368719de2a5",
      "message": "Submission includes required evidence references.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes required evidence references.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_evidence_integrity",
      "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "95dda22a-9486-4e2f-9ada-1ff6def7c0cc",
      "message": "Artifact manifest and evidence references are structurally valid.",
      "metadata": {
        "artifact_count": 4,
        "artifact_manifest_hash": "sha256:69c050a6f5042e96d4775d666722bc5f5f231a64052e4e37ebee8c978df36eb6"
      },
      "severity": "info",
      "status": "passed",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "worker_evidence_refs": [],
      "worker_message": "Artifact manifest and evidence references are structurally valid.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_required_files",
      "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "e5d0538a-79c2-40a7-90c5-56ef67538dd2",
      "message": "Submission includes required artifact files.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes required artifact files.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_forbidden_files",
      "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "183eeb53-03f2-4c7d-8f9c-9b4544241bd2",
      "message": "Submission does not include default forbidden paths.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "worker_evidence_refs": [],
      "worker_message": "Submission does not include default forbidden paths.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_confidentiality_attestation",
      "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "ec9e8111-1128-4a34-a576-27afb8d5f664",
      "message": "Submission includes the required confidentiality attestation.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "worker_evidence_refs": [],
      "worker_message": "Submission includes the required confidentiality attestation.",
      "worker_visible": true
    },
    {
      "blocks_review": false,
      "checker_name": "check_low_quality_generated_artifacts",
      "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
      "created_at": "2026-07-08T23:45:18.592353Z",
      "id": "024d7ea5-69f8-4c68-a457-b0c24c8c4eca",
      "message": "Submission does not contain obvious generated-output placeholder signals.",
      "metadata": {},
      "severity": "info",
      "status": "passed",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "worker_evidence_refs": [],
      "worker_message": "Submission does not contain obvious generated-output placeholder signals.",
      "worker_visible": true
    }
  ],
  "routing_recommendation": "allow_review",
  "started_at": "2026-07-08T23:45:18.864215Z",
  "status": "completed",
  "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
  "submission_version": 1,
  "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
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
    "actor_id": "5080787a-cb3b-591d-9948-6b38354788ab",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:03.452947Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
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
    "external_subject": "terminal-benchmark-manager-ws16-clean-cb1540ba",
    "from_status": null,
    "id": "3c645ce6-9cf1-498c-bff2-b5a53e481c3d",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "draft"
  },
  {
    "actor_id": "5080787a-cb3b-591d-9948-6b38354788ab",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:03.630101Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-ws16-clean-cb1540ba",
    "from_status": "draft",
    "id": "43563128-a38c-41ef-baad-f4a5ea77e153",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API screening; lock active guide and policy context.",
    "to_status": "screening"
  },
  {
    "actor_id": "5080787a-cb3b-591d-9948-6b38354788ab",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.041939Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-ws16-clean-cb1540ba",
    "from_status": "screening",
    "id": "b8264b10-3383-4138-ab3b-6071850aaff9",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API ready for worker claim.",
    "to_status": "ready"
  },
  {
    "actor_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.503583Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
      "assignment_id": "47f47a44-cd98-41e6-859e-86ac232cd83b",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-ws16-clean-cb1540ba",
    "from_status": "ready",
    "id": "b5a3091c-8506-41fe-800c-58dd1aadfb8a",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API worker claim.",
    "to_status": "claimed"
  },
  {
    "actor_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:44:04.727342Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
      "assignment_id": "47f47a44-cd98-41e6-859e-86ac232cd83b",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "operator_override": false,
      "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
    },
    "event_type": "task_status_changed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-ws16-clean-cb1540ba",
    "from_status": "claimed",
    "id": "3f3f1439-662a-4c42-b2bf-6e5543489d46",
    "is_dev_auth": false,
    "reason": "Terminal Benchmark final clean live API worker started work.",
    "to_status": "in_progress"
  },
  {
    "actor_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:17.452515Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "assigned_to": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
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
        "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3"
      }
    },
    "event_type": "pre_submission_check_failed",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-ws16-clean-cb1540ba",
    "from_status": "in_progress",
    "id": "aaeaf9c7-4482-4bdf-956f-075f539175eb",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "in_progress"
  },
  {
    "actor_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
    "actor_roles": [
      "worker"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:18.127472Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "artifact_hash_manifest": [
        {
          "artifact": "environment/Dockerfile",
          "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": 1327
        },
        {
          "artifact": "environment/.dockerignore",
          "hash": "sha256:cb2d67a46a111652f3bb388ee15d455eed7542905bdc61cd2a3c6d2fc23cc709",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": 185
        },
        {
          "artifact": "rubric.md",
          "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": 34
        },
        {
          "artifact": "task.toml",
          "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": 1562
        }
      ],
      "assigned_to": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
      "finalized_at": null,
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "submission_version": 1,
      "supersedes_submission_id": null,
      "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
    },
    "event_type": "submission_created",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-worker-ws16-clean-cb1540ba",
    "from_status": "in_progress",
    "id": "6eb6b53f-01c1-421b-806c-2a9e23b2117a",
    "is_dev_auth": false,
    "reason": null,
    "to_status": "submitted"
  },
  {
    "actor_id": "5080787a-cb3b-591d-9948-6b38354788ab",
    "actor_roles": [
      "project_manager"
    ],
    "auth_source": "flow",
    "claim_snapshot": {},
    "created_at": "2026-07-08T23:45:18.592353Z",
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "artifact_hash_manifest": [
        {
          "artifact": "environment/Dockerfile",
          "hash": "sha256:c91a62df2e7075d06fa53255f331f19559d301549201ae693ae3a465891087fa",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": 1327
        },
        {
          "artifact": "environment/.dockerignore",
          "hash": "sha256:cb2d67a46a111652f3bb388ee15d455eed7542905bdc61cd2a3c6d2fc23cc709",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": 185
        },
        {
          "artifact": "rubric.md",
          "hash": "sha256:4786d11876205560bb85de2ab09b333645b714c43d6f46bee27ef6b0b410816e",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": 34
        },
        {
          "artifact": "task.toml",
          "hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
          "notes": "Required by locked Terminal Benchmark project policy.",
          "size_bytes": 1562
        }
      ],
      "assigned_to": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
      "finalized_at": "2026-07-08T23:45:18.750577+00:00",
      "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
      "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
      "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
      "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
      "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "package_hash": "sha256:24297fe175abfa9998d0195e0a990e9e9557e8b361afb1fd0680c0e9d41889fd",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "submission_version": 1,
      "supersedes_submission_id": null,
      "worker_id": "d0c5c1f3-7689-5965-bba3-975bbac3c815"
    },
    "event_type": "submission_finalized",
    "external_issuer": "https://auth.flow.local/e2e",
    "external_subject": "terminal-benchmark-manager-ws16-clean-cb1540ba",
    "from_status": "submitted",
    "id": "a6843c8e-dc22-45db-9fd2-de16877fde01",
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
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "requester_actor_id": "5080787a-cb3b-591d-9948-6b38354788ab",
      "requester_auth_source": "flow",
      "requester_external_issuer": "https://auth.flow.local/e2e",
      "requester_external_subject": "terminal-benchmark-manager-ws16-clean-cb1540ba",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "submission_version": 1,
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "trigger_source": "submission_finalized"
    },
    "event_type": "pre_review_gate_started",
    "external_issuer": "workstream",
    "external_subject": "workstream-system:pre-review-gate",
    "from_status": "submitted",
    "id": "f6d7a015-51cd-4419-9b3b-c502a10681bc",
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
    "entity_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
    "entity_type": "task",
    "event_payload": {
      "blocking_count": 0,
      "checker_run_id": "d7885348-fd08-4820-b209-36a704765a2b",
      "failed_count": 0,
      "locked_guide_version": "v1",
      "locked_payment_policy_version": "v1",
      "locked_post_submit_checker_policy_hash": "sha256:e2730e8ecea2eca2d8dce218ba1548f7c675d801045b58e1f211df3a35bdc41d",
      "locked_post_submit_checker_policy_id": "30095d84-e5c5-46e3-a292-3788bd34699f",
      "locked_post_submit_checker_policy_version": "v1",
      "locked_review_policy_version": "v1",
      "locked_revision_policy_version": "v1",
      "outcome_source": "none",
      "requester_actor_id": "5080787a-cb3b-591d-9948-6b38354788ab",
      "requester_auth_source": "flow",
      "requester_external_issuer": "https://auth.flow.local/e2e",
      "requester_external_subject": "terminal-benchmark-manager-ws16-clean-cb1540ba",
      "review_decision_id": null,
      "routing_recommendation": "allow_review",
      "submission_id": "ba25f15a-e36a-4925-9891-09d394eae2ec",
      "submission_version": 1,
      "task_id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
      "trigger_source": "submission_finalized",
      "warning_count": 0
    },
    "event_type": "pre_review_gate_passed",
    "external_issuer": "workstream",
    "external_subject": "workstream-system:pre-review-gate",
    "from_status": "evaluation_pending",
    "id": "fef7e1c4-78b8-4c4e-a740-bbdcb046c2ae",
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
  "assigned_to": "d0c5c1f3-7689-5965-bba3-975bbac3c815",
  "base_amount": "25.00",
  "created_at": "2026-07-08T23:44:03.452947Z",
  "created_by": "5080787a-cb3b-591d-9948-6b38354788ab",
  "currency": "USD",
  "description": "Real Terminal Benchmark reviewer fixture with 3 milestones, languages=['rust', 'json'], category=software-engineering.",
  "difficulty": "medium",
  "estimated_time_minutes": 75,
  "external_task_id": "terminal-benchmark-1c027e78be41",
  "id": "d8cfda33-6c7e-461a-bdcd-036a6cefeda3",
  "locked_effective_project_submission_artifact_policy_hash": "sha256:5595f7aa03a671ff81decf94e0a2edd18189391c7524b0367277f177a0b01850",
  "locked_effective_project_submission_artifact_policy_id": "40acb2dd-b1a4-4a8f-90cf-038e6b5941e3",
  "locked_guide_source_snapshot_hash": "sha256:9843f69ef5b7f7631f98a61dcd0a5be4c592be597fc859d9e5ac8142bdf606fb",
  "locked_guide_source_snapshot_id": "2b6592db-ae88-4fd8-b9d0-c16bd9dbf09b",
  "locked_guide_version": "v1",
  "locked_payment_policy_version": "v1",
  "locked_pre_submit_checker_bundle_hash": "sha256:aa7bb902a63cb031a809533cf1939e1fc1dc47f3834aead923c9679e0302aa63",
  "locked_pre_submit_checker_policy_id": "f9b527da-6831-40d5-b834-b3fb3a6471fe",
  "locked_review_policy_version": "v1",
  "locked_revision_policy_version": "v1",
  "payout_type": "fixed",
  "project_id": "36331e8e-c849-484d-9e9e-c8ebc2f70130",
  "rejection_criteria": "Missing required artifacts, evidence, hashes, or attestation blocks submission intake.",
  "skill_tags": [
    "rust",
    "json",
    "seccomp",
    "containers",
    "cli"
  ],
  "source_payload_hash": "sha256:4a464edbf1b9047733412e228af0755227f2e44440125761c094324cff3a3811",
  "source_ref": "terminal-benchmark/terminal-benchmark-1c027e78be41/live-api/ws16-clean-cb1540ba",
  "source_type": "manual",
  "status": "review_pending",
  "task_type": "terminal_benchmark",
  "title": "Terminal Benchmark terminal-benchmark-1c027e78be41 live-api",
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
