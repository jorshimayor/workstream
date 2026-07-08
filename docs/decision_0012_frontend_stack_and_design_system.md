# ADR 0012: Canonical Frontend Is React + Vite + TypeScript With A Paper-And-Ink Design System

## Status

Accepted

## Context

`AGENTS.md` and `docs/architecture_system_architecture.md` lock the frontend as
React + Vite + TypeScript owning the internal operations UI, deferred until
backend contracts stabilize. Those contracts are now stable for auth
(`/api/v1/health`, `/api/v1/auth/me`), tasks, projects, checkers, and actors, so
upstream issue #50 asks for the canonical app foundation. Before this ADR the
repository had no committed frontend, and no committed source of truth for how the
UI should look.

Two decisions needed recording so later screen chunks do not drift: the exact
frontend stack and conventions, and the visual design language.

## Decision

The canonical frontend lives at `frontend/`. There is one operations console; no
separate demo UI exists in the tree. (Issue #50's reference to a
`demos/week1_api_demo_ui` describes a state not present on `upstream/main`.)

Stack and conventions, locked for v0.1:

- React + Vite + TypeScript, strict mode.
- Routing via React Router. A single native `fetch` wrapper (`src/api/client.ts`)
  is the API client; it targets `/api/v1`, attaches a Flow-style bearer token, and
  raises one typed `ApiError` shape on non-2xx. No server-state cache library is
  introduced until a real screen needs one.
- Auth is token-carry only. The app reads a Flow-issued bearer token from an env
  var or local storage and never owns login, signup, password, or server sessions
  (consistent with ADR 0006).
- Testing via Vitest + React Testing Library. Lint via ESLint. Typecheck via
  `tsc --noEmit`. A `frontend` CI job runs lint, typecheck, test, and build.
- No opinionated UI component kit (Material, Bootstrap, Chakra, Ant, Tailwind UI).
  The design system is intentionally thin and custom.

Design language, captured in `docs/design_system.md` and `docs/website_flow.md`:

- A warm paper-and-ink system: `--paper` background, editorial serif (Source
  Serif 4) for content, uppercase letter-spaced monospace (IBM Plex Mono) for
  metadata and status, hairline dividers instead of cards or shadows.
- One accent color plus four desaturated state colors, used only as small text —
  never as a large fill. No dark theme in v0.1. No sans-serif face.
- Fonts are self-hosted via `@fontsource`, so the app makes no external font
  requests.

These documents are the source of truth for every later frontend chunk.

## Consequences

Positive:

- Later screen chunks inherit fixed conventions (app location, routing, API
  client, token handling, test tooling) and a committed visual language, so they
  do not each re-decide the basics.
- The app proves backend connectivity from the first chunk (`/api/v1/health` and
  `/api/v1/auth/me`), catching auth and API-contract drift early.
- The paper-and-ink system keeps the console visually consistent with Flow
  Research's publication aesthetic and avoids generic dashboard styling.

Tradeoff:

- A custom, library-free design system means primitives (list row, status label,
  command prompt, inline confirm) must be built and maintained in-repo rather than
  pulled from a kit.
- Token handling is deliberately minimal in v0.1; a fuller session model arrives
  only if and when the Flow handoff flow requires it.
