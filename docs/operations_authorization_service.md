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
: "${WORKSTREAM_DATABASE_URL:?set a disposable migrated test database URL}"
WORKSTREAM_DATABASE_URL="$WORKSTREAM_DATABASE_URL" .venv/bin/python -m pytest -q
WORKSTREAM_DATABASE_URL="$WORKSTREAM_DATABASE_URL" .venv/bin/python scripts/api_contract_e2e.py
cd ..
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_authorization_docs.py
python3 scripts/check_markdown_links.py
python3 scripts/check_loop_memory_state.py
git diff --check
```

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

The tool must:

- support dry-run;
- reject unknown fields/kinds, duplicates, missing rows, extra rows, stale
  rows, mismatched issuer/subject, invalid UUIDs, and ambiguous classification;
- compute a complete live-row digest and manifest checksum;
- bind evidence to a non-secret database/environment identifier;
- write no grants;
- emit a bounded remediation report.

The migration recomputes the live digest inside its transaction and aborts on
mismatch. After upgrade, only the recorded classification version/checksum and
migration state are required for downgrade. Manual SQL classification is not a
supported path.

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
