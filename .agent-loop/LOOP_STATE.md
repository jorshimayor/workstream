# Loop State

## Current State

- This authored file is reviewed planning/history context, not canonical live
  post-merge state. Canonical state is the signed schema-v2 output on
  `automation/loop-memory`.
- Active initiatives include parallel `WS-AUTH-001` and `WS-ART-001`.
- PR #132 merged `WS-AUTH-001-09A` into `main` as `299363a` on
  2026-07-17; signed schema-v2 memory recorded the stopped checkpoint.
- Active implementation chunk: `WS-AUTH-001-09B` on
  `codex/ws-auth-001-09b-controlled-service-provisioning` after explicit user
  start.
- AUTH-09B is bounded to one controlled service-actor provisioning route and
  activates only `actor.service.provision`. AUTH-09C remains inactive.
- Start basis: trusted `main` at `299363a` after PR #132, integrated through
  `a947b86` after PR #142 before publication.
- PR #119 merged `WS-AUTH-001-05B` as `ad71c7e`.
- PR #120 merged `WS-ART-001-OBJECT-STORAGE-AMENDMENT` as `4408256`.
- PR #122 merged the first automated post-merge memory implementation as
  `fc89fb6`; its schema-v1 cross-initiative next pointer is superseded by the
  schema-v2 initiative-local clean cut.
- Current gate: AUTH-09B implementation, deterministic evidence, and all
  required internal reviewer tracks pass at integrated code SHA `641b439`.
  Lifecycle evidence and PR publication remain; no service caller becomes
  executable before AUTH-09E.
- Scope checkpoint: AWS S3 is the only v0.1 production provider; MinIO is
  local/CI S3 protocol proof; LocalStorage is focused development/test; R2 and
  Flow Node are deferred. Product modules receive narrow artifact capabilities,
  and AWS cannot instantiate in production without release-bound live proof.
- Authorization checkpoint: merged main contains 74 PermissionIds and 65
  ActionIds, with the two actor-self and seven AUTH-08 administrative actions
  active. AUTH-09A defines seven fixed artifact service identities and eleven
  exact planned static matrix memberships. The
  plan now requires availability-neutral ART/REV custody transfer, fixed-service
  admission, prepared mutation authority, feature-owned hidden behavior, and
  exact AUTH-only activation chunks. This planning amendment activates nothing.
- Parallel artifact checkpoint: `WS-ART-001-02A1` was explicitly started and
  merged through PR #127 as `f64a8e5`; it is at the post-merge memory/stop
  checkpoint. ART-02A2 merged through PR #129, and ART-02A3 is reviewed in its
  isolated parallel worktree but has no open PR at this checkpoint.
- Authorization checkpoint: AUTH-07B, AUTH-08, and AUTH-09A merged through PRs
  #130, #131, and #132. Signed memory stopped after 09A, and the user explicitly
  started 09B.
- Parallel coverage work: `WS-QUAL-001-01B2` remains paused. Its last official
  whole-app result is `6466/8159` statements (`79.249908%`); no replacement
  evidence exists.
- Parallel initiative: `WS-POL-002-03` merged through PR #90 as `a7aa474`; its
  post-merge memory merged through PR #94 as `b1270d7`. `WS-POL-002-04` remains
  inactive pending the relevant authorization proof and a separate explicit
  start.

## Operating Rule

Workstream engineering chunks move through:

```text
Intent -> Discovery -> Plan -> Chunk Map -> Chunk Contract -> Implementation -> Evidence -> Internal Review -> PR -> Human Checkpoint -> Automated Merge Memory -> Stop
```

The merged `WS-POL-001-03` chunk moved task readiness and submission creation
onto the locked project guide-source snapshot, effective project submission
artifact policy, and compiled project `PreSubmitCheckerPolicy` bundle. It did
not implement frontend behavior, payment, reputation, settlement, blockchain
integrations, post-submit policy splitting, or revision resubmission drill
behavior.

