# Authorization Service Operations

## Purpose

This runbook assigns ownership and stop conditions for the staged WS-AUTH-001
authorization rollout. The verified-token configuration and evidence commands
are executable contracts; later actor/grant sections remain staged until their
owning implementation chunks.

## Ownership

| Area | Primary owner | Required evidence |
|---|---|---|
| Issuer/audience/algorithm configuration | Platform security | Approved non-secret configuration inventory and verifier tests. |
| JWKS endpoint, cache, and rotation | Platform security/on-call | Rotation drill, cache bounds, outage behavior, alerts. |
| Introspection/revocation policy | Platform security | Approved mode, endpoint trust policy, timeout/failure proof. |
| First Access Administrator bootstrap | Restricted deployment operator | Dry-run, target verification, one-time result, authority event. |
| Legacy actor classification | Data migration owner plus security reviewer | Versioned manifest, live-row digest, checksum, dry-run report. |
| Actor/grant administration | Access Administrator | Supported API/command, reason, idempotency, evidence. |
| Project contributor grants | Covered Project Manager | Exact-project target and privacy-bounded candidate lookup. |
| Recovery operations | Operator or covered Project Manager as specified | Matched permission, reason, resource scope, immutable evidence. |
| Rollout and rollback | Release owner | Migration round trip, compatibility inventory, rollback stop conditions. |
| Live authorization proof | Release owner plus security/QA | API-visible drill with redacted committed evidence. |

## Required Configuration

Platform security owns the following inventory. Production, staging, and
preview fail closed when a required value is absent or outside its bound.

| Variable | Accepted value | Default/requirement |
|---|---|---|
| `WORKSTREAM_TOKEN_ISSUER` | Canonical HTTPS URL; no userinfo, query, or fragment | Required |
| `WORKSTREAM_TOKEN_AUDIENCE` | Non-empty string | `workstream` |
| `WORKSTREAM_TOKEN_JWKS_URL` | Canonical HTTPS URL; no userinfo, query, or fragment | Required |
| `WORKSTREAM_TOKEN_ALGORITHMS` | One-family subset of `RS256,RS384,RS512,ES256,ES384,ES512,EdDSA` | Required; no symmetric algorithms |
| `WORKSTREAM_REQUIRED_HUMAN_SCOPE` | One scope token | `workstream:access` |
| `WORKSTREAM_REQUIRED_SERVICE_SCOPE` | One scope token | `workstream:service` |
| `WORKSTREAM_TOKEN_CLOCK_SKEW_SECONDS` | Integer `0..300` | `30` |
| `WORKSTREAM_TOKEN_MAX_BYTES` | Integer `512..32768` | `16384` |
| `WORKSTREAM_TOKEN_HEADER_MAX_BYTES` | Integer `128..8192`, not above token max | `4096` |
| `WORKSTREAM_TOKEN_PAYLOAD_MAX_BYTES` | Integer `256..24576`, not above token max | `12288` |
| `WORKSTREAM_TOKEN_JWKS_CACHE_TTL_SECONDS` | Integer `30..3600` | `300` |
| `WORKSTREAM_TOKEN_JWKS_MAX_RESPONSE_BYTES` | Integer `1024..1048576` | `262144` |
| `WORKSTREAM_TOKEN_JWKS_MAX_KEYS` | Integer `1..100` | `20` |
| `WORKSTREAM_TOKEN_UNKNOWN_KID_CACHE_TTL_SECONDS` | Integer `1..300` | `30` |
| `WORKSTREAM_TOKEN_UNKNOWN_KID_CACHE_MAX_ENTRIES` | Integer `1..1000` | `100` |
| `WORKSTREAM_TOKEN_JWKS_CONNECT_TIMEOUT_SECONDS` | Float `0.1..10` | `2` |
| `WORKSTREAM_TOKEN_JWKS_READ_TIMEOUT_SECONDS` | Float `0.1..10` | `3` |
| `WORKSTREAM_TOKEN_JWKS_WRITE_TIMEOUT_SECONDS` | Float `0.1..10` | `3` |
| `WORKSTREAM_TOKEN_JWKS_POOL_TIMEOUT_SECONDS` | Float `0.1..10` | `1` |
| `WORKSTREAM_TOKEN_JWKS_TOTAL_TIMEOUT_SECONDS` | Float `0.5..15` | `5` |
| `WORKSTREAM_TOKEN_INTROSPECTION_MODE` | `disabled` or `required` | Required |
| `WORKSTREAM_TOKEN_INTROSPECTION_DISABLED_REASON` | Issuer-policy evidence reference | Required in `disabled` mode |
| `WORKSTREAM_TOKEN_INTROSPECTION_URL` | Canonical HTTPS URL | Required in `required` mode |
| `WORKSTREAM_TOKEN_INTROSPECTION_CLIENT_ID` | Non-empty secret-backed identifier | Required in `required` mode |
| `WORKSTREAM_TOKEN_INTROSPECTION_CLIENT_SECRET` | Non-empty secret value | Required in `required` mode |
| `WORKSTREAM_TOKEN_INTROSPECTION_MAX_RESPONSE_BYTES` | Integer `256..262144` | `65536` |
| `WORKSTREAM_TOKEN_INTROSPECTION_CONNECT_TIMEOUT_SECONDS` | Float `0.1..10` | `2` |
| `WORKSTREAM_TOKEN_INTROSPECTION_READ_TIMEOUT_SECONDS` | Float `0.1..10` | `3` |
| `WORKSTREAM_TOKEN_INTROSPECTION_WRITE_TIMEOUT_SECONDS` | Float `0.1..10` | `3` |
| `WORKSTREAM_TOKEN_INTROSPECTION_POOL_TIMEOUT_SECONDS` | Float `0.1..10` | `1` |
| `WORKSTREAM_TOKEN_INTROSPECTION_TOTAL_TIMEOUT_SECONDS` | Float `0.5..15` | `5` |
| `WORKSTREAM_API_RATE_LIMIT_KEY_SECRET` | Canonical padded RFC 4648 Base64 decoding to `32..64` bytes | Optional until a protected route is attached; then required |
| `WORKSTREAM_API_FIRST_ACCESS_RATE_LIMIT` | Integer `1..10000` | `10` |
| `WORKSTREAM_API_FIRST_ACCESS_RATE_WINDOW_SECONDS` | Integer `1..3600` | `60` |
| `WORKSTREAM_API_ADMIN_MUTATION_RATE_LIMIT` | Integer `1..10000` | `30` |
| `WORKSTREAM_API_ADMIN_MUTATION_RATE_WINDOW_SECONDS` | Integer `1..3600` | `60` |

