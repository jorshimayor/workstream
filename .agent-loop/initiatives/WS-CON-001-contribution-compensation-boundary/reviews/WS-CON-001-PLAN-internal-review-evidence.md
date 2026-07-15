# Internal Review Evidence: WS-CON-001-PLAN

## 2026-07-15 AUTH-07B Executable-Boundary Reconciliation

This addendum is the current authoritative review state. It supersedes the
older trusted-main SHA, AUTH runtime assumptions, activation choreography and
parallel-REV freshness statements below. The reviewed plan is based on trusted
`main` `90eca12f6398f2ef168e634244d912765572c3e5` (merged AUTH-07B).

Reviewed code SHA: 31f7350be4a964faed4f3f0487a53de65c3f6840

Reviewed planning-tree SHA-256:
`07f8ed891ff15302b7b1a8e223cc122d98298d99ab0dd35660699866fff63cac`

The tree digest excludes this evidence file and includes the final initiative
status. It is reproduced from the initiative directory with:

```bash
find . -type f ! -path './reviews/WS-CON-001-PLAN-internal-review-evidence.md' -print0 | sort -z | xargs -0 sha256sum | sha256sum
```

Reviewed at: 2026-07-15T20:22:23Z

Reviewer run IDs: architecture/senior/reuse=`/root/plan_arch_senior`;
QA/test/product/ops/docs=`/root/plan_qa_product_docs`;
security/auth/privacy=`/root/plan_security_auth`

| Reviewer | Result | Blocking findings | Notes |
|---|---|---|---|
| senior engineering | PASS | None | Activation waves, prepared mutation seams, transaction ownership and chunk boundaries are executable. |
| QA/test | PASS | None | Local gates, failure cases, races, real-kernel denial and post-activation proof are explicit. |
| security/auth | PASS | None | Canonical identifiers, grants, fixed service identities, one-decision semantics and AUTH-only activation are coherent. |
| product/ops | PASS | None | Complete PaymentPolicy removal, legacy-row human gate, callback/delivery behavior and release dependencies remain explicit. |
| architecture | PASS | None | Review choreography is non-circular; outbox, ART, REV, AUTH and CON ownership boundaries do not cross. |
| CI integrity | N/A - with approved reason | None | This delta changes planning Markdown only and does not modify CI, dependencies, tests or coverage gates. |
| docs | PASS | None | Trusted-main facts, sibling freshness, source provenance, blockers and ownership language are truthful. |
| reuse/dedup | PASS | None | The plan reuses the central prepared protocol, shared dispatcher, ART capability, `workstream.artifact.binding` and existing grants/permissions. |
| test delta | N/A - with approved reason | None | No runtime test file changed; every later runtime chunk still requires test-delta review and retained evidence. |

Open sub-agent sessions: none

Valid findings addressed: yes

- Recorded the exact merged AUTH-07B state: 74 PermissionIds, 50 ActionIds,
  two active and 48 planned actions. All 23 proposed WS-CON ActionIds remain
  absent. The two proposed service-only PermissionIds remain absent.
- Kept authorization implementation entirely AUTH-owned: catalogue/owner/audit
  parity, closed typed contexts, evaluator dispatch, matched authority, grant
  loading/revalidation, service actors/assignments, composition dependencies and
  availability changes.
- Added an AUTH-owned D10 prepared-mutation protocol for every `T` operation:
  authority rows lock first, an opaque caller-session-bound handle is finalized
  once against locked product facts, one decision is staged, and AUTH never
  commits. Missing, reused, mismatched and cross-session/action handles deny.
- Repaired activation into registration -> hidden fail-closed feature behavior
  -> AUTH evaluator/activation waves. Review actions add the required REV-owned
  composition stage: AUTH registration -> CON capability/participant -> REV
  hidden composition while planned -> AUTH activation -> later readiness/public
  activation.
- Added the missing upstream dependency that `task.claim` has an existing
  PermissionId but no ActionId. AUTH-13 or a reviewed AUTH successor must order
  registration/typed-prepared contract, task resource behavior and evaluator/
  activation before CON-05A.
- Required the callback ActionId/new PermissionId and active binding-specific
  service actor/link/exact assignment before CON-04A so binding creation is
  executable while the callback action remains planned. Binding retirement
  remains planned until its CON-10B dependency guards exist and a later AUTH
  gate activates it.
- Put the D10 call site in CON-02B before OutboxEvent claim and made the active
  `outbox.dispatch` evaluator/assignment proof a local CON-08A gate.
