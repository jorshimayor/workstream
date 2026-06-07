# ADR 0004: v0.1 Implementation Stack Is Locked

## Status

Accepted

## Context

Workstream needs to move quickly through the first internal loop without reopening stack debates every chunk.

The stack still needs clean boundaries so a later specialized runtime can be added when there is a clear reason.

## Decision

The v0.1 implementation stack is:

- Backend API: Python with FastAPI
- ORM and migrations: SQLAlchemy 2.x async with Alembic
- API schemas: Pydantic schemas
- Frontend: React + Vite + TypeScript
- Database: Postgres

Workstream is a modular monolith for v0.1. Routers handle HTTP, services own business rules, repositories own database access, interfaces define external boundaries, and adapters implement those boundaries.

Rust, TypeScript backend services, or another language can be introduced later only for a specific layer with a documented reason.

## Consequences

Positive:

- implementation chunks have a stable default
- review can focus on workflow correctness instead of stack selection
- API and database contracts stay explicit
- later specialized runtimes remain possible behind interfaces

Tradeoff:

- some future optimizations wait until the internal loop proves them necessary
- stack changes require a new ADR or an amendment to this one