Secrets, private keys, bearer tokens, full claims, and raw JWKS documents must
not appear in committed configuration or evidence.

Verification evidence:

```bash
tmp_venv="$(mktemp -d)"
python3 -m venv "$tmp_venv"
"$tmp_venv/bin/python" -m pip install -e ./backend
"$tmp_venv/bin/python" -c 'import jwt, cryptography, httpx'
"$tmp_venv/bin/python" -m pip check
rm -rf "$tmp_venv"

cd backend
.venv/bin/python -m pytest -q tests/test_auth.py tests/test_config.py
.venv/bin/python -m ruff check app tests scripts
: "${WORKSTREAM_TEST_DATABASE_URL:?set a disposable migrated test database URL}"
WORKSTREAM_DATABASE_URL="$WORKSTREAM_TEST_DATABASE_URL" \
  WORKSTREAM_TEST_DATABASE_URL="$WORKSTREAM_TEST_DATABASE_URL" \
  .venv/bin/python -m pytest -q
WORKSTREAM_DATABASE_URL="$WORKSTREAM_TEST_DATABASE_URL" \
  .venv/bin/python scripts/api_contract_e2e.py
cd ..
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
python3 scripts/check_loop_memory_state.py
git diff --check
```

During the compatibility period, `/api/v1/auth/me` and actor registration use
only the verified issuer/subject plus bounded legacy roles. They do not copy
issuer email or display name into actor storage or responses, so both response
fields remain `null`. Consumers must not treat token identity metadata as a
profile source of truth; canonical profile metadata belongs to the later actor
profile migration.

## Request And Error Context