- Repaired evidence ownership: CON prepares authority and locks only CON facts;
  ART locks/composes admission facts and performs the one final evaluation in
  durable Transaction A without commit/provider I/O. Provider continuation is
  post-commit under ART authority. The exact action reuses the existing fixed
  `workstream.artifact.binding` principal and existing
  `artifact.binding.create` PermissionId.
- Recorded sibling REV head `e59e2bbe823bc0ee2b0e59ff35f8352349618b2e`
  as non-consumable until its AUTH-07B choreography, outbox claim wording,
  source SHA and commit-bound evidence are refreshed and reviewed.
- Preserved the approved complete PaymentPolicy semantic cutover and physical
  removal. Only the legacy-row rebuild-versus-classified-backfill choice remains
  a human decision.

Deterministic evidence passed: `git diff --check`; Markdown links for 38 changed
Markdown files; stale Workstream wording; artifact-contract state; loop-memory
state; 71 agent-gate tests; and direct AUTH catalogue/runtime assertions for the
counts, availability, absent WS-CON IDs, absent service permissions,
`task.claim`, resource variants and matched-authority state. The authorization
stale-doc scan continues to flag exactly ten `HUMAN_WORKER_VOCABULARY`
occurrences in the explicitly non-canonical working transcription; CON-01 owns
its exact byte-preserving archival rename/classification and active-spec
reconciliation. This is not a waiver for an active document.

The focused async AUTH test environment was unavailable at final rerun because
this worktree's `backend/.venv` lacked an interpreter/plugin installation. That
does not weaken the planning proof: runtime files are byte-unchanged from
trusted main, the catalogue assertion passed with the available interpreter,
and no runtime completion is claimed.

Application/runtime code changed: no. The original PDF deletion remains an
unstaged user-worktree change and is excluded from both reviewed commits.

## 2026-07-15 Final Trusted-Main And Parallel-Dependency Review

This addendum is the current authoritative review state and supersedes older
statements below about D2, AUTH-07A merge status, REV joint-release adoption, or
an uncommitted planning candidate. D2 is approved:
`CompensationPolicyVersion` completely supersedes `PaymentPolicy`; only the
legacy-row reset-versus-classified-backfill rule remains a human gate.

Reviewed code SHA: ebdd21d231207845d44832a502de9dc56f237fd9

Reviewed planning-tree SHA-256:
`c3a82c1d5db19038709ff844a3bbde6cc77b21d525f408f2768d71c34883181d`

The tree digest excludes this evidence file and is reproduced from the
initiative directory with:

```bash
find . -type f ! -path './reviews/WS-CON-001-PLAN-internal-review-evidence.md' -print0 | sort -z | xargs -0 sha256sum | sha256sum
```

Reviewed at: 2026-07-15T17:08:45Z

Reviewer run IDs: architecture/senior/reuse=`/root/plan_arch_senior`;
QA/test/product/ops/docs=`/root/plan_qa_product_docs`;
security/auth/privacy=`/root/plan_security_auth`

| Reviewer | Result | Blocking findings | Notes |
|---|---|---|---|
| senior engineering | PASS | None | The chunk map, ownership seams, stop conditions, and long-term boundaries are coherent. |
| QA/test | PASS | None | Gates, races, failure cases, evidence retention, and the exact scanner regression contract are executable. |
| security/auth | PASS | None | Merged AUTH has 74 PermissionIds/50 ActionIds; 23 WS-CON actions and two service permissions remain absent/proposed; all 12 reused permissions exist. |
| product/ops | PASS | None | Complete PaymentPolicy removal, legacy-row gate, fulfillment lifecycle, drain, and joint release behavior are explicit. |
| architecture | PASS | None | CON-02B solely owns outbox transitions; CON owns narrow ports; REV supplies only hidden release-control composition. |
| CI integrity | N/A - with approved reason | None | This reviewed delta changes planning Markdown only; CON-01 itself requires CI-integrity review when its script/test files change. |
| docs | PASS | None | Source provenance, active/archive precedence, current REV status, and PaymentPolicy removal are truthful. |
| reuse/dedup | PASS | None | Claim validation, drain observation, and lifecycle fences reuse sole owners through narrow ports without repository duplication. |
| test delta | N/A - with approved reason | None | No test file changes in this planning delta; CON-01 requires test-delta review for its planned gate regression. |

Open sub-agent sessions: none

Valid findings addressed: yes

- Rebased onto trusted `main` `e9d72a1`, including merged ADR 0014 and AUTH-07A
  catalogue/audit foundations, and validated exact AUTH counts/mappings.
- Preserved complete PaymentPolicy removal in split semantic-cutover and physical
  removal chunks; no advisory, compatibility, or execution fallback survives.
