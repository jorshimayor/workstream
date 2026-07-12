# Review Log

## WS-QUAL-001-01B1

Status: BLOCKED. Candidate `7bfe3a0` has 496/500 lines and 66 focused behavior
tests. Senior engineering, QA, security, product/ops, architecture, CI, docs,
and reuse passed, but final test-delta review found three valid gaps after the
second semantic-integrity repair cycle.

Scope: read-only coverage policy core, parameterized contract behavior tests,
and truthful compute-floor documentation. No config, workflow, evidence, Git
publication logic, production behavior, or coverage-raising tests.

Next: review a smaller policy-core versus semantic-delta split and obtain
explicit user approval. No PR, 01B2, chunk 02, or AUTH resume is permitted.

User checkpoint: the user approved the proposed parser-core versus semantic-
delta split direction on 2026-07-12. Internal plan review must pass before
activating only 01B1A; 01B1B retains a later separate start checkpoint.

Split review result: PASS at `d1819873e5ac353da3963771f70dc2be13bc72f9`
across senior engineering, QA/test, security/auth, product/ops, architecture,
CI integrity, docs, reuse/dedup, test delta, and circuit breaker. Only 01B1A is
active; 01B1B and 01B2 retain later checkpoints.

## WS-QUAL-001-01B

Status: user started the chunk after PR #104 merged. Its repaired L1 contract
passed plan review at `7a16ee4`, but implementation hit the hard circuit breaker
at 480/500 lines before required config, CI, runbook, and negative proof.

Scope: coverage policy, contract tests, configured initial floor, canonical CI
validation, baseline evidence, and runbook only. No production or coverage-
raising behavior tests.

Result: executable draft and partial candidate run were stopped and cleaned up.
A policy-core versus baseline/CI split is proposed for internal and explicit
human approval. Do not start either split chunk or chunk 02.

## WS-QUAL-001-01A

Status: merged through PR #103 on 2026-07-12 as `2901a3e`.

Final reviewed implementation SHA: `d1582ec64b9176c5ead62f695c7a23b48e4c72b9`

Final evidence-bound branch head: `8cd7616b497ceb46d8359c25de689192632dfee8`

Scope: isolated least-privilege database runner, API guards, focused behavior
tests, two-phase complete-suite CI, and database-testing runbook.

User quality direction: behavior and safety proof outrank percentage gains;
execution-only line-chasing tests are prohibited.

Review findings: child credentials must not retain admin authority; destructive
helpers must revalidate identifiers; collision proof must preserve an existing
session; runner lifecycle tests and provisioned suite require explicit phases.

Evidence: `.agent-loop/initiatives/WS-QUAL-001-backend-coverage-floor/reviews/WS-QUAL-001-01A-internal-review-evidence.md`

Trust bundle: `.agent-loop/initiatives/WS-QUAL-001-backend-coverage-floor/reviews/WS-QUAL-001-01A-pr-trust-bundle.md`

External response: `.agent-loop/initiatives/WS-QUAL-001-backend-coverage-floor/reviews/WS-QUAL-001-01A-external-review-response.md`

Merge checks: Agent Gates, Backend, and CodeRabbit passed. CodeRabbit's valid
contract, runbook, timeout, and reuse findings were repaired. Role-aware cleanup
was retained with ownership justification and real-catalog behavior proof.

Next: merge post-merge memory and stop. Do not start 01B automatically.

## WS-QUAL-001-PLAN

Status: merged through PR #99 on 2026-07-12 as `9046d52`.

Final reviewed planning SHA: `0d9dd987d546c864fa8de7bae462e5e73a1b5ea9`

Final evidence-bound branch head: `3da1769882e9f6db4c48ef3dba33da8380e6a613`

Result: PASS after repairs across senior engineering, QA/test, security/auth,
product/ops, architecture, docs, CI integrity, reuse/dedup, and test delta. All
reviewer sessions are closed.

Scope: plan a safe, non-decreasing path from the measured 78.26 percent
diagnostic baseline to a permanent 90 percent full-backend application floor.
No runtime, test, dependency, workflow, API, migration, or product behavior
changed.

