# Decisions: WS-QUAL-001 Backend Coverage Floor

## D1: Ninety percent is authoritative

Status: accepted by the user on 2026-07-11.

The complete backend application must maintain at least 90 percent statement
coverage. The user corrected the initial 80 percent instruction to "90% not
80". The floor applies to all modules under `backend/app`, not only changed
files.

## D2: No exclusion-based compliance

Status: accepted through planning PR #99 on 2026-07-12.

Coverage may not be raised by omitting application modules, adding coverage
suppression pragmas, or measuring only a favorable package subset.

## D3: Ratchet from a reproducible baseline

Status: accepted through planning PR #99 on 2026-07-12.

Because current coverage is materially below 90 percent, implementation uses a
non-decreasing enforced ratchet across bounded PRs and reaches 90 in the final
chunk. Machine evidence preserves exact covered/total statements and a
six-decimal configured floor; base-ref comparison prevents regression. This is
an execution strategy, not a reduction of the final requirement.

## D4: Coverage work pauses AUTH-02 publication

Status: accepted through planning PR #99 on 2026-07-12.

AUTH-02 remains implemented on its own worktree but is not published while the
new 90 percent repository requirement lacks an approved enforcement path. The
pause avoids mixing roughly 849 statements of legacy coverage debt into an auth
PR. Resumption requires WS-QUAL to complete through its permanent 90 percent CI
floor and final post-merge memory, followed by an explicit user signal. This
decision does not discard or redesign the off-main auth implementation.

## D5: Behavior proof outranks percentage gains

Status: accepted by the user on 2026-07-12.

Coverage is a safety signal, not the purpose of a test. Every new test must
protect a real behavior or safety invariant and assert an observable result such
as state, lifecycle, authorization, audit, queue/retry, HTTP, redaction, cleanup,
or fail-closed behavior. Execution-only tests added to hit lines or percentages
are prohibited even if they increase coverage. Test-delta and product/ops
reviewers must reject them.

## D6: Chunk 01A uses a bounded 700-line exception for genuine proof

Status: accepted from the user's D5 direction on 2026-07-12 after internal L1
circuit-breaker review.

The original 500-line forecast proved incompatible with the required owned-DB
lifecycle, redaction, cleanup, ratchet, and negative behavior matrix: the two
control scripts alone require 387 readable lines before tests, guards, workflow,
and runbook. After the D7 split, `WS-QUAL-001-01A` may use at most 700
implementation lines; the cap applies to 01A, not the former combined Chunk 01
or 01B. The added budget is reserved for behavior tests and safety/error
handling. Allowed files and all production exclusions remain unchanged.
Crossing 700 requires another split and a new human decision.

## D7: Split database isolation from coverage policy

Status: accepted on 2026-07-12 after all required L1 reviewer groups rejected A2.

The executable harness reached 923 implementation lines before completing the
required ratchet and negative behavior matrix. Real concurrency/interruption
catalog proof, strict policy failure tests, and the operator runbook were
underestimated by A1. The rejected A2 proposal would have raised the cap to
1,100. Reviewers required `01A` for the least-privilege database lifecycle and
`01B` for coverage policy/CI/evidence. The split preserves genuine proof without
compressing safety code. Production scope and later chunks remain unchanged.

## D8: Split 01B policy core from baseline and CI publication

Status: accepted after internal split review and explicit user approval on
2026-07-12. Only 01B1 is started; 01B2 retains its later separate checkpoint.

The reviewed combined 01B contract proved larger than its 500-line boundary:
policy plus 19 behavior tests reached 480 lines before configured coverage,
workflow integration, the runbook, and several required negative cases. Further
compression would weaken proof or readability. The proposed repair is 01B1 for
pure policy parsing/arithmetic/schema/delta behavior, followed after merge and
memory by 01B2 for Git provenance, configured baseline evidence, CI ratchet,
and operations. Each retains a separate 500-line cap, L1 review, PR, merge,
memory, and explicit start checkpoint. No production or coverage-raising test
scope is added.

## D9: Stop 01B1 after repeated semantic-integrity findings

Status: circuit breaker triggered on 2026-07-12; replacement split not approved.

The 01B1 candidate reached 496/500 lines after two repair cycles. Eight review
tracks passed, but final test-delta review still found executable unittest skip
forms, aliased `pytest.raises` deletion, and missing successful arithmetic
boundaries. These are valid acceptance-criterion gaps in the same repeated
semantic-integrity class. The chunk must split again rather than compress tests
or exceed its cap. No replacement chunk may start without internal plan review
and explicit user approval.

## D10: Split parsing from semantic repository-delta enforcement

Status: direction explicitly approved by the user on 2026-07-12; internal split
review pending.

`01B1A` owns complete-app coverage arithmetic, intended configuration parsing,
canonical evidence parsing, strict runner metadata parsing, application pragma
validation, the compute-only CLI, and their behavior tests. `01B1B` separately
owns Git-helper integration, bounded memory/scope accounting, executable
skip/xfail detection, aliased assertion-deletion detection, and real repository
regressions. `01B2` remains unchanged. This boundary keeps parser arithmetic
independent from repository-diff semantics without weakening either proof set.
