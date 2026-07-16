# Plan: WS-CON-001 Contribution Record And Compensation Boundary

## Proposed approach

Reconcile the supplied candidate into an active repository contract first, then
deliver the backend through small hidden-composition chunks. Land the shared
outbox and compensation policy ownership before Review persistence needs them;
interleave the remaining WS-CON participants with WS-REV at explicit gates;
activate public contribution/compensation APIs only after AUTH, ART, REV, and
outbox dependencies are mandatory and proven.

## Design chosen

### Canonical records

- `ContributionRecord` is immutable and recognizes one exact contributor unit:
  `completed_review` for every valid Review and `accepted_submission` only for
  `accept`.
- Existing `Submission` is the versioned submission identity. Contribution
  fields use `submission_id`, not a new `SubmissionVersion` table.
- `CompensationPolicyVersion` is the sole executable economic authority for new
  assignments/leases. Rules match only contribution type and create at most one
  money plus one project-points award.
- `CompensationAward` is immutable. Adapter delivery/acknowledgement and
  immutable fulfillment receipts are separate; a rebuildable status projection
  supports reads.
- `PaymentPolicy` is removed completely. `CompensationPolicyVersion` is the
  only economic policy in persistence, APIs, task/review freezes, checker
  context and active documentation; no alias or fallback survives.
- Provider payment attempts, balances, payout batches, points ledgers, and
  settlement remain external.

### Authorization dependency

WS-CON never reads grants, roles, or AUTH repositories. Every protected command
or query declares one ActionId and consumes a request-scoped, caller-session-
bound `AuthorizationService`.

Every WS-CON ActionId is currently absent and proposed. Trusted `main`
`9a04434` includes AUTH-08's scoped administrative grants at `aa0fdcd` and
ART-02A2 PR #129, which adds no authority. The closed AUTH catalogue
contains 74 PermissionIds and 57 non-WS-CON ActionIds: nine self/admin actions
are active and 48 actions remain planned. The exact handoff is in
`AUTHORIZATION_HANDOFF.md`. It enumerates each proposed action separately, its
existing or proposed PermissionId, canonical target, candidate principal class,
typed resource facts and guards, transaction protocol, AUTH activation gate,
and feature resource owner.

AUTH-08 now evaluates actor-self and administrative grant families, carries a
complete resource-context digest plus matched grant/scope evidence, and rolls
back a transaction a feature route fails to commit. It still rejects service
subjects and has no ProjectRoleGrant, service-assignment, D10 or WS-CON action
evaluator. WS-AUTH therefore owns not only identifier/owner-enum registration
and typed/PostgreSQL parity, but also action availability, closed evaluator
dispatch, action-specific candidate-role filtering, matched-authority
expansion, remaining grant semantics, service-capable composition, service
ActorProfile/action-assignment construction, and transaction-local authority
revalidation. Every WS-CON route owns its explicit commit; the feature chunk
named in the handoff owns product-row loading, construction of AUTH-approved
typed resource facts, lifecycle guards, and behavioral proof. WS-CON never
edits AUTH-owned files or activates an AUTH action.

Merged AUTH-08 also exposes a closed-role mismatch that must not be hidden in
CON. Finance Authority contains `compensation.delivery.reconcile`, but Operator
does not, while the reconciled candidate matrix proposes both. D11 requires a
human choice before CON-10B. If Operator delivery recovery is retained, a
reviewed AUTH-owned successor adds that existing PermissionId to Operator; if
not, the active WS-CON authority matrix removes the candidate before action
registration. D11 also decides whether Project Manager's broad
`compensation.award.read` candidate carries into WS-CON monetary detail and
which merged audit candidates remain eligible. CON-01 records the chosen sets;
AUTH activation proves them without CON role logic.

D12 separately resolves activation custody. The merged ActionOwner type means
the implementation chunk permitted to activate an action; it cannot name a CON
feature chunk while this plan says AUTH alone flips availability. The handoff
therefore proposes exact AUTH-owned activation owners for all 23 WS-CON actions
and the two coupled review actions, plus all eleven existing ART-02D Operator/
internal actions required by contribution evidence. The ART transfer preserves
every merged ActionId -> PermissionId mapping, including
`operations.artifact_storage_admission.read` -> `operations.status.read`.
Human/AUTH approval of that model—or a global feature-owner semantic plus a
separate closed activation-custody type containing the same mappings—is a
registration gate. In the recommended transfer, AUTH also removes the unused
`REV_08` and `ART_02D` enum members atomically; `REV_06` remains for its other
actions and closed owner-definition parity must still be exact. In the global
alternative those enums remain feature owners and the separate custody type is
closed independently. No action may have two activation authorities.