The merged `WS-POL-001-08` chunk corrected the project setup orchestration path:
normal guide/source capture starts the pre-submit setup pipeline automatically
through Celery. It did not redesign post-submit policy, review, revision,
payment, reputation, blockchain integrations, frontend behavior, or task
submission runtime.

The merged `WS-POL-001-09` chunk was a corrective hardening chunk for the
project setup runtime boundary. It removed the production fixture adapter and
did not change task, checker, post-submit, review, revision, payment,
reputation, blockchain, frontend, or object-storage behavior.

The merged `WS-POL-001-10` chunk was a corrective hardening chunk for the
pre-submit live API drill. It fixed guide-version conflict mapping,
guide-create source snapshot capture, active-guide checker summary visibility,
contributor self-profile onboarding, and failed pre-submit audit evidence. It did
not change post-submit policy, review, revision, payment, reputation,
blockchain, frontend, or agent-runtime behavior.

## Last Review State

- Last completed initiative: `WS-ENG-001` Codex zero-trust engineering loop bootstrap.
- PR #23 merged into `main` on 2026-06-20.
- PR #24 updated post-merge loop memory on `main`.
- PR #25 added Terminal Benchmark example material under `examples/`.
- PR #26 approved and merged WS-POL-001 planning into `main` on 2026-06-27.
- PR #27 updated WS-POL post-merge memory on `main`.
- PR #28 implemented `WS-POL-001-01` and was merged into `main`.
- PR #61 implemented `WS-POL-001-02` and was merged into `main`.
- PR #63 implemented `WS-POL-001-03` from `codex/ws-pol-001-03-task-locked-context` and was merged into `main` on 2026-07-03.
- Internal review evidence for `WS-POL-001-03` is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-internal-review-evidence.md`.
- PR trust bundle for `WS-POL-001-03` is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-pr-trust-bundle.md`.
- External review response for `WS-POL-001-03` is tracked separately at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-03-external-review-response.md`.
- `WS-POL-001-04` started on branch `codex/ws-pol-001-04-post-submit-policy` after the user's explicit start signal.
- `WS-POL-001-04` internal reviewer fanout completed with no open sub-agent sessions.
- `WS-POL-001-04` internal review evidence is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-04-internal-review-evidence.md`.
- `WS-POL-001-04` PR trust bundle is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-04-pr-trust-bundle.md`.
- `WS-POL-001-04` external review response is tracked separately at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-04-external-review-response.md`.
- `WS-POL-001-04` merged to `main` before `WS-POL-001-05` started.
- `WS-POL-001-05` started on branch `codex/ws-pol-001-05-revision-resubmission` after the user's explicit start signal.
- `WS-POL-001-05` reviewed implementation SHA: `5019afc57e7c6f5f7488f26a05b11c65a33e9f18`.
- `WS-POL-001-05` internal review evidence is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-05-internal-review-evidence.md`.
- `WS-POL-001-05` PR trust bundle is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-05-pr-trust-bundle.md`.
- `WS-POL-001-05` external review response is tracked separately at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-05-external-review-response.md`.
- PR #66 merged into `main` as `b20988ba79626e1edbc03953aba60f54f2fc94ab`.
- `WS-POL-001-06` started on branch `codex/ws-pol-001-06-terminal-benchmark-drill`
  after the user's explicit start signal.
- `WS-POL-001-06` real Terminal Benchmark manual HTTP drill passed against a
  local Terminal Benchmark reference fixture; committed evidence uses placeholder fixture
  paths and local IDs only.
- `WS-POL-001-06` live drill exposed and fixed an OpenAI Agents SDK adapter
  strict-schema issue for the policy derivation result's open `policy_body`.
- `WS-POL-001-06` follow-up cleanup removed stale project-owned payment fields
  and removed construction-state guide checklist fields, preserved server-written activation
  provenance on reads, added fail-closed migration behavior for old
  guide-source snapshots, and aligned then-active docs around a payment-term
  model later superseded by `ContributionPolicyVersion` as the sole award-policy
  authority.
- `WS-POL-001-06` internal review evidence is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-06-internal-review-evidence.md`.
- `WS-POL-001-06` PR trust bundle is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-06-pr-trust-bundle.md`.
- PR #67 merged into `main` as `3cce92c`.
- `WS-POL-001-07` started on branch `codex/ws-pol-001-07-task-contract-cleanup`
  after the user's explicit start signal.
- PR #68 merged into `main` as `3dc6a95`.
- `WS-POL-001-08` started on branch `codex/ws-pol-001-08-celery-project-setup`
  after the user's explicit correction that project setup must run
  automatically from guide/source capture through Celery.
- `WS-POL-001-08` internal review evidence is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-08-internal-review-evidence.md`.
- `WS-POL-001-08` external review response is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-08-external-review-response.md`.
- `WS-POL-001-08` PR trust bundle is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-08-pr-trust-bundle.md`.
- PR #69 merged into `main` as `aea7024`.
- `WS-POL-001-09` started on branch `codex/ws-pol-001-09-openai-agent-sdk-only`
  after the user's explicit correction to remove the production fixture runtime.
