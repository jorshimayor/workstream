# WS-AUTH-001-09A PR Trust Bundle

## Chunk

`WS-AUTH-001-09A` - Fixed Service Identity Foundation

## Goal And Human-approved Intent

Give every internal service ActorProfile one stable ServiceAccount-style local
identity, keep its Identity Issuer subject as a separate credential link, and
define one closed service-action matrix without provisioning or activating a
service authority path.

## What Changed And Why

- Added seven fixed service identities and a unique immutable
  `ActorProfile.service_identity` for service profiles only.
- Added eight planned AUTH-09 route actions and extended PostgreSQL audit parity
  without changing the nine active actions.
- Added one static seven-identity/eleven-action matrix with exact row,
  PermissionId, ActionOwner, and planned-state validation.
- Added guarded migration `0023` plus a confidential exact-set operator tool for
  any preexisting service profiles.
- Retained only immutable counts and non-secret digests as migration evidence.

## Design Chosen

The ActorProfile is the stable local principal, comparable to a Kubernetes
ServiceAccount name plus server-generated UID. The external `(issuer, subject)`
is only the credential link. Authority candidates come from reviewed typed code,
not email, token roles, display fields, grants, dynamic assignment rows, or
request input.

## Alternatives Rejected

No service registration table, database action-assignment table, inferred
identity, deterministic ID from issuer/subject, generic service locator, seeded
actor, service grant, or active artifact action was added.

## Scope And Product Behavior

This is schema/catalogue/migration foundation only. It adds no route, actor or
link provisioning, service-token admission, artifact resource composer,
evaluator, grant, or executable permission. Internal services are not human
Contributors.

## Acceptance Criteria Proof

- Exact zero/subset/all-seven private mapping and database binding pass.
- Missing, stale, noncanonical, in-repository, or insecure mapping evidence
  fails closed with redacted errors.
- Actor kind/identity uniqueness and immutability pass direct SQL tests.
- Migration evidence rejects malformed values and update/delete/truncate.
- All eight new route actions and eleven service actions remain planned.
- Downgrade rejects any fixed identity or any of the eight new evidence actions.

## Tests And Test Delta

- 379 isolated behavior and full Alembic tests passed.
- 47 focused adversarial mapping/path tests passed.
- Actors branch coverage: 90.55 percent.
- Authorization branch coverage: 91.50 percent.
- Mapping module branch coverage: 95.91 percent.
- Tests are additive; no skip, assertion weakening, exclusion, or threshold
  change was made.

## CI Integrity And Reviewer Results

Ruff, merge-intent validation, all stale scans, links, 71 agent-gate tests,
docstring coverage, and diff integrity pass. Exact reviewed SHA
`beab5d9149a04c5ab0f8f4ce226b1b61ce24190a` passed senior engineering,
QA/test, security/auth, product/ops, architecture, CI integrity, docs,
reuse/dedup, and test-delta review after all valid findings were repaired.

## External Review

The first GitHub Backend and Agent Gates runs passed. CodeRabbit found two
valid issues: mutable historical migration imports and cross-event-loop engine
cleanup. The repair packages a versioned migration-only `0023` contract and
uses one async execution/cleanup loop with explicit error precedence. Focused
regressions include installed-wheel location independence and cleanup
cancellation precedence; refreshed external checks remain pending on the repair
head.

## Remaining Risk

A host crash during direct private-envelope publication may require regenerating
the file. Migration still rejects missing, partial, or unverifiable evidence,
so this cannot activate authority.

## Follow-up Work

AUTH-09B may later provision the fixed service ActorProfiles and credential
links after this PR merges, signed memory updates, and the user explicitly
starts it. Activation custody for ART/REV/CON remains a separate reviewed
decision and is not resolved here.

## Human Review Focus And Merge Ownership

Review the ServiceAccount-style identity model, strict private mapping custody,
exact matrix metadata, inert actions, immutable evidence, and lack of assignment
rows. Only the human may approve and merge this PR.
