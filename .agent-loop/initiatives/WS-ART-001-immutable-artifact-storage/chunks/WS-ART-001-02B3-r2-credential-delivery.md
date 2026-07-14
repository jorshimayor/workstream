# Chunk Contract: WS-ART-001-02B3 R2 Credential Delivery

Initiative: `WS-ART-001` | Risk: L1 | Status: Proposed after 02B2

## Goal

Add a Cloudflare R2 production profile to the same adapter by using the AWS SDK
standard container-credential endpoint contract implemented by the
deployment-owned issuer from 02B2. Workstream does not implement or own
credential signing.

## Allowed Files

- R2/container-credential settings in `backend/app/core/config.py` and exact
  composition-root wiring in `backend/app/adapters/artifacts/__init__.py`;
- deployment wiring for the exact issuer image digest produced by 02B2, without
  embedding parent secret access key/signing material in Workstream;
- focused credential refresh, endpoint/token validation, redaction, scope, and
  R2 S3-protocol tests;
- `.github/workflows/backend.yml` for secrets-free test configuration and the
  exact 90 percent scoped coverage gate;
- `scripts/test_agent_gates.py` only to assert that backend CI retains the exact
  adapter/configuration coverage sources and fail-closed 90 percent threshold;
- R2 operations/readiness documentation and chunk memory.

## Not Allowed

- issuer implementation changes, a Workstream broker HTTP client, product
  route, credential-signing library,
  parent R2 credential, or persisted temporary credential;
- user-selectable account, bucket, prefix, actions, TTL, or audience;
- remote plaintext credential endpoint, expired credential fallback, or static
  R2 production credentials;
- any explicit, environment, profile, role/web-identity, SSO, credential-
  process, login-session/cache, shared-file, legacy `AWS_CREDENTIAL_FILE` /
  `OriginalEC2Provider`, Boto2, or instance-metadata credential taking
  precedence over the container provider;
- `AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` or direct
  `AWS_CONTAINER_AUTHORIZATION_TOKEN` in R2 mode;
- product cutovers, verification/recovery models, or Flow Node.

## Acceptance Criteria

- the only Workstream-side delivery mechanism is the SDK's standard container-
  credential endpoint via `AWS_CONTAINER_CREDENTIALS_FULL_URI` plus
  `AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE`;
- production permits only a pinned loopback endpoint; the bearer-token file is
  private, bounded, reloadable, never logged, and supplied by deployment;
- startup proves the issuer shares Workstream's network namespace through
  Compose `network_mode: service:<workstream-service>` or the same Pod in
  Kubernetes; bridge DNS, a separate sidecar network namespace, and host ports
  fail;
- the deployment sidecar contract fixes account, bucket, prefix, exact actions
  (`PutObject`, `HeadObject`, `GetObject`), minimum/maximum TTL, and audience
  server-side; the minimum TTL exceeds the pinned SDK advisory window plus
  request and scheduling margin;
  Workstream cannot request or widen scope;
- deployment proof confirms the issuer parent token is limited to the exact
  Cloudflare account and artifact bucket, uses the narrowest non-admin minting
  permission, cannot cross buckets, and supports tested rotation and revocation;
- the sidecar owns the parent secret access key and local R2 temporary-
  credential signing; Cloudflare local signing reuses the parent access-key ID
  as the temporary access-key ID, so Workstream receives that non-secret ID,
  derived temporary secret access key, session token, and expiry in the
  standard SDK response shape, but never the parent secret/signing key;
- SDK refresh single-flights; advisory-window failure may continue with a
  cached unexpired credential, while mandatory-window failure blocks provider
  I/O before nominal expiry and expired credentials are never used;
- R2 startup rejects all higher-precedence ambient credential sources, uses
  isolated empty config paths with instance metadata disabled, and verifies the
  resolved SDK credential method is the container provider;
- the pinned resolver inventory is exactly `env`, `assume-role`,
  `assume-role-with-web-identity`, `sso`, `shared-credentials-file`, `login`,
  `custom-process`, `config-file`, `ec2-credentials-file`, `boto-config`,
  `container-role`, and `iam-role`; after forbidden-source pre-validation and
  before any credential load, R2 composition constrains the resolver to the
  single `container-role` provider and fails on inventory/order drift;
- startup requires `AWS_CONTAINER_CREDENTIALS_FULL_URI` and
  `AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE` to exactly match the configured
  pinned loopback URI and private mounted token-file path; method, endpoint, or
  authorization-source mismatch fails before artifact I/O;
- Workstream never extends credential validity or
  performs a per-provider-request sidecar liveness check;
- tests cover advisory and mandatory refresh failure, expiry, rotation,
  concurrent refresh, poisoned environment/profile/metadata sources,
  `login_session`, login-cache, `AWS_CREDENTIAL_FILE`/`OriginalEC2Provider`,
  relative-URI and direct-token poisoning with actual endpoint/token-source
  assertions, and instrumentation proving no competing provider reads a file,
  starts a process, touches a cache, or calls a metadata/network endpoint,
  replayed/expired token, endpoint redirection, scope escalation attempts,
  parent-secret absence from the
  Workstream process, and complete secret redaction/non-retention;
- the same adapter passes R2 protocol smoke tests with `region=auto` and the
  required HTTPS account endpoint;
- focused adapter, configuration, and composition-root coverage is at least 90
  percent and repository coverage remains at least 78 percent.
- backend CI installs this chunk's exact focused 90 percent gate, preserves
  every earlier scoped 90 percent gate, and retains the exact 78 percent
  repository command below; `scripts/test_agent_gates.py` fails on workflow
  command, source-set, threshold, or cumulative-retention drift.

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
docker compose up -d --wait postgres redis minio r2-credential-test-endpoint
cd backend && .venv/bin/ruff check app tests
cd backend && .venv/bin/pytest tests/test_r2_credential_delivery.py tests/test_s3_artifact_store.py tests/test_config.py -q --cov=app.adapters.artifacts --cov=app.core.config --cov-report=term-missing --cov-fail-under=90
cd backend && WORKSTREAM_TEST_ADMIN_DATABASE_URL=postgresql+asyncpg://workstream:workstream@localhost:5433/postgres .venv/bin/python scripts/run_isolated_tests.py --metadata-json /tmp/ws-art-02b3-coverage.json --timeout-seconds 12600 -- .venv/bin/python -m pytest -q --ignore=tests/test_isolated_database_runner.py --cov=app --cov-report=term-missing --cov-fail-under=78
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/test_agent_gates.py
```

The chunk replaces the protocol fixture with the exact deployment-owned issuer
image from 02B2 and independently proves the Workstream client boundary.

## Required Reviewers

Senior engineering, architecture, QA/test, security/auth, product/ops,
reuse/dedup, CI integrity, test delta, and docs.

## Human Review Focus

- Is R2 a peer provider rather than a separate artifact architecture?
- Is every credential trust boundary concrete and fail closed?
- Is the parent secret access key/signing material absent from Workstream code,
  config, and memory while the reused non-secret access-key ID is handled only
  as part of the temporary SDK credential set?