Evidence:
`.agent-loop/initiatives/WS-QUAL-001-backend-coverage-floor/reviews/WS-QUAL-001-PLAN-internal-review-evidence.md`

Trust bundle:
`.agent-loop/initiatives/WS-QUAL-001-backend-coverage-floor/reviews/WS-QUAL-001-PLAN-pr-trust-bundle.md`

External response:
`.agent-loop/initiatives/WS-QUAL-001-backend-coverage-floor/reviews/WS-QUAL-001-PLAN-external-review-response.md`

External review: one valid CodeRabbit wording finding was addressed; the thread
resolved, description check passed, and final Agent Gates/Backend/CodeRabbit
checks passed before merge.

Next: merge post-merge memory and stop. `WS-QUAL-001-01` remains inactive until
that memory completes and the user gives a separate explicit start.

## WS-ART-001-PLAN

Status: merged through PR #97 on 2026-07-12 as `8644a43`.

Reviewed planning SHA: `f7fbc33`

Final evidence-bound branch head: `c069064`

Result: PASS after fixes across senior engineering, QA/test, security/auth,
product/ops, architecture, docs, CI integrity, reuse/dedup, and test delta.
All reviewer sessions were closed before publication.

Scope: immutable artifact storage boundary, provider-neutral port, local and
Flow Node adapters, exact-byte admission/binding/recovery, failure/migration
matrices, clean legacy cutover, and ten bounded cross-repository chunk
contracts. No runtime implementation changed.

Evidence: `.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/reviews/WS-ART-001-PLAN-internal-review-evidence.md`

Trust bundle: `.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/reviews/WS-ART-001-PLAN-pr-trust-bundle.md`

External review: CodeRabbit posted seven actionable comments; all were fixed in
`567a052`. Response:
`.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/reviews/WS-ART-001-PLAN-external-review-response.md`

Merge checks: Agent Gates and Backend passed on the final head. CodeRabbit's
initial review findings were fixed; its final status check passed, while the
last incremental narrative review was rate-limited and posted no new finding.

Next chunk: `WS-ART-001-01` remains proposed and inactive until post-merge
memory completes and the user provides a separate start signal.

## WS-AUTH-001-01

Status: merged through PR #93 on 2026-07-11 as `772af1d`.

Reviewed implementation SHA: `be0b836`

Final merged branch head: `b5217e1` (review/evidence and latest-main memory
files only after the reviewed implementation SHA)

Result: PASS after fixes across senior engineering, QA/test, security/auth,
product/ops, architecture, docs, reuse/dedup, CI integrity, and test delta.

Scope: canonical authorization ADR/spec/runbook, active-document and diagram
reconciliation, stale-authorization scanner/tests, additive Agent Gates step,
latest-main/PR #90 reconciliation, and terminology-only prompt/test wording.

Evidence: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/reviews/WS-AUTH-001-01-internal-review-evidence.md`

Trust bundle: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/reviews/WS-AUTH-001-01-pr-trust-bundle.md`

Merge checks: Agent Gates, Backend, and CodeRabbit passed before explicit human
merge. CodeRabbit had zero unresolved current review threads.

Next chunk: `WS-AUTH-001-02` remains proposed but inactive until a separate
explicit user start.

## WS-POL-002-03

Status: merged through PR #90 on 2026-07-11 as `a7aa474`.

Reviewed implementation SHA: `0e59873`

Final merged branch head: `1e20b79` (review/evidence files only after the
reviewed implementation SHA)

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS after fixes. Required internal reviewer tracks passed with no open
sessions; CodeRabbit reported no unresolved actionable comments; Agent Gates
and Backend checks passed before explicit human merge.

Scope: server-owned post-submit checker policy setup visibility, approval, and
correction APIs; safe operator summaries; immutable approval provenance; and
negative authorization coverage for non-setup roles.

Evidence: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-03-internal-review-evidence.md`

Trust bundle: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-03-pr-trust-bundle.md`