For mutations crossing AUTH and product rows, AUTH must add the prepared
authorization protocol specified in the handoff. The preliminary target lets
AUTH lock actor/link/grant or service-assignment rows first; the opaque handle is
then evaluated exactly once against facts recomposed from product rows locked by
the feature in canonical order. AUTH stages one decision and never commits.
The final decision retains AUTH-08's resource-context digest and exact matched
grant/project evidence. Hidden domain services flush and never commit; the
actual route/worker/callback transaction owner explicitly commits the complete
decision-plus-business transaction. REV-13 owns the public route proof.
This prevents both product-before-AUTH lock inversion and authorization based on
an unlocked resource snapshot.

Current trusted `main` also lacks an ActionId for upstream `task.claim`, even
though PermissionId `task.claim` exists. AUTH-13 or an approved AUTH-owned
successor must register and activate that action before CON-05A adds the
compensation freeze participant. Review choreography is deliberately staged:
AUTH first registers the planned `review.claim` and `review.decision` contracts;
CON-06/07 then supply their hidden capability/participant; REV-06/08 build the
core claim/decision behavior and REV-10 proves the final contribution
composition and typed resource behavior while the real kernel remains fail-
closed; only then may AUTH integrate the evaluators and activate those actions.
Production execution and public routes remain blocked until the later readiness/
REV-13 gates.

Derived contribution/award writes are mandatory participants of the already
authorized `review.decision` transaction. They are not separately callable
human/service commands and do not invent `contribution.materialize` or
`compensation.award.materialize` permissions. Shared outbox dispatch likewise
belongs to the outbox subsystem, not WS-CON.

### Review composition

`ContributionCompensationDecisionParticipant` accepts the caller's
`AsyncSession`, exact Review/lease/assignment/Submission facts, originating
AuthorizationDecision reference, and canonical request/correlation IDs. It
flushes contributions, awards, projections, audit, and outbox events but never
commits. WS-REV owns the decision and final commit. No optional/no-op production
participant exists.

Policy lookup/freezing uses separate narrow participants:

- task-owned assignment claim calls a WS-CON policy-freeze participant;
- review-owned lease claim calls the same policy lookup contract with a distinct
  lease freeze operation;
- both lock the Project active compensation selector and copy exactly one
  published version ID.

`ReviewLease` schema and review-claim wiring remain wholly WS-REV-owned:
REV-03 adds the immutable policy-version FK/field, CON-06 supplies only the
narrow compensation lookup/freeze participant against caller-supplied canonical
facts, and REV-06 injects it and proves integrated claim behavior. Likewise,
CON-07 supplies the decision participant; REV-10 alone wires it into review
composition and proves end-to-end atomicity.

### Canonical lock and revalidation order

The active contract extends, and may not replace, WS-REV's accepted order:

1. AUTH-owned current actor/identity/grant/service-assignment/control rows in
   AUTH internal order, locked by the prepared authorization handle for `T`
   operations;
2. the operation idempotency row;
3. for lifecycle-controlled commands, the shared lifecycle advisory fence and
   captured phase snapshot; this is held through the database transaction but
   never through remote I/O;
4. for an already-claimed outbox handler command only, read-only validation of
   the immutable event/claim generation through the outbox-owned capability;
   the handler acquires no OutboxEvent row lock and performs no outbox state
   transition;
5. `Project`;
6. active/candidate ProjectGuide, GuideSourceSnapshot, submission-artifact,
   effective, checker, review, revision and legacy payment-policy rows in the
   existing REV order; then the active compensation selector,
   CompensationPolicyVersion and referenced CompensationAdapterBinding rows;
7. WorkstreamTask, TaskAssignment, Submission, CheckerRun,
   RevisionContextPreparation, ReviewQueueEntry, ReviewLease,
   ReviewReconciliationFinding and prior Review/finding rows in REV order;
8. stabilized ArtifactBinding/Replica facts without remote provider I/O;
9. ContributionRecord, CompensationAward, delivery, receipt and projection rows
   in WS-CON order;
10. append-only audit and shared-outbox rows after all state locks.

Multiple same-type rows are locked by ascending primary key/UUID. Operations
skip absent classes but never reorder shared classes.

