# Plan: WS-FE-001 — Frontend Operations Console

## Approach

Deliver the console as a sequence of bounded chunks, each mapped to an upstream
issue under epic #29, each following the repository loop (contract → implement →
evidence → internal review → PR → human checkpoint). The foundation chunk fixes
the conventions every later chunk inherits; screen chunks then wire one surface at
a time to its stable backend contract.

## Locked conventions (set by WS-FE-001-01, see ADR 0012)

- Stack: React + Vite + TypeScript, strict.
- Routing: React Router. API client: one native `fetch` wrapper at
  `src/api/client.ts` targeting `/api/v1`, bearer-token attach, typed `ApiError`.
- Auth: token-carry only (env/local storage); no login/session ownership.
- Tests: Vitest + React Testing Library. Lint: ESLint. Typecheck: `tsc --noEmit`.
- CI: a `frontend` workflow runs lint, typecheck, test, build.
- Design: paper-and-ink system, no component kit, no sans-serif, no dark theme.

## Chunk sequence

See `CHUNK_MAP.md`. Foundation is active; screen chunks are planned and each needs
its own start signal.

## Risks

- Backend contract gaps for a given screen → a chunk stops and escalates rather
  than inventing endpoints (stop condition in each chunk contract).
- Design drift → `docs/design_system.md` is the single arbiter; deviations require
  an ADR update, not ad-hoc styling.
