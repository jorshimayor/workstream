# Chunk Contract: WS-XINT-001-PLAN Boundary Reconciliation

Initiative: `WS-XINT-001` | Risk: L1 | Status: Active after explicit user start

## Goal

Publish one planning-only source of truth for AUTH, ART, REV, and CON ownership,
activation custody, transaction order, and cross-initiative handoffs.

## Allowed files

- `.agent-loop/initiatives/WS-XINT-001-lifecycle-boundary-reconciliation/**`
- ART initiative plans, decisions, risks, chunk map, and future chunk contracts
  only where stale activation language must be corrected
- AUTH initiative/specification planning documents where stale feature-owned
  activation language must be corrected
- `scripts/check_stale_authorization_docs.py`,
  `scripts/check_stale_workstream_wording.py`, and
  `scripts/test_agent_gates.py` only for deterministic activation-custody and
  contribution/compensation wording enforcement
- `.agent-loop/WORK_QUEUE.md`, `.agent-loop/REVIEW_LOG.md`, and one merge intent
- `.agent-loop/LOOP_STATE.md` for exact parallel planning-state reconciliation
- directly related active architecture, product, operations, roadmap, template,
  and diagram documents under `docs/` only to reconcile the reviewer
  `completed_review`, submitter `accepted_submission`, and conditional
  compensation contract exposed by trusted-main reference specifications

## Not allowed

- backend, frontend, migration, workflow, provider, Celery, action-catalogue,
  grant, evaluator, service-actor, route, review, contribution, or payment code;
- action availability changes;
- edits in another agent's active worktree;
- implementation of any downstream handoff;
- a cross-initiative successor in merge intent.

## Acceptance criteria

- one canonical definition separates feature/resource owner from AUTH activation
  custodian;
- all 25 currently registered ART actions retain exact mappings and receive a
  proposed AUTH custody group;
- all seven fixed artifact service identities and exact assignments are listed;
- Operator retry remains independent from internal service actions;
- ART, REV, AUTH, and CON transaction/commit/audit ownership is explicit;
- ReviewPacketManifest and ReviewEvidenceArtifact remain REV semantic records
  backed by ART bindings/bytes through typed ports;
- review evidence binding has one exact proposed ActionId, existing PermissionId,
  fixed service identity, ART capability owner, and AUTH activation custodian;
- core ContributionRecord creation makes no ART capability/provider call while
  copying canonical `SubmissionVersion.artifact_hash` into
  `ContributionRecord.artifact_hash` lineage;
- every valid human Review creates one reviewer `completed_review`; `accept`
  additionally creates one submitter `accepted_submission`; compensation is
  independently evaluated from each frozen policy and may be explicitly unpaid;
- each parallel agent receives a bounded handoff and no runtime start signal;
- ART plans no longer claim that ART registers or activates authorization;
- Markdown links, stale wording, diff hygiene, and internal review pass.

## Verification

```bash
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_workstream_wording.py
git diff --check
```

The `rg` command must return no stale active-contract matches. Historical review
evidence is not rewritten.

## Required reviewers

Senior engineering, architecture, QA/test, security/auth, product/ops,
reuse/dedup, and docs.

## Human review focus

- Is AUTH the only activation custodian?
- Can each feature owner implement hidden behavior without an active action?
- Is the transaction order race-safe without mixing persistence ownership?
- Is core contribution creation correctly independent of ART?
- Can all four agents continue in parallel after merge without editing one
  another's runtime code?

## Stop conditions

Stop if a boundary requires runtime implementation, a new permission, an
unapproved service identity, dual activation ownership, or a direct repository
dependency. Stop after publishing the reviewed planning PR.
