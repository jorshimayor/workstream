# DECISIONS: WS-ENG-001

## Accepted

- Use `.agents/skills/` for repo-scoped Codex skills.
- Use `.codex/agents/` for Codex custom reviewer agents.
- Use `.agent-loop/` for durable engineering memory and evidence.
- Do not copy Claude-specific files into Workstream in this bootstrap.
- Add Product/Ops as a first-class reviewer track.
- Preserve existing `docs/internal_reviews/` evidence compatibility.
- Treat the manager-approved implementation PR as the only human merge
  checkpoint. Post-merge state is deterministic process output, not another
  reviewable chunk.
- Store canonical live merge state on `automation/loop-memory` so protected
  `main` is never bypassed and generated bookkeeping needs no PR.
- Require one strict, newly added merge-intent JSON file in every reviewed PR
  rather than deriving chunk or next-gate intent from mutable prose, branch
  names, or chat history.
- Run the write-capable workflow only from trusted code already merged to
  `main`; never use `pull_request_target` or pull-request-head execution.

## Deferred

- Packaging the loop as a reusable Codex plugin for other Flow projects.
- Adding hooks that block local PR creation before evidence exists.
- Automating reviewer fanout beyond Codex's explicit subagent workflow.
- Packaging generated-state storage behind a GitHub App or external service;
  the repository-scoped automation branch is sufficient for the current loop.
