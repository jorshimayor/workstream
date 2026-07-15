# Internal Review Evidence: WS-CON-001-PLAN

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
| product/ops | SUPERSEDED | Re-review required | This row predates approved complete PaymentPolicy removal and the end-to-end reference reconciliation. |
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
- Reconciled trusted-main 73 PermissionIds versus unmerged AUTH-07A 74/50 state;
  every WS-CON ActionId remains proposed with exact target/principal/facts/
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

- D1/D2/D7/D8 and the callback PermissionId require explicit human approval.
- Original PDF disposition remains a pre-existing user-worktree concern;
  generation-2 PDF preservation and working-Markdown provenance remain CON-01
  gates.
- AUTH, ART and REV prerequisites are unmerged. The WS-REV owner must adopt and
  internally review `JOINT_RELEASE_HANDOFF.md` before either public surface can
  activate.
- Exact migration numbers, merged symbols, production adapter/provider and live
  values must be refreshed at each approved implementation chunk.
- This uncommitted reviewed plan still requires a committed exact-head review
  cycle before it can be published or treated as PR evidence.

## Stop Condition

Planning is internally reviewed. No implementation/specification chunk is
active. Await explicit human approval; do not start WS-CON-001-01 automatically.
