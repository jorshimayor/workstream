# Decisions: WS-AUTH-001 - Workstream Authorization Service

## D1: Adopt WS-AUTH-001 as the authorization authority source

Status: accepted by the user on 2026-07-11.

`WS-AUTH-001` supersedes the repository's token-role bootstrap and current
multi-profile authorization semantics. Existing code and docs remain evidence
of current behavior, not the target authority contract.

## D2: Preserve `/api/v1`

Status: accepted by the user on 2026-07-11.

The repository's existing `/api/v1` namespace remains canonical. The imported
specification's `/v1` examples will be reconciled during the baseline-adoption
chunk. Workstream will not expose two versioned route trees as permanent
aliases.

## D3: Prioritize auth before WS-POL-002-03

Status: accepted by the user on 2026-07-11.

`WS-POL-002` is paused after merged chunk 02. New post-submit approval APIs must
not be built on authority rules that have been declared obsolete.

## L0 human approval boundary

The user explicitly approved the authorization direction, source precedence,
API namespace, and priority recorded in D1-D3 on 2026-07-11. On 2026-07-11,
after the planning and post-merge memory PRs merged, the user said "ok start" in
direct response to the recorded D4-D10 approval and separate chunk-start gate.
That response approves D4-D10 and starts only `WS-AUTH-001-01`. Every bounded
implementation chunk remains L1 and retains its own human PR/merge checkpoint.

## D4: No dual canonical authority

Status: accepted by the user on 2026-07-11.

Token roles may be retained as non-authoritative diagnostic input during a
bounded migration only. A protected command must never accept either a token
role or a local permission as interchangeable proof. Cutover chunks replace
authorization for complete resource surfaces and remove the old check.

## D5: Preserve historical actor identifiers where classification is safe

Status: accepted by the user on 2026-07-11.

Existing `ActorIdentity.actor_id` values for externally verified callers are
UUID5 strings and are referenced throughout tasks, submissions, checker runs,
project provenance, and audit rows. For a classified legacy row, that UUID
becomes the canonical `ActorProfile.id`; the new `ActorIdentityLink` receives a
separate UUID. Migration must validate UUID shape and uniqueness before reuse.
Invalid or ambiguous rows fail preflight and are not silently rewritten.

The unrelated UUIDs on legacy typed `actor_profiles` rows are workflow-row IDs,
not actor IDs, and never become canonical profile IDs.

## D6: Existing typed profiles do not become grants

Status: accepted by the user on 2026-07-11.

Observed or active `worker`, `reviewer`, `admin`, or `project_manager` profile
rows do not create `AdminRoleGrant` or `ProjectRoleGrant` records. Skills and
non-authoritative workflow metadata may be preserved under a clearly named
metadata model only when required by an existing workflow.

## D7: Internal workers use explicit system authority

Status: accepted by the user on 2026-07-11.

Project setup, pre-review gating, reconciliation, and repair work use fixed
Workstream system principals and registered system permissions. They do not
receive fabricated human admin roles and do not become normal ActorProfiles.

## D8: Production issuer details remain configuration

Status: accepted by the user on 2026-07-11.

The token adapter will require explicit issuer, audience, JWKS URL, algorithm,
scope, clock-skew, and cache configuration and will fail closed when incomplete.
The real issuer values are required for live production-token proof, not for
deterministic adapter implementation with local JWKS fixtures.

## D9: Authority evidence is foundational

Status: accepted by the user on 2026-07-11 after internal review repair.

Request/correlation context, canonical idempotency records, and the shared
append-only authority-event writer are introduced before canonical actor
persistence and before any authority-changing public API. Every later authority
mutation commits state, idempotency result, audit event, and invalidation event
atomically. The final evidence chunk verifies completeness; it does not invent
or backfill the evidence model.

## D10: Legacy classification uses a versioned supported manifest

Status: accepted by the user on 2026-07-11 after internal review repair.

Non-empty legacy registries require a versioned JSON classification manifest
processed by a supported management/preflight tool. Entries bind exact legacy
actor ID, canonical issuer, opaque subject, and `subject_kind`. The tool rejects
duplicates, stale/missing rows, mismatches, unknown fields, and unsupported
kinds; supports dry-run; emits a checksum-bound report; and never writes grants.
The schema migration consumes only validated staged classification evidence or
fails closed. Manual SQL is not a supported path.

## D11: Contributor is the human product term

Status: accepted by the user on 2026-07-11.

Contributor is the umbrella term for a human participating in Workstream. A
contributor has an exact-project `submitter`, `reviewer`, or `both` grant.
Celery, checker, setup, and reconciliation workers are internal services and
background jobs, not human product roles. Existing human-role
values using the old term are migration inputs to remove, not target product
vocabulary or authority concepts.
