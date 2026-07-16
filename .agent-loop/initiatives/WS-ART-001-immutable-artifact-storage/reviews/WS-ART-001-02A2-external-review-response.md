# External Review Response: WS-ART-001-02A2

## Pull Request

PR #129: `https://github.com/Flow-Research/workstream/pull/129`

Reviewed code SHA: `aba8325321b35a92778ffe3ddfb414ac7772f57f`

Published evidence-bound head: `236155a790fb0a2b71261bb316dcece8a93c4231`

## External Checks

- Agent Gates: passed on `236155a` in GitHub Actions run `29479578885`.
- Backend: passed on `236155a` in GitHub Actions run `29479571744`, including
  the full repository suite and coverage gates.
- CodeRabbit: passed on `236155a`; all five actionable findings across the two
  review rounds are marked addressed and no new finding was posted.

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
`WS-ART-001-02A2-internal-review-evidence.md`. GitHub Agent Gates, Backend, and
CodeRabbit all inspected and passed the evidence-bound published head.

## Remaining Risks

- The preparation boundary is intentionally inactive until `02A3`.
- No external finding remains open. Any later implementation change invalidates
  this evidence and requires relevant internal and external review again.
