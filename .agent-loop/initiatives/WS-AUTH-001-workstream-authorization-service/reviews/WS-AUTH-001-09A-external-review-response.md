# WS-AUTH-001-09A External Review Response

## Review Source

CodeRabbit completed its first review of PR #132 on 2026-07-16 and posted two
actionable comments against head `c4200a7`.

## Comments Addressed

1. **Historical migration inputs were mutable - valid, fixed.** Revision
   `0023` now imports its identity values, canonical mapping envelope, private
   loader/path custody, source digest, and database-binding derivation only from
   `migration_contracts.service_identity_0023`. That versioned migration-only
   package imports no actor or authorization application module. Setuptools
   explicitly includes the package so installed-wheel replay matches source
   checkout replay. Tests prove the revision import boundary and full mapped
   upgrade/downgrade behavior using an envelope produced by the current
   operator tool. The revision supplies its checkout/deployment root explicitly,
   so installed-wheel module location cannot weaken repository/worktree path
   custody.
2. **CLI engine disposal used a second event loop - valid, fixed.** One async
   entrypoint now runs the workflow and `dispose_engine()` on the same event
   loop. Cleanup failure cannot replace an existing mapping/database failure;
   `database_cleanup_failed` is returned only when workflow execution itself
   succeeded. Cleanup `BaseException`, including cancellation, cannot replace
   an existing privacy-bounded failure. Regression tests prove loop identity
   and both error-priority cases.

## Informational Warning Not Applied

CodeRabbit's separate 25.69 percent docstring warning does not use the
repository's enforced configuration. GitHub Backend passed, and local
`docstr-coverage --config .docstr.yaml` reports 92.1 percent against the required
repository threshold. No docstring gate or exclusion changed.

## Validation

- Frozen-contract, installed-location custody, and CLI lifecycle tests: passed.
- Focused revision `0023` mapped upgrade/downgrade test: passed against isolated
  PostgreSQL.
- Ruff over the application, migration-only package, tests, operator script,
  and revision: passed.
- Full GitHub Backend and Agent Gates passed before the repair and will rerun on
  the pushed repair head.

## Remaining Gate

Exact-head internal re-review passes with no remaining finding. Refreshed GitHub
checks and CodeRabbit re-review remain before human merge approval.
