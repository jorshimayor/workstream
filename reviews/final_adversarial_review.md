# Final Adversarial Review

Reviewer role: Adversarial Quality Reviewer.

Scope: markdown planning package and metadata-level process baseline.

## Findings

### High: Fake evidence remains the hardest v0.1 risk

Finding:

The docs now require evidence, hashes, preflight records, and immutable submission versions. That reduces risk, but fake or irrelevant evidence can still pass structural checks.

Suggested change:

During pilot, second-review accepted submissions and compare evidence against the actual deliverable. Add project-specific evidence checkers as soon as repeat patterns appear.

Status: mitigation documented; implementation remains P0/P1 depending on checker complexity.

### High: Bad reviewers can still harm the system

Finding:

Reviewer independence, second-review sampling, reviewer reputation, and overturned decision tracking are documented. These need to be implemented early because review quality is a core product promise.

Suggested change:

Build reviewer metrics and second-review sampling in week 3, not after the pilot.

Status: documented in `operations/reviewer_workflow.md` and `roadmap/day_by_day_execution_plan.md`.

### Medium: Low-quality generated artifacts need project-specific bans

Finding:

Generic low-quality artifact patterns cannot be fully handled by one global checker. Each project guide must define suspicious artifacts and common generated-scaffold failure modes.

Suggested change:

Add banned/generated artifact patterns in every project guide and feed repeated misses into `check_low_quality_generated_artifacts`.

Status: documented in `architecture/checker_framework.md`, `templates/project_guide_template.md`, and `docs/risk_register.md`.

### Medium: Lessons learned must not become another passive document

Finding:

The docs now require action owners and target updates. This should be enforced in weekly project review.

Suggested change:

Treat unresolved lessons older than one week as project operations debt.

Status: documented; enforcement should be implemented in dashboards later.
