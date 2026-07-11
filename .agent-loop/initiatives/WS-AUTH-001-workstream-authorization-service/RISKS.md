# Risks: WS-AUTH-001 - Workstream Authorization Service

## Classification

- Initiative direction/auth/data-model strategy: L0, human-led; D1-D10 approved
  by the user on 2026-07-11 before `WS-AUTH-001-01` activation
- Bounded implementation chunks: L1 after the L0 planning gate
- SLA: P1
- Work type: architecture, authentication, authorization, migration, audit
- Human gate: required for every implementation PR and merge
- Budget posture: deep reasoning and full required reviewer fanout

## Risk register

| ID | Risk | Impact | Mitigation | Proof |
|---|---|---|---|---|
| A1 | Token roles remain authoritative on one path | Privilege escalation | Remove role-based helpers surface by surface; repository scan gate | Negative token-role tests and zero runtime `require_any_role` uses at final gate |
| A2 | Parallel actor models survive cutover | Ambiguous identity and authority | One migration design, no `V2` model, explicit legacy metadata disposition | Metadata/model inspection and migration tests |
| A3 | Legacy actors are misclassified | Service actor gains human authority or history breaks | No inference from email/subject/roles; fail-closed classification gate | Non-empty ambiguous migration failure test |
| A4 | Bootstrap races or the final Access Administrator is lost | Multiple trust roots or administrative lockout | Bootstrap and every final-admin-removal path lock `AuthorityControl(id=1) FOR UPDATE` before the effective-admin check and mutation | Different-target concurrent bootstrap plus revoke/suspend/deactivate concurrency tests |
| A5 | Cross-project grant or IDOR | Unauthorized project access | Canonical DB resource resolution and composite ownership constraints | Cross-project read/mutation tests |
| A6 | Revocation loses a race to mutation | Revoked actor commits sensitive change | Revalidate grants and state inside sensitive transaction | Grant-revoke versus command concurrency test |
| A7 | Worker job trusts serialized authority | Stale grant remains effective | Serialized context is evidence only; reload current authority before commit | Revoked queued-command test |
| A8 | JWKS outage weakens verification | Unverifiable token accepted | Pinned algorithms, bounded cache, one refresh, fail closed | Cache/rotation/outage contract tests |
| A9 | Claims or personal data leak | Security/privacy incident | Minimal verified token type, bounded logging, no raw token/JWKS persistence | Log/error/audit redaction tests |
| A10 | Approval provenance breaks | Existing policy activation becomes unreadable or forgeable | Preserve historical values; new actions reference matched local grant | Migration and project approval tests |
| A11 | API namespace forks | Client and documentation drift | Adopt `/api/v1` only and update references together | Route/OpenAPI and stale-reference scan |
| A12 | Existing intake regresses | Project/task/checker pipeline stops | Run full current suite and API drill after actor migration and each cutover surface | Existing backend suite and live drill |
| A13 | Auth initiative becomes one oversized PR | Review failure and hidden coupling | Sixteen bounded implementation chunks, one active at a time | Circuit-breaker and PR-size evidence |
| A14 | Later WS-POL work resumes on obsolete auth | Rework and inconsistent authority | Keep WS-POL-002-04 inactive until PR #90 merges, auth proof exists, and the user starts it | Loop-memory gate |
| A15 | Authority mutation ships before durable evidence | Missing provenance cannot be reconstructed | Introduce correlation/idempotency/shared audit with canonical actor persistence | Atomic state+idempotency+event tests in every authority chunk |
| A16 | Identity-link revocation strands final administrator | Administrative lockout despite active grant row | Apply AuthorityControl lock to link revoke plus grant/profile changes | Mixed concurrent link/grant/profile final-admin tests |
| A17 | Canonical actor migration deletes typed-profile workflow eligibility before task/submission cutover | An intermediate merged release cannot claim, start, or submit work | Bounded non-authoritative workflow-eligibility adapter in chunk 06; remove task consumers in 13 and final consumer plus adapter in 14 | Full suite/API drill after chunks 06, 13, 14, and scanner proof in 15 |
| A18 | Authority evidence is mutable or denial events arrive late | Security decisions cannot be reconstructed | Insert/read-only repository API, database append-only enforcement, per-mutation allowed/denied event proof, operational retention controls | Update/delete rejection plus atomic allowed/denied event tests in owning chunks |
| A19 | Authority invalidation releases a needs-revision task as ordinary ready work | Prior findings, context, supersession, or replay obligations are bypassed | Keep the task in needs_revision with a durable unassigned obligation and controlled replacement assignment | Replacement-contributor revision-context, supersession, and high/medium replay tests |

## Required reviewers

Every implementation chunk requires:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- reuse/dedup
- test delta when tests change
- docs when docs or public contracts change
- CI integrity when workflows, scripts, dependencies, or test configuration change
