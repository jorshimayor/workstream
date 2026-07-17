# WS-AUTH-001-09B Internal Review Evidence

Reviewed code SHA: `ebf65f525b01cc07e12c79bb08300bbb40b70db2`

Reviewed implementation SHA: `641b439ceb370ecc792322e33c73b6668c244290`

Reviewed against trusted main:
`a947b8693a97bdb94c9dc63202a51e197834d613`

Reviewed at: `2026-07-17T19:53:40Z`

Reviewer run IDs: `auth_xint_roles`, `auth_xint_art_service`,
`auth_xint_rev_con`

Reviewer tracks: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, and test delta

## Deterministic Evidence

- The catalogue contains 74 PermissionIds and 65 ActionIds: exactly 10 active
  and 55 planned. AUTH-09B activates only `actor.service.provision`; no ART,
  REV, CON, service-admission, grant, or assignment action becomes active.
- `POST /api/v1/service-actors` accepts one closed fixed service identity, one
  opaque subject, one bounded reason, and one UUID idempotency key. The issuer
  comes only from the configured `AuthVerifier.canonical_issuer()` port.
- Creation atomically commits one service ActorProfile, one unverified exact
  issuer/subject link, decision/success/invalidation evidence, and idempotency
  completion. Service `last_seen_at` and `last_verified_at` remain null.
- Service and other nonhuman tokens are denied inside the actor service before
  lookup, canonical resolution, or timestamp touch. AUTH-09E remains the only
  future service-token admission boundary.
- Independent-session behavior tests cover same-key replay and mismatch,
  fixed-identity and external-identity races, same pair with different keys,
  crossed grant revocation, rollback/retry, and deterministic conflict
  precedence without deadlock or partial state.
- Injected decision-evidence, success-evidence, invalidation-evidence,
  idempotency-completion, and commit failures return the stable retryable 503
  envelope and prove full rollback before successful retry.
- Privacy tests scan every response body, application log, and audit row and
  prove raw tokens, subjects, issuer, email, and reasons never escape. OpenAPI
  documents the strict request and explicit 409 response contracts.
- The broad actor/auth/authorization selection passed 236 tests. Actor legacy
  classification and migration tooling passed 109 tests. The focused API and
  OpenAPI selection passed 16 tests after current-main integration.
- The isolated real HTTP API contract drill passed through
  `scripts/run_isolated_tests.py` and cleaned up its derived database. The
  GitHub Backend workflow and an exact agent-gate regression prevent use of a
  persistent application database for that destructive drill.
- Branch-aware coverage is 92.74 percent for the actor boundary, 90.18 percent
  for authorization, and 92.27 percent for the verifier boundary. The last
  official repository-wide result remains 79.249908 percent, above the 78
  percent CI floor; GitHub Backend remains authoritative for the PR head.
- Migration `0024` upgrade, guarded downgrade, and re-upgrade behavior passed
  against isolated PostgreSQL. Human links remain timestamped while newly
  provisioned service links are explicitly unverified.
- Compileall, Ruff, merge-intent validation, stale Workstream, authorization,
  and artifact scans, Markdown links, all 80 agent-gate tests, the focused
  current-main integration tests, and diff integrity pass.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---|---|---|
| senior engineering | PASS AFTER FIXES | none | The route, transaction owner, replay contract, and fixed identity boundary are coherent and bounded. |
| QA/test | PASS AFTER FIXES | none | Behavior tests prove races, rollback, retry, privacy, migration, replay, denial, and stable API envelopes. |
| security/auth | PASS AFTER FIXES | none | Issuer configuration is server-owned, opaque identity data does not escape, and service callers remain denied before lookup. |
| product/ops | PASS | none | Only an effective system Access Administrator may provision; provisioning grants no service or human authority. |
| architecture | PASS AFTER FIXES | none | AUTH retains central identity, evaluator, activation, and evidence ownership without feature-owned authorization paths. |
| CI integrity | PASS AFTER FIXES | none | The real HTTP drill uses an isolated derived database and no threshold, skip, or exclusion was weakened. |
| docs | PASS AFTER FIXES | none | Specification, operations, chunk, and authored lifecycle state match runtime behavior and keep AUTH-09C inactive. |
| reuse/dedup | PASS AFTER FIXES | none | The implementation reuses canonical actor locks, authorization evidence, idempotency, and adapter ports without compatibility paths. |
| test delta | PASS AFTER FIXES | none | Tests are behavior-first and assert exact state, evidence, privacy, rollback, and retry outcomes. |

## Findings Resolved

Valid findings addressed: yes

Open sub-agent sessions: none

Review repairs added pre-lookup service denial inside `ActorService`, bounded
independent race proofs, crossed grant-revocation proof, injected evidence and
idempotency failure matrices, complete privacy scanning, explicit OpenAPI 409
contracts, and isolated-only real API verification. The final current-main
integration changed no reviewed AUTH runtime and preserved the WS-CON handoff's
registration -> hidden behavior -> AUTH activation order.

## Remaining Risk And Gate

This chunk records an unverified service credential binding; it deliberately
does not prove or admit the service token. A later separately approved AUTH-09E
must implement fixed-service verification and admission without weakening the
human boundary.

Replacement GitHub Backend, Agent Gates, CodeRabbit, and explicit human merge
approval remain. Do not start `WS-AUTH-001-09C` automatically.
