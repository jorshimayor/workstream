# PR Trust Bundle: WS-REV-001-02A

## Chunk

`WS-REV-001-02A` - Guide Chronology And Task Locking Split.

## Goal

Replace one oversized L1 runtime contract with three independently reviewable
and explicitly started children, without implementing runtime behavior.

## Human-approved intent

Preserve one Project Guide pipeline, exact Task-bound guide context,
canonical-human approval provenance, immutable chronology, and the existing
separation between checker remediation and Review-rooted human revision. Do not
start any runtime child from this planning parent.

## What changed

- Converted parent 02A into a permanently non-executable planning split.
- Added complete contracts for 02A1 Project/setup publication fencing, 02A3
  guide activation chronology, and 02A4 Task guide triplet screening.
- Reconciled the initiative plan, decisions, risks, discovery, conformance,
  source manifest, test design, status, review log, and downstream gates.
- Preserved the existing deferred 02A2 prepared-guide reactivation identity.
- Added exactly one schema-v2 merge intent naming 02A1 with explicit start.

## Why it changed

Required L1 preimplementation review found that the former contract crossed
three independent PostgreSQL concurrency and migration boundaries: the complete
Project/setup writer fence, canonical-human guide chronology, and Task guide
triplet screening. Those boundaries could not receive credible migration,
direct-SQL, race, rollback, downgrade, coverage, and human review proof in one
PR.

## Design chosen

02A1 serializes every current setup writer through a Project-first publication
fence. 02A3 builds immutable per-Project activation chronology and canonical
human provenance on that fence. 02A4 then stamps and protects the exact Task
guide triplet after chronology exists. The later 02A2 remains separately gated
after chunk 08 for hidden prepared superseded-guide reactivation.

## Alternatives rejected

- No combined two-migration runtime PR crossing all three boundaries.
- No guide activation before all setup writers share the publication fence.
- No current/latest fallback for ambiguous guide or Task history.
- No duplicated AUTH actor/profile lifecycle logic or ad hoc identity guards.
- No public superseded-guide reactivation in 02A3.
- No automatic start of 02A1 or any later child.

## Scope control

The candidate changes 18 files under the REV initiative and one merge-intent
file. It changes no backend code, model, schema, migration, service, route,
worker, test, dependency, CI workflow, frozen reference specification, active
product document, or AUTH/ART/CON owner artifact.

## Product behavior

This PR activates no product behavior. Current guide activation continues to
reject an already-active candidate. Task guide storage and screening remain
unchanged. Stored Review decisions remain only `accept`, `needs_revision`, and
`reject`, and adjudication remains deferred beyond v0.1.

## Acceptance criteria proof

The parent records exact merged AUTH dependencies and the sole migration head.
Each child specifies allowed and prohibited files, database objects, lock order,
migration refusal, direct-SQL parity, race and rollback proof, downgrade rules,
coverage floors, required reviewers, human focus, and a stop condition. The
merge intent names only same-initiative successor 02A1 and requires a separate
human start.

## Tests/checks run

All four stale-contract scanners, Markdown links, loop-memory state, 88 agent
gate tests, docstring coverage at 90.3 percent, one-head Alembic verification,
schema-v2 merge-intent validation, scope checks, ancestry checks, and diff
integrity passed on the planning candidate.

## Test delta

No executable test changed. No assertion, skip, xfail, test command, coverage
floor, or CI gate was removed or weakened.

## CI integrity

No CI or package-script file changed. The repository-wide 78 percent baseline
and independent 90 percent minimum for future new or materially changed backend
subsystems remain explicit in the executable child contracts.

## Reviewer results

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
reuse/dedup, test delta, and CI integrity all pass on reviewed planning SHA
`d5162648c3b6d8e045bac4c7f17c15589a06fabf`. The circuit breaker approved the
planning-only size exception because every executable boundary is split and
separately gated.

## External review

GitHub CI, CodeRabbit, and human review are pending. They supplement but do not
replace the completed internal review evidence.

## Remaining risks

Historical chronology or Task context ambiguity must fail closed in future
migrations. ART and CON capabilities remain dependency-owned future work. All
24 planned REV action dependencies remain unavailable. Later duration and human
revision exhaustion semantics still require explicit human decisions.

## Follow-up work

After merge, automated loop memory may name 02A1 with an explicit-start gate.
02A1 must refresh trusted main, the complete writer inventory, migration head,
plan review, and reviewer routing before any implementation. 02A3, 02A4, 02A2,
and 02B remain separately gated successors.

## Human review focus

Review the split boundaries and order, complete writer-fence inventory,
canonical-human ownership, immutable chronology, migration refusal/downgrade
safety, Task triplet integrity, and the absence of runtime changes.

## Human merge ownership

Only the user may approve and merge this specific PR. Merge does not authorize
02A1 or any other runtime implementation.
