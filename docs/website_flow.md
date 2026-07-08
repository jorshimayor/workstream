# Workstream website flow

Full site flow and screen-by-screen spec for the v0.1 internal operations console.
Every screen is designed against [`design_system.md`](design_system.md) — read
that first for color, type, and component rules. This file is the flow and content
layer on top of it.

> **Foundation reconciliation note.** The first frontend chunk (WS-FE-001-01,
> upstream issue #50) scaffolds the app shell with navigation *placeholders* for
> the five operations surfaces named in that issue — project setup, task queue,
> worker tasks, review queue, dashboards. The full route set and nav labels below
> are the target; they are reconciled with the placeholders as each screen chunk
> lands.

---

## 1. Sitemap

```
/login                     session start (Flow token handoff)
/                           dashboard (role-aware)
/guides                     project + guide list          [Project Manager]
/guides/:id                 guide & policy editor          [Project Manager]
/tasks                      task queue                     [all roles]
/tasks/:id                  task detail + claim + submit   [Contributor]
/review                     review queue                   [Reviewer]
/review/:id                 review decision                [Reviewer]
/contributions/:id          contribution / payment / reputation record   [read-only, all roles]
/audit                      audit console                  [Operator / Admin]
```

Four roles share one navigation shell; the nav and dashboard adapt per role, but
every URL is reachable by anyone with permission — Workstream doesn't fork into
separate apps per role. ("Contributor" below is the human-facing name for the
`worker` actor profile in `docs/glossary.md`.)

## 2. Navigation shell (present on every screen except login)

Layout, left to right, single row, bottom hairline, paper background, no
elevation:

1. Wordmark: small accent-colored mark + "Workstream" in editorial serif, bold —
   links to `/`.
2. Primary nav, serif regular — only the items the current actor has permission
   for are shown (a Contributor never sees Audit; a Reviewer sees Tasks + Review;
   a Project Manager sees Tasks + Guides; Operator/Admin sees all).
3. Right-aligned: current actor name (mono, muted) and a command-prompt trigger
   (`:`).

Global keyboard model:

| Key | Action |
|---|---|
| `:` | Open command prompt — type an action or record id directly |
| `/` | Search across tasks, guides, submissions |
| `g t` / `g r` / `g g` / `g a` | Go to Tasks / Review / Guides / Audit |
| `j` / `k` | Move down / up a list |
| `Enter` | Open selected row |
| `Esc` | Back out one level, or collapse an inline confirm |

## 3. Role entry flows

- **Project Manager** — dashboard shows "guides awaiting activation" and "tasks
  awaiting screening" → Guide editor, then Task queue.
- **Human-Agent Contributor** — dashboard shows "ready tasks matching your scope"
  → Task queue → Task detail (claim) → Submission packet.
- **Reviewer** — dashboard shows "needs your review" → Review queue → Review
  decision, repeated via `n`/`p`.
- **Operator / Admin** — dashboard shows recent audit events and flagged records →
  Audit console, with one-key override into any record.

## 4. Screens

Each screen spec has the same shape: purpose, layout (mapped to the three-column
row pattern or a detail-view pattern), content, states, and the UX flow.

### 4.1 Session start — `/login`

Exchange a Flow-issued token for a Workstream session. Workstream never owns
signup, password reset, or primary sessions. Full-bleed paper, no nav, centered.
A single serif line ("Verifying your Flow session.") with a mono status line that
updates in place (`token: verifying` → `token: ok` → `redirecting`). On failure,
a mono line in `--state-rejected` with a plain accent link back to Flow. Zero user
steps — the actor arrives already carrying a token.

### 4.2 Dashboard — `/`

Role-aware landing view — a jumping-off point, not a workspace. A short serif
intro ("Here's what needs you today"), then one or two list-row groups, each with
a small mono section label (e.g. "NEEDS YOUR REVIEW (4)"), rows in the standard
three-column pattern, hairline-divided. Empty state is a plain serif line
("Nothing needs you right now."), no illustration.

### 4.3 Guide & policy setup — `/guides` and `/guides/:id`

Project Manager creates a project, drafts a guide, and locks a policy version
before any task under it can reach ready. List uses three-column rows (mono status
/ serif name + description / mono version). Editor is a detail view with a large
serif project title, a mono status line, and a vertical stack of labeled fields
(mono label above serif value), editable inline with underline-on-focus only.
DRAFT (pending state color) vs ACTIVE (ready color). Activating locks the guide
and policy in one action; no modal.

### 4.4 Task queue — `/tasks`

Every role's shared view into task state. The clearest application of the
three-column row pattern: left = mono task id + date, center = serif task title +
one-line guide/claimant context, right = mono status label in the appropriate
state color. A thin mono filter/sort line sits above the list. Single-key actions:
`c` claim, `Enter` open, `r` jump to review.

### 4.5 Task detail & claim, submission packet — `/tasks/:id`

Two states of one screen. Unclaimed: large serif title, mono "READY," a serif
instructions block (the one place longer body copy appears), a single "claim"
action. Claimed: status "IN PROGRESS," an evidence drop zone (the one exception to
"no borders," since a drop target needs a boundary), a "submit" action. Submitted:
status "SUBMITTED," a mono checker results line (`checks: 4/4 passed`). Three steps
total across the task's life on this screen: claim, attach, submit.

### 4.6 Review queue & review decision — `/review` and `/review/:id`

Reviewer reads evidence and checker output, then issues exactly one of three
decisions: accept, needs revision, reject. Queue uses the task-queue row pattern
filtered to submitted work; right column shows checker pass/fail. Decision view:
large serif submission title, mono check-results line, read-only evidence block,
and — only on a revision replay — a muted serif-italic "prior findings" block.
Three plain mono text actions in one row: accept · request revision · reject.
"request revision"/"reject" expand an inline mono field for findings — never a
modal. `n`/`p` move through the queue without returning to the list.

### 4.7 Contribution, payment & reputation record — `/contributions/:id`

A read-only certification trail, generated automatically on acceptance. Detail
view: serif record title, then a stacked list of mono-labeled / serif-valued
fields (accepted date, payment status, amount, reputation event status). No
charts, no summary tiles. Payment status is its own state-colored mono label
(`PENDING`, `PAID`).

### 4.8 Audit console — `/audit`

Cross-cutting chronological log for Operator/Admin. A dense list variant of the
three-column row: left = mono timestamp, center = serif event description
("review.accept on WS-1042"), right = mono actor id. A thin filter line above.
Overridden records get a small inline mono `--state-pending` marker. Every
override is a single typed command against a record id via the global command
prompt, logged immediately as its own audit row.

## 5. Build order

Matches the backend's own 30-day internal-loop priority — build the narrowest
working loop first, expand outward after it's proven:

1. Task queue + task detail/claim/submit (`/tasks`, `/tasks/:id`).
2. Review queue + review decision (`/review`, `/review/:id`).
3. Dashboard (`/`).
4. Guide & policy setup (`/guides`, `/guides/:id`).
5. Contribution/payment/reputation record (`/contributions/:id`).
6. Audit console (`/audit`).

## 6. Component build notes

- Load `design_system.md` first — it defines every color, font, and component
  referenced above by name (list row, status label, inline confirm, command
  prompt, tag list).
- Reusable components to scaffold, since every screen composes from them: nav
  shell, list row (three-column), detail-view header, status label, command
  prompt, inline confirm.
- No component library with its own opinionated visual style — the
  row/hairline/serif system is intentionally custom and thin; a heavy component
  kit will fight it.
- Fonts: Source Serif 4 and IBM Plex Mono are the freely available stand-ins used
  by the canonical app, self-hosted via `@fontsource`.
