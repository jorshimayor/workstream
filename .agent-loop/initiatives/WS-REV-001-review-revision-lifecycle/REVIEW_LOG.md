# Internal Plan Review Log: WS-REV-001

## CON Reconciliation Addendum - 2026-07-15

REV's joint integration evidence was refreshed against CON planning commit
`42cf11f`. Its content-level reviews closed 05A/05B PaymentPolicy
removal, AUTH service-only outbox/callback authority, ART capability/recovery,
adapter composition, disclosure, provenance, and REV-13 joint activation.
CON runtime publication remains a dependency-owned gate; this planning chunk
does not treat sibling uncommitted changes as merged contracts.
Remaining runtime gates are the immutable reviewed-submission digest/context
contract, unsafe canonical-row downgrade refusal, merged dependency SHAs, and
the normal human start gate.

Current post-CON delta review:

| Track | Agent | Result | Disposition |
|---|---|---|---|
| Security/auth + senior engineering | `/root/rev_con_security` | PASS AFTER FIXES | Trust-state wording corrected; dependency-owned CON publication remains gated; merge intent added |
| Product/ops + QA/test | `/root/rev_con_product` | PASS AFTER FIXES | Merge intent scoped; missing CON-05A REV-02 gate recorded as an owning-CON blocker |
| Architecture + docs | `/root/rev_con_arch` | PASS AFTER FIXES | Stale untracked/reviewed wording corrected; original archival deletions excluded from publication |


## Scope

Reviewed the initiative intent, discovery, decisions, risks, plan, conformance
matrix, chunk map, and every chunk contract. These are planning reviews only;
each implementation chunk still requires its own zero-trust reviewer fanout.

## Final results

| Track | Agent | Final result | Material repairs verified |
|---|---|---|---|
| Senior engineering | `/root/rev_plan_senior` | PASS | Submission lineage constraints, admitted-only backfill, chunk split, outbox gate, lock/race proof |
| QA/test | `/root/rev_plan_qa` | PASS | Fresh isolated Postgres coverage, conformance matrix, live drill order, WS-CON rollback/replay matrix |
| Security/auth | `/root/rev_plan_security` | PASS | Transaction-aware AUTH links, eligibility/self-review, evidence authorization, replay disclosure, bounded privacy, closed rollout |
| Product/ops | `/root/rev_plan_product` | PASS | Final coherent cutover, existing-row activation, D6 effects, invalidations, metrics/notifications, no non-review CON effects |
| Architecture | `/root/rev_plan_architecture` | PASS | AUTH/ART/CON ownership, shared audit/outbox, lock hierarchy, one-way ports, composition and activation sequence |
| Docs/spec adoption | `/root/rev_plan_docs` | PASS | Immutable archival provenance, active contract, scanner scope, migration/worker docs, generated/checksum proof |
| Reuse/dedup | `/root/rev_plan_reuse` | PASS | Existing Submission/task/checker/audit/outbox/idempotency/Celery reuse and single canonical submission path |

## Initial failures and disposition

Initial reviews failed or imposed conditions around early public activation,
dependency-owned wildcard scope, duplicate outbox/audit/idempotency mechanics,
submission/checker transaction ownership, indiscriminate historical queueing,
revision chunk size, archival replacement, stale coverage evidence, incomplete
live proof, and underspecified authorization/privacy races. Every valid finding
was incorporated into the plan and explicitly re-reviewed to PASS.

## Residual human gates

Internal PASS does not approve implementation. The decisions in `INTENT.md`
remain human-owned, especially D6 limit/deadline behavior. Chunk 01 remains
inactive until explicit approval, and every later dependency gate is refreshed
from trusted `main` when that chunk is activated.

## Post-clarification final review - 2026-07-15

Human clarification confirmed the one-Project-Guide ADR 0010 flow, ART-backed
current packet, immutable Submission/Review history, and WS-CON creation matrix.
The plan was then repaired and re-reviewed across the following tracks.

The later D5 clarification confirmed that any different currently active guide,
including an older activation sequence, is authoritative and causes a recorded
backward rebase rather than a manager-repair block.

