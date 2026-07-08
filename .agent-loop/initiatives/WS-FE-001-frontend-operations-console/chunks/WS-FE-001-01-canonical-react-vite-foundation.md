# Chunk Contract: WS-FE-001-01 — Canonical React + Vite App Foundation

## Parent initiative

WS-FE-001 — Frontend Operations Console

> **Prerequisite note.** WS-FE-001 is a new, large initiative and per `AGENTS.md`
> ("an initiative plan for large work") it needs `INTENT.md`, `PLAN.md`, and
> `CHUNK_MAP.md` before the second chunk. This foundation chunk is bounded and can
> be contracted first, but the initiative plan should be authored and human-approved
> immediately after this contract is accepted.

## Upstream issue

Flow-Research/workstream#50 — "Frontend: Canonical React + Vite app foundation"
(parent epic #29; area/frontend, priority/P0, focus/v0.1). This contract maps
directly to that issue's five acceptance criteria. Contribution path: sync then
branch off `upstream/main`, push to `origin` (fork `jorshimayor/workstream`), PR
into `Flow-Research/workstream`.

> **Two ground-truth notes recorded during discovery:**
> 1. The fork `main` is 10 commits behind `upstream/main` (missing WS-POL-001-14).
>    Sync before branching.
> 2. Issue #50's "Why" states the repo "currently has only `demos/week1_api_demo_ui`".
>    That directory exists on **neither the fork nor `upstream/main`**, and no
>    README "demo UI" note exists either. There is no demo UI to retire; the
>    "demo UI separated or retired" criterion is met by documenting this, not by
>    removing a nonexistent artifact. Flag the stale premise to the maintainer.

## Goal

Establish the single canonical React + Vite + TypeScript operations app under
`frontend/` that proves a live connection to the backend and gives every later
frontend chunk a shell to build into.

Scope is deliberately modest and matches issue #50 exactly: the app builds, it
calls `/api/v1/health` and `/api/v1/auth/me` against the backend with Flow-style
bearer-token handling, its shell carries navigation placeholders for the five
operations surfaces, and the docs explain how to run it. It applies the
`design.md` visual language to the shell so the look is correct from the start,
but it does **not** build the full primitive library, keyboard model, or any real
screen — those are later chunks.

## Why this chunk exists

`AGENTS.md` locks the frontend as React + Vite + TypeScript and
`docs/architecture_system_architecture.md` gives that stack the internal
operations UI, but no canonical app exists yet. `docs/roadmap_30_day_master_plan.md`
sequences dashboards and review UI after backend contracts stabilize — which they
now have for task/project/checker/actor and for auth (`/api/v1/auth/me` and
`/api/v1/health` are live). This chunk creates that canonical foundation and
proves backend connectivity, unblocking the per-surface screen chunks
(#49/#51/#52/#56).

## Approved plan reference

- Authoritative scope: Flow-Research/workstream#50 (parent #29)
- INTENT: `.agent-loop/initiatives/WS-FE-001-frontend-operations-console/INTENT.md` *(to be created)*
- PLAN: `.agent-loop/initiatives/WS-FE-001-frontend-operations-console/PLAN.md` *(to be created)*
- CHUNK_MAP: `.agent-loop/initiatives/WS-FE-001-frontend-operations-console/CHUNK_MAP.md` *(to be created)*
- Design reference (committed in-repo by this chunk): `docs/design_system.md`,
  `docs/website_flow.md` — the visual language for the shell and all later chunks.

## Risk class

L2 — additive and frontend-only (no backend, data, migration, or auth-boundary
change), but architecturally load-bearing: it fixes the canonical app location,
routing, API-client, and token-handling conventions every later frontend chunk
inherits. Requires the architecture reviewer.

## SLA

P0

## Allowed files

```text
frontend/**
docs/design_system.md
docs/website_flow.md
docs/decision_0012_frontend_stack_and_design_system.md
docs/architecture_system_architecture.md
README.md
.gitignore
.github/workflows/**
.agent-loop/LOOP_STATE.md
.agent-loop/WORK_QUEUE.md
.agent-loop/initiatives/WS-FE-001-frontend-operations-console/**
```

## Not allowed

```text
backend/**
any change to the /api/v1 request/response contract
real screen content or business logic for guides, task queue, worker tasks,
review, dashboards, contributions, or audit (navigation placeholders only)
the full reusable primitive library and global keyboard model (deferred to a
follow-up chunk and the per-screen chunks #49/#51/#52/#56)
payment, reputation, or finance UI logic
a dark theme or theme-switching system (paper-first only, design.md)
any sans-serif typeface (design.md)
any opinionated UI component kit: Material/MUI, Bootstrap, Chakra, Ant Design,
Tailwind UI kits, or similar (design.md, flow handoff notes)
Workstream-owned login, signup, password, or session storage (Flow token
handoff only — ADR 0006, AGENTS.md)
```

## Implementation boundaries

- Stack is locked: React + Vite + TypeScript. Routing via React Router; a single
  native `fetch` wrapper for the API client; unit tests via Vitest + React
  Testing Library. No visual component library, no server-state cache library in
  this chunk (kept minimal; add later if a screen chunk needs it).
- Auth: the client attaches a Flow-style bearer token to backend calls and reads
  it from a single configurable source (env/local input for dev). It stores no
  credentials and owns no session primitives; the unauthenticated `/auth/me`
  response is handled as a first-class state, not an error crash.
- Visual language comes only from `design.md`: warm paper background, editorial
  serif for content, uppercase letter-spaced IBM Plex Mono for metadata/status,
  hairline dividers, no cards/shadows, one accent plus the state colors used as
  small text only. Fonts: IBM Plex Mono for mono; editorial serif via a licensed
  face if available, else the approved Google Fonts stand-in (Source Serif 4 /
  Newsreader / Lora) per `website-flow.md`, self-hosted or pinned.
- Navigation placeholders name the five operations surfaces from issue #50 —
  project setup, task queue, worker tasks, review queue, dashboards — mapped to
  the project-manager / worker / reviewer / admin-finance roles. Full nav-label
  and role-visibility reconciliation with `website-flow.md` happens in the screen
  chunks.
- The canonical UI lives at `frontend/`. Because no demo UI exists in the tree,
  the docs must state that `frontend/` is the one canonical UI and note the stale
  issue reference; nothing is "retired".

## Acceptance criteria

Mapped to issue #50 (first five are the issue's own criteria):

- [ ] Canonical `frontend/` React + Vite + TypeScript app builds with TypeScript
      (`npm run build` and `tsc --noEmit` both clean).
- [ ] The app calls `GET /api/v1/health` against the backend and renders the
      connectivity result.
- [ ] The app calls `GET /api/v1/auth/me` with a Flow-style bearer token and
      renders the current actor (name/role), handling the unauthenticated case
      gracefully.
- [ ] The app shell includes navigation placeholders for: project setup, task
      queue, worker tasks, review queue, dashboards.
- [ ] Docs state that `frontend/` is the canonical UI and record that the
      `demos/week1_api_demo_ui` named in issue #50 is not present on
      `upstream/main` (nothing to retire) — the "demo UI separated or retired"
      criterion, satisfied by documentation.
- [ ] README/docs are updated with how to run the canonical frontend against the
      backend (install, dev server, backend base URL, dev token).

Supporting quality gates:

- [ ] The API client is a single typed `fetch` wrapper targeting `/api/v1` with
      bearer-token handling and a typed error shape.
- [ ] The shell applies the `design.md` visual language (paper background,
      serif content, uppercase mono metadata, hairline dividers, no cards/shadows);
      no sans-serif face, no dark theme, and no UI component kit is present in
      `package.json`.
- [ ] Lint, typecheck, unit tests, and build all pass in a new `frontend` CI job.
- [ ] Screenshot evidence of the shell (nav placeholders + health/actor status)
      matches `design.md`.

## Verification commands

```bash
git fetch upstream
cd frontend && npm ci
cd frontend && npm run lint
cd frontend && npm run typecheck          # tsc --noEmit
cd frontend && npm run test -- --run      # vitest
cd frontend && npm run build
# manual backend-connectivity proof (dev): with backend running, load the app and
# confirm /api/v1/health and /api/v1/auth/me render; capture as evidence.
# repo loop + docs gates for the contract and design docs
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_loop_memory_state.py
python3 scripts/workstream_agent_gate.py --base upstream/main --head HEAD --format json
```

## Required reviewers

Every listed reviewer must end with one exact result value:

- `PASS`
- `PASS AFTER FIXES`
- `PASS WITH LOW RISKS`
- `N/A - with approved reason`

Required:

- senior engineering
- QA/test
- security/auth — bearer-token handling only; assert no credential/session storage
- product/ops
- architecture — establishes canonical app location, routing, API-client, tokens
- docs — README run instructions, in-repo design/flow docs, new ADR, arch doc note
- CI integrity — new `frontend` workflow, `package.json`, build/test config
- reuse/dedup — API client and shell are single-source, not duplicated
- test delta — new Vitest suites for the client wrapper and shell

## Human review focus

- The three backend-connectivity criteria genuinely work: `/api/v1/health` and
  `/api/v1/auth/me` are called against a running backend with a real bearer token,
  and the unauthenticated path is handled, not crashed.
- Scope stayed at foundation: navigation is placeholders only; no screen content,
  primitive library, or keyboard model leaked in.
- Strictly additive and frontend-only — no `backend/**` or `/api/v1` contract drift.
- No Workstream-owned auth: token handling only, no credential/session storage (ADR 0006).
- No heavy UI component kit and no sans-serif face entered the dep tree.
- Docs correctly record the stale demo-UI premise instead of inventing a retirement.

## Stop conditions

Stop and escalate if:

- scope must expand beyond the allowed files (e.g. a placeholder needs a new backend endpoint)
- the design direction in `design.md` must change to proceed
- an auth/session/data boundary change becomes necessary to call `/auth/me`
- CI/test must be weakened to pass
- the same blocker remains after 2 repair attempts
- secrets or production data are needed
```