- Made merged REV-02 exact `Submission.task_assignment_id` lineage a hard
  CON-05A prerequisite.
- Preserved CON-02B as the sole OutboxEvent claim/retry/finalization owner. A
  feature handler only validates immutable claim generation through
  `OutboxClaimValidationPort`, never locks or mutates OutboxEvent, and returns a
  typed outcome after CON work.
- Added canonical lifecycle-fence lock ordering, durable pre-I/O state, and the
  prohibition on provider I/O under a database transaction, lifecycle fence,
  or OutboxEvent lock.
- Assigned `FulfillmentDispatchFence`, `FulfillmentCallbackFence`, and
  `FulfillmentLifecycleDrainObservationPort` to CON-owned chunks while limiting
  REV-12A to hidden composition and REV-13 to sole activation/live drill.
- Recorded the content-reviewed but dirty REV snapshot atop `3e09e99` as
  non-consumable. Its stale handler-claim wording must be repaired, committed,
  commit-freshness reviewed, refreshed, and merged before use.
- Made CON-01 own the exact authorization-scanner history entry created by its
  hash-proven archival rename plus fail-closed tests. The cross-scanner equality
  assertion subtracts only that named auth-only path and separately proves the
  unchanged artifact scanner already excludes reference specs by prefix.
- Preserved AUTH ownership: WS-CON proposes identifiers and supplies resource
  facts/guards only; it does not implement the authorization service.

Deterministic evidence passed: Markdown links for 38 changed Markdown files,
general stale wording, artifact-contract state, loop-memory state, 71 agent-gate
tests, reference hashes, and `git diff --check`. The authorization stale-doc
scan continues to flag ten human-worker vocabulary occurrences only in the
explicitly non-canonical working transcription. CON-01 now owns its exact
byte-preserving archive rename/classification and the reconciled active spec;
this is not a waiver for an active document.

Application/runtime code changed: no. The original PDF deletion remains an
unstaged user-worktree change and was excluded from both reviewed commits.

## 2026-07-15 End-to-End Reference Reconciliation Addendum

The supplied generation-2 Markdown was audited against AUTH head `3ab25cf`,
canonical ART/REV decisions, ADR 0014, the shared-outbox plan, and current
PaymentPolicy consumers. Final internal delta reviews passed:

| Track | Result | Closed findings |
|---|---|---|
| security/auth + senior engineering | PASS | Exact ActionId/PermissionId handoff, request-scoped AUTH boundary, service-only callback/outbox authority, human/request versus dispatcher execution, bounded callback data, split award routes |
| product/ops + QA/test | PASS | 05A/05B executable removal scope, contribution/evidence disclosure, delivery retry and callback transitions, conformance traceability |
| architecture + docs | PASS | ART typed capabilities/recovery/provider matrix, centralized adapter factory, shared outbox ownership, source provenance/hash, stale-prefix and Markdown-link checks |

The reconciled Markdown remains a non-normative working transcription. CON-01
still owns creation and review of the active specification/ADR; no runtime chunk
is activated by this addendum.

## Chunk

`WS-CON-001-PLAN` - Contribution And Compensation Planning

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: f5995518a0d1723be5600d4bb306d99d3ba077a7

Reviewed planning-tree SHA-256: `367a43d2913276b1b700f9d55ae30ff812d8478c520bf338035c3b8671048f43`

Reviewed at: 2026-07-15T14:24:59Z

Reviewer run IDs: senior-engineering/architecture/reuse=`/root/plan_arch_senior`;
QA/test/product/ops/docs=`/root/plan_qa_product_docs`;
security/auth/privacy=`/root/plan_security_auth`

The planning-tree digest excludes this post-review evidence file. After the
reviewed digest, only this evidence and initiative status/chunk-status fields
changed.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS AFTER FIXES | None | Cross-initiative ownership, PR sizing, reusable infrastructure, and executable contracts repaired. |
| QA/test | PASS AFTER FIXES | None | Traceability, isolated PostgreSQL evidence, separate subsystem coverage, retained attempts, and release handoff repaired. |
| security/auth | PASS AFTER FIXES | None | Proposed action/resource contracts, service actor, binding states, rate controls, retirement and privacy repaired. |
| product/ops | PASS AFTER FIXES | None | Current re-review confirms complete PaymentPolicy removal, the open legacy-row gate, REV-02 ordering, fence ownership, and joint activation operations. |
| architecture | PASS AFTER FIXES | None | REV ownership, sole activation, outbox/audit/factory boundaries and ART/AUTH ownership are coherent. |
| CI integrity | N/A - with approved reason | None | Planning Markdown only; no workflow, script, dependency, test, or coverage gate changed. |
| docs | PASS AFTER FIXES | None | Archive provenance, active-doc inventory and generated-companion release ownership are explicit. |
| reuse/dedup | PASS AFTER FIXES | None | Shared hashing, idempotency, workers, rate control, audit, outbox, typed factory and existing Submission are reused. |
| test delta | N/A - with approved reason | None | No runtime test file changed; runtime contracts prohibit weakening and require same-run evidence. |