| Track | Final result | Final scope verified |
|---|---|---|
| Senior engineering | PASS | Submission/CheckerRun rebase constraints, guide activation sequence, preparation/reconciliation identity, legacy cutover, admin persistence |
| QA/test | PASS | Migration/direct-SQL proof, race permutations, ART authority races, contribution lineage, duplicate reconciliation, recurrence, rollback |
| Security/auth | PASS | Relationship-scoped history, active-lease content, two-phase ART intake, 22-action AUTH gate, typed PM/Operator resources, replay/denial guards |
| Product/ops | PASS | Frozen Task Context, PM successor repair, Operator legacy closure, reviewer/submitter history, exact CON effects, operable routes |
| Architecture | PASS | Task-owned guide/revision participants, Submission-bound checker context, canonical lock order, AUTH/ART/CON ownership, admin schema ownership |
| Docs/spec adoption | PASS | Impacted-doc scope, 22-action AUTH gate, exact routes, admin/reconciliation schema, status, and review evidence |
| Reuse/dedup | PASS | Existing Submission/ProjectGuide/CheckerRun/task participants reused; justified decision/admin idempotency and reconciliation evidence aggregates |

Material repairs included:

- activated-guide-only ordering and deterministic revision preparation;
- non-branching Review-rooted preparation episodes and a non-forgeable legacy
  revision cutover;
- immutable exact checker admission, active-packet ART disclosure, and two-phase
  evidence authorization;
- exact Submission-to-TaskAssignment and WS-CON actor/lease/policy/hash lineage;
- Project Manager successor repair and evidence-linked Operator legacy closure;
- AUTH-owned repair/closure ActionIds mapped to existing PermissionIds; and
- canonical reconciliation fingerprints, one unresolved generation, atomic
  resolution, duplicate-scan reload, and controlled post-resolution recurrence.
- corrected source provenance for the current revised Markdown hash/counts and
  its section 4.6 divergence from the unchanged PDF companion.

## Post-Main Release-Control Final Review - 2026-07-15

`git pull --no-rebase origin main` merged trusted main `e9d72a1` into REV HEAD
`3e09e99` without conflict. AUTH-07A became merged foundation rather than
unmerged discovery evidence. The later amended AUTH-08 contract supersedes the
old catalogue arithmetic: after AUTH-08's prospective 57 actions (9 active, 48
planned), the four REV additions require 57-to-61 typed catalogue, owner, and
PostgreSQL audit parity, producing 9 active and 52 planned.

The first fresh review failed because shutdown persistence had no executable
owner. Chunk 12A was added, then repaired through repeated zero-trust review:
exact cutover/shutdown phases, generation-aware reactivation, fresh Operator
authority, command-class mapping, typed review/CON drain ports, mandatory
dispatch/callback hooks, durable provider-I/O handoff, and complete race proof.

| Track | Agent | Final result | Final scope verified |
|---|---|---|---|
| Senior engineering | `/root/rev_repair_senior` | PASS | Executable graph, command mapping, remote-I/O handoff, operable drill |
| QA/test | `/root/con_contract_review` | PASS | Phase/class matrix, races, crash/retry, migration, coverage gates |
| Security/auth | `/root/con_code_boundary` | PASS | Actor kind, fresh authority, exact action parity, fences, no lock-held I/O |
| Product/ops | `/root/con_contract_review` | PASS | Legacy continuity, revision/CON behavior, drain, reactivation |
| Architecture | `/root/rev_repair_senior` | PASS | Port ownership, composition, repository isolation, ADR 0014 |
| Docs/spec adoption | `/root/con_code_boundary` | PASS | Provenance, dependency status, terminology, proof ownership |
| Reuse/dedup | `/root/rev_repair_senior` | PASS | Shared hashing/idempotency/audit/outbox/workers/adapters reused |

All valid findings are closed. The human approved D6, reviewer-current
precedence, coherent activation, the sequence, and planning publication on
2026-07-15. Dependency merges, planning merge, and the successor's separate
post-merge start gate still prevent runtime implementation.

## AUTH-07B Dependency Refresh - 2026-07-15

Trusted main `90eca12` merges AUTH-07B. REV reviewed the merged runtime before
updating its dependency snapshot. The kernel shape, canonical actor boundary,
deny-by-default action handling, exact two active self actions, update lock
order, and bounded denial evidence are compatible with the planned boundary.

The dependency is not yet safe for REV consumption:

- High: `get_authorization_service` commits any open request-session transaction
  during generic successful teardown, so future feature work could be committed
  without its owning service or route doing so.
- Medium: SQL failure while `AuthorizationService.require` stages decision
  evidence can escape the dependency as an unstructured 500 on self-read.
- Medium: the actor-self cutover returns existing actors without advancing
  `ActorProfile.last_seen_at` or `ActorIdentityLink.last_verified_at`.

