# Discovery: WS-CON-001 Contribution Record And Compensation Boundary

## Baseline inspected

- trusted `origin/main` at `5d353b6`, merged PR #139;
- complete WS-XINT intent, decisions, plan, REV/CON, AUTH/role-service,
  AUTH/REV, AUTH/ART, and ART/REV handoffs;
- current WS-CON initiative package and archival reference inputs;
- canonical README, glossary, architecture lockdown/data model/lifecycle,
  authorization spec, artifact spec, roles/operations docs, and ADRs 0012-0015;
- current backend project/task/submission/checker, AUTH, audit, artifact, and
  migration code/tests;
- human-approved 2026-07-17 FinalAcceptance/no-adjudication direction and the
  current sibling REV planning head `69fb231` as discovery-only context;
- stale wording, authorization, artifact, link, loop-memory, and agent-gate
  scanners/tests.

## Current runtime observations

- The backend stops before the human Review/ContributionRecord implementation.
- Project code still has the retired guide-bound economic schema. There is no
  canonical ContributionPolicy aggregate, ContributionRecord,
  CompensationAward, fulfillment receipt, or status projection runtime.
- Existing Submission rows carry `version` and supersession lineage. A separate
  SubmissionVersion model would duplicate current identity. The handoff field
  named `submission_version_id` therefore maps to canonical `Submission.id` and
  is stored as `submission_id`.
- No FinalAcceptance runtime or reviewed merged REV contract exists yet. The
  current sibling REV plan creates Review/task effects directly and must be
  reconciled and merged before CON consumes the new fact.
- The merged AUTH catalogue has 74 PermissionIds and 57 ActionIds. Nine
  self/admin actions are active and 48 are planned. No WS-CON ActionId is
  registered.
- Current AUTH supports actor-self and AdminRoleGrant evaluation. Independent
  ProjectRoleGrant runtime, fixed-service runtime admission, CON evaluators,
  and the cross-domain prepared mutation protocol remain future AUTH work.
- AUTH's static service-action matrix is typed code; it is not a database grant
  table. AUTH-09E is the required runtime admission path.
- PR #129 added inactive ART preparation/source values only. It added no
  contribution-evidence capability, ART admission/provider execution, binding,
  action, permission, or CON dependency.
- No shared transactional outbox exists with the required generic dispatcher,
  claim fencing, replay, and typed handler outcome contract.

## Canonical merged changes affecting CON

1. `ContributionPolicy`, `ContributionPolicyVersion`, `ContributionRule`, and
   `ContributionAwardDefinition` decide award eligibility. CompensationAward
   is the evaluated downstream result.
2. Every valid Review creates reviewer `completed_review`. REV creates exactly
   one FinalAcceptance for `accept`; submitter `accepted_submission` consumes
   FinalAcceptance rather than inferring acceptance from Review.decision.
3. Core contribution creation is a flush-only CON participant in the REV-owned
   transaction. It performs no ART call or evidence projection.
4. CON copies the stabilized versioned Submission/packet digest supplied by REV
   into `ContributionRecord.artifact_hash`; it does not verify or rederive it.
5. The current shipping path consumes exact submitter and reviewer grants only.
   The separate global AUTH role catalogue is not expanded here; no adjudication
   behavior or readiness dependency enters WS-CON.
6. ActionOwner is AUTH activation custody. ART and REV transfers must be
   complete across their full current catalogues; WS-CON cannot prescribe
   partial subsets.
7. Fixed services use provisioned ActorProfile/ActorIdentityLink, immutable
   ServiceIdentity, exact static ActionId row, and AUTH-09E admission.
8. The shared outbox dispatcher cannot inherit protected feature-handler
   authority. Delivery, reconciliation, rebuild, and callback boundaries need
   exact approved service contracts.
9. REV owns FinalAcceptance persistence, Review/task effects, shared audit/
   outbox staging, and the single commit. CON validates the locked acceptance
   fact, flushes contributions/awards, returns a typed result, and never commits.

## Relevant files and symbols

| Source | Observation |
|---|---|
| `docs/architecture_data_model.md` | Canonical policy/rule/definition, binding, contribution, award, receipt, and projection names/fields |
| `docs/decision_0015_project_contributor_roles_are_independent.md` | Exact project role values and independent revocation |
| `docs/spec_authorization_service.md` | Stable permissions, current actions, ActionOwner semantics, static service matrix, AUTH-09E order |
| `WS-XINT-001/REV_CON_HANDOFF.md` | Exact core participant sequence and optional-evidence boundary |
| `WS-XINT-001/AUTH_ROLE_SERVICE_HANDOFF.md` | Fixed service and project grant contract |
| `WS-XINT-001/AUTH_REV_HANDOFF.md` | Full review activation-custody/hidden behavior sequence |
| `WS-XINT-001/AUTH_ART_HANDOFF.md` | Full 25-action ART transfer; not a core CON gate |
| `backend/app/modules/projects/{models,schemas,repository,service}.py` | Current guide-bound economic fields and consumers to cut over/remove |
| `backend/app/modules/tasks/**` | TaskAssignment creation and future submitter policy freeze seam |
| `backend/app/modules/tasks/models.py::Submission` | Existing immutable version identity: `id`, integer `version`, and `supersedes_submission_id`; no SubmissionVersion table |
| `backend/app/modules/authorization/{catalogue,policy,kernel,schemas}.py` | Current 74/57/9/48 runtime and stable PermissionIds |
| `backend/app/modules/audit/**` | Shared append-only audit extension point |
| `backend/app/modules/artifacts/{preparation,sources}.py` | Inactive ART-only preparation; no core CON import |