- `WS-POL-001-09` internal review evidence is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-09-internal-review-evidence.md`.
- `WS-POL-001-09` external review response is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-09-external-review-response.md`.
- `WS-POL-001-09` PR trust bundle is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-09-pr-trust-bundle.md`.
- PR #71 merged into `main` as `8a524de`.
- `WS-POL-001-10` started after the user's explicit start signal for the first
  five pre-submit hardening fixes from the live API drill.
- PR #72 merged into `main` as `1bbde47`.
- `WS-POL-001-11` merged through PR #74 as `5cec0e0`; it added local
  Workstream actor identity and actor profile registries for verified Flow
  actors before the next Terminal Benchmark live API drill.
- `WS-POL-001-11` internal review evidence is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-11-internal-review-evidence.md`.
- `WS-POL-001-11` PR trust bundle is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-11-pr-trust-bundle.md`.
- PR #76 merged into `main` as `46e74de`; it implemented `WS-POL-001-12`
  project setup-run and policy visibility APIs.
- `WS-POL-001-13` started on branch `codex/ws-pol-001-13-task-context-apis`
  after the user's explicit start signal.
- PR #77 merged into `main` as `b567bac`; it implemented `WS-POL-001-13`
  task work-context, submission-requirements, and operator-only locked-context APIs.
- `WS-POL-001-13` internal review evidence is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-13-internal-review-evidence.md`.
- `WS-POL-001-13` external review response is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-13-external-review-response.md`.
- `WS-POL-001-13` PR trust bundle is tracked at `.agent-loop/initiatives/WS-POL-001-submission-artifact-policy-foundation/reviews/WS-POL-001-13-pr-trust-bundle.md`.
- PR #79 merged into `main` as `53a57c3`; it implemented `WS-POL-001-14`
  submission finalization and HTTP-visible Terminal Benchmark proof semantics.
- PR #84 merged into `main` as `a3d2a3f`; it implemented `WS-POL-001-16`
  Terminal Benchmark live API drill evidence, privacy scrub, and a professional
  PDF report proving the current lifecycle through HTTP-visible APIs.
- PR #85 merged into `main` as `3fc1a68`; it completed `WS-POL-002-PLAN`
  planning for project-guide-derived post-submit checker setup.
- PR #87 merged into `main` as `ed52c21`; it implemented `WS-POL-002-01`
  Post-Submit Compiler Contract with version-stamped default-checker snapshots,
  canonical policy hashing, compiler-boundary validation, and default-drift
  regression tests.
- PR #90 merged into `main` as `a7aa474` on 2026-07-11; it implemented
  `WS-POL-002-03` server-owned post-submit checker policy approval, correction,
  immutable correction history, and bounded setup visibility APIs.