## Valid Findings Addressed

- Removed all REV-owned ReviewLease schema/claim/composition work from WS-CON;
  REV-03/06/10 retain their exact ownership.
- Made REV-13 the sole joint production activation/live-drill owner and added an
  exact evidence-driven release handoff without editing the sibling worktree.
- Split shared outbox truth from its dispatcher, added a shared lifecycle-audit
  participant owner, and kept feature handlers separate.
- At the original pre-merge review point, reconciled trusted-main 73
  PermissionIds versus AUTH-07A's 74/50 candidate state. The current addendum
  records AUTH-07A merged through `e9d72a1`; every WS-CON ActionId remains
  proposed with exact target/principal/facts/
  guard/revalidation/registry/resource/activation ownership.
- Added canonical service ActorProfile binding, exact callback assignment,
  actor/link/binding state distinctions, per actor+binding rate control, and
  dependency-safe deferred retirement.
- Extended the accepted REV lock order and assigned every cross-feature race to
  a chunk where both sides exist.
- Superseded the advisory PaymentPolicy direction with complete semantic and
  physical removal plus TaskAssignment compensation freeze
  one atomic cutover with drain/rebuild/downgrade rules.
- Split persistence, services, delivery, callback, evidence, reads, operations,
  and release readiness into explicit contracts with exact allowed/not-allowed
  paths and reviewer requirements.
- Added deterministic ADR-0014 compensation adapter/factory composition and
  prohibited provider-specific/fallback/service-locator construction.
- Added exact versioned event names and a conformance matrix for retained source
  invariants, role/privacy cases, races, failures, replays and live evidence.
- Added a normative runtime proof that erases stale coverage, retains immutable
  attempt-specific isolated-PostgreSQL metadata, preserves the 78-percent global
  floor, and runs a separate 90-percent report for every changed subsystem.

## Commands Run

```bash
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_loop_memory_state.py
python3 scripts/test_agent_gates.py
python3 scripts/check_internal_review_evidence.py
git diff --check
sha256sum <revised WS-CON pair>
git show HEAD:<original WS-CON PDF> | sha256sum
python3 scripts/check_stale_authorization_docs.py
```

Results:

- Markdown links passed for 35 changed Markdown files.
- General stale wording, artifact-contract and loop-memory checks passed.
- Agent gate regression suite passed: 71 tests.
- The internal-evidence gate correctly remains red in this uncommitted planning
  worktree because its reviewed-SHA protocol accepts only a committed candidate,
  not the supplementary planning-tree digest. Before any PR, commit the approved
  planning candidate, rerun exact-head reviewers/evidence, and require this gate
  to pass; this local evidence is not PR-ready proof.
- `git diff --check` passed.
- Superseded after the 2026-07-15 end-to-end reconciliation: the Markdown is
  now an editable working transcription with a new truthful hash in
  `SOURCE_MANIFEST.md`; the generation-2 PDF hash remains unchanged.
- Authorization stale-contract scan intentionally rejects the unadopted raw
  candidate Markdown for `/v1` and legacy human-worker vocabulary. This is the
  evidence requiring archival treatment and a reconciled active spec in CON-01,
  not a gate waiver for an active document.

## Remaining Risks

- D1/D7/D8 and the callback/outbox service PermissionIds require explicit human
  approval. D2 removal is approved; only legacy-row handling remains open.
- Original PDF disposition remains a pre-existing user-worktree concern;
  generation-2 PDF preservation and working-Markdown provenance remain CON-01
  gates.
- AUTH, ART and REV prerequisites are unmerged. The active REV working delta
  incorporates `JOINT_RELEASE_HANDOFF.md` but must become a branch-reachable
  reviewed commit, rebase, and merge before either public surface can activate.
- Exact migration numbers, merged symbols, production adapter/provider and live
  values must be refreshed at each approved implementation chunk.
- This uncommitted reviewed plan still requires a committed exact-head review
  cycle before it can be published or treated as PR evidence.

## Stop Condition

Planning is internally reviewed. No implementation/specification chunk is
active. Await explicit human approval; do not start WS-CON-001-01 automatically.
