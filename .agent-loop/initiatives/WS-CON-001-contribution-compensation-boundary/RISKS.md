# Risks: WS-CON-001 Contribution Record And Compensation Boundary

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Competing award-eligibility models | Critical | ContributionPolicy is sole authority; semantic then physical clean cut with no fallback | CON-05A/B |
| Review commits without contribution | Critical | Mandatory flush-only participant and one REV-owned commit; fault-injection rollback | CON-07 + REV |
| Mandatory ART projection blocks product truth | Critical | No ART/evidence work in core transaction or release; optional successor only | CON-07/09/11 |
| Wrong frozen policy | Critical | Assignment/lease freeze before work; immutable versions; concurrency proof | CON-05A/06 |
| Dispatcher inherits handler authority | Critical | Dispatcher-only action; exact independent service authority for protected handlers | CON-02B/08A/10C + AUTH |
| Operations request authority leaks into execution | Critical | 10B persists bounded human requests only; 10C uses exact fixed-service actions, cross-executor denial, replay/finding proof, and projection-only mutation | CON-10B/10C + AUTH |
| Broad or dynamic service access | Critical | Closed ServiceIdentity/static rows, controlled provisioning, AUTH-09E, cross-service denial | AUTH + CON |
| Partial ART/REV custody transfer | High | Reference complete WS-XINT handoffs; no local subset or dual writer | AUTH |
| Cross-domain deadlock/partial commit | Critical | AUTH-first common prefix; operation-specific REV/task lifecycle-before-policy order; one session/commit; both-order PostgreSQL tests | AUTH + REV + CON |
| Role coupling or substitution | High | Independent submitter/reviewer/adjudicator grants and exact invalidation | AUTH + lifecycle owners |
| Provider I/O under locks | Critical | Durable pre-I/O state; release transaction/fence before adapter call | CON-08A/outbox |
| Callback spoofing/replay | Critical | Exact service identity/static row, binding match, prepared protocol, idempotent receipt | CON-08B + AUTH |
| Legacy row ambiguity | High | Human-approved deterministic rebuild/classification; migration fails closed | Human + CON-05 |
| Premature public release | High | Hidden OpenAPI, exact manifest, AUTH activation, joint REV/CON gate | CON-11 + REV |

No runtime work starts while a blocking decision or prerequisite remains open.
