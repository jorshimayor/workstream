# External Review Response: WS-ART-001-02A2

## Pull Request

PR #129: `https://github.com/Flow-Research/workstream/pull/129`

Reviewed code SHA: `aba8325321b35a92778ffe3ddfb414ac7772f57f`

Published evidence-bound head: pending

## External Checks

- Agent Gates: the prior published head `98a7f88` passed; final-head rerun is
  pending publication.
- Backend: the prior published head `98a7f88` passed; final-head rerun is
  pending publication.
- CodeRabbit: reviewed `98a7f88`, reported two additional actionable findings,
  and marked its check successful. Final-head incremental review is pending
  publication.

## Comments Addressed

- CodeRabbit: reject `NaN` and infinity in artifact preparation durations.
  Fixed with finite-number validation and regression cases.
- CodeRabbit: do not validate an in-progress root marker before acquiring the
  ledger lock. Fixed by validating marker contents under the lock.
- CodeRabbit: bound multiprocessing pipe receives and guarantee child cleanup.
  Fixed with timed `poll`, explicit failure, and `finally` cleanup.
- CodeRabbit: preserve the original cancellation when temporary cleanup fails
  and retain retryable `.part` ownership. Fixed in `aba8325` with exact
  cancellation-message proof, retained-file proof, canonical cleanup retry,
  and successful exact-request retry.
- CodeRabbit: make marker-validation ordering independent of spawned-process
  startup speed. Fixed in `aba8325` with explicit child-start and lock/order
  events plus bounded cold-start and child-shutdown limits.

## Comments Deferred

- None.

## Human Decisions Needed

The user remains the only merge authority for PR #129. Passing external checks
will not authorize merge or start `02A3`.

## Commands Rerun

Local deterministic and internal review evidence is recorded in
`WS-ART-001-02A2-internal-review-evidence.md`. GitHub checks and CodeRabbit must
still inspect the evidence-bound published head.

## Remaining Risks

- The preparation boundary is intentionally inactive until `02A3`.
- Final external status must be recorded only after GitHub reports the exact
  published head.
