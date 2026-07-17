# Chunk Contract: WS-CON-001-05A - Legacy Economic Terms Cutover And Task Freeze

## Goal

Remove the retired guide-bound economic contract from every semantic consumer,
classify existing rows, and freeze the active published
ContributionPolicyVersion on each successful new TaskAssignment. Physical dead-
schema removal belongs to 05B.

## Risk

L1 economic/task lifecycle/authorization; SLA P1.

## Allowed files

```text
backend/app/modules/contributions/{ports,service}.py
backend/app/modules/projects/{schemas,repository,service}.py only legacy consumer removal
backend/app/modules/tasks/{models,schemas,repository,service}.py only cutover/freeze
backend/app/modules/checkers/{schemas,repository,service,runner}.py only legacy consumer removal
backend/alembic/versions/<next>_task_assignment_contribution_policy_freeze.py
backend/app/db/models.py
backend/tests/{test_contributions,test_projects,test_tasks,test_checkers,test_authorization,test_alembic,test_api_contract_e2e}.py
docs/spec_contribution_compensation.md
docs/architecture_data_model.md only exact implemented reconciliation
docs/operations_payment_reputation.md only implemented operations
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-05A.json
```

## Not allowed

```text
task-claim permission/grant/kernel implementation
ReviewLease or Review behavior; contribution/award creation
public policy routes; dead physical schema removal
fallback, alias, automatic conversion, or guessed historical rewrite
provider/artifact calls; unrelated checker behavior
```

## Acceptance criteria

- [ ] Every new TaskAssignment has immutable non-null
  `submitter_contribution_policy_version_id`.
- [ ] Exact merged Submission.task_assignment_id lineage is preserved; no
  parallel submission identity is added.
- [ ] No runtime/API/setup/task/checker/review consumer treats retired guide-
  bound terms as current economic authority. A zero-consumer scanner proves
  remaining physical schema is unreachable until 05B.
- [ ] `task.claim` is registered and active through AUTH with exact same-project
  submitter ProjectRoleGrant, prepared T protocol, actor/link/grant
  revalidation, and canonical task guards. No unrelated project/admin grant
  substitutes and CON contains no role logic.
- [ ] Claim locks active ContributionPolicy, published version, exact rule/
  definition/binding dependencies, evaluates the prepared handle once, and
  copies one same-project published version.
- [ ] Missing/invalid policy fails with no assignment/task/audit/outbox partial
  state. Later publication never updates an assignment.
- [ ] Publish versus claim and binding-state versus claim pass both lock orders
  without deadlock or mixed versions.
- [ ] Existing rows follow the approved deterministic classification and cannot
  enter new Review decisions without a valid freeze. Migration fails on
  ambiguity and downgrade refuses post-cutover data loss.
- [ ] Changed subsystems remain at least 90 percent; global floor remains 78.

## Review and stop

Required tracks: senior, QA, security, product, architecture, docs, reuse, test-
delta, and CI integrity. Stop if exact task/Submission lineage, task.claim
authority, or migration classification is not merged.
