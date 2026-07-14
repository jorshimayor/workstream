# RISKS: WS-ENG-001

| Risk | Severity | Mitigation |
|---|---:|---|
| Generic kit wording conflicts with Workstream language | High | Rewrite policies and AGENTS additions in Workstream terms. |
| Codex does not automatically discover custom agents in a project until trusted | Medium | Keep reviewer requirements in `AGENTS.md` and `.agent-loop` as durable fallback. |
| CI gate creates friction for docs-only work | Medium | Gate reports as sensor; internal evidence gate remains targeted to relevant paths. |
| Future agents still forget subagent review | High | Encode in `AGENTS.md`, `.agent-loop/policies`, PR template, CI evidence gate, and reviewer configs. |
| Agents merge without explicit approval | Critical | Encode no-merge rule in `AGENTS.md`, merge policy, PR template, and trust bundle. |
| Changed-file discovery drifts across gate scripts | Low | Current tests cover the duplicated logic; extract a shared helper in a later cleanup chunk if drift appears. |
| Write-capable workflow is tricked into executing PR code | Critical | Trigger only from protected-main push or explicit replay, run the updater from trusted `main`, disable checkout credential persistence, and never use `pull_request_target`. |
| Automation writes to protected `main` | Critical | Hard-code and test `automation/loop-memory` as the sole push ref; do not create, approve, or merge a bot PR. |
| Concurrent merges race and overwrite state | High | Serialize workflow runs, enforce monotonic merge timestamps, reject conflicting duplicate SHAs, and keep an append-only ledger. |
| Missing PR metadata forces intent inference | High | Agent Gates requires one newly added strict merge-intent JSON file; updater reloads its reviewed head blob and fails closed on missing, modified, duplicate, malformed, or inconsistent metadata. |
| A required check is missing or failed despite merge | High | Record observed conclusions and mark generated integrity as attention required; never report missing evidence as passed. |
| Automation permissions or transient GitHub failure prevent update | Medium | Preserve idempotent trusted-default-branch `repository_dispatch` replay by exact merge SHA; do not hand-edit generated state. |
| Generated branch is edited manually | High | Declare workflow-only ownership, validate JSON/render/ledger agreement, and reject conflicting replay state. |
