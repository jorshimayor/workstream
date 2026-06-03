# Adversarial Quality Review

Scope: markdown planning package only.

Review stance: try to break Workstream through gaming, weak operations, fake evidence, reviewer abuse, status bypass, payment disputes, bad guides, low-quality generated submissions, confidentiality failures, and checker blind spots.

## Findings

### High: Evidence Can Be Structurally Present But False

Files: `architecture/checker_framework.md`, `architecture/lifecycle_state_machine.md`, `templates/project_guide_template.md`

Finding: The plan required evidence, but did not strongly bind evidence to immutable submission versions. A worker could submit logs from an earlier local run, attach unrelated screenshots, or replace artifacts after checks.

Suggested change: Require artifact hashes, immutable submission versions, checker runs tied to exact hashes, and evidence policies per project. This has been added.

### High: Status Bypass Needs Code-Level Enforcement

Files: `architecture/lifecycle_state_machine.md`, `docs/roles_permissions.md`

Finding: The state model listed blocked transitions, but did not explicitly block direct `SUBMITTED -> ACCEPTED`, checker-version mismatch, or non-destructive override behavior.

Suggested change: Enforce transition guards in code and record guide version, artifact hashes, review id, checker run id, and override id in audit events. This has been added.

### High: Reviewer Collusion And Rubber-Stamping Could Corrupt Quality

Files: `docs/roles_permissions.md`, `operations/reviewer_workflow.md`, `docs/risk_register.md`

Finding: Reviewer reputation existed, but collusion signals were underspecified. A reviewer could repeatedly accept the same worker's weak submissions with short comments.

Suggested change: Flag repeated worker-reviewer pairs, fast accepts with no evidence, overturned accepts, and require second review for high-value, disputed, or override-backed tasks. This has been added to role and risk docs; implementation backlog should include the metrics.

### High: Bad Project Guides Can Poison The Whole Workflow

Files: `templates/project_guide_template.md`, `docs/risk_register.md`

Finding: Project guides are first-class, but the template did not require version approval, effective dates, unacceptable-work definitions, evidence policy, or known checker blind spots.

Suggested change: Add guide versioning, approver, unacceptable-work criteria, evidence policy, mandatory second-review triggers, and payment dispute policy. This has been added.

### High: Payment Disputes Need Explicit Holds And Adjustment Records

Files: `operations/payment_reputation.md`, `templates/project_guide_template.md`, `docs/risk_register.md`

Finding: Payment states existed, but dispute opening, amount adjustment, and payment holds were not explicit enough.

Suggested change: Project guides must define dispute rules; accepted amount changes require adjustment records; disputed payments must not silently become paid. The template and risk register now call this out. Payment implementation should add adjustment records.

### Medium: Low-Quality LLM-Generated Artifacts Can Pass Formatting Checks

Files: `architecture/checker_framework.md`, `templates/project_guide_template.md`, `docs/risk_register.md`

Finding: A generic generated submission can satisfy markdown structure while being hollow. This includes fabricated helper files, generic "model_for_test" style artifacts, placeholder reports, or evidence that only looks official.

Suggested change: Each project guide should define banned generated patterns and a checker should flag repeated boilerplate and placeholder artifacts. This has been added as `check_low_quality_generated_artifacts`.

### Medium: Confidentiality Depends Too Much On Worker Honesty

Files: `architecture/checker_framework.md`, `docs/risk_register.md`, `templates/project_guide_template.md`

Finding: Worker attestation is necessary but not sufficient. Confidential or copied data can leak through packages, screenshots, logs, and evidence files.

Suggested change: Keep attestation, but pair it with forbidden-file checks, guide-specific allowed-material rules, and reviewer escalation for suspected confidential data. The docs now make this explicit.

### Medium: Checker Blind Spots Need A Feedback Loop

Files: `architecture/checker_framework.md`

Finding: Checkers will initially miss real issues and produce false positives. Without a blind-spot review, the system will rely on memory and repeated manual corrections.

Suggested change: Weekly compare checker output against reviewer findings and convert repeated misses into guide, checker, template, or reviewer-policy updates. This has been added.

## Remaining Implementation Requirements

- Add database fields for submission artifact hashes, checker-run submission version, guide version, and payment adjustment records.
- Add backend transition guards so illegal transitions cannot be performed through the UI or API.
- Add reviewer-pair and fast-accept anomaly metrics.
- Add a project-guide approval workflow before guides can become active.
- Add a dispute flow that holds payment without changing task acceptance.
