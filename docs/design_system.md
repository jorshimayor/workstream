# Workstream design system

Source of truth for the visual design of the Workstream internal operations
console (`frontend/`). Extracted from flowresearch.tech and adapted for a working
console. Paired with [`website_flow.md`](website_flow.md), which specifies the
screen flow on top of this system.

## 1. Direction, in one line

**An editorial research journal that happens to run a task pipeline.** Flow
Research's own site reads like a literary/academic publication — warm paper
background, high-contrast serif headlines, quiet monospace metadata, hairline
rules, almost no color. Workstream borrows that exact calm, confident,
publication-grade restraint and applies it to a working console: dense records
instead of essays, status instead of read time, but the same typographic
hierarchy and the same refusal to decorate.

Anti-references: no dashboard-template gradients, no card-shadow SaaS look, no
dark hacker-terminal green-on-black. If a screen looks like it could be a
Bloomberg terminal or a generic admin template, it's wrong. If it looks like a
page from Flow Research that happens to have a "claim" button, it's right.

## 2. Color

Background is warm and light throughout — this is a paper-and-ink system, not a
dark-mode system. Color is reserved almost entirely for state; everything else is
ink, paper, and one hairline gray.

| Token | Hex | Usage |
|---|---|---|
| `--paper` | `#F3EFE3` | Page background, everywhere |
| `--paper-raised` | `#FAF8F1` | Rare — a single elevated surface (e.g. command palette overlay) |
| `--ink` | `#1A1A22` | Primary text, headlines |
| `--ink-soft` | `#5A5850` | Body copy, descriptions |
| `--ink-muted` | `#8C887D` | Metadata, labels, timestamps, placeholder text |
| `--hairline` | `#DAD5C4` | All dividers and borders — always 0.5–1px, never heavier |
| `--accent` | `#3E7CB1` | Links, the wordmark mark, focus states, the command prompt caret — used sparingly |
| `--accent-soft` | `#E6EEF5` | Rare hover fill behind accent text |

State colors — desaturated, ink-mixed, never neon. These are the only saturated
colors in the system and they carry meaning, nothing else:

| Token | Hex | Meaning |
|---|---|---|
| `--state-ready` | `#3B6D11` (text) / `#EAF3DE` (fill) | ready, passed, accepted |
| `--state-pending` | `#854F0B` (text) / `#FAEEDA` (fill) | in progress, pending payment, awaiting action |
| `--state-blocked` | `#993C1D` (text) / `#FAECE7` (fill) | needs revision, warning-level check |
| `--state-rejected` | `#A32D2D` (text) / `#FCEBEB` (fill) | rejected, failed check |

Rules:

- Never place a state color on a large surface. It appears as small text, a 1–2
  word pill, or a thin left-border accent on a row — never as a background fill
  for a whole card or page.
- No gradients, no drop shadows, no glassmorphism, no glow. A hairline and
  whitespace do the work a shadow would do elsewhere.
- Dark mode is out of scope for v0.1 — this is a paper-first system by design.

## 3. Typography

Two families carry the entire interface. Never blend them within a single text
element.

**Editorial serif** — for anything a human reads as content: record titles, task
names, descriptions, section headers, the wordmark. Implemented with Source
Serif 4 (variable) as the licensed-face stand-in.

**Monospace** — for anything the system reports: record IDs, timestamps, status
labels, tags, the command prompt, keyboard shortcuts, filter chips. Always
uppercase, always letter-spaced (`0.04em`). Implemented with IBM Plex Mono.

No third font. No sans-serif anywhere in this system — even UI chrome like nav
labels stays serif.

### Scale

| Role | Family | Size | Weight | Notes |
|---|---|---|---|---|
| Display / hero statement | Editorial serif | 48–64px | 700 | Used once per screen at most |
| Record title (H1 in a detail view) | Editorial serif | 32px | 700 | |
| List-row title | Editorial serif | 20px | 700 | |
| Section heading | Editorial serif | 22px | 700 | |
| Body / description | Editorial serif | 15–16px | 400 | line-height 1.6 |
| Metadata / label / status | Mono | 11px | 400–500 | uppercase, letter-spaced |
| Command prompt input | Mono | 14px | 400 | |

## 4. Layout

- **Grid, not cards.** Content sits directly on the paper background, separated by
  hairline rules. Lists are rows, not cards.
- **Three-column row pattern** for list screens (task queue, review queue, audit
  log): left column (fixed ~110–140px) mono metadata; center column (flexible)
  serif title + serif description stacked; right column (fixed ~140px,
  right-aligned) mono status label or a link with an arrow icon.
- **Generous vertical rhythm.** Rows get 18–24px padding top and bottom; sections
  get 64–96px between them. Density comes from column discipline, not tight
  spacing.
- **Container width:** max 1100–1200px, centered, with 32–48px side margins.
- **Hairline dividers** (`--hairline`, 0.5px) between every row and every major
  section — the primary structuring device, replacing borders/shadows/cards.
- **Top nav:** paper background, no elevation, bottom hairline only. Wordmark left
  (serif, bold, small icon mark in `--accent`), primary nav center-left (serif,
  regular), one right-aligned utility element.

## 5. Components

- **Wordmark** — a small line-mark in `--accent` + "Workstream" in editorial
  serif, bold, 17px, left-aligned in the nav.
- **Nav link** — editorial serif, 15px, regular weight, `--ink`. No underline at
  rest; `--accent` on hover/active. No pill backgrounds, no active-tab bar.
- **List row** — the core repeating unit: full-width hairline top and bottom,
  generous padding, three-column grid, entire row clickable, subtle title color
  shift to `--accent` on hover.
- **Status label** — mono, uppercase, 11px, letter-spaced, colored per the state
  table. Never a filled pill or badge — plain colored text.
- **Tag list** — mono, uppercase, small, `--ink-muted`, separated by a literal
  " / " character, no chips or borders.
- **Link with arrow** — serif or mono with a small outline diagonal-arrow icon
  (↗) trailing, `--ink` at rest, `--accent` on hover. No button chrome.
- **Command prompt** — a single-line mono input shown as a `>` caret in `--accent`
  followed by placeholder text in `--ink-muted`. Summoned with `:`; never a modal.
- **Inline confirm** — for destructive or terminal actions, the row expands in
  place to reveal a mono input requesting a short typed reason, hairline top
  border — never a modal dialog.
- **Icons** — thin single-weight outline icons only, never filled, never colored
  except inheriting `--accent` on interactive elements.

## 6. Motion

Minimal and functional only:

- Hover: color transition on text only (title → `--accent`), 120ms ease, no
  scale/shadow changes.
- Row expand (inline confirm): height/opacity transition, 160ms ease-out.
- No page-transition animation, no skeleton shimmer.

## 7. Voice

- Sentence case everywhere — headings, labels, buttons. Uppercase is a
  type-system choice for mono metadata only, not a voice choice.
- Plain, declarative, unhurried. State facts; avoid exclamation points,
  "successfully," and filler like "seamless" or "simply."
- Status is reported, not celebrated: "checks: 4/4 passed," not "All checks
  passed! 🎉"

## 8. What not to do

- No cards with shadows or rounded-rect containers around list items.
- No colorful dashboard summary tiles or icon-in-a-circle stat blocks.
- No dark theme, no neon, no terminal-green-on-black.
- No sans-serif typeface anywhere.
- No modal dialogs for routine actions — use inline row expansion instead.
- No more than one accent color and four state colors on any single screen.
