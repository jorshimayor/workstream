# Status: WS-POL-001 - Submission Artifact Policy Foundation

## Current Status

`WS-POL-001-01`, `WS-POL-001-02`, `WS-POL-001-03`, `WS-POL-001-04`,
`WS-POL-001-05`, `WS-POL-001-06`, `WS-POL-001-07`, `WS-POL-001-08`,
`WS-POL-001-09`, and `WS-POL-001-10` are merged to `main`. `WS-POL-001-11`
contract evidence is ready for external review and human approval.
Implementation remains inactive until human review approves the actor
identity/profile implementation boundary and the user gives an explicit
implementation start signal.

## Active Chunk

`WS-POL-001-11` contract review. Implementation is inactive.

## Chunk Status

| Chunk | Status | Branch | PR | Notes |
|---|---|---|---:|---|
| `WS-POL-001-01` | Merged | `codex/ws-pol-001-01-submission-artifact-policy` | 28 | Implements guide-source snapshots, guide sufficiency reports, submission artifact policy, effective project policy, project pre-submit checker contract, activation guards, and key-based artifact policy merge. |
| `WS-POL-001-02` | Merged | `codex/ws-pol-001-02-agent-runtime-compiler` | 61 | Adds async guide sufficiency / derivation agents, runtime port, OpenAI Agents SDK adapter boundary, trusted compiler path, and server-owned provenance guards. |
| `WS-POL-001-03` | Merged | `codex/ws-pol-001-03-task-locked-context` | 63 | Moves task locked-context and submission runtime to the effective policy and project checker bundle. |
| `WS-POL-001-04` | Merged | `codex/ws-pol-001-04-post-submit-policy` | 65 | Splits post-submit checker policy provenance and locks durable checker runs to post-submit policy context. |
| `WS-POL-001-05` | Merged | `codex/ws-pol-001-05-revision-resubmission` | 66 | Proves revision resubmission, real API drill, and `evaluation_pending` lifecycle status. |
| `WS-POL-001-06` | Merged | `codex/ws-pol-001-06-terminal-benchmark-drill` | 67 | Hardens the Terminal Benchmark proof harness and removes stale project guide/payment contracts before continuing pre-submit checker work. |
| `WS-POL-001-07` | Merged | `codex/ws-pol-001-07-task-contract-cleanup` | 68 | Removes task-owned `required_files`/`required_evidence` from request/response/model/migration and keeps artifact requirements project-policy driven. |
| `WS-POL-001-08` | Merged | `codex/ws-pol-001-08-celery-project-setup` | 69 | Makes guide/source capture enqueue Celery pre-submit setup automatically: sufficiency first, blocked stops, draft submission artifact policy next; removes remaining construction-state compatibility surfaces. |
| `WS-POL-001-09` | Merged | `codex/ws-pol-001-09-openai-agent-sdk-only` | 71 | Removes the production `local_fixture` project setup runtime and old runtime selector; keeps deterministic test behavior in explicit test-local fakes only. |
| `WS-POL-001-10` | Merged | `codex/ws-pol-001-10-pre-submit-hardening` | 72 | Hardens duplicate guide-version conflicts, guide-create source snapshots, active-guide checker summaries, worker self-profile onboarding, and failed pre-submit audit evidence. |
| `WS-POL-001-11` | Internal review complete; implementation inactive | `codex/ws-pol-001-11-actor-identity-profile-contract` | 73 | Defines local Workstream actor identity and actor profile registries for verified Flow actors before the next live API drill. |

## Blockers

| Blocker | Owner | Next action |
|---|---|---|
| None | - | Human review decides whether to accept the contract before implementation starts. |

## Follow-Ups

| Item | Source | Priority |
|---|---|---|
| Add public revision lifecycle coverage instead of direct `needs_revision` test setup | Test-delta review | High for `WS-POL-001-05` |
| Add focused `0007 -> 0006` downgrade assertion for locked-context columns and constraints | QA/test-delta review | Medium follow-up |
| Extract shared artifact path and forbidden-pattern helpers before further checker-policy expansion | Reuse/dedup review | Medium follow-up |
| Add profile-level audit events if actor/profile changes become reputation-sensitive | Security review on PR #72 | Medium follow-up |
