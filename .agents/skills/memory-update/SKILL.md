---
name: memory-update
description: Update durable repo memory after planning, merge, rejection, blocker, or repeated agent mistake.
---

# Memory Update

Use before publication to provide bounded next-state metadata, and use the
generated state after merge.

## Before Merge

- Put one valid `workstream-loop-state` JSON marker in the PR body.
- Record the initiative, completed chunk, title, next chunk or `null`, and
  whether the next chunk requires a separate explicit start.
- Keep implementation/specification memory in the owning PR where it can be
  reviewed with the change.

## Generated After Merge

The trusted `Loop Memory` workflow records:

- `.agent-loop/STATE.json`
- `.agent-loop/LOOP_STATE.md`
- `.agent-loop/MERGE_LOG.jsonl`

on `automation/loop-memory`.

Do not open a manual post-merge memory PR or rerun internal reviewers when this
automation succeeds.

## Manual Updates As Applicable

- `.agent-loop/LOOP_STATE.md`
- `.agent-loop/WORK_QUEUE.md`
- `.agent-loop/REVIEW_LOG.md`
- initiative `STATUS.md`
- initiative `DECISIONS.md`
- initiative `RISKS.md`
- chunk contract status notes

## Capture

- What was completed
- What was merged/rejected/blocked
- PR links
- Remaining risks
- Follow-up items
- Repeated agent mistakes
- Policy/skill improvements needed

## Rules

- Durable repo memory beats chat memory.
- Do not bury decisions in conversation only.
- If a repeated issue appears, suggest policy/skill update.
- Generated state is exempt from repeated review only on
  `automation/loop-memory` and only when written by the trusted workflow.
- If automation fails, use `workflow_dispatch` with the exact merge SHA after
  correcting metadata or permissions. Do not hand-edit generated state.