No feature may reverse this order. For `T` operations, AUTH prepares and locks
authority first; publish, retire, binding suspend/resume/retire, assignment
claim, review claim, delivery, callback, reconciliation, and projection rebuild
then evaluate the same prepared handle against final facts recomposed from their
locked product rows. The handle is request/session/action/target bound and
single-use. `Q` reads remain request-scoped.
Freezing requires a published version whose referenced bindings are active.
Suspension blocks new freezes and new delivery but does not erase already-frozen
obligations; exact callback/replay behavior is state-matrix controlled. Real
PostgreSQL tests cover publish/suspend versus both claim types and suspend/
retire versus dispatch/callback in both lock permutations.

The dispatcher claim is a separate, previously committed CON-02B transaction.
It releases its session and every database lock before invoking a feature
handler. The handler starts a new caller transaction, acquires the lifecycle
fence/phase, validates the supplied claim generation through the typed outbox
capability without locking or mutating the OutboxEvent, and only then locks CON
rows. It commits durable pre-I/O state and releases the transaction/fence before
remote I/O. Only the dispatcher later applies the handler's typed outcome to
outbox retry/finalization state.

### Artifact evidence

The Review transaction creates only a pending contribution-evidence projection
row and a shared-outbox wake-up event. After commit, a worker loads canonical
PostgreSQL records, produces deterministic canonical JSON, computes its
expected SHA-256 and exact byte count, and passes a bounded async byte source,
media type `application/vnd.workstream.contribution-evidence+json;version=1`
and those expected facts to an ART-owned typed capability.

Merged ART-02A2 PR #129 supplies only ART's inactive preparation foundation.
Before D10 or any database mutation lock, the future capability uses ART's
`ArtifactPreparationService` to write the complete first pass to canonical
bounded private scratch, compute digest/size, validate the exact media contract,
reject mismatch, and retain a sealed source behind an opaque ART operation.
Transaction A then locks AUTH -> CON -> ART, recomputes the canonical evidence
commitment from locked product facts, final-evaluates D10 and stages the durable
attempt. The caller commits explicitly; only then may an ART-owned same-process
continuation prove/claim that committed attempt in a fresh transaction and
consume the single second-pass stream outside every database transaction.

Rollback, cancellation and exact replay close the preparation or retain
fail-closed ART cleanup custody until retry succeeds. Process loss persists no
handle/path: stale scratch cleanup reclaims custody and deterministic outbox
replay regenerates identical bytes against the durable attempt. CON never
imports or constructs `ArtifactScratchManager`, `PreparedArtifact` or
`CommittedArtifactSource`, receives a scratch path/descriptor, or owns cleanup.

PR #129 does not implement the named contribution-evidence capability or the
remaining ArtifactStore v2, S3/MinIO, durable admission, provider execution,
verification/publication, recovery/authorization, binding or receipt gates.
02A3, 02B1, 02C1, 02C2, 02C3 and 02D must precede the separately approved
`WS-ART-001-CON-EVIDENCE` chunk, which delivers both named write and read ports.
It returns only bounded verified ArtifactBinding/receipt data. WS-CON validates
their digest/size/media/owner/project/role/schema/idempotency facts before it
stores projection state and the verified Workstream binding reference.

LocalStorage and MinIO exercise the same product capability contract. AWS S3
deployment proof gates production. Flow Node, R2, semantic search, provider
retain/pin APIs, and raw provider refs are excluded.

### Shared outbox

Land one generic PostgreSQL outbox before contribution integration. CON-02A
owns persistence/caller-transaction append. CON-02B owns the feature-neutral
Celery dispatcher, claim fencing, stable task IDs, retry/dead-letter/replay,
retention, operational recovery, a single explicit handler registry, and the
read-only same-session `OutboxDrainObservationPort` plus
`OutboxClaimValidationPort`. Feature handlers own deterministic delivery
semantics, never dispatch infrastructure or repository queries.

## Alternatives considered

### Edit the supplied reference pair in place

Rejected because reference inputs are provenance evidence, the original PDF is
already checksum-bound, and the revised PDF is not a declared reproducible
Markdown build. Preserve generations and create an active reconciled spec.

### Replace broad PermissionIds with granular strings

Rejected because the merged AUTH contract preserves 74 stable PermissionIds
and separately registers 57 ActionIds, of which nine self/admin actions are
active on current trusted `main`. Granular action names do not replace
permissions.

### Let WS-CON flip AUTH catalogue availability

Rejected because availability without an AUTH-owned typed evaluator, grant or
service-assignment path, audit parity, and transaction protocol is either
deny-only or an authorization bypass. AUTH owns registration, evaluator
dispatch, principal truth and activation; CON owns canonical product facts and
behavior only.