## Existing tests and gaps

- Project/task tests cover current setup/claim/submission behavior but not
  ContributionPolicy freezes or retirement of the legacy economic schema.
- AUTH tests cover catalogue parity, planned denial, actor-self/admin grants,
  decision digest, scope evidence, and route commit/rollback. They do not cover
  CON contexts, independent project grants at CON call sites, AUTH-09E CON
  identities, or prepared cross-domain mutations.
- ART tests prove preparation only. No optional evidence projection capability
  exists or is needed for core contribution tests.
- No tests yet cover ContributionRecord cardinality, frozen rule evaluation,
  money/points award uniqueness, fulfillment callback, delivery replay,
  shared-outbox handler isolation, or REV/CON atomic rollback.
- No tests yet cover FinalAcceptance one-per-task/Review/Submission constraints,
  accept-only creation, source-lineage exclusivity, or rollback when CON fails.

## Dependencies

- AUTH: reviewed registration and later activation chunks, independent project
  grants, prepared mutation protocol, fixed service admission, exact CON
  service identities/static rows, and action-specific evaluators.
- REV: ReviewLease reviewer policy FK; canonical claim/decision composition;
  REV-owned FinalAcceptance with exact policy-context typing; stabilized
  artifact-hash facts; mandatory CON participant injection; REV-staged shared
  audit/outbox; single route commit; and no no-op fallback.
- Task/Submission: submitter policy freeze and stable assignment/version lineage.
- Shared outbox/audit: caller-transaction append and feature-neutral dispatch.
- ADR 0014 adapters: typed capability port, factory, and composition-root
  registration for external fulfillment.
- ART: no core dependency; optional projection only after separate approval.

## Risks

| Risk | Mitigation |
|---|---|
| Two award-eligibility models | Clean semantic then physical cutover; no fallback |
| Contribution missing after Review | Mandatory flush-only participant and one caller commit |
| Submitter contribution inferred from Review decision | REV-owned immutable FinalAcceptance is the only submitter source; exact one-to-one constraints and lineage checks |
| ART outage suppresses contribution | No core ART/evidence operation |
| Wrong policy version | Assignment/lease freeze before work; immutable published versions |
| Cross-domain deadlock | AUTH-first lock order and two-order PostgreSQL tests |
| Dispatcher gains feature authority | Exact dispatcher-only action plus independent handler authorization |
| Dynamic/broad service access | Closed ServiceIdentity/static rows, AUTH-09E, cross-service denial |
| Role coupling | Independent grants and role-specific invalidation consumers |
| Partial activation transfer | Consume complete WS-XINT AUTH handoffs, never local subsets |
| Legacy row ambiguity | Human-approved deterministic rebuild/classification before migration |
| Premature public surface | Hidden behavior until AUTH activation and joint release proof |
| Adjudication leaks into v0.1 | No adjudication type/action/state/queue/readiness dependency; reject and accept remain terminal |

## Resolved FinalAcceptance policy lineage

The handoff's UUID `policy_context_ref` maps to canonical immutable
`ReviewPolicy.id`, stored as `review_policy_id`. REV must enforce that exact
locked policy and its same project/task/Submission/Review lineage. CON does not
interpret it as contribution policy or use it for award eligibility.

## Open questions

- Exact D11 AdminRole candidates for award detail, delivery recovery, and audit.
- Exact ServiceIdentity/ActionId/static-row contracts for delivery,
  reconciliation, projection rebuild, and callback execution.
- Deterministic treatment of pre-production legacy rows.
- Whether optional evidence projection is ever approved; it is not part of the
  current core plan.

## Conventions to preserve

- Review decisions are only `accept`, `needs_revision`, and `reject`.
- PostgreSQL owns canonical contribution/award/receipt truth.
- External I/O occurs only after commit and outside lifecycle/database locks.
- Domain participants flush and never commit.
- AUTH and feature repositories never cross-import.
- Fixed service identity is authorization; Celery executor/generation is
  separate execution fencing.
- `/api/v1` is the only public prefix.
