# Chunk Contract: WS-ART-001-02B2 R2 Credential Issuer

Initiative: `WS-ART-001` | Risk: L1 | Status: Proposed after 02B1

## Goal

Implement the small deployment-owned credential issuer required for R2
production. It locally signs short-lived R2 credentials behind the AWS SDK
container-credential endpoint contract and remains a separate infrastructure
process, not a Workstream product service or authorization authority.

## Allowed Files

- `services/r2_credential_issuer/` as an independently packaged Python 3.12
  service with exact dependency locks, tests, and a digest-pinned non-root
  container build;
- deployment manifests that place the issuer in Workstream's exact network
  namespace, with read-only secret mounts, resource limits, health checks, and
  no host/public port;
- a secrets-free Compose fixture that exercises the same endpoint protocol with
  disposable test signing material;
- `.github/workflows/backend.yml` for the exact issuer test and 90 percent
  coverage gate, image build, and secrets-free protocol proof;
- `scripts/test_agent_gates.py` only to enforce the exact unconditional CI step;
- issuer operations, rotation, audit, and incident documentation.

## Not Allowed

- issuer code, parent secrets, or signing logic in `backend/app/`;
- Workstream product routes, product authorization, actor identity, artifact
  policy, provider I/O, or database access;
- request-selected account, bucket, prefix, action, TTL, or audience;
- a public listener, host-network binding, outbound network requirement,
  plaintext remote endpoint, shell execution, or dynamic plugin loading;
- credential persistence, credential response logging, committed secrets, or a
  compatibility path for static R2 production credentials.

## Acceptance Criteria

- the service source is owned in this repository and its release image is built
  from a digest-pinned base with exact locked dependencies; deployment records
  the immutable release image digest;
- the process runs non-root, read-only except for an explicit temporary area,
  without Linux privilege escalation, a host/public port, or outbound network;
- parent access-key ID and parent secret/signing key are supplied through
  separate private read-only deployment files; the parent secret never enters
  Workstream configuration, environment, logs, errors, metrics, or memory;
- the parent token is restricted to the exact Cloudflare account and artifact
  bucket, has only the narrowest non-admin permission capable of minting the
  fixed child credentials, cannot access another bucket, and has tested
  rotation and revocation procedures;
- the bearer token is a separate private reloadable file. Token comparison is
  constant time, failed authorization reveals no credential metadata, and
  token rotation does not require exposing a second endpoint;
- every request is a parameter-free authenticated `GET`; account, bucket,
  prefix, exact `PutObject`/`HeadObject`/`GetObject` actions, minimum/maximum
  TTL, and audience are deployment-owned immutable configuration;
- startup rejects unsafe file permissions, malformed scope, non-loopback bind,
  missing secrets, TTL below the pinned SDK refresh margin, and unknown config;
- Compose uses `network_mode: service:<workstream-service>` and Kubernetes uses
  the same Pod, so the issuer's `127.0.0.1` listener is reachable only through
  Workstream's shared network namespace; a bridge-network DNS endpoint or
  issuer-owned network namespace is rejected;
- each issuance reloads the mounted parent and bearer files so deployment can
  rotate either secret atomically without retaining obsolete material;
- responses follow the pinned AWS container-credential JSON contract and use
  Cloudflare's documented local-signing algorithm; offline vectors and a live
  private-R2 smoke proof verify signature and scope behavior;
- structured audit records include issuance time, expiry, configured scope
  fingerprint, release digest, success/failure class, and request correlation,
  but never tokens, access keys, secrets, session tokens, signed material, or
  response bodies;
- timeouts, malformed secret rotation, concurrent requests, replayed/expired
  bearer tokens, clock boundaries, log/error object graphs, and process restart
  fail closed without returning stale credentials;
- issuer tests and source remain at least 90 percent covered; backend repository
  coverage remains at least 78 percent.
- backend CI preserves every earlier scoped 90 percent gate, adds the exact
  issuer gate below, and retains the exact 78 percent repository command;
  `scripts/test_agent_gates.py` fails on command, placement, condition,
  threshold, working-directory, or cumulative-retention drift.

## Exact CI Coverage Gates

```bash
coverage report --include='app/adapters/artifacts/*,app/interfaces/artifacts.py,app/modules/artifacts/*' --precision=2 --fail-under=90
coverage report --include='app/interfaces/external_services.py' --precision=2 --fail-under=90
coverage report --include='app/core/config.py' --precision=2 --fail-under=90
coverage report --include='app/workers/*' --precision=2 --fail-under=90
python -m pytest services/r2_credential_issuer/tests -q --cov=services/r2_credential_issuer/src --cov-report=term-missing --cov-fail-under=90
```

## Verification

```bash
python -m pytest services/r2_credential_issuer/tests -q --cov=services/r2_credential_issuer/src --cov-report=term-missing --cov-fail-under=90
cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json /tmp/ws-art-02b2-coverage.json --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78
docker compose build r2-credential-issuer
docker compose up -d --wait r2-credential-issuer r2-credential-protocol-probe
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/test_agent_gates.py
```

## Required Reviewers

Senior engineering, architecture, QA/test, security/auth, product/ops,
reuse/dedup, CI integrity, test delta, and docs.

## Human Review Focus

- Is this a bounded deployment component rather than a product service?
- Can request input, Workstream, or another container widen credential scope?
- Are parent-secret injection, reload/rotation, audit, image provenance,
  isolation, and live R2 proof concrete enough to operate safely?