Clients may send one `X-Request-ID` and one `X-Correlation-ID`. Each supplied
value must be a canonical lowercase, hyphenated, non-nil RFC 9562 UUID using the
RFC variant and version 1 through 8. A missing request ID is generated as
UUIDv4; a missing correlation ID reuses the effective request ID. Duplicate,
comma-joined, malformed, non-ASCII, nil, or unsupported-version values stop
before route/dependency execution with HTTP 400 `invalid_request`. That response
uses one newly generated UUIDv4 for both safe headers and never reflects the
rejected bytes.

Every success and error response returns the effective IDs in
`X-Request-ID` and `X-Correlation-ID`. Application-supplied response values for
those headers are overwritten. Status, content length, duplicate unrelated
headers, `WWW-Authenticate`, `Retry-After`, streaming chunks, and background
work remain unchanged.

Errors add this canonical object while retaining the existing top-level
`detail` or domain `code/details` compatibility fields:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Request validation failed",
    "details": {},
    "correlation_id": "00000000-0000-4000-8000-000000000001",
    "retryable": false
  }
}
```

The authentication boundary uses `missing_token`, `invalid_token`,
`identity_verification_unavailable`, and `unsupported_subject_kind` for their
exact branches. Verification/registry unavailability is retryable; invalid
credentials, unsupported kinds, validation, permission, not-found, conflict,
and internal application errors are not. The canonical nested validation
summary is capped at 20 errors with type/location evidence only. Existing
sanitized validator messages remain solely in the bounded compatibility
`detail` list.

Use the correlation ID to join operator evidence. Never add bearer tokens,
claims, subjects, emails, SQL, provider bodies, exception text, or secrets to
responses or logs. AUTH-04A does not activate rate controls, grant APIs, or new
product authority; those remain owned by later separately reviewed chunks.

## PostgreSQL Rate Controls

AUTH-04B provides unattached dependencies for future first-access and
authority-management mutations. No production route is rate limited by this
chunk. When an owning route attaches one, every replica must use the same
secret and settings. Missing secret or database access fails the dependency
closed with retryable HTTP 503; an exhausted window returns retryable HTTP 429
with an integer `Retry-After`.

Generate the secret outside the repository and store it in the deployment
secret manager:

```bash
python3 -c 'import base64,secrets; print(base64.b64encode(secrets.token_bytes(32)).decode())'
```

Counters store only the server-owned scope and an HMAC-SHA256 digest of the
verified issuer/subject. They do not store raw identity, actor, token, claim,
role, email, or network values. Consumption uses database time and commits in
an independent session before the protected mutation may continue or return
429, so downstream rollback does not restore allowance.

Secret rotation intentionally creates a new digest space. Before rotating:

1. Quiesce every protected write for at least the largest effective
   pre-rotation window configured on any replica.
2. Rotate every replica while writes remain quiesced; mixed-secret replicas
   must not serve protected writes.
3. Delete only rows expired by PostgreSQL time:

```sql
DELETE FROM api_rate_control_counters
WHERE window_expires_at <= statement_timestamp();
```

4. Confirm all replicas use the new secret, then resume protected writes.

Runtime consumption opportunistically deletes at most 100 expired other rows.
On idle systems, operators may run the same expired-only SQL cleanup. Never
delete active rows to recover capacity, and never downgrade migration `0017`
while the table is nonempty; the guarded downgrade takes an exclusive table
lock, refuses, and rolls back. Quiesce every protected write before attempting
the downgrade so waiting writers cannot resume against a removed table.

## JWKS Rotation And Outage

Rotation procedure:

1. Confirm the new key is published by the configured issuer over trusted
   HTTPS.
2. Verify algorithm and key-use constraints.
3. Exercise unknown-key refresh once; do not create refresh loops.
4. Verify both old and new unexpired tokens only during the issuer's approved
   overlap.
5. Confirm cache, refresh-success, and refresh-failure metrics use bounded
   labels.
6. Remove the retired key according to issuer policy and repeat denial tests.

During an outage, cached keys may be used only inside the configured safe
window. Once verification cannot be established, protected requests fail
closed. Operators must not switch to an unpinned algorithm, shared production
HMAC secret, development verifier, unsigned token, or unverified claim parsing.

## Introspection And Revocation Mode

Production must select an explicit mode:

- disabled only with documented issuer revocation/short-lifetime evidence;
- required bearer-token introspection only to a separately configured HTTPS
  endpoint with OAuth client-secret Basic authentication, no redirects or
  environment proxies, and strict time/response bounds.

Required introspection responses contain `active=true`, `iss`, `sub`, `aud`,
and `jti`; every identity value must match the already signature-verified
token. Introspection cannot provide or replace identity, kind, scope, roles, or
grants. Identifier-only introspection is not supported in this chunk. Platform
security owns the client ID/secret, rotation, and revocation procedure.

JWKS and introspection use separate clients and policies. Bearer tokens never
reach JWKS endpoints, redirect targets, logs, traces, errors, or audit events.
An introspection outage fails according to the approved mode; it cannot silently
degrade to token-role authority.

## Bootstrap Custody

Bootstrap is a restricted local management operation.

Before execution:

- verify the target is the intended active human profile and identity link;
- verify the environment and database;
- capture a redacted dry-run result;
- confirm no effective Access Administrator exists;
- confirm the deployment operator has restricted environment access;
- confirm audit and database-time behavior are available.

Execution must lock `AuthorityControl(id = 1) FOR UPDATE` before checking the
effective administrator count. Exactly one initial grant and one success event
may commit. Later or concurrent attempts return the stable audited conflict.

Never bootstrap through public HTTP, direct SQL, a shared secret, or a
fabricated human/system role.

## Legacy Actor Classification

Non-empty legacy registries require the supported classification tool and a
versioned JSON manifest. Each entry binds the exact legacy actor ID, issuer,
opaque subject, and subject kind.

Platform security owns the manifest and envelope. Both files contain
confidential identity-linking evidence even though the command report is
redacted. Store them in an environment-specific owner-only directory outside
the repository, every linked worktree, and the Git common directory. Do not
attach either file to tickets, CI logs, PRs, or engineering-loop evidence.

Manifest schema version 1 has exactly this shape:

```json
{
  "schema_version": 1,
  "classifications": [
    {
      "actor_id": "00000000-0000-5000-8000-000000000000",
      "issuer": "https://issuer.example.invalid",
      "subject": "opaque-subject-from-the-legacy-row",
      "subject_kind": "human"
    }
  ]
}
```

`subject_kind` is only `human` or `service`. The actor ID must be the canonical
UUIDv5 derived by the existing registry from the byte-exact HTTPS issuer and
case-sensitive opaque subject. Operators must classify from authoritative
issuer records; email, subject syntax, token roles, profile rows, and manual SQL
are not classification evidence.

The tool must:

- support dry-run;
- reject unknown fields/kinds, duplicates, missing rows, extra rows, stale
  rows, mismatched issuer/subject, invalid UUIDs, and ambiguous classification;
- compute a complete live-row digest and manifest checksum;
- bind evidence to a non-secret database/environment identifier;
- write no grants;
- emit a bounded remediation report.

Prepare a restricted directory and validate without writing an envelope:

```bash
cd backend
WORKSTREAM_DATABASE_URL='<target async Postgres URL>' \
  .venv/bin/python scripts/legacy_actor_classification.py \
  --manifest /secure/workstream/prod/legacy-actor-manifest-v1.json