REV owns no repair in AUTH code. PLAN, DECISIONS, RISKS, CHUNK_MAP, chunk 01,
the first AUTH-consuming chunk 05, and final chunk 13 now fail closed on
AUTH-owned repair and regression proof. The catalogue snapshot is corrected to
74 PermissionIds and 50 ActionIds split into 2 active actor-self actions and 48
planned actions; every one of the 24 REV action dependencies remains inactive.

Review tracks: senior engineering/architecture/reuse found the generic commit
and error mapping defects; QA/product confirmed the error and timestamp
regressions; security/auth found no separate canonical identity, action parity,
or denial privacy defect. Ruff and 24 focused authorization tests passed
locally; merged PR #130's Backend, Agent Gates, and CodeRabbit checks passed.
Database integration was not rerun locally because the isolated test database
URL was not configured.

At this 2026-07-15 refresh, PR #128 was parked and its local main merge was not
pushed. ART PR #129 was conflict-blocked despite approval and green checks; it
still needed to refresh from main and merge before the final dependency refresh,
reviewer pass, SHA binding, and PR update.

The human also corrected the reference-file ownership decision: the revised
supplied Markdown/PDF contents belong at the canonical WS-REV filenames. The
temporary `(2)` paths were removed, canonical hashes were refreshed in the
reference README/SHA256SUMS, and no second archival generation remains in the
active plan.

## AUTH-08 Dependency Refresh - 2026-07-16

`git pull origin main` rebased the four local REV planning commits without
conflict onto trusted main `aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3`.
That merge commit is AUTH-08 PR #131; its final branch head is
`0832358a0262805f553d05b50b0d778e6e6ad995`.

REV reviewed the merged runtime, migration, tests, AUTH evidence, and external
review response. AUTH-08 resolves all three AUTH-07B consumption findings:

- dependency teardown rolls back rather than committing an open caller-owned
  transaction;
- typed authorization-evidence persistence failure maps once to retryable
  `503 service_unavailable`; and
- successful existing-actor GET/PATCH routes advance both canonical
  verification timestamps in the route-owned transaction while denial or
  persistence failure rolls them back.

The merged catalogue now contains 74 PermissionIds and 57 ActionIds: 9 active
and 48 planned. All 20 existing revised-spec submission/review actions remain
planned, the four later REV additions remain absent, and all 24 REV dependencies
remain inactive. The later AUTH-owned migration is therefore exactly 57-to-61,
producing 9 active and 52 planned without activating an action early.

AUTH evidence records 275 focused behavior tests at 90.17 percent branch-aware
focused coverage, 17 isolated Alembic tests, final Backend run `29481047118`,
PR-head Agent Gates runs `29481047119` and `29481057005`, final-head Agent Gates
run `29482246184`, and successful CodeRabbit.
The three former blockers are retained as regression invariants at every REV
consumer rather than unresolved AUTH work.

At this AUTH-08 refresh, ART PR #129 was open and conflict-blocked at
`a7432c87719e694038dae5b386b7c9b3ecf9e9b4` despite green checks. PR #128 was
parked and unpushed. Final PLAN publication review and exact-SHA evidence binding
were deferred until ART merged and its contracts were reconciled from trusted
main.

## ART-02A2 Dependency Refresh - 2026-07-16

`git pull origin main` rebased the five local REV planning commits without
conflict onto trusted main `9a04434e2f23c5dec8939dadb943bba4d85110c0`.
That merge commit is ART-02A2 PR #129; its final branch head is
`32aab89262a3944f305e9e5dc4c65a2d31e2e144`.

REV reviewed the merged ART contract, implementation, tests, internal evidence,
external response, and downstream ART chunk gates. ART-02A2 establishes only an
inactive committed-source/private-scratch preparation boundary. It changes no
active ArtifactStore v1 interface, provider selection, schema, product route,
action, permission, reviewer packet read, or evidence-intake behavior.

The boundary is compatible with REV only by remaining behind ART-owned future
capabilities. REV never imports `ArtifactScratchManager`, `PreparedArtifact`, or
`CommittedArtifactSource`; stores scratch paths, ledger reservations, or source
descriptors; or creates an alternate preparation manager. Later ART v2,
MinIO/AWS S3, admission, verification/publication, read/intake/retention,
recovery, checker, projection, and live-proof chunks remain hard runtime gates.

ART evidence records 154 focused tests at 94.40 percent scoped coverage, 38
isolated artifact PostgreSQL tests, 207 isolated AUTH/authentication/Alembic
tests, final Backend run `29487194049`, Agent Gates runs `29487194116` and
`29487194180`, and successful CodeRabbit. PR #129 is merged, so the planning
publication dependency is resolved. PR #128 still requires current-snapshot
internal review, exact reviewed-SHA evidence binding, branch update, and fresh
external checks before human merge.

