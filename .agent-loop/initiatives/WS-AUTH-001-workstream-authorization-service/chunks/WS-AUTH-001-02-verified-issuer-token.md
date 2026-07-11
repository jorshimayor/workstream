# Chunk Contract: WS-AUTH-001-02 - Verified Issuer Token And JWKS Boundary

## Parent initiative

`WS-AUTH-001` - Workstream Authorization Service

## Goal

Implement a fail-closed final-token verifier with pinned issuer, audience,
algorithms, JWKS resolution/refresh, temporal claims, subject kind, coarse
scope, and typed verification errors. This chunk authenticates only; it does
not grant Workstream product authority.

## Why this chunk exists

The current production verifier is intentionally unimplemented and the local
HS256 fixture lacks the adopted token contract.

## Approved plan reference

- INTENT: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/INTENT.md`
- PLAN: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/PLAN.md`
- CHUNK_MAP: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/CHUNK_MAP.md`

## Risk class

L1

## SLA

P1

## Allowed files

```text
backend/pyproject.toml
backend/app/core/config.py
backend/app/core/auth.py
backend/app/interfaces/auth.py
backend/app/adapters/auth/**
backend/app/api/deps/auth.py
backend/app/schemas/auth.py
backend/tests/test_auth.py
backend/tests/test_config.py
backend/scripts/api_contract_e2e.py
docs/operations_authorization_service.md
.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/REVIEW_LOG.md
```

## Not allowed

```text
actor/grant database models or migrations
product permission checks
project/task/checker authorization changes
Workstream token issuance, login, sessions, or passwords
trusting token role claims
```

## Acceptance criteria

- `VerifiedIssuerToken` contains only verified identity/coarse-access claims.
- Signature, issuer, audience, `exp`, `iat`, optional `nbf`, `jti`,
  `subject_kind`, and required scope are validated.
- Algorithms are configured and pinned; unknown `kid` triggers at most one
  controlled refresh.
- Valid cached keys obey bounded cache policy; unavailable verification fails
  closed.
- An explicit introspection/revocation mode is configured. Production rejects
  an unspecified mode; disabled mode is explicit and evidence-backed by issuer
  policy. Enabled bearer-token introspection uses a separately configured,
  allowlisted HTTPS endpoint, POSTs only to that origin, follows no redirects,
  has strict connect/read/total timeout and response-size bounds, and redacts
  request credentials and responses from logs/errors. A `jti`-only issuer
  contract is allowed only when documented and tested explicitly.
- JWKS retrieval and credential-bearing introspection use separate clients and
  policies. JWKS requires HTTPS outside deterministic local tests, follows no
  redirects, and enforces response-size and key-count bounds. Tests prove a
  bearer token never reaches JWKS or any redirect target.
- Human/service scope differs; agent and Space kinds are represented for the
  resolver to deny later.
- Token roles do not appear in the verified authority contract.
- The existing `AuthVerifier` protocol/factory is evolved in place; no second
  TokenVerifier hierarchy is created.
- Untouched legacy product surfaces receive one explicitly named
  `LegacyAuthorizationCompatibilityContext` built only after successful final
  token verification. It may expose verified legacy role claims only to an
  enumerated shrinking allowlist of unmigrated dependencies. Migrated surfaces
  cannot import or consume it, and chunk 15 removes it completely.
- The API drill is updated to emit the final token claim shape (`jti`,
  `subject_kind`, scope, issuer/audience/time) while retaining legacy roles only
  for the bounded compatibility context. Intake remains executable and no test
  treats the canonical verified-token type as role authority.
- Dev/local fixtures remain impossible in staging/production.
- Any production dependency addition is narrowly justified and reviewed.
- No production dependency is added until explicit human approval is durably
  recorded; absence of that approval stops the chunk.
- The operations runbook assigns ownership for issuer/JWKS configuration, key
  rotation, cache bounds, introspection policy, outage response, and evidence.
- Bounded-cardinality metrics for verification result, JWKS cache hit/refresh,
  refresh failure, and introspection result are emitted at the verifier boundary
  without issuer subject, token, `jti`, key material, or raw URL labels.

## Verification commands

```bash
(cd backend && .venv/bin/python -m ruff check app tests)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python -m pytest -q)
(cd backend && WORKSTREAM_DATABASE_URL=<test-db> .venv/bin/python scripts/api_contract_e2e.py)
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
git diff --check
```

## Required reviewers

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

## Human review focus

Inspect algorithm pinning, JWKS outage behavior, cache refresh, scope/subject
classification, dependency choice, and absence of role authority.

## Stop conditions

Stop if verification requires accepting unverified claims, permissive algorithm
selection, a shared production HMAC secret, forwarding bearer tokens anywhere
except the separately approved/configured introspection origin under the rules
above, a second verifier hierarchy, or an unapproved production dependency.
