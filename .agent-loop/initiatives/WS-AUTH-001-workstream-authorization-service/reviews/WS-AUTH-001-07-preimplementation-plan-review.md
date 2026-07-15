# WS-AUTH-001-07 Preimplementation Plan Review

## Initial verdict

`FAIL` before runtime implementation.

## Review tracks

| Track | Result | Blocking findings |
|---|---|---|
| senior engineering / architecture / reuse | FAIL | Combined catalogue, migration, kernel, APIs, manifest, and transaction proof were not one bounded L1 change; required ORM and route files were omitted. |
| security/auth / product/ops / docs | FAIL | Grant-backed and project-scoped APIs preceded authority sources; active actions, denial precedence, transaction ownership, response privacy, and planned artifact boundaries were incomplete. |
| QA/test / CI integrity | PASS WITH CONDITIONS | Missing allowed tests, exact action tables, migration versioning, synchronized race proof, isolated-test runner contract, and changed-subsystem 90 percent coverage. |

No application, migration, dependency, workflow, or test code was changed before
these verdicts.

## Valid repair

- Split parent AUTH-07 into AUTH-07A and AUTH-07B.
- AUTH-07A owns exactly 73 PermissionIds, 30 four-field planned ActionIds, and
  migration `0021` action-aware audit parity. No action is executable.
- AUTH-07B owns the minimal deny-by-default kernel and activates exactly
  `actor.profile.read_self` and `actor.profile.update_self` on the existing
  `/api/v1/actors/me` routes.
- Permission/admin-role definition APIs move to AUTH-08.
- Project-scoped authorization context moves to AUTH-10.
- Feature loaders, grant matrices, concealment, and revoke races remain with
  their owning cutovers.
- Verification uses `WORKSTREAM_TEST_DATABASE_URL`, the isolated-test runner,
  branch coverage at or above 90 percent for materially changed subsystems, and
  the unchanged repository-wide 78 percent CI floor.

## Re-review gate

Fresh architecture, security/auth, and QA/CI plan review must pass the repaired
AUTH-07A contract before runtime implementation. Prior failed/conditional
results are not implementation approval.