### Reuse `PaymentPolicy` directly as the award policy

Rejected because it is guide-version-bound, submitter-oriented, and cannot
represent reviewer compensation, explicit unpaid rules, points, bindings, or
immutable publication lifecycle without becoming a second incompatible model.

### Retain `PaymentPolicy` as advisory or historical context

Rejected by the human. CompensationPolicyVersion supersedes it. A two-step
expand/contract removal keeps the semantic cutover atomic in CON-05A and drops
the unreachable physical schema in CON-05B; neither step exposes a fallback.

### Call ArtifactStore from contribution workers

Rejected by ADR 0013/0014 because it bypasses ART admission, verification,
binding, receipts, recovery, and composition ownership.

### Implement ContributionRecordRequested first

Rejected because the approved REV/CON seam is direct atomic participation in
the Review transaction. A temporary event would create a partial-history risk.

### Publish partial APIs early

Rejected because action activation, policy freeze, callback service identity,
review atomicity, and artifact capabilities must fail closed as one coherent
backend contract.

## Boundaries preserved

- Auth/session: external tokens are verified by existing issuer adapters;
  WS-AUTH alone owns product authorization and service actors.
- Permission/policy: WS-CON supplies resource facts/guards but never edits
  grants or implements an authorization kernel.
- Payment/execution: Workstream records awards/instructions/receipts; external
  adapters own provider attempts, approvals, balances, and ledgers.
- Persistence/data: PostgreSQL owns canonical contribution/award/receipt truth;
  provider bytes are never canonical product state.
- Presentation/API: `/api/v1`; deterministic concealment and pagination; no
  provider refs, tokens, or credentials.
- CI/deployment: no threshold weakening; no new production provider or
  dependency without explicit approval.

## Rollout/migration strategy

1. Adopt the ADR-backed active contract while preserving both archival
   generations. The same chunk adds only the exact renamed generation-2
   Markdown path to the stale-authorization scanner's reviewed history map,
   with near-miss/new-document fail-closed regression proof; the active spec
   remains scanned. Its gate test repairs the existing cross-scanner set
   comparison by subtracting only this authorization-only path and proves the
   artifact scanner already excludes it through the reference-spec prefix; the
   artifact scanner itself is unchanged.
2. Merge outbox persistence then its feature-neutral dispatcher; add split,
   inactive binding/policy/contribution/award/delivery/receipt persistence.
3. Complete the ART sequence needed by evidence intake: merged 02A2 committed-
   source preparation -> 02A3 ArtifactStore v2 cutover -> 02B1 MinIO/AWS S3 ->
   02C1 durable admission/put-attempt -> 02C2 verification/publication -> 02C3
   recovery chain -> 02D hidden internal-executor/Operator recovery behavior ->
   AUTH-owned evaluator integration/activation -> separately approved
   `WS-ART-001-CON-EVIDENCE` write/read ports. AUTH-09 first owns the fixed
   verifier/scanner/resolver registrations, identities and assignments; D12
   first transfers the eight ART-02D Operator and three internal actions to the
   exact AUTH activation custodians (or a separate closed custody map); 02D
   proves hidden resource/feature behavior but never changes availability; AUTH
   separately activates Operator recovery and internal execution. None of these
   gates moves scratch, provider, ART
   persistence or authorization ownership into CON.
4. Interleave each AUTH registration -> feature implementation -> AUTH
   activation wave in `AUTHORIZATION_HANDOFF.md`. The registration checkpoint
   provides planned ActionId/PermissionId/owner/audit parity, typed context
   contracts, principal prerequisites and prepared mutation protocol. The
   CON/ART chunk then merges hidden authorization-ready behavior while the real
   kernel still denies. Only a later AUTH-owned checkpoint integrates the
   evaluator, proves the exact merged feature and changes availability. CON/ART
   never edits AUTH or supplies a production allow fallback. Merge required ART
   capabilities in ART.
5. Activate hidden binding/policy services. CON-05A atomically removes every
   PaymentPolicy semantic consumer and enables only task claims that freeze a
   CompensationPolicyVersion, only after merged REV-02 establishes the exact
   `Submission.task_assignment_id` lineage. CON-05B drops the unreachable old
   model/table/columns/constraints after a zero-consumer scan.
6. Interleave with WS-REV: policy schema before REV lease schema; lease freeze
   before claims; atomic participant after revision/decision persistence.
7. Add delivery/callback, evidence projection, reads, and operations behind
   unregistered production routes.
