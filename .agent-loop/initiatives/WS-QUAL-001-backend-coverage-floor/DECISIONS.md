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
