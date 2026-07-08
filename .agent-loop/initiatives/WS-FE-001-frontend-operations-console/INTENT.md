# Intent: WS-FE-001 — Frontend Operations Console

## Problem

`AGENTS.md` and `docs/architecture_system_architecture.md` lock the frontend as a
React + Vite + TypeScript internal operations UI, but no canonical frontend
exists. Backend contracts for auth, tasks, projects, checkers, and actors are now
stable, and the upstream frontend epic (`Flow-Research/workstream#29`) with its
starter issue (#50) is ready to start.

## Goal

Build the canonical Workstream operations console incrementally, one screen family
at a time, against the paper-and-ink design system, so operators (project manager,
worker, reviewer, admin/finance) can run the internal loop through a UI.

## Non-goals (v0.1)

- No Workstream-owned auth: Flow token handoff only (ADR 0006).
- No marketing site; operations/workflow surfaces only.
- No dark theme, no heavy component library.
- No screens whose backend contracts are not yet stable (e.g. payment/reputation
  screens wait on their backends).

## Design source of truth

`docs/design_system.md` and `docs/website_flow.md`.

## Sequencing

Foundation first (`WS-FE-001-01`, upstream #50), then screen chunks following the
`docs/website_flow.md` build order: task queue, review, dashboard, guides,
contribution record, audit.
