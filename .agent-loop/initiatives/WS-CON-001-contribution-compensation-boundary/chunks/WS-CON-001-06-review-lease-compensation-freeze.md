# Chunk Contract: WS-CON-001-06 - ReviewLease Compensation Freeze Participant

## Parent initiative

`WS-CON-001` - Contribution Record And Compensation Boundary

## Goal

Deliver and independently prove the narrow WS-CON compensation lookup/freeze
participant that REV-06 will invoke with canonical caller-supplied project and
binding facts inside the review-claim transaction.

## Why this chunk exists

Reviewer compensation must be fixed before review work begins and cannot depend
on the later decision outcome or current policy at decision time.

## Approved plan reference

- `../INTENT.md`
- `../PLAN.md`
- `../CHUNK_MAP.md`

## Risk class

L1 payment/review lifecycle/authorization; SLA P1.

## Allowed files

```text
backend/app/modules/compensation/ports.py
backend/app/modules/compensation/service.py
backend/tests/test_compensation.py
backend/tests/test_authorization.py only action/transaction proof
docs/spec_contribution_compensation.md
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
.agent-loop/merge-intents/WS-CON-001-06.json
```

## Not allowed

```text
review claim/queue/lease policy invention
review models, migrations, services, routes, or composition
AUTH catalogue/grants/kernel changes
review decision or contribution/award creation
task assignment freeze changes
provider/artifact/adapter calls
```

## Acceptance criteria

- [ ] Port accepts caller AsyncSession plus canonical project/claim facts,
  follows PLAN lock order, locks referenced bindings by UUID, returns one
  published same-project version, flushes nothing outside its ownership, and
  never commits.
- [ ] Missing/inactive/invalid policy or binding returns stable typed failure
  with no WS-CON/audit/outbox partial state.
- [ ] Contract explicitly requires REV-03's immutable non-null ReviewLease FK
  and REV-06's `review.claim` revalidation, injection, lease write, audit/outbox,
  release/expiry behavior, and integrated tests; CON-06 implements none of them.
- [ ] Policy publish vs claim concurrency freezes one committed version and
  passes both lock permutations without deadlock.
- [ ] Binding suspend/retire versus lookup is covered in both permutations.
- [ ] Reviewer award behavior is not implemented here.
- [ ] Changed modules remain >=90 percent; global floor stays >=78 percent.

## Verification commands

Execute the exact CON-06 expansion in `../RUNTIME_VERIFICATION.md`; the same run
proves changed compensation code at least 90 percent.

## Required reviewers

Baseline plus architecture, security/auth, product/ops, docs, reuse/dedup, and
test-delta.

## Human review focus

Exact lease freeze timing, REV ownership, review.claim authority, no
decision-dependent rate, lock ordering, and no contribution on incomplete lease.

## Stop conditions

Stop if REV-03's exact caller facts/FK contract is not merged or if any review
schema, claim wiring, or composition edit would move into WS-CON. REV-06, not
this chunk, owns integrated claim behavior.