External review response: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-03-external-review-response.md`

Next chunk: `WS-POL-002-04` remains inactive until the authorization foundation
is proven and the user provides a separate explicit start signal.

Parallel-work note: stale point-in-time WS-POL pause wording in WS-AUTH planning
artifacts is owned by the separate WS-AUTH worktree and was deliberately not
rewritten by this memory-only update.

## WS-POL-002-02

Status: merged through PR #88 on 2026-07-11.

Merge commit: `32af6a7`

Reviewed implementation SHA: `67fb3ca`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; PR #88 external review addressed; GitHub checks passed.

Scope: setup-time post-submit checker derivation, resumable setup continuation,
generated project `PostSubmitCheckerPolicy` persistence, automatic contributor
submission handoff to the pre-review gate, and repair-only `/finalize`
semantics.

Evidence: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-02-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-02-external-review-response.md`

Trust bundle: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-02-pr-trust-bundle.md`

Next chunk: `WS-POL-002-03` server-owned policy approval and setup visibility
APIs, inactive until explicit user start.

## WS-POL-002-01

Status: merged through PR #87 on 2026-07-09.

Merge commit: `ed52c21`

Reviewed implementation SHA: `438361a`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; PR #87 external review addressed; GitHub checks passed.

Scope: trusted post-submit compiler contract, version-stamped default-checker
snapshots, canonical policy hashing, compile/parse validation, and regression
tests around default-drift safety.

Evidence: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-01-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-01-external-review-response.md`

## WS-ENG-001-01

Status: merged through PR #23 on 2026-06-20.

Merge commit: `b9fe19b96109e9786e1d6d89488abfbe68a05d4a`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; external review addressed; GitHub checks passed.

Evidence: `.agent-loop/initiatives/WS-ENG-001-codex-zero-trust-loop-bootstrap/reviews/WS-ENG-001-01-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-ENG-001-codex-zero-trust-loop-bootstrap/reviews/WS-ENG-001-01-external-review-response.md`

## WS-POL-001-PLAN

Status: merged through PR #26 on 2026-06-27.

Merge commit: `acf2bcf62a7af391c506c960769268c393aefdab`

Reviewed code SHA: `8b51a84b1bede193bbafe0b1eeb7b7981a271a0e`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS with low risks; external review addressed; GitHub checks passed.

Scope: planning approval only. No runtime product behavior, database schema, API
behavior, or frontend behavior changed.

Next chunk at that point: `WS-POL-001-01` implementation on a new branch.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-01-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-01-external-review-response.md`

## WS-POL-001-01

Status: merged through PR #28.

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; external review addressed; GitHub checks passed.

Scope: guide-source snapshots, guide sufficiency reports, submission artifact
policy, effective project policy, project pre-submit checker contract,
activation guards, and key-based artifact policy merge.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-01-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-01-external-review-response.md`

## WS-POL-001-02

Status: merged through PR #61.

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; external review addressed; GitHub checks passed.

Scope: async guide sufficiency and submission artifact policy derivation agents,
agent runtime port, OpenAI Agents SDK adapter boundary, trusted compiler path,
and server-owned provenance guards.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-02-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-02-external-review-response.md`

## WS-POL-001-03

Status: merged through PR #63 on 2026-07-03.

Merge commit: `a73be67bf6c3c2ac0194f8aecbda89d748baa92c`

Reviewed implementation SHA: `d1e80e3903038cb9c99aec9e83faf164a010c46d`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; external review addressed; GitHub checks passed.

Scope: task locked-context columns, readiness guards, submission creation
pre-submit enforcement, exact locked context propagation into submission
versions, and real Week 1 API drill repair.

Next chunk: `WS-POL-001-04` is planned but inactive until the user gives an
explicit start signal.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-external-review-response.md`

## WS-POL-001-04

Status: merged through PR #65.

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; external review addressed; GitHub checks passed.

Scope: post-submit checker policy provenance, durable checker-run policy locks,
and separation of post-submit/internal checks from pre-submit intake.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-04-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-04-external-review-response.md`

## WS-POL-001-05

Status: merged through PR #66.

Result: PASS after fixes; external review addressed; GitHub checks passed.

Scope: revision resubmission proof, real API drill, and `evaluation_pending`
lifecycle status.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-05-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-05-external-review-response.md`

## WS-POL-001-06

