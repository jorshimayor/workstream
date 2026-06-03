# Product Brief

## Product Name

Workstream

## One-Sentence Description

Workstream is Flow's task evaluation and contribution infrastructure. It helps teams run project-specific task queues through automated checks, reviewer routing, evaluation sprints, human review, revision, contribution records, payment tracking, and reputation.

## Problem

High-quality task work fails for operational reasons more often than technical reasons:

- rules are scattered across chats, markdown, and reviewer memory
- submissions reach reviewers before basic checks pass
- revision feedback is not replayed carefully
- payout status is tracked manually and inconsistently
- reviewers disagree because the project guide is not encoded into the workflow
- operators cannot see the true state of the pipeline

This creates wasted effort, delayed payments, repeated mistakes, and low trust.

## Insight

Across serious task projects, the surface language changes but the lifecycle is stable:

```text
Guide -> Task -> Submission -> Checker -> Review -> Revision -> Acceptance -> Payment
```

Workstream makes that lifecycle explicit and configurable.

The system is source-agnostic without becoming source-adapter-first. A task created manually, imported from markdown, imported from CSV, or later received from an external origin normalizes into the same Workstream task contract.

## Target Users

### Primary User: Operator

The person who creates tasks, packages work, submits evidence, monitors status, and resolves revisions.

Needs:

- know what to do next
- avoid missing project rules
- package submissions correctly
- track accepted, pending, paid, rejected, and needs-revision work

### Secondary User: Reviewer

The person who checks whether work satisfies the project guide and acceptance criteria.

Needs:

- see only review-ready submissions
- apply a consistent checklist
- issue actionable revision feedback
- avoid reviewing broken packages

### Admin

The person configuring projects, rules, checkers, payments, and roles.

Needs:

- create project templates
- configure statuses and checkers
- audit review decisions
- track throughput and payout exposure

## MVP Boundary

The first version includes:

- project guide records
- task queue
- task detail
- task contract screening
- submission packet records
- checker framework
- human review workflow
- revision replay
- contribution records
- payment ledger
- reputation basics
- status dashboard

## First Operator Value

The first version must make a small operator team better immediately:

- fewer missed project rules before submission
- fewer avoidable needs-revision cycles
- faster review readiness because broken packets are blocked early
- clearer reviewer feedback because findings are structured
- cleaner payout tracking because accepted and paid are separate states
- less dependency on scattered chat memory

If the product does not reduce repeat mistakes and status confusion in the first pilot, it is not yet working.

## v0.1 Task Intake

The only v0.1 intake paths are:

- manual task creation in the app
- import from a controlled markdown or CSV template

External source adapters, origin onboarding, webhook drop notifications, automated routing, owner-agent execution workspace, and on-chain settlement are later work. This keeps the first 30 days focused on proving the lifecycle, not integrating every source.

The first version excludes:

- built-in AI workspace
- on-chain settlement
- public marketplace
- external client portal
- fully autonomous task routing
- agent identity protocols
- complex dispute arbitration

## Product Promise

Workstream helps Flow measure, certify, and coordinate useful human-agent work by turning project rules into a repeatable evaluation and contribution system.

## First Market Wedge

Start with internal and partner-operated task programs where the team already understands the review loop:

- AI task creation
- technical review
- rubric/evaluation writing
- code/test quality review
- data QA

Avoid broad gig marketplace positioning until the quality engine is proven.

## Success Metrics

By day 30:

- 3 project templates configured
- 20 tasks entered
- 10 submissions created
- 5 accepted or rejected by review
- 3 needs-revision loops completed
- 100 percent of submissions have checker results
- 100 percent of accepted tasks have evidence, contribution record, and payment record
- status dashboard reconciles with manual records