## PR #128 External Review Response - 2026-07-16

The refreshed PR passed Backend, Agent Gates, and CodeRabbit status checks, but
a thread-aware audit found eight unresolved actionable CodeRabbit comments.
Every comment was valid and in scope. The plan was repaired to:

- add the exact WS-IMP archival pair to REV-01 allowed scope;
- clarify the merged WS-CON compensation-policy prerequisite for REV-03;
- require TaskService route, checker-worker, and composition-path proof in
  REV-05 and correct `later-admitted` wording;
- define submitter chain ownership through the canonical contributor on the
  exact Submission-associated TaskAssignment;
- add explicit API-contract/OpenAPI absence proof to REV-07 and REV-09A; and
- expand REV-13 final conformance tests and lifecycle-control package coverage.

No comment is deferred. The detailed thread mapping is recorded in
`reviews/WS-REV-001-PLAN-external-review-response.md`. Because these are
non-evidence planning-contract changes after the prior reviewed SHA, required
internal reviewer tracks and exact-SHA evidence binding must run again before
the branch is republished.

## WS-XINT-001 Boundary Reconciliation - 2026-07-17

The branch rebased without conflict onto trusted main
`5d353b6d3f8a36b9b9ffdc1959487a150ac25fd1`, merge commit for WS-XINT-001 PR
#139. Its ADR 0015 and AUTH/REV, AUTH role/service, ART/REV, and REV/CON handoffs
supersede conflicting active REV planning wording. The archival WS-REV Markdown
and PDF remain provenance inputs, not authority over merged boundary decisions.

Three read-only discovery reviews failed the pre-reconciliation plan and found
the same material drift:

| Review | Result before repair | Required correction |
|---|---|---|
| Architecture | FAIL | AUTH-only activation custody; prepared mutation order; ART v2 ports; no CON or ART repository ownership |
| Security/auth + product/ops | FAIL | Independent exact reviewer grant; role-specific invalidation; fixed AUTH-09E services; canonical task effects |
| ART + CON integration | FAIL | REV-owned packet/evidence relations; two-phase binding; mandatory flush-only CON participant; stable artifact lineage |

The reconciled plan now requires registration -> hidden behavior -> AUTH
activation -> REV product release, derives future action totals from trusted
main, and keeps the four proposed REV actions separate from ART's proposed
`artifact.review_evidence.binding.create` action. It uses request-scoped AUTH
for reads and the AUTH-first prepared protocol for mutations.

ART v2 is the only future provider boundary. REV owns
`ReviewPacketManifest` and `ReviewEvidenceArtifact` while ART owns bytes,
bindings, candidates, finalization, and providers. The currently merged ART
plan does not schedule `WS-ART-001-REV-EVIDENCE`; REV-07 is blocked until ART
adds, approves, and merges that owner chunk.

Review authority requires one exact active `reviewer` grant. Reviewer
invalidation changes only review preference, lease, and queue state. Six
protected review jobs use separate fixed AUTH-09E identities for preference
expiry, lease expiry, authority-invalidation reconciliation, general review
reconciliation, artifact-reference reconciliation, and projection. Human
Operator authority is never borrowed as a job identity.

REV-08 now freezes the decision contract without committing a canonical
Review. REV-10 creates the first canonical Review transaction only after the
CON flush-only participant is merged; every Review creates a reviewer
ContributionRecord, accept also creates the submitter record, and CON performs
no ART call. The plan interprets the handoff's versioned Submission lineage as
the repository's existing immutable versioned `Submission`, requiring the ART
cutover to stabilize server-derived `Submission.artifact_hash` before CON copies
it to `ContributionRecord.artifact_hash`. Optional contribution-evidence
projection is outside the core transaction and release gate.

Human reject moves the task to canonical `rejected`; approved administrative
limit/deadline or unrecoverable-legacy closure moves it to `cancelled` with an
exact reason. No `closed/review_rejected` status is introduced. REV-13 exposes
only REV-owned surfaces after AUTH activation and CON-owned readiness; it does
not edit or register CON routers.

All earlier exact-SHA PLAN review evidence is historical after this material
change. Fresh senior engineering, QA/test, security/auth, product/ops,
architecture, docs, reuse/dedup, test-delta, and CI-integrity review plus a new
snapshot binding are required before PR #128 is republished.
