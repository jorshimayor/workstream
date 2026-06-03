# Systems Architecture Review

Review scope: markdown docs in `/home/abiorh/flow/workstream`.

Reviewer role: Systems Architecture Reviewer.

## Findings

### High: Payment state was mixed into task lifecycle

Task lifecycle initially included `PAID` as a terminal task state. That risks the same reporting confusion seen in task platforms where accepted work and paid work are separate dimensions.

Suggested change: keep task status and payment status separate. Task terminal states should be accepted, rejected, or cancelled, while payment status should move through pending, payout submitted, paid, or disputed.

Status: fixed in `roadmap/30_day_master_plan.md`, `architecture/lifecycle_state_machine.md`, and `operations/payment_reputation.md`.

### High: Roles and permissions needed a first-version matrix

The plan mentioned roles, but did not define who can review, override, or update payment. That creates risk of self-review, unsafe overrides, and payment changes without authority.

Suggested change: add a permission matrix and separation rules.

Status: fixed in `operations/roles_permissions.md`.

### Medium: Guide and policy versioning needed to attach to submissions, checks, reviews, and payments

Tasks recorded guide version, but submissions, checker runs, reviews, and payment records also need policy versions so later guide edits do not make old decisions ambiguous.

Suggested change: add guide and policy version fields to those records.

Status: fixed in `architecture/data_model.md`.

### Medium: Artifact immutability needed to be explicit

The evidence model had hashes but did not clearly say when artifacts become immutable.

Suggested change: artifacts should be hash-locked when checker execution begins; changes require a new submission version.

Status: fixed in `architecture/system_architecture.md` and `architecture/data_model.md`.

### Low: Duplicate older docs exist and should be treated as supporting notes

The repository contains older docs such as `architecture/domain_model.md`, `architecture/state_machine.md`, and `roadmap/30_day_roadmap.md`. The canonical docs now linked from `README.md` are more complete.

Suggested change: either archive older docs later or add a short note marking the canonical set.

Status: noted for later cleanup.

### Low: README had duplicate roles/permissions links

README linked both `docs/roles_permissions.md` and `operations/roles_permissions.md`.

Suggested change: keep the operations document as canonical because it has the permission matrix.

Status: fixed in `README.md`.

## Baseline Scope Update

Baseline scanned at metadata/process level only under `/home/abiorh/snorkel`, covering Sequoia, Geranium, Excalibur, Marlin, and Termius. The scan looked at guide names/headings, queue/status structures, review guards, checker/preflight scripts, review packet/evidence/status patterns, and submission package/provenance structures. No task content or confidential details were copied.

### Medium: Packaged submission provenance should be first-class

Baseline pattern: submission packages commonly carry hashes, provenance metadata, checker logs, validation logs, and status records. Workstream already had artifact hashes, but needed a named readiness/provenance concept that ties a submission packet to the exact checker run that cleared it for review.

Suggested change: add readiness certificate and submission provenance fields.

Status: fixed in `architecture/data_model.md`, `architecture/checker_framework.md`, and `templates/submission_packet_template.md`.

### Medium: Lessons learned should be a data object, not only prose

Baseline pattern: repeated workflow misses become guide updates, review-guard updates, checker updates, or workflow lessons. Workstream mentioned lessons learned, but did not model them as a durable object.

Suggested change: add `ProjectLesson` with status and recommended change.

Status: fixed in `architecture/data_model.md` and `operations/operator_workflow.md`.

### Low: Workstream captures the reusable operating model

Baseline pattern: project guide, queue/status, checker/preflight, review guard, review packet, evidence, status ledger, needs-revision replay, accepted/rejected/payment tracking.

Assessment: Workstream captures this reusable model through the canonical docs linked in `README.md`. Remaining duplicate older docs should be cleaned later, but they do not block the planning package.
