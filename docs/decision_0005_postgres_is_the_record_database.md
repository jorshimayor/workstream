# ADR 0005: Postgres Is The Record Database

## Status

Accepted

## Context

Workstream depends on database-enforced lifecycle and policy invariants.

The project guide foundation already relies on Postgres behavior such as partial unique indexes and composite foreign keys tying guide policies to guide versions.

Using a different local or CI database can hide production failures or create false confidence.

## Decision

Postgres is the record database for local development, CI, and production.

SQLite is not a supported test target for Workstream backend behavior.

Local development uses the repository Docker Compose Postgres service. CI uses a Postgres service container. Production uses managed or operator-provided Postgres.

## Consequences

Positive:

- local, CI, and production validate the same database family
- database constraints can be trusted as part of the product contract
- migration smoke tests exercise Postgres DDL directly
- review findings about Postgres-specific behavior are not hidden by a fallback database

Tradeoff:

- local backend tests require a running Postgres service
- CI must provision a Postgres service container
