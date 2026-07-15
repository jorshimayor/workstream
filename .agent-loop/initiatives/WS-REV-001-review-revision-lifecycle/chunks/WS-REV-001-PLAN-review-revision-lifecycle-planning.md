# Chunk Contract: WS-REV-001-PLAN

## Goal

Reconcile the revised WS-REV source with the current repository and produce a
reviewed end-to-end initiative plan without changing runtime behavior.

## Risk class

L0 planning with L1 downstream implications.

## Allowed files

```text
.agent-loop/initiatives/WS-REV-001-review-revision-lifecycle/**
.agent-loop/merge-intents/WS-REV-001-PLAN.json
docs/reference_specs/WS-REV-001-review-lifecycle-specification.md
docs/reference_specs/WS-REV-001-review-lifecycle-specification.pdf
docs/reference_specs/README.md only for exact canonical WS-REV provenance/hash rows and directly associated provenance/checksum prose
docs/reference_specs/SHA256SUMS only for exact canonical WS-REV hash rows
.gitattributes only for the canonical byte-immutable WS-REV Markdown whitespace classification
```

## Not allowed

```text
backend/**
docs/reference_specs/** except the four exact canonical-reference repairs above
docs active product/architecture/operations files
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
runtime implementation or dependency changes
```

## Acceptance criteria

- Revised Markdown and PDF are read end to end; heading/token parity and their
  non-identical status wording are recorded without claiming byte-derived
  semantic equivalence.
- The supplied revised Markdown/PDF contents live at the canonical WS-REV
  filenames, their hashes match README/SHA256SUMS, and no duplicate `(2)` path
  remains.
- Git classifies the canonical revised Markdown's supplied hard-break trailing
  spaces path-specifically; no global whitespace rule is weakened.
- Current task, submission, checker, auth, artifact, contribution, audit,
  worker, API, migration, test, and documentation boundaries are cited.
- Observations, decisions, risks, unknowns, and dependencies are separated.
- Every proposed chunk has scope, exclusions, testable criteria, risk,
  verification, reviewers, and human focus.
- Specification sections 25.1-25.9 have an executable conformance matrix.
- First implementation chunk remains proposed and inactive.
- Exactly one merge intent names WS-REV-001-01 as the successor and requires a
  separate explicit start; it does not activate that chunk.

## Verification

```text
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
sha256sum -c docs/reference_specs/SHA256SUMS
git diff --check
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
and reuse/dedup.

## Human review focus

Archival provenance, provider correction, revision-limit behavior, controlled
rebase, server-selected review offers, cross-initiative gates, and coherent
production activation only after recovery/operations/live proof.

## Stop condition

Present the plan and wait for explicit human approval. Do not start 01.
