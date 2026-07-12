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
PR. Resumption requires an explicit user signal after the coverage plan is
approved; this decision does not discard or redesign the auth implementation.