8. Finish WS-CON hidden readiness and an exact dependency manifest. WS-REV-13
   is the sole production router activation and joint live-drill owner for the
   review/contribution/compensation release. Before it, REV-12A may own hidden
   persisted joint release control and inject its implementation through the
   required CON-owned dispatch/callback fence ports while consuming the
   read-only fulfillment-drain observation port; it may not edit CON product
   files or import CON/outbox repositories.
   Sibling reviewed baseline `6faccc0` correctly treats PR #129 as inactive
   preparation; later same-turn external-review repairs are in progress. Both
   are discovery only. The future merged snapshot must repair REV-06/08 one-step
   authorization, REV-10 final CON composition, D12 custody and REV-12A's
   handler-owned outbox transitions. It must adopt the current
   registration -> CON -> REV hidden -> AUTH activation/prepared-handle
   choreography and dispatcher-owned typed command/outcome contract, then pass
   fresh review and merge before consumption. Do not pin the live sibling head/
   cleanliness or change archival sources.

At every chunk activation, rebase discovery on trusted `main`, refresh exact
migration numbers and dependency symbols, and stop if an expected port/action
is absent or materially changed.

## Verification strategy

- Ruff and focused unit/service tests for every chunk.
- Every runtime chunk uses `scripts/run_isolated_tests.py` with one unique,
  attempt-specific metadata JSON retained under the initiative evidence
  directory and same-invocation `pytest --cov=app --cov-fail-under=78`; stale
  `.coverage` output is never evidence. Focused reports from that invocation
  prove each new/materially changed subsystem is at least 90 percent.
- Fresh isolated real-PostgreSQL tests cover migrations, constraints,
  transaction rollback, idempotency, and both concurrency permutations.
- New/materially changed module coverage at or above 90 percent; same-run
  repository coverage at or above 78 percent.
- OpenAPI action inventory requires one ActionId per protected surface and
  proves hidden routes remain absent before final activation.
- Authorization contract tests prove every planned WS-CON action denies, every
  active action has exactly one AUTH evaluator and one approved typed context,
  and no active action exists without its owning feature behavior. Mutation
  tests reject missing/reused/cross-session prepared handles and exercise
  actor/link/grant or service-assignment revocation against product mutation in
  both lock permutations. AUTH role-matrix/evaluator tests prove D11's exact
  human-approved delivery/award/audit sets, including only the amendments and
  inclusion/exclusion cases that outcome requires, plus exact matched-grant/
  project evidence and resource-context digest equality.
- Static architecture tests reject AUTH persistence imports, local role checks,
  provider-specific compensation adapters, concrete-adapter imports or
  construction outside the explicit composition root, raw ArtifactStore
  injection, provider refs, and duplicate outbox implementations. The
  deterministic conformance adapter is allowed only through the shared typed
  factory and explicit composition.
- Contract tests prove proposed ActionId -> PermissionId parity with the merged AUTH
  catalogue and stable event payload/digest identity.
- LocalStorage and MinIO evidence-capability conformance; AWS deployment proof
  remains owned by ART.
- ART capability tests prove expected digest/size mismatch causes zero durable
  admission/provider calls; only ART preparation can mint the committed source;
  the second pass is single-use; success/failure/cancellation either completes
  close/release or leaves explicit ART-owned cleanup custody unavailable for
  reuse until retry succeeds; and no scratch path/type crosses into CON. PR
  #129's preparation tests alone do not satisfy this integration gate.
- Final live drill covers paid accept, needs revision, reject, unpaid policy,
  frozen-version change, money+points, acknowledgement vs fulfillment,
  failure-then-fulfillment, replay, adapter outage, storage outage, recovery,
  authorization denials, atomic rollback, and reconciliation.
- `CONFORMANCE_MATRIX.md` maps every adopted candidate invariant to an owning
  chunk, executable case, final live case, and retained evidence; activation
  replaces proposed names with collected test node IDs.
- Stale wording scan, Markdown links, reference checksums, `git diff --check`,
  and one-sheet roadmap checks when sheets are present.

## Review strategy

Planning and every specification/runtime chunk require senior engineering,
QA/test, security/auth, product/ops, architecture, docs, and reuse/dedup.
Runtime/test chunks add test-delta. Outbox/worker/script/config/CI changes add CI
integrity. Critical/High findings block; Medium findings require human decision.

## Sequencing

See `CHUNK_MAP.md`. Only one WS-CON chunk is active at a time. Cross-initiative
gates do not authorize another initiative's work and no successor starts
without a new explicit human instruction.
