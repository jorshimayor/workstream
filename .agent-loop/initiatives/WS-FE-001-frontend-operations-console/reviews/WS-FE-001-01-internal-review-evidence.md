# Internal Review Evidence: WS-FE-001-01 — Canonical React + Vite App Foundation

Chunk: `WS-FE-001-01` (upstream Flow-Research/workstream#50, epic #29)
Branch: `codex/ws-fe-001-01-frontend-foundation` off `upstream/main`

## Automated gates (final, post-fix)

| Gate           | Command                                     | Result                                 |
| -------------- | ------------------------------------------- | -------------------------------------- |
| Lint           | `npm run lint`                              | PASS (exit 0)                          |
| Typecheck      | `npm run typecheck` (`tsc --noEmit`)        | PASS (exit 0)                          |
| Unit tests     | `npm run test -- --run`                     | PASS — 8/8 (client 4, shell 5... 3+5)  |
| Build          | `npm run build`                             | PASS (`dist` built, fonts self-hosted) |
| Markdown links | `scripts/check_markdown_links.py`           | PASS (12 files)                        |
| Stale wording  | `scripts/check_stale_workstream_wording.py` | PASS                                   |
| Loop memory    | `scripts/check_loop_memory_state.py`        | PASS                                   |

Shell verified visually via preview screenshot: nav wordmark + five surface
placeholders, mono status strip (`API: UNREACHABLE / ACTOR: UNAVAILABLE` handled
offline state, since no local backend ≥Python 3.11 was available in the build
environment), paper-and-ink design system, no console errors.

## Acceptance criteria (issue #50)

1. Canonical frontend builds with TypeScript — MET.
2. Calls `/api/v1/health` and `/api/v1/auth/me` — MET (client + BackendStatus;
   URL prefixing now asserted in tests; 401 → handled `signed out`).
3. Nav placeholders for the five surfaces — MET (`src/routes/surfaces.ts`).
4. Demo UI separated or retired — MET via documentation: `demos/week1_api_demo_ui`
   does not exist on `upstream/main`; docs record `frontend/` as the one canonical
   UI and flag the issue's stale premise.
5. README/docs updated to run the canonical frontend — MET.

## Reviewer tracks

| Track                             | Verdict             | Notes                                                               |
| --------------------------------- | ------------------- | ------------------------------------------------------------------- |
| Senior engineering + architecture | PASS AFTER FIXES    | must-fix: frontend CI job; fix NavShell label inconsistency         |
| Security/auth                     | PASS WITH LOW RISKS | token-carry only; add prod-build caveat for `VITE_WORKSTREAM_TOKEN` |
| QA/test                           | PASS WITH LOW RISKS | assert `/api/v1/*` URLs; cover unreachable/authed/not-found         |

## Findings addressed

- \[MAJOR] No `frontend` CI job → added `.github/workflows/frontend.yml` running
  lint + typecheck + test + build on `frontend/**`.
- \[MAJOR] Client tests never asserted the request URL → added assertions that
  `apiFetch` hits `/api/v1/health` and `/api/v1/auth/me`.
- \[MINOR] NavShell collapsed every actor error to `signed out` while BackendStatus
  distinguished 401 → shared `actorErrorLabel` in `components/actor.ts`, used by
  both; a backend outage now reads `unavailable` consistently.
- \[MINOR] Coverage gaps → added tests for authenticated actor (name + roles),
  health-unreachable, and the not-found route (5→8 tests).
- \[MINOR] `useAsync` load-once footgun → added an optional `deps` argument so
  screen chunks can pass `[id]`; default preserves load-once.
- \[MINOR] `VITE_WORKSTREAM_TOKEN` prod-build risk → README caveat: dev-only, never
  in a production build.
- \[MINOR] Glossary drift ("Contributor" vs `worker`) → note added in
  `docs/website_flow.md` mapping the human-facing name to the `worker` profile.

## Deferred (documented, not blocking)

- `useAsync` AbortController cancellation — add when a frequently-mounted screen
  needs it.
- `setToken`/`clearToken` currently unused — retained as the minimal dev-token
  API for a later dev-token input control.
- Bearer attached regardless of `VITE_API_BASE_URL` origin — documented that the
  base must be a trusted backend origin; guard can be added if remote bases arrive.

## Open sub-agent sessions

None remain open at report time.
