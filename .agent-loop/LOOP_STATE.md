# Loop State

## Current State

- Active initiative: `WS-QUAL-001` - Backend Coverage Floor
- Active planning chunk: none
- Active implementation chunk: `WS-QUAL-001-01B1B-R10` TypeVar child order
- Branch: `codex/ws-qual-001-01b1b-semantic-delta-guards`
- Status: B1B stopped at 223/300 lines after its second binding/AST repair
  cycle. Review at `10dff4f` found lexical-shadow false positives and a
  weakened local-lookalike `skipTest` expectation. B1B-R1 was proposed as the
  bounded lexical-binding replacement. R1 passed plan review but stopped at its
  first size checkpoint: the shared resolver alone measured 282 lines before
  its required matrix, so its 300-line cap could not preserve proof. R2 is
  stopped at implementation review `d4cef1d`: the 348/350 candidate omitted
  standard Python scope and control-flow cases, and proof could not fit its
  two-line reserve. R3 is proposed to use stdlib `symtable` for lexical facts
  with bounded AST value flow under the normal 500-line L1 cap. Cycle-zero
  review at `10ca508` found path joins, chained ambiguity, binding targets, and
  future-annotation gaps. R3 stopped before cycle-one edits because the 32-line
  reserve lacked credible proof. R4 stopped at `06a6d61` after review found AST
  replay corrupting symbol-table consumption, target/unpack bypasses, and
  optional comprehension effects. R5 stopped at `5f59f40`: review found
  non-transitive loop summaries, evaluation-order/iterable-target bypasses, and
  incorrect `except*` flow. R6 stopped at `68174d1`: review found incomplete
  comprehension/set/dict element provenance, structural generator consumption,
  and class-global bindings. R7 passed all ten plan tracks at `f0134aa`.
  Cycle-zero review at `26a4e6e` found lazy-generator, unpacked provenance,
  conditional provenance, empty-dict reachability, and class-global transfer
  gaps. Cycle-one review at `a8e1e78` found incomplete structural consumption,
  empty-comprehension provenance, and class-control/import boundary gaps. The
  final permitted repair is bound at `5fcd9bb`; review found transparent-wrapper
  provenance, sequential/qualified/async consumer, relative-import, and nested
  class-expression gaps. R7 is stopped under its two-cycle rule. R8 now proposes
  a bounded syntactic policy with no runtime execution model. All required plan
  tracks passed at `9d72e42`. The implementation is bound at `3acf572`; 117
  focused tests and the exact 412/700 delta gate passed. Cycle-zero review found
  bounded lexical namespace/scope gaps; the cycle-one repair is bound at
  `1a13bea`. Cycle-one review found five bounded syntax traversal gaps. The
  final permitted repair is bound at `e2ac216`; final QA found Python 3.11
  comprehension symtable incompatibility. R8 is stopped. R9 proposes only the
  dual-version scope-pairing closure. Implementation is bound at `5a971d8`;
  initial dual-version proof passed at `5a971d8`. Review found nested 3.12 inline
  and Python 3.13 public scope-name gaps. The one permitted repair is bound at
  `a5395c1`; identical 165-test matrices pass on Python 3.11, 3.12, and 3.13 at
  553/600 raw lines. Final review found Python 3.13 bound/default children need
  one shared public ordinal. R9 is stopped; all R10 plan tracks passed at
  `c42a67a`. Reviewed implementation `15d0b80` passes identical 171-test
  matrices on Python 3.11, 3.12, and 3.13 at 577/620 raw lines. All required
  internal tracks pass; evidence binding and PR publication are active.
- Prior WS-ART reviewed planning SHA: `f7fbc33`
- Prior WS-ART final evidence-bound planning branch head: `c069064`
- WS-ART planning merge commit: `8644a43`
- Prior WS-AUTH-001-01 reviewed implementation SHA: `be0b836`
- Prior WS-AUTH-001-01 final merged branch head: `b5217e1`
- Latest integrated `main` merge commit: `060b780190435bc79464ae92fd9235a652f70e00`
- WS-QUAL final reviewed planning SHA: `0d9dd987d546c864fa8de7bae462e5e73a1b5ea9`
- WS-QUAL final evidence-bound branch head: `3da1769882e9f6db4c48ef3dba33da8380e6a613`
- WS-QUAL planning merge commit: `9046d52f31c7c39f06e06c45c43783bb08a5181c`
- WS-QUAL post-merge memory merged through PR #100 as `58d4459`.
- WS-ART-001-01 reviewed implementation SHA: `5574bf59cf1cb86da76749e0cbc529036346fa8a`
- WS-ART-001-01 final evidence-bound branch head: `2b8c2a0`
- WS-ART-001-01 merge commit: `050eb15eab8c57e6bc265477a5e92484d27a893c`
- WS-QUAL-001-01A implementation base SHA: `58d44596f614895964b82bb344e0ed98596eaae8`
- Current 01B split base SHA: `8829a7ec3aa5199aae0aecbe5fda030c42a051cd`
- WS-QUAL-001-01A reviewed implementation SHA:
  `d1582ec64b9176c5ead62f695c7a23b48e4c72b9`
- WS-QUAL-001-01A final evidence-bound head:
  `8cd7616b497ceb46d8359c25de689192632dfee8`
- WS-QUAL-001-01A merge commit: `2901a3ebe68b7c770ccb1ff06841d79ce0c20d94`
- WS-QUAL-001-01A post-merge memory merge commit:
  `8829a7ec3aa5199aae0aecbe5fda030c42a051cd`
- Current gate: publish only the reviewed R10 PR. 01B2 remains inactive;
  AUTH-02 merged through PR #107 as `060b780`.
- Next chunk: `WS-QUAL-001-02` remains inactive; do not start it automatically.
- Parallel initiative: `WS-AUTH-001-02` merged through PR #107 as `060b780`.
  `WS-AUTH-001-03` is active after explicit user start in isolated worktree
  `workstream-auth-001-03`; its plan repair and implementation run independently.
- Parallel initiative: `WS-ART-001-01` merged through PR #101 as `050eb15`.
  `WS-ART-001-02` remains proposed and inactive pending a separate explicit
  user start.
- Parallel initiative: `WS-POL-002-03` merged through PR #90 as `a7aa474`; its
  post-merge memory merged through PR #94 as `b1270d7`. `WS-POL-002-04` remains
  inactive pending the relevant authorization proof and a separate explicit
  start.

## Operating Rule

Workstream engineering chunks move through:

```text
Intent -> Discovery -> Plan -> Chunk Map -> Chunk Contract -> Implementation -> Evidence -> Internal Review -> PR -> Human Checkpoint -> Memory Update -> Stop
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
  guide-source snapshots, and aligned active docs around `PaymentPolicy` as the
  payment-term authority.
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