Status: merged through PR #67.

Result: PASS after fixes; GitHub checks passed.

Scope: Terminal Benchmark fixture proof harness, OpenAI Agents SDK strict-schema
fix, and cleanup of stale project guide/payment contracts.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-06-internal-review-evidence.md`

## WS-POL-001-07

Status: merged through PR #68.

Result: PASS after fixes; external review addressed; GitHub checks passed.

Scope: removed task-owned artifact fields and kept artifact requirements driven
by project submission artifact policy.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-07-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-07-external-review-response.md`

## WS-POL-001-08

Status: merged through PR #69 on 2026-07-06.

Merge commit: `aea7024`

Reviewed implementation SHA: `0c32c97a3895f0435b7602698730b5d40b1bacbd`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; external review addressed; GitHub checks passed.

Scope: Celery-backed automatic project setup from guide/source capture,
sufficiency-first pipeline ordering, draft submission artifact policy creation,
and removal of remaining construction-state compatibility surfaces.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-08-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-08-external-review-response.md`

## WS-POL-001-09

Status: merged through PR #71 on 2026-07-06.

Merge commit: `8a524de`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; external review addressed; GitHub checks passed.

Scope: removed the production `local_fixture` project setup runtime and old
runtime selector, kept deterministic test behavior in explicit test-local
fakes only, and preserved OpenAI Agents SDK as the configured project setup
runtime boundary.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-09-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-09-external-review-response.md`

## WS-POL-001-10

Status: merged through PR #72 on 2026-07-06.

Merge commit: `1bbde47`

Reviewed implementation SHA: `cc78f2a`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS after fixes; external review addressed; GitHub checks passed.

Scope: duplicate guide-version conflict handling, guide-create source snapshot
capture, active-guide checker summary visibility, worker self-profile
onboarding through authenticated API, nullable worker identity response
coverage, and durable failed-pre-submit audit evidence without creating a
submission.

Next chunk: `WS-POL-001-11` should define and then implement local actor
identity and actor profile registries before the next Terminal Benchmark live
API drill.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-10-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-10-external-review-response.md`

## WS-POL-001-11

Status: merged through PR #74 on 2026-07-07.

Merge commit: `5cec0e0`

Branch: `codex/ws-pol-001-11-actor-profile-registry-impl`

Reviewed implementation SHA: `0729531`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- CI integrity
- docs
- reuse/dedup
- test delta

Result: PASS after fixes from internal review and CodeRabbit. GitHub Agent
Gates, Backend, and CodeRabbit passed before merge.

Scope: local `ActorIdentity` and shared `ActorProfile` registry for verified
Flow actors, destructive removal of obsolete worker/reviewer profile stores,
explicit actor-registration dependency, worker profile activation through the
canonical worker endpoint, claim eligibility requiring verified worker token
role plus active worker profile, stale demo route cleanup, and Flow
issuer-plus-subject identity compatibility wording.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-11-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-11-external-review-response.md`

External review status: CodeRabbit comments triaged; valid findings fixed;
legacy-profile backfill request rejected because it contradicts the
no-backward-compatibility chunk decision.

Next gate: rerun the Terminal Benchmark live API drill through real HTTP calls
using `POST /api/v1/workers/me/profile`, then review findings before starting
the next product chunk.

## WS-POL-001-13

Status: merged through PR #77 on 2026-07-08.

Merge commit: `b567bac`

Branch: `codex/ws-pol-001-13-task-context-apis`

Reviewed implementation SHA: `f533f1a`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- reuse/dedup
- test delta

Result: PASS after fixes from internal review and CodeRabbit. GitHub Agent
Gates, Backend, and CodeRabbit passed before merge.

