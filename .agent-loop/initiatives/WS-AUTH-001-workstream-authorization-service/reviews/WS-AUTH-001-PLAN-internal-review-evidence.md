# Internal Review Evidence: WS-AUTH-001-PLAN

## Chunk

`WS-AUTH-001-PLAN` - Workstream Authorization Service Planning

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: d5b0ca96cc8010ae136eb5a3295248cd04197d2f

Reviewed at: 2026-07-11T13:15:59Z

Reviewer run IDs: senior-engineering=/root/final_senior_review; QA/test=/root/final_qa_review; security/auth=/root/final_security_review; product/ops=/root/final_product_review; architecture=/root/final_arch_review; docs=/root/final_docs_review; CI-integrity=/root/final_ci_review; reuse/dedup=/root/final_reuse_review; test-delta=/root/final_test_delta_review

## Reviewed Change

Scope:

- Imported and SHA-256 bound eight user-supplied Workstream reference files as
  immutable archival planning inputs with an adjacent precedence marker.
- Adopted WS-AUTH-001 as the target authorization source while preserving the
  external Flow authentication boundary and canonical `/api/v1` namespace.
- Added intent, discovery, decisions, risks, plan, source manifest, status,
  chunk map, and 16 bounded implementation chunk contracts.
- Defined fail-closed issuer verification, legacy actor classification,
  canonical actor/link migration, local grants, permission evaluation,
  authority evidence, revocation, bootstrap safety, and product cutovers.
- Preserved intermediate-release intake operability and revision obligations,
  assigned every temporary compatibility consumer and deletion owner, and
  prohibited test/CI/dependency bypasses.
- Paused `WS-POL-002-03` and left every implementation chunk inactive.
- Recorded D1-D3 as user-approved L0 direction and D4-D10 as an explicit human
  approval gate before `WS-AUTH-001-01` activation.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Confirmed policy ownership, L0/L1 boundary, bootstrap locking, metrics ownership, and worker registration. |
| QA/test | PASS AFTER FIXES | None | Confirmed fresh-database compatibility, grant cutover, contributor reads, revision proof, and complete cleanup sequencing. |
| security/auth | PASS AFTER FIXES | None | Confirmed bootstrap serialization, append-only evidence, introspection/JWKS transport, privacy, and denial proof. |
| product/ops | PASS AFTER FIXES | None | Confirmed contributor discovery, Operator/Audit reads, and durable needs-revision replacement behavior. |
| architecture | PASS AFTER FIXES | None | Confirmed service/repository boundaries, intermediate operability, feature persistence ownership, and atomic compatibility removal. |
| docs | PASS AFTER FIXES | None | Confirmed archival/canonical labeling and active-document reconciliation ownership. |
| CI integrity | PASS | None | No gate weakening; migrations, dependency approvals, scanners, commands, and post-review closure are explicit. |
| reuse/dedup | PASS AFTER FIXES | None | Existing verifier, audit, repositories, AsyncSession, and Celery registry are reused; no stranded compatibility code remains. |
| test delta | PASS | None | No tests changed; the plan forbids deletion, skip/xfail, assertion weakening, or authorization-fixture bypass. |

## Valid Findings Addressed

- Added `AuthorityControl(id=1) FOR UPDATE` to one-time bootstrap and exact
  different-target concurrency proof.
- Made audit evidence append-only, denial evidence owner-local, and
  idempotency/rate controls feature-owned behind repositories/services.
- Specified safe HTTPS, redirect, response-bound, logging, and client-separation
  rules for JWKS and token introspection.
- Corrected `ResourceContext` composition to application services/resource
  loaders rather than persistence repositories.
- Distinguished human-approved L0 direction from pending D4-D10 choices and L1
  implementation chunks.
- Preserved fresh-database intake through a bounded workflow-eligibility
  compatibility path until exact-project grants replace it; chunk 14 removes
  the final consumer, activation surface, adapter, and allowlist atomically.
- Added contributor candidate lookup and exact-project contributor project
  reads with pre-filtered pagination and minimal disclosure.
- Added Operator/Audit task, submission, checker, and evidence projections with
  read-only, redaction, concealment, and mutation-denial proof.
- Kept revoked needs-revision work in a durable revision obligation and required
  replacement-context, supersession, high/medium replay, rollback, and retry
  proof at submission time.
- Reused the existing Celery include list for durable reconciliation.
- Added adjacent archival input labeling and complete active-doc/scanner
  ownership for the baseline adoption chunk.

## Commands Run

```bash
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/check_loop_memory_state.py
python3 scripts/test_agent_gates.py
sha256sum -c docs/reference_specs/SHA256SUMS
git diff --check
```

Results:

- Stale wording: passed.
- Markdown links: passed for 34 changed Markdown files before evidence creation.
- Loop memory: passed.
- Agent gate regression suite: 26 passed.
- All eight imported-file hashes: passed.
- `git diff --check`: passed.

## Remaining Risks

- D4-D10 still require explicit durable human approval before implementation.
- Production issuer/JWKS/introspection values and production legacy actor
  classifications remain future implementation/live-proof inputs.
- Each L1 chunk must prove its own migration, concurrency, authorization,
  compatibility-shrinkage, and full regression requirements; this planning
  evidence is not implementation proof.

## Stop Condition

No implementation chunk is active. Do not activate `WS-AUTH-001-01` without
explicit human approval of D4-D10 and a separate implementation start signal.
Do not resume `WS-POL-002-03` while authorization remains the priority.
