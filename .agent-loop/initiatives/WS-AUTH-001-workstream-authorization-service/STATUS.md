# Status: WS-AUTH-001 - Workstream Authorization Service

## Current status

Planning merged through PR #91 as
`ad6d6444e497b76d7cb925f3b0999ed4b74a3dac` after required internal reviews,
Agent Gates, and Backend passed. CodeRabbit produced a walkthrough with no
actionable findings, then its final check was cancelled when the PR closed.
D4-D10 were explicitly approved and WS-AUTH-001-01 was started by the user on
2026-07-11. The final branch head `b5217e1` passed required internal reviews,
Agent Gates, Backend, and CodeRabbit, then merged through PR #93 as `772af1d` on
2026-07-11. The user separately started `WS-AUTH-001-02` on 2026-07-11. Its
preimplementation plan review passed, and the user explicitly approved D12's
exact production dependency changes. After a coverage-priority pause, the user
explicitly resumed AUTH in its separate worktree on 2026-07-12. Bounded runtime
implementation and repair review are complete on reviewed code SHA `47dd5a7`;
all required internal tracks passed and PR #107 merged as `060b780` on
2026-07-13. The user then explicitly started `WS-AUTH-001-03`. Its L1
preimplementation plan review passed with conditions. Bounded implementation,
repair, and all required internal reviewer tracks now pass on reviewed code SHA
`8c5334c`, including external repair implementation `4923b67`. PR #108 merged
to `main` as `5c47aba`; that main revision is integrated into AUTH, whose prior
lifecycle reconciliation was reviewed at `a70b89c`. Backend, Agent Gates, and
CodeRabbit passed on final branch head `43ffbfe`, then explicit human approval
merged PR #109 to `main` as `f06532e` on 2026-07-13. AUTH-03 post-merge memory
merged through PR #110 as `1864867`. The user then explicitly started AUTH-04.
Required L1 plan review rejected the combined request/error/rate-control scope
before runtime edits and required a split. Only AUTH-04A contract repair and
preimplementation re-review are now active; AUTH-04B is inactive.

## Active planning chunk

None.

## Active implementation chunk

`WS-AUTH-001-04A` - Request And Error Context. Runtime edits remain gated on
the required repaired-contract preimplementation re-review.

## Current implementation branch

`codex/ws-auth-001-04-request-api-controls`.

## Chunk status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-AUTH-001-PLAN` | Merged | `authorization-service` | #91 | Merged as `ad6d644`; D4-D10 later approved. |
| `WS-AUTH-001-01` | Merged | `codex/ws-auth-001-01-adopt-authorization-baseline` | #93 | Authorization baseline, Contributor terminology boundary, scanner, and repository contracts; merged as `772af1d`. |
| `WS-AUTH-001-02` | Merged | `codex/ws-auth-001-02-verified-issuer-token` | #107 | Merged as `060b780`; reviewed code SHA `47dd5a7`. |
| `WS-AUTH-001-03` | Merged | `codex/ws-auth-001-03-legacy-actor-classification` | #109 | Merged as `f06532e`; reviewed code `8c5334c`; final branch head `43ffbfe`. |
| `WS-AUTH-001-04` | Split | `codex/ws-auth-001-04-request-api-controls` | - | Parent split before runtime implementation. |
| `WS-AUTH-001-04A` | Active | `codex/ws-auth-001-04-request-api-controls` | - | Repaired contract awaiting required preimplementation re-review; no runtime edit yet. |
| `WS-AUTH-001-04B` | Inactive | - | - | PostgreSQL rate controls; requires 04A merge/memory and separate explicit start. |
| `WS-AUTH-001-05` | Proposed | - | - | Authority evidence and idempotency foundation. |
| `WS-AUTH-001-06` | Proposed | - | - | Canonical actor profile and identity link. |
| `WS-AUTH-001-07` | Proposed | - | - | Authorization kernel and permissions. |
| `WS-AUTH-001-08` | Proposed | - | - | Bootstrap and administrative grants. |
| `WS-AUTH-001-09` | Proposed | - | - | Actor/link states and service actors. |
| `WS-AUTH-001-10` | Proposed | - | - | Project contributor grants. |
| `WS-AUTH-001-11` | Proposed | - | - | Project identity/guide/source/read cutover. |
| `WS-AUTH-001-12` | Proposed | - | - | Project policy/setup mutation cutover. |
| `WS-AUTH-001-13` | Proposed | - | - | Task management and assignment cutover. |
| `WS-AUTH-001-14` | Proposed | - | - | Submission/checker/audit visibility cutover. |
| `WS-AUTH-001-15` | Proposed | - | - | Remaining system worker and obsolete authority removal. |
| `WS-AUTH-001-16` | Proposed | - | - | Conformance and live proof. |

## Blockers

No external blocker. The combined AUTH-04 plan failed its internal gate and was
split before runtime edits. AUTH-04A must pass repaired-contract review before
implementation. AUTH-04B later owns the migration corrected from the now-owned
`0016` prefix to `0017` on current main, but remains inactive. Non-test
operators must later supply explicit classification evidence rather than
inferred kinds before the owning canonical actor migration.

AUTH-03 review evidence and its PR trust bundle are recorded at
`reviews/WS-AUTH-001-03-internal-review-evidence.md` and
`reviews/WS-AUTH-001-03-pr-trust-bundle.md`. Prior AUTH-02 evidence remains at
`reviews/WS-AUTH-001-02-internal-review-evidence.md` and
`reviews/WS-AUTH-001-02-pr-trust-bundle.md`.

Production issuer configuration and legacy non-test actor classification are
future implementation/live-proof inputs and are tracked explicitly in
`DISCOVERY.md` and chunk stop conditions.

The user accepted D13 on 2026-07-13: the target provider-neutral boundary is
`IdentityIssuerVerifier`, extending the shared `ExternalServiceAdapter`
convention and using its typed factory. The current verifier/configuration
names remain functional migration inputs. The atomic AUTH adoption requires
its own reviewed chunk after `WS-ART-001-01C` installs the shared foundation;
it is not part of the size-capped AUTH-04A request/error implementation.
