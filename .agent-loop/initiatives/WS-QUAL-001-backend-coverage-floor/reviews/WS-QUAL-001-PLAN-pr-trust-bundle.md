# PR Trust Bundle: WS-QUAL-001-PLAN

## Goal and intent

Plan a non-bypassable path from the measured backend coverage baseline to the
user-required permanent 90 percent application floor.

The user corrected the requirement from 80 to 90 percent. The plan treats 90
as repository-wide statement coverage under `backend/app`, not diff coverage.

## What changed

- Added intent, discovery, decisions, risks, plan, status, and six exact chunk
  contracts.
- Recorded the clean isolated diagnostic: 5,660/7,232 statements, 78.26%, about
  849 additional covered statements required for 90% on the AUTH-02 tree.
- Defined safe per-worktree database isolation after a shared database caused
  27 cascading migration errors; the isolated rerun passed 234/234 project tests.
- Updated loop state and queue to show coverage planning active and AUTH-02
  paused before publication.

## Design

Use one coverage/database harness, then bounded additive test chunks for project
service, project boundaries, tasks, checkers, and enumerated residual modules.
The enforced floor never decreases and reaches at least 90 in chunk 06.

Rejected alternatives: a permanently red 90% gate without tests, diff-only
coverage, application exclusions/pragmas, and one giant cross-domain PR.

## Scope and product behavior

Planning and loop-memory files only. No application, test, dependency, workflow,
migration, API, authorization, or product behavior changed.

## Evidence

- Reviewed SHA: `93c2f30c1cfa1d404cb04748c177fd4d8001cd30`
- All nine required internal tracks passed after two repair rounds.
- Stale wording, Markdown links, and diff hygiene passed.
- Test delta: none in this planning PR.
- CI integrity: no CI file changed; future contracts mechanically preserve all
  existing gates and prohibit threshold regression or coverage gaming.

## Remaining risks and follow-up

- Chunk 01 must measure clean main and implement the reviewed harness before
  domain coverage tests begin.
- Each chunk can expose a production defect; that stops coverage work and
  requires a separate corrective change.
- Suite runtime is high, so isolation and exact-tree evidence are operationally
  important; speed work cannot weaken lifecycle or migration proof.

## Human review focus

- Whether staged 82/84/86/88/90 floors are credible and reviewable.
- Whether DB ownership and credential/redaction rules are fail-closed.
- Whether coverage inventory and base-ref comparison prevent gaming/regression.
- Whether pausing AUTH-02 publication is the intended sequencing decision.

## Human ownership

Only the user may approve and merge this planning PR. Planning does not start
`WS-QUAL-001-01`; implementation requires the merged plan, post-merge memory,
and a separate explicit user start.
