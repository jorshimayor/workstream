# Internal Review Evidence: WS-AUTH-001-01

## Chunk

`WS-AUTH-001-01` - Adopt Authorization Baseline And Repository Contracts

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: 6756e6cb397da5f813eca39fb738633bc24f2ab2

Reviewed at: 2026-07-11T17:43:32Z

Reviewer run IDs: senior-engineering=/root/auth01_plan_engineering; QA/test=/root/auth01_plan_quality_ci; security/auth=/root/auth01_plan_security_product; product/ops=/root/auth01_plan_security_product; architecture=/root/auth01_plan_engineering; docs=/root/auth01_plan_security_product; CI-integrity=/root/auth01_plan_quality_ci; reuse/dedup=/root/auth01_plan_engineering; test-delta=/root/auth01_plan_quality_ci

## Reviewed Change

- Adopted ADR 0012 and the canonical authorization specification/runbook.
- Preserved external Flow authentication ownership while assigning local
  actors, grants, permissions, guards, idempotency, invalidation, and evidence
  to Workstream modules.
- Standardized five administrative grants, three exact-project contributor
  grants, `/api/v1`, system-only Operator scope, and registered recovery
  permissions.
- Reconciled active architecture, operations, product-flow, template, diagram,
  roadmap, and durable-memory documents.
- Added an active-document scanner, direct fail-closed Agent Gates invocation,
  independent regression fixtures, and a pinned local diagram renderer.
- Kept all eight imported reference inputs and their checksum/manifest records
  byte-immutable.
- Incorporated PR #90 correction and activation semantics without importing or
  claiming its backend implementation.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS WITH LOW RISKS | None | Large atomic docs adoption is justified; scanner is simpler after removing natural-language negation parsing. |
| QA/test | PASS | None | All supplied token-role/profile authority bypasses fail closed; 31 independent gate tests pass. |
| security/auth | PASS | None | External identity verification and local product authorization are separated; grants and recovery remain scoped. |
| product/ops | PASS | None | Worker/submitter, review-decision, correction, activation, and chunk-gating behavior remain correct. |
| architecture | PASS | None | No backend, schema, migration, dependency, frontend, or immutable-source boundary drift. |
| docs | PASS | None | Canonical/archival precedence, active corpus, diagrams, runbook, and lifecycle memory are consistent. |
| CI integrity | PASS | None | Scanner invocation is direct and fail closed; no workflow step or threshold was weakened. |
| reuse/dedup | PASS WITH LOW RISKS | None | Existing gate, discovery, rendering, and test conventions are reused without a new framework. |
| test delta | PASS | None | Existing tests remain; independent fixtures cover every rule and all reviewer-supplied bypasses. |

## Valid Findings Addressed

- Restored source-compatible system-only Operator scope and
  `actor.profile.read_any`.
- Explicitly approved the eight changed diagram source/generated paths.
- Reconciled durable memory so PR #90 owns chunk 03 and chunk 04 remains
  inactive.
- Replaced a whole-file archive-marker exclusion with one exact line/rule
  exemption.
- Replaced self-derived scanner examples with independent fixtures.
- Expanded ordinary token-role, named-role-token, typed-profile, and generic
  admin authority detection.
- Removed attempted natural-language negation interpretation after adversarial
  review proved it ambiguous. Authority-shaped token/profile statements now
  fail closed regardless of negation; canonical docs state local-grant
  authority directly.
- Added a renderer that pins PlantUML 1.2026.6 by SHA-256, strips PNG metadata,
  fixes the source epoch/PDF identifier, and writes only approved artifacts.

## Commands Run

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/test_agent_gates.py
python3 scripts/check_loop_memory_state.py
python3 -m py_compile scripts/check_stale_authorization_docs.py scripts/test_agent_gates.py
bash -n scripts/render_authorization_docs.sh
sha256sum -c docs/reference_specs/SHA256SUMS
PLANTUML_JAR=/tmp/workstream-plantuml.jar scripts/render_authorization_docs.sh
sha256sum -c /tmp/auth-artifacts.sha
git diff --check
```

Results: all passed. The repeated local render produced stable hashes for both
SVGs, all three PNGs, and the architecture brief PDF.

## Evidence Gate

Evidence gate: PASS

Scope exception: 58 files and more than 500 changed lines are accepted because
this is one approved atomic active-document reconciliation plus its scanner,
tests, CI step, and generated companions. Splitting would leave contradictory
canonical authority documentation. No runtime or dependency boundary is mixed
in.

## Remaining Risks

- PlantUML is pinned; Java, ImageMagick, Pandoc, WeasyPrint, and fonts remain
  environment-provided, so cross-host rendering is not fully hermetic.
- Production issuer/JWKS/introspection configuration and legacy actor
  classification remain future chunk inputs.
- This chunk specifies authorization; it does not implement runtime authority.

## Stop Condition

Stop after PR publication for human review. Do not start `WS-AUTH-001-02` or
`WS-POL-002-04` automatically, and do not merge without explicit user approval.