Scope: worker-safe task work context, exact submission requirements, existing
worker task-read redaction, fail-closed locked-context validation, and
operator-only locked task provenance APIs.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-13-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-13-external-review-response.md`

External review status: CodeRabbit comments triaged; the valid test
maintainability nitpick was fixed; PR description warning was fixed by updating
the trust bundle and PR body.

Historical next gate at the time of PR #77 merge: `WS-POL-001-14` remained
inactive until the user explicitly started it. That gate was later satisfied by
PR #79.

## WS-POL-001-14

Status: merged through PR #79 on 2026-07-08.

Branch: `codex/ws-pol-001-14-submission-finalize`

Merge commit: `53a57c3`

Reviewed implementation SHA: `ebf9d1d`

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- reuse/dedup
- test delta

Result: PASS after internal review fixes and CodeRabbit review. GitHub Agent
Gates, Backend, and CodeRabbit passed before merge. The broad non-creator
project-manager visibility suggestion was rejected because it conflicts with
the current scoped-operator security contract.

Scope: public submission handoff renamed to `finalize`, finalized response
fields replace public lock wording, pre-review checker execution is audited
under `workstream-system:pre-review-gate` with requester provenance, checker
and audit visibility use scoped operator authorization, and the API contract
plus Terminal Benchmark drills prove the lifecycle through HTTP-visible
responses.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-14-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-14-external-review-response.md`

External review status: CodeRabbit comments triaged; valid findings fixed;
GitHub checks and CodeRabbit passed before merge.

Next gate update before PR #81: the accepted no-DB Terminal Benchmark live API
drill from `main` exposed an agent-derived submission artifact policy
self-conflict during policy derivation. Corrective chunk `WS-POL-001-15`
hardened the derivation contract and reran that live API drill successfully.

## 2026-07-08 - WS-POL-001-15 Merged

PR #81 merged into `main` as `b1a9851a5fe00580b704fe42bdeb511638dfe688`.

Result: PASS after internal review, CodeRabbit, Agent Gates, and Backend checks.

Scope: hardened the OpenAI Agents SDK submission artifact policy derivation
prompt so it produces a project-level worker submission contract, avoids
required/forbidden self-conflicts, avoids secret-like required fields, and
requires exact safe relative artifact paths. Server-side default forbidden
artifact validation remains fail-closed.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-15-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-15-external-review-response.md`

External review status: CodeRabbit generated no actionable code comments; the
description warning was fixed before merge.

Next gate: no active implementation chunk. Wait for the user's next explicit
chunk start signal.

## 2026-07-09 - WS-POL-001-16 Merged

PR #84 merged into `main` as `a3d2a3f1701391c8dafdca6cff2f0f80dbebda3b`.

Reviewed revision: `49101d4ad3fc22ec6e6065b1e593ef04145db953`.

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- reuse/dedup
- test delta
- CI integrity

Result: PASS after internal review and privacy-scrub fixes. Agent Gates,
Backend, Week 1 API Demo UI, and external review passed before merge.

Scope: Terminal Benchmark live API drill evidence, privacy scrub, professional
PDF report, setup/policy/task/submission/checker-run lifecycle proof through
HTTP-visible APIs, and no database inspection as proof.

Evidence: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-16-internal-review-evidence.md`

Trust bundle: `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-16-pr-trust-bundle.md`

Next gate: `WS-POL-002` planning for post-submit checker foundation. No
implementation chunk is active until the user explicitly starts it.

## 2026-07-09 - WS-POL-002-PLAN Merged

PR #85 merged into `main` as `3fc1a688743f13476d6092078d40792592823d27`.

Reviewed planning SHA: `f07160145fd5b92515cfbbd1c78c81a583a86508`.

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- CI integrity
- reuse/dedup - N/A with approved reason; no skills, agents, backend app code,
  or scripts changed in the final repair.
- test delta - N/A with approved reason; no tests or test-like files changed in
  the final repair.

Result: PASS after CodeRabbit and internal review fixes. GitHub Agent Gates,
Backend, and CodeRabbit passed before merge.

Scope: created WS-POL-002 intent, discovery, plan, decisions, risks, status,
chunk map, and chunk contracts for project-guide-derived post-submit checker
setup. The plan keeps `PostSubmitCheckerPolicy` project-scoped, keeps derivation
setup-time only, keeps runtime deterministic, and forbids per-task checker
generation.

