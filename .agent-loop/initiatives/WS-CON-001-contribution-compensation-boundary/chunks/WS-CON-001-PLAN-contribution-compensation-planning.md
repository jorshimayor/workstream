# Chunk Contract: WS-CON-001-PLAN - Contribution And Compensation Planning

## Parent initiative

`WS-CON-001` - Contribution Record And Compensation Boundary

## Goal

Reconcile the supplied WS-CON pair with current code and parallel AUTH/REV
contracts, then produce a human-reviewable initiative plan without implementing
runtime behavior.

## Why this chunk exists

The candidate spans architecture, permissions, payment, artifacts, lifecycle,
workers, APIs, and migrations and contains conflicts with accepted repository
decisions. Implementation cannot safely begin from the candidate alone.

## Approved plan reference

This chunk creates the parent `INTENT.md`, `DISCOVERY.md`, `PLAN.md`, and
`CHUNK_MAP.md`; no prior implementation plan exists.

## Risk class

L0 architecture/payment/authorization direction; P1 planning priority.

## Allowed files

```text
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
```

## Not allowed

```text
backend application, migrations, tests, workflows, dependencies
AUTH/ART/REV sibling worktree edits
reference-spec byte edits or archival replacement
active runtime documentation adoption
```

## Acceptance criteria

- [x] Candidate Markdown/PDF and original PDF are inventoried by hash/status.
- [x] Current code, tests, docs, AUTH catalogue, REV plan, and ART contract are
  cited concretely.
- [x] ActionIds and PermissionIds are separated and incorrect candidate IDs are
  rejected.
- [x] `/api/v1`, Submission identity, provider, artifact capability, payment
  model, outbox, and review integration conflicts are explicit.
- [x] Required initiative artifacts and bounded chunk contracts exist.
- [x] First implementation/spec chunk remains proposed until human approval.
- [x] Required plan reviewers complete and all valid findings are resolved or
  recorded for human decision.
- [x] AUTH-07B refresh records the two-active/48-planned runtime, separates AUTH
  registration from post-feature AUTH activation, adds the prepared `T`
  protocol and absent upstream `task.claim` gate, and receives fresh required
  review/evidence against current trusted main.

## Verification commands

```bash
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
git diff --check
sha256sum docs/reference_specs/*
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
and reuse/dedup. CI integrity and test-delta are N/A because this chunk changes
only planning Markdown and no CI/tests.

## Human review focus

Review unresolved D1/D4/D7/D8/D10, confirm accepted D3/D5/D6/D9 and approved D2,
and assess D2's unresolved legacy-row handling rule, exact authorization
dependencies, artifact boundary, cross-initiative gates, and whether every
runtime chunk is independently reviewable.

## Stop conditions

Stop after presenting the reviewed plan. Do not start `WS-CON-001-01` without
explicit human approval.