```

Dry-run is the default. An empty registry needs no manifest and returns an
explicit empty proof. A non-empty registry without a manifest fails closed. The
JSON report contains only row count, mode, empty status, checksums, and the
non-secret database binding; stderr uses stable error codes and does not render
identity values, paths, database names, or connection URLs.

After the dry-run report is reviewed, export one write-once envelope:

```bash
cd backend
WORKSTREAM_DATABASE_URL='<target async Postgres URL>' \
  .venv/bin/python scripts/legacy_actor_classification.py \
  --manifest /secure/workstream/prod/legacy-actor-manifest-v1.json \
  --output /secure/workstream/prod/legacy-actor-classification-v1.json \
  --generated-at 2026-07-13T12:30:00Z
```

`--generated-at` is an explicit UTC RFC3339 second so the same reviewed inputs
produce byte-identical evidence. Export writes mode `0600` through a
crash-safe, atomic no-overwrite publish. Repeating the exact command is
idempotent only when the existing regular file has identical bytes and private
permissions. A different existing file, symlink, relative path, repository
path, or Git-directory path fails closed.

The envelope contains schema version, sorted classifications, live source-row
digest, canonical manifest digest, generated-at, database binding, and a digest
over the complete envelope. The binding hashes PostgreSQL database name and
database OID. It is a non-secret same-cluster wrong-database guard, not a
globally unique deployment identity. A clone, restore, or database recreation
requires a fresh dry run and envelope even when the human environment label is
unchanged.

The later actor-schema migration must locate this envelope only through:

```bash
export WORKSTREAM_LEGACY_ACTOR_CLASSIFICATION_FILE=/secure/workstream/prod/legacy-actor-classification-v1.json
```

Do not set the variable or run the future migration until its owning reviewed
AUTH chunk is deployed. That migration must load the strict envelope, recompute
the complete live row-set digest and database binding inside its transaction,
and abort on checksum, TOCTOU, missing/extra row, identity, or binding mismatch.
The envelope never creates grants and is not a supported ad hoc migration path.

On validation failure, correct the authoritative manifest or target database,
rerun dry-run, and export to a new secure path when the evidence bytes change.
Never edit an envelope or bypass the failure with SQL. Rollback stops at the
pre-migration schema boundary; it does not restore obsolete authority. Retain
the envelope only through migration verification and the approved rollback
window. After the migration records the schema version, manifest checksum,
envelope checksum, source-row checksum, and migration result durably, delete
the identity-bearing manifest and envelope from operator storage and retain
only the bounded report and durable checksum record.

## Staged Rollout

For each chunk:

1. Confirm allowed files and stop conditions.
2. Run focused tests plus the full backend suite/API drill required by the
   contract.
3. Run migration upgrade, downgrade-one, and re-upgrade where applicable.
4. Confirm the temporary compatibility allowlist only shrinks.
5. Run required internal reviewers and repair valid findings.
6. Publish one chunk-sized PR and stop for human merge approval.
7. Update post-merge memory before activating the next chunk.

Do not cut over a resource family until its local actor, grant, permission,
resource loader, lifecycle guards, negative tests, and evidence path exist.

## Rollback

Rollback stops rather than bypasses authorization. A deployment may roll back
only to the preceding reviewed chunk state and compatible schema revision.

Stop rollout when:

- issuer behavior would require trusting a token role/unverified claim;
- classification requires guessing subject kind;
- a second canonical actor/verifier/authorization path appears necessary;
- authority state and evidence cannot commit atomically;
- final-administrator safety depends on an unlocked count;
- an intermediate release cannot execute the established intake lifecycle;
- tests, CI, privacy, or auth defaults would need weakening.

Do not restore deleted authority through direct SQL or re-enable an obsolete
token-role path outside its reviewed compatibility owner.

## Recovery Permission Inventory

| Operation | Authority | Required controls |
|---|---|---|
| Normal covered task/setup repair | Covered Project Manager `project.task.manage` | Exact project, lifecycle guard, reason/evidence where mutation is corrective. |
| Start override | Operator `operations.task.start_override` | Recovery-only path, exact task/project, reason, matched grant/permission, audit. |
| Submission gate repair | Operator `operations.submission_gate.repair` | No submission/review rewrite; reason, matched authority, immutable checker evidence. |
| Checker retry | Operator `operations.checker.retry` | New attempt/supersession evidence; no prior result deletion. |
| Review lease force release | Operator `review.lease.force_release` under WS-REV-001 | Review-owned lease guards and evidence; no review decision. |

Conceptual historical “admin override” statements are not operations. No
recovery permission may erase checker evidence, create a review decision,
alter an immutable submission, create/alter a contribution record, or bypass
compensation policy.

## Monitoring And Alerts

Required bounded-cardinality metrics cover:

- `workstream_auth_verification_total{result}`;
- `workstream_auth_jwks_cache_total{result}`;
- `workstream_auth_jwks_refresh_total{result}`;
- `workstream_auth_introspection_total{mode,result}`;
- actor first access/conflict and actor/link state;
- authorization allow/deny code and registered permission;
- administrative/project grant state;
- invalidation backlog and reconciliation retry;
- bootstrap attempt/result.

Alerts require an owner, diagnosis steps, safe recovery, escalation path, and
evidence-retention period. Alert on sustained verification failure, unusable
JWKS cache, repeated bootstrap/final-administrator denial, unusual grant
mutation rate, invalidation backlog, and abnormal first-access conflicts.

Platform security/on-call alerts when verification or refresh failures exceed
5% for five minutes, when all JWKS refreshes fail for two consecutive cache
windows, or when required introspection is unavailable for two minutes.
Diagnosis checks the approved issuer configuration, HTTPS reachability, key
rotation window, cache age, and introspection health without printing response
bodies or credentials. Recovery restores the approved issuer endpoint/policy;
it never enables HMAC, development auth, redirects, or an unpinned algorithm.
Escalate to the release owner and security lead and retain redacted incident
metrics/configuration evidence for the normal security incident period.

Never use token, subject, email, `jti`, raw URL, key material, or unbounded
resource IDs as metric labels.

## Authority Mutation Idempotency

Service-actor creation, administrative/project grant issue or revocation,
actor suspension/reactivation/deactivation, and identity-link
revocation/reactivation require a canonical UUID idempotency key. The namespace
is actor-kind, opaque actor reference, closed operation, and key. Reusing that
namespace with a different canonical request produces `idempotency_mismatch`
without exposing the stored digest, record, or response.

Reservation must be the first database write. Business state, one concrete
success event, one linked invalidation event, and the typed replay reference
commit in the same caller-owned transaction. The authorization repository and
service never commit, roll back, open a second session, expire a pending row, or
steal a claim. On mismatch the caller rolls back the reservation transaction,
starts a clean transaction on the same injected session, commits exactly one
privacy-bounded denial event, and then translates the conflict.

A replay reference is internal only. Before responding, the future route owner
must load the canonical resource and evaluate current authority again. There is
currently no invalidation consumer or backlog processor; the durable event is
foundation evidence for the owning later chunk.

## Authority Audit Custody

Authority decisions and invalidation requests use the shared `audit_events`
ledger. Database triggers reject normal `UPDATE`, `DELETE`, and `TRUNCATE` for
both lifecycle and authority rows. There is no runtime flag, session setting,
or application-user bypass. Authority timestamps come from the database, and
the application writer joins the caller's transaction so evidence cannot
commit separately from the authority mutation it explains.

Production must run Workstream with a dedicated non-owner database role that
has no DDL, trigger-management, table-owner, superuser, or bypass privileges.
Release verification must fail if the application credential owns
`audit_events` or can disable its triggers. Schema migration credentials are
separate and unavailable to the running service.

Owner-level maintenance is exceptional and requires an approved change record,
an outage or writer drain, and an explicit list of rows and purpose. The
database owner must:

1. begin one transaction and take `ACCESS EXCLUSIVE` lock on `audit_events`;
2. record the pre-change row count and trigger state without exporting private data;
3. disable only the named mutation trigger needed for the approved operation;
4. perform only the listed maintenance statements and verify affected IDs/counts;
5. re-enable the trigger before commit and prove all three audit triggers enabled;
6. retain redacted change evidence and return credentials to controlled storage.

Do not use owner maintenance to revise authority history, erase a denial, or
fabricate evidence. Normal migration downgrade refuses while authority rows
exist; destructive cleanup requires a separately reviewed retention or legal
procedure and is not an application operation.

## Incident Response

For suspected authority misuse:

1. Preserve request/correlation IDs and append-only authority evidence.
2. Suspend/revoke through supported operations when current authority permits.
3. Confirm same-token denial on the next request.
4. Inspect exact matched grant, permission, project, and resource guards.
5. Reconcile affected assignments without rewriting submitted/review history.
6. Escalate final-administrator risk before any state mutation.
7. Record corrective action and retained evidence without secrets or private
   artifact content.

## Live Proof Responsibility

The final release owner coordinates a supported API/command drill proving:

- first human access;
- one-time bootstrap and concurrent conflict;
- scoped administrative grants;
- exact-project submitter/reviewer grants;
- admin/contributor separation and self-action denial;
- same-unexpired-token revocation;
- suspension/reactivation and link revocation;
- service subject handling;
- cross-project concealment;
- final-administrator concurrency safety;
- authorized audit export and absence of direct database authority edits.

Committed proof uses approved redacted placeholders and never production
tokens, private keys, raw claims, private actor/source IDs, or local paths.
