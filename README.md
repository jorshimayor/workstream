# Workstream

Workstream is Flow's task evaluation and contribution infrastructure.

It manages project guides, task queues, submission packets, automated checks, reviewer routing, evaluation sprints, revision loops, contribution records, payment status, and reputation signals.

Workstream is how Flow measures, certifies, and coordinates useful human-agent work.

It is not a workspace and it is not blockchain-first. Operators can work with any local tools, human-agent workflow, or external execution environment. Workstream owns the project guide, task queue, submission packet, automated checks, human review, revision loop, acceptance state, payment ledger, and reputation record.

Workstream is source-agnostic, but v0.1 is manual-first. External origin onboarding, source adapters, automated routing, owner-agent execution workspaces, and on-chain settlement remain later adapters until the internal evaluation loop is proven.

The first 30 days are focused on building serious internal infrastructure that can run real projects end to end:

```text
Project Guide
-> Task Queue
-> Task Record
-> Submission Packet
-> Platform Checkers
-> Human Review
-> Needs Revision / Accepted / Rejected
-> Contribution Record
-> Payment Record
-> Reputation Update
-> Lessons Learned
```

## Core Thesis

Different projects speak different domain languages, but serious task evaluation and contribution systems share the same lifecycle:

- every project has a guide
- every task belongs to a project
- every project has a base amount or payout policy
- every task has acceptance criteria
- every submission has evidence
- every submission passes automated checks before human review
- every review creates a decision
- every revision must close prior feedback
- every accepted task updates payment and reputation

Workstream turns that operating knowledge into reusable infrastructure.

## Planning Package

- [30-Day Master Plan](roadmap/30_day_master_plan.md)
- [Roadmap Status](roadmap/status.md)
- [Day-by-Day Execution Plan](roadmap/day_by_day_execution_plan.md)
- [Implementation Backlog](roadmap/implementation_backlog.md)
- [Product Principles](product/product_principles.md)
- [Product Brief](product/product_brief.md)
- [First User Flows](product/first_user_flows.md)
- [System Architecture](architecture/system_architecture.md)
- [Data Model](architecture/data_model.md)
- [Lifecycle State Machine](architecture/lifecycle_state_machine.md)
- [Checker Framework](architecture/checker_framework.md)
- [Operator Workflow](operations/operator_workflow.md)
- [Project Operating Manual](operations/project_operating_manual.md)
- [Queue Policy](operations/queue_policy.md)
- [Workspace And Packet Convention](operations/workspace_packet_convention.md)
- [Reviewer Workflow](operations/reviewer_workflow.md)
- [Revision Replay](operations/revision_replay.md)
- [Roles And Permissions](operations/roles_permissions.md)
- [Payment And Reputation](operations/payment_reputation.md)
- [Risk Register](docs/risk_register.md)
- [Process Pattern Baseline](docs/process_pattern_baseline.md)
- [Architecture Lockdown](docs/architecture_lockdown.md)
- [Glossary](docs/glossary.md)

## Review Passes

- [Process Baseline Operations Review](reviews/process_baseline_operations_review.md)
- [Final Product Strategy Review](reviews/final_product_strategy_review.md)
- [Final Architecture Review](reviews/final_architecture_review.md)
- [Final Adversarial Review](reviews/final_adversarial_review.md)
- [Adversarial Quality Review](reviews/adversarial_quality_review.md)
- [Process Pattern Baseline Review](reviews/process_pattern_baseline_review.md)
- [Review Closure](reviews/review_closure.md)

## Templates

- [Project Guide Template](templates/project_guide_template.md)
- [Checker Policy Template](templates/checker_policy_template.md)
- [Task Template](templates/task_template.md)
- [Preflight Evidence Template](templates/preflight_evidence_template.md)
- [Submission Packet Template](templates/submission_packet_template.md)
- [Review Packet Template](templates/review_packet_template.md)
- [Task Status Template](templates/task_status_template.md)
- [Prior Feedback Checklist Template](templates/prior_feedback_checklist_template.md)

## Decisions

- [ADR 0001: Core Scope](decisions/0001-core-scope.md)
- [ADR 0002: Database Ledger Before Blockchain Settlement](decisions/0002-db-first-not-blockchain-first.md)
- [ADR 0003: Project Guides Are First-Class](decisions/0003-project-guides-are-first-class.md)

## Day-30 Success Standard

By day 30, Workstream runs a real internal task cycle with real people:

```text
Create project guide
Create task
Assign task
Submit packet
Run checks
Review packet
Request revision or accept
Create contribution record
Record payment status separately
Update reputation
Review lessons learned
```

The system is successful only if it prevents weak work from reaching review, preserves evidence, and gives operators a clear path from task intake to accepted paid output.

## Operating Standard

Workstream is built as durable operational infrastructure:

- project rules live in guides and policies, not chat memory
- status is a ledger, not a loose label
- reviews cite evidence and required changes
- revisions replay prior findings one by one
- payments are recorded separately from task acceptance
- every checker result is stored and auditable
- lessons learned become guide updates or new checkers
- submitted artifacts are immutable and hash-bound to checker runs
- accepted work cites evidence before payment exposure is created
- guide versions are locked per task so rules do not drift silently
- accepted work creates an evidence-backed contribution record before payment or reputation updates
- quality gates remain separate: project activation, task screening, and submission quality
