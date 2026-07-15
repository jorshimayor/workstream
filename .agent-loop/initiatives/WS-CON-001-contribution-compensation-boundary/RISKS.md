# Risks: WS-CON-001 Contribution Record And Compensation Boundary

| Risk | Severity | Mitigation | Owner | Status |
|---|---|---|---|---|
| Candidate spec replaces canonical API/permission/storage rules | Critical | Preserve as input; reconcile into active spec with ADR precedence and exact scans. | WS-CON-001-01 | Open |
| Dual `PaymentPolicy` and `CompensationPolicyVersion` truth | Critical | D2 approved complete removal; 05A cuts all consumers atomically and 05B drops schema under a zero-consumer scanner. | WS-CON-001-05A/B | Direction resolved; implementation open |
| Existing rows lack safe frozen compensation refs | High | CON-05A classifies/drains or approved-backfills; migration fails on ambiguity and never guesses conversion. | Human / WS-CON-001-05A | Legacy rule decision needed |
| Bound adapter callback lacks a safe current service permission | Critical | AUTH-owned additive service-only PermissionId/action, fixed actor, exact binding guards. | WS-AUTH | Open |
| Shared outbox dispatcher borrows human retry/reconciliation authority | Critical | Add service-only `outbox.dispatch`, fixed dispatcher assignment, and claimed-command generation guards in CON-02B; CON-08A is only a handler. | WS-AUTH / WS-CON-001-02B | Open |
| Review/CON circular dependency | High | Interleaved gates: policy schema -> lease schema -> freeze -> claims -> participant -> integration. | WS-CON / WS-REV | Mitigated in plan |
| Partial Review/contribution/economic commit | Critical | Caller-owned session, shared lock order, DB constraints, fault injection, exact replay. | WS-CON-001-07 / WS-REV | Open |
| Direct provider call bypasses ART controls | Critical | Named `WS-ART-001-CON-EVIDENCE` capability prerequisite; import/composition tests reject raw store/provider access. | WS-ART / WS-CON-001-09A | Open |
| Outbox duplication or loss | High | 02A owns truth/append; 02B alone owns dispatch/retry/replay with stable identities. | WS-CON-001-02A/B | Open |
| Human role or token claims leak into feature authorization | Critical | Central AUTH service only; no grant queries/local role checks; deny/race tests. | WS-AUTH / all WS-CON | Open |
| Provider payment logic leaks into Workstream | High | Typed instruction/ack/receipt contract; provider attempts/balances/ledger prohibited. | WS-CON-001-08A/B | Open |
| Fulfilled state regresses or duplicates | High | Immutable receipts, unique fulfilled row, row locks, exact callback idempotency. | WS-CON-001-08B | Open |
| Lifecycle disable races adapter I/O or authenticated callback | Critical | CON-owned mandatory dispatch/callback fence ports, durable pre-I/O in-flight state, same-session drain observations, REV-12A exclusive transition lock, and both-order PostgreSQL tests. | WS-CON-001-03D/08A/08B/10B/11 + WS-REV-001-12A | Open |
| Artifact outage changes contribution truth | High | Projection is post-commit/rebuildable; canonical records never depend on provider availability. | WS-CON-001-09A | Open |
| Sensitive financial/provider/token data leaks | Critical | Bounded schemas, redaction, no human-token forwarding, no provider refs in APIs/events. | Security review | Open |
| Public routes expose partial system | High | CON-11 proves hidden readiness; REV-13 alone registers the joint surface. | WS-CON-001-11 / WS-REV-001-13 | Open |
| Initiative becomes unreviewable | High | One PR-sized chunk, circuit-breaker, explicit stop after each. | Primary agent / human | Mitigated in plan |
