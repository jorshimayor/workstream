# Chunk Contract: WS-CON-001-05A - PaymentPolicy Semantic Consumer Cutover And Task Freeze

## Parent initiative

`WS-CON-001` - Contribution Record And Compensation Boundary

## Goal

Atomically remove PaymentPolicy from every runtime/API semantic consumer,
classify existing rows, and freeze the active published compensation version on
every successful new TaskAssignment. Physical schema removal belongs to 05B.

## Why this chunk exists

Submitter compensation must be known before work begins and must not drift when
the project changes policy later.

## Approved plan reference

- `../INTENT.md`
- `../PLAN.md`
- `../CHUNK_MAP.md`

## Risk class

L1 payment/task lifecycle/authorization; SLA P1.

## Allowed files

```text
backend/app/modules/compensation/ports.py
backend/app/modules/compensation/service.py
backend/app/modules/projects/{schemas,repository,service}.py only PaymentPolicy consumer removal
backend/app/modules/tasks/models.py
backend/app/modules/tasks/schemas.py only PaymentPolicy consumer removal/frozen-version API semantics
backend/app/modules/tasks/repository.py only exact cutover locking/classification
backend/app/modules/tasks/service.py only task-owned participant integration
backend/app/modules/checkers/{schemas,repository,service,runner}.py only PaymentPolicy consumer removal
backend/alembic/versions/<next>_task_assignment_compensation_freeze.py
backend/app/db/models.py
backend/tests/test_compensation.py
backend/tests/test_projects.py
backend/tests/test_tasks.py
backend/tests/test_checkers.py
backend/tests/test_authorization.py only action/transaction proof
backend/tests/test_alembic.py
backend/tests/test_api_contract_e2e.py
docs/spec_contribution_compensation.md
docs/architecture_data_model.md only removed/canonical authority reconciliation
docs/operations_payment_reputation.md only setup/cutover operations
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-05A.json
```

## Not allowed

```text
task claim permission/grant/kernel implementation
ReviewLease or Review behavior
contribution/award creation
public compensation routes
PaymentPolicy physical table/model/column removal, fallback, automatic conversion, or historical row rewrite
provider/artifact calls
review behavior or unrelated checker behavior
```

## Acceptance criteria

- [ ] TaskAssignment has non-null immutable
  `submitter_compensation_policy_version_id` for all new claims.
- [ ] Merged REV-02 has established exact non-null
  `Submission.task_assignment_id` lineage and its accepted task-owned creation
  contract; 05A preserves that lineage and introduces no parallel submission
  ownership field.
- [ ] No runtime service, API schema/OpenAPI path, setup gate, task claim,
  checker, review, or award consumer treats PaymentPolicy as current business
  or economic authority; Finance publication is the only authority. CON-01 owns
  the active specification inventory and REV-13 owns final joint release docs.
- [ ] A zero-consumer scanner proves the remaining PaymentPolicy model/table is
  unreachable compatibility residue pending 05B, not an executable fallback.
- [ ] Existing task-claim ActionId/authority is allowed and revalidated before
  assignment/freeze commit; WS-CON introduces no local role checks.
- [ ] Claim follows the PLAN lock order, locks every referenced binding by UUID,
  revalidates task-claim authority after relevant locks, and copies one
  published same-project version whose bindings are active.
- [ ] Missing/suspended/invalid policy fails with stable compensation error and
  creates no assignment/task/audit/outbox partial state.
- [ ] Concurrent publish vs claim freezes one committed old or new version,
  never a mixture and without deadlock in either permutation.
- [ ] Binding suspend/retire versus claim is proved in both permutations: new
  work never freezes an inactive binding while already-frozen work is retained.
- [ ] Later policy change never updates the assignment.
- [ ] Legacy rows follow the approved migration classification and cannot enter
  new Review decisions without a valid frozen ref.
- [ ] Deployment either drains all pre-cutover active assignments or executes
  the explicitly approved deterministic rebuild; migration fails on ambiguity.
  There is no intermediate deployment that changes economic meaning while
  allowing unfrozen claims.
- [ ] Downgrade requires task claims and review intake disabled and refuses when
  post-cutover assignments exist; rollback never silently drops a frozen ref.
- [ ] Changed subsystems remain >=90 percent; global floor remains >=78 percent.

## Verification commands

Execute the exact CON-05A expansion in `../RUNTIME_VERIFICATION.md`; same-run
changed compensation code is at least 90 percent and repository coverage at
least 78 percent.

## Required reviewers

Baseline plus architecture, security/auth, product/ops, docs, reuse/dedup, and
test-delta.

## Human review focus

Atomic semantic-consumer/claim cutover, exact freeze timing, auth/lock order,
policy/binding races, legacy drain/rebuild, rollback, and no PaymentPolicy
fallback.

## Stop conditions

Stop if merged REV-02 does not expose its exact reviewed
`Submission.task_assignment_id` lineage, AUTH task-claim cutover is incomplete,
TaskService cannot accept the participant within the listed files, or the lock
order conflicts with merged REV/ART/AUTH. Any future composition path requires
contract amendment and a new internal review before implementation.
