# Chunk Contract: WS-ART-001 Object Storage Planning Amendment

Initiative: `WS-ART-001` | Risk: L1 | Status: Active planning only

## Goal

Replace the deferred Flow Node-first v0.1 plan with one provider-neutral object-storage
contract using AWS S3 as the only production provider, MinIO for local/CI
protocol proof, LocalStorage for focused development, and separately deferred
R2 and Flow Node adapter plans. It also records the user's separately explicit
repository-wide external-service adapter convention while leaving every
non-artifact capability migration to its own initiative. This chunk changes
planning and guardrails only.

## Allowed Files

- `AGENTS.md`, `README.md`, and artifact-related active architecture/spec/ADR/
  glossary/template documentation;
- `docs/decision_0014_external_service_adapter_convention.md` for the explicitly
  approved repository-wide adapter/factory convention only;
- `.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/` planning,
  chunk contracts, decisions, risks, status, and planning review evidence;
- `.agent-loop/initiatives/FN-ART-002-deferred-flow-node-artifact-store/`;
- `docs/spec_authorization_service.md` and
  `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/`
  `DECISIONS.md`, `STATUS.md`, `CHUNK_MAP.md`, and proposed WS-AUTH contracts
  `07`, `08`, `09`, `11`, `14`, and `15` only to register and map the exact
  artifact permissions that later WS-ART chunks consume;
- `.agent-loop/MEMORY.md`, `.agent-loop/LOOP_STATE.md`,
  `.agent-loop/WORK_QUEUE.md`, `.agent-loop/REVIEW_LOG.md`, and
  `.agent-loop/policies/engineering-review-policy.md` only where the planning
  contract requires durable state or clarification;
- `scripts/check_stale_artifact_contracts.py`,
  `scripts/agent-gate-requirements.txt`, focused gate tests, and exact
  Agent Gates/backend coverage workflow controls.

## Not Allowed

- backend application, migration, product dependency, Compose service, or
  product-runtime workflow implementation;
- active ArtifactStore, LocalStorage, S3, MinIO, Flow Node, Celery, API,
  authorization, guide, task, submission, checker, or review behavior changes;
- backward-compatibility aliases, dual providers, runtime fallbacks, or product
  role/decision changes;
- implementation of any proposed chunk.

## Acceptance Criteria

- AWS S3 is the only v0.1 production provider behind
  `S3CompatibleArtifactStore`; MinIO is local/CI protocol proof and LocalStorage
  is not production eligible;
- every untrusted byte source is server-hashed before provider I/O and the v2
  port accepts only a sealed `CommittedArtifactSource`;
- R2 has no active credential, runtime, deployment, or implementation contract;
- deferred Flow Node is fully planned but absent from the v0.1 dependency graph;
- active v0.1 implementation is split into reviewable L1 chunks with exact
  scope, acceptance criteria, runnable commands, 90 percent changed-subsystem
  coverage, and the 78 percent repository floor; deferred Flow Node commands
  remain placeholders until mandatory discovery activates that initiative;
- active-doc stale checks are discovery-based and historical evidence/reference
  paths are explicitly excluded;
- no application/runtime files differ from the planning chunk base.

## Verification

```bash
git diff --check origin/main...HEAD
python3 scripts/check_markdown_links.py --changed-only origin/main...HEAD
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/test_agent_gates.py
git diff --name-only origin/main...HEAD -- backend/app backend/alembic backend/pyproject.toml docker-compose.yml
```

The final command must print no paths.

## Required Reviewers

Senior engineering, architecture, QA/test, security/auth, product/ops,
reuse/dedup, CI integrity, test delta, and docs.

## Human Review Focus

- Is object storage simpler than operating Flow Node while preserving future
  portability?
- Is AWS S3 production-ready without coupling product services to its adapter?
- Are implementation chunks narrow enough to review and stop independently?
