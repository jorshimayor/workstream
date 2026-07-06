# Risks: WS-POL-001 - Submission Artifact Policy Foundation

| Risk | Impact | Mitigation |
|---|---|---|
| Big-bang lifecycle rewrite | High | Split policy, generation, submission runtime, post-submit split, and revision proof into separate chunks. |
| Default policy can be weakened | High | Validate effective policy rejects any project policy that removes or downgrades defaults. |
| Project owner schema burden | High | Project owners provide plain-language material; Workstream derives policy and actors with the `admin` or `project_manager` role approve it. |
| Naming drift | High | Human review field names before migrations. |
| Worker-facing internal route leakage | Medium | Keep `task_setup_blocked` and `checker_retry` internal; expose `needs_revision` only when worker action is needed. |
| Stale construction-state field drift | Medium | Removed guide-field artifact rules, task-level artifact/evidence shortcuts, and generic checker-policy version locks; keep stale wording scans and request-body tests fail-closed. |
| Worker enqueue durability gap | Medium | Current Celery enqueue semantics are honest after commit; add a durable outbox later if guaranteed eventual enqueue is required. |
| Agent scope creep | Medium | Project setup agent execution is now isolated behind Celery; future agent expansion must stay behind chunk contracts and must not run inline in request handlers. |
| Insufficient real API proof | High | Require Postgres-backed API tests and real API drill before closing the initiative. |