Evidence: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-PLAN-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-PLAN-external-review-response.md`

Trust bundle: `.agent-loop/initiatives/WS-POL-002-post-submit-checker-foundation/reviews/WS-POL-002-PLAN-pr-trust-bundle.md`

Next gate: `WS-POL-002-01` Post-Submit Provenance And Compiler Contract. No
implementation chunk is active until the user explicitly starts it.

## 2026-07-11 - WS-AUTH-001-PLAN Internal Review Passed

Required reviewer tracks:

- senior engineering
- QA/test
- security/auth
- product/ops
- architecture
- docs
- CI integrity
- reuse/dedup
- test delta

Result: PASS after plan repairs. The reviewed planning tree preserves the
external Flow authentication boundary, replaces token roles only through a
staged local-grant cutover, keeps `/api/v1`, protects intermediate-release
operability, and leaves all runtime implementation inactive.

Scope: imported and hash-bound eight Workstream reference files; added the
WS-AUTH-001 intent, discovery, decisions, risks, plan, source manifest, status,
16 implementation chunk contracts, and durable WS-POL-002 pause. D1-D3 are
human-approved. D4-D10 remain at the L0 human approval checkpoint.

Evidence: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/reviews/WS-AUTH-001-PLAN-internal-review-evidence.md`

Next gate: stop. Do not activate `WS-AUTH-001-01` without explicit human
approval of D4-D10 and a separate implementation start signal.

## 2026-07-11 - WS-AUTH-001-PLAN Merged

PR #91 merged into `main` as
`ad6d6444e497b76d7cb925f3b0999ed4b74a3dac`.

Reviewed planning SHA: `5739e1d6fc8df0fa620bd007c45e370530ac8d12`.

Result: PASS after internal plan repair and a CI-discovered PDF binary-diff
repair. Agent Gates and Backend passed. CodeRabbit produced a walkthrough with
no actionable findings, then its final check was cancelled when the PR closed.

Scope: merged the immutable reference-spec archive and the complete
WS-AUTH-001 planning package with 16 bounded implementation chunks. No runtime,
schema, dependency, frontend, review, contribution, or compensation behavior
was implemented.

Evidence: `.agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/reviews/WS-AUTH-001-PLAN-internal-review-evidence.md`

Next gate: explicit durable human approval of D4-D10 and a separate
`WS-AUTH-001-01` start signal. Create a fresh worktree/branch from the latest
merged `main`; do not implement chunk 01 in the planning worktree.

## 2026-07-11 - WS-AUTH-001-01 Started

The user explicitly approved D4-D10 and started only `WS-AUTH-001-01` by saying
"ok start" after the planning and post-merge memory PRs merged.

Branch: `codex/ws-auth-001-01-adopt-authorization-baseline`

Worktree: `/home/abiorh/flow/workstream-auth-001-01`

Scope: authorization ADR, canonical repository documentation, deterministic
stale-authorization documentation gate, operations runbook, and durable loop
state. Backend runtime, migrations, tests, dependencies, review, contribution,
compensation, frontend, and later authorization chunks remain inactive.

Next gate: implement and verify only the WS-AUTH-001-01 contract, run all
required internal reviewer tracks, prepare the trust bundle, and stop for human
review.

## 2026-07-12 - WS-ART-001-01 Merged

[PR #101](https://github.com/Flow-Research/workstream/pull/101) merged into `main` as
`050eb15eab8c57e6bc265477a5e92484d27a893c`.

Reviewed implementation SHA:
`5574bf59cf1cb86da76749e0cbc529036346fa8a`.

Final evidence-bound branch head: `2b8c2a0`.

Result: PASS after internal review, CodeRabbit repair, cancellation ownership
hardening, and a CI-order fixture repair. Agent Gates, Backend, and CodeRabbit
passed on the final head. The merge adds the provider-neutral immutable
artifact domain and local development adapter; it does not add public artifact
APIs, Flow Node integration, or product cutovers.

Evidence: `.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/reviews/WS-ART-001-01-internal-review-evidence.md`

External review response: `.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/reviews/WS-ART-001-01-external-review-response.md`

Trust bundle: `.agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/reviews/WS-ART-001-01-pr-trust-bundle.md`

Next gate: merge the post-merge memory update and stop. `WS-ART-001-02`
remains inactive pending a separate explicit user start.
