# WS-ART-001-07: Recovery And Real API Proof

Parent: `WS-ART-001` | Repository: Workstream | Risk: L1 | SLA: P1

Dependency: all earlier WS-ART chunks and required WS-AUTH cutovers.

## Goal

Prove a clean-checkout local stack, adapter parity, exact-byte pre/post binding,
operator recovery, and privacy-safe evidence through supported APIs.

## Allowed Files

- Workstream Dockerfile/Compose/runtime config and health checks
- artifact status/reconciliation APIs under existing registered permissions
- deterministic storage drill and professional redacted report
- focused operations/README/CI changes and tests

## Not Allowed

No semantic search, review decisions, contribution/payment/reputation,
production fault controls, direct DB edits, production OpenAI key requirement,
or provider totals/private paths in evidence.

## Acceptance Criteria

- Clean checkout starts Postgres, Redis, Workstream API, Celery, and pinned
  focused Flow Node with health checks and migrations.
- Local test issuer and deterministic setup fixture need no production secret.
- Real APIs prove guide capture, task upload/seal/admission, failed pre-submit
  no-side-effect, successful submission, post-submit exact artifact-set match,
  log/output bindings, and operator status/retry.
- Stop/restart Flow Node proves 503/retry/evaluation_pending/recovery behavior.
- Crash-after-provider-success proof covers both persisted-commitment recovery
  and no-commitment `replay_required` recovery, proves receipt-only acceptance
  is impossible, and creates no second provider object.
- Test-only corruption/retain-refusal controls prove quarantine without
  contributor blame or downstream review/contribution/payment/reputation.
- A production-image route audit proves crash/corruption/retain-refusal test
  controls are not compiled or routed in the production target.
- Polling deadlines, API row-count invariants, request/response summaries, and
  redacted identifiers/hashes are in the report.

## Verification

```bash
docker compose down -v --remove-orphans
docker compose up -d --build --wait --wait-timeout 180 postgres redis flow-node api celery-worker
docker compose ps
docker compose exec -T api python scripts/artifact_flow_live_api_drill.py --phase healthy
docker compose exec -T api python scripts/artifact_flow_live_api_drill.py --phase crash-window
docker compose exec -T api python scripts/artifact_flow_live_api_drill.py --phase integrity-faults
docker compose stop flow-node
docker compose exec -T api python scripts/artifact_flow_live_api_drill.py --phase provider-down
docker compose start flow-node
docker compose exec -T api python scripts/artifact_flow_live_api_drill.py --phase recovery
docker compose run --rm flow-node-production-route-audit
docker compose exec -T api ruff check app tests scripts
docker compose exec -T api docstr-coverage --config .docstr.yaml
docker compose exec -T api pytest -q
docker compose exec -T api python scripts/api_contract_e2e.py
python3 scripts/test_agent_gates.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/check_loop_memory_state.py
python3 scripts/check_internal_review_evidence.py
git diff --check
docker compose down -v
```

Reviewers: all required tracks.

Human focus: reproducibility, fault ownership, no hidden DB/script shortcut,
privacy, and whether the report proves exact bytes end to end. Stop after this
PR; do not start checker/review feature work automatically.
