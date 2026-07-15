# Conformance Matrix: WS-CON-001

## Rule

This matrix is the traceability index for the reconciled active contract. Chunk
01 expands every retained candidate requirement into an exact row. Runtime
chunks replace proposed case names with collected pytest node IDs and retained
metadata at `.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/evidence/<chunk-id>-<attempt-id>-isolated-tests.json`
plus live-evidence paths before activation. Failed attempts remain immutable;
the matrix records the one accepted attempt ID/path. Archival candidate text is
evidence, not executable authority.

| Requirement family | Owner | Minimum executable cases before owner completes | Final live evidence owner |
|---|---|---|---|
| Central authorization integration | AUTH executable gates + each CON resource owner | all absent/planned actions deny; each active action has exact ActionId/PermissionId/owner/context/evaluator parity; human grant and service assignment never substitute; `T` prepared handles reject missing/reuse/cross-session/cross-action/target drift; authority-loss versus product mutation runs in both orders; no CON AUTH-repository import or local role fallback | AUTH conformance + REV-13 |
| Contribution identity and review lineage | CON-03C/07 + REV-10 | one completed-review contribution per valid Review; accept adds one accepted-submission contribution; second revision review creates a distinct reviewer contribution; automated checker outcomes create none; at-most-one DB constraints and mandatory-participant at-least-one proof | REV-13 |
| Policy publication and freezing | CON-04B/05/06 + REV-06 | absent/incomplete setup denies; unpaid is explicit; retired frozen version remains valid for started work; later activation changes new assignments/leases only; publish versus both claims in both lock orders | REV-13 |
| Binding lifecycle | CON-04A/08A/08B/10B | suspended blocks new freeze/delivery but accepts valid existing-work callback; retirement denies dependencies then permits exact accepted-receipt replay only; actor/link revocation denies; project/instrument mismatch denies | REV-13 |
| Immutable award evaluation | CON-03C/07 | at most one money plus one points award; exact decimals; accept/needs_revision/reject rules; replay stable; changed facts fail; no PaymentPolicy fallback | REV-13 |
| Outbox and delivery | CON-02A/02B/03D/08A + REV-12A | immutable event/payload/binding/idempotency identity; stale claim fencing; durable in-flight generation; retry/dead-letter/replay; reconciliation preserves original identity; provider I/O occurs outside every database transaction/lifecycle fence; dispatch-versus-admission fencing in both orders | REV-13 |
| Callback and fulfillment | CON-08B + REV-12A | callback before acknowledgement suppresses later delivery; duplicate exact receipt idempotent; changed receipt conflicts; per-actor/binding limits; suspended/retired matrices; callback allowed through delivery drain and denied after disable; callback-versus-disable in both orders; no human authority | REV-13 |
| Evidence artifact | CON-09A/09B | deterministic versioned schema; self/project disclosure matrix; no reviewer-private, provider, credential, external-receipt or unnecessary actor data; newer-schema rebuild retains prior immutable bundle; LocalStorage/MinIO capability conformance | REV-13 |
| Product reads | CON-10A | self/project role matrix, cross-project concealment, stable pagination, money/points/status separation, no provider refs | REV-13 |
| Operations and audit | CON-10B + REV-12A | Finance versus Operator reconciliation and PM/contributor denials; bounded rebuild; immutable truth unchanged; audit read/export scope and redaction; same-session drain observation never reports false zero or exposes repositories | REV-13 |
| Atomic review integration | CON-07 + REV-10 | allowed exact `review.decision` evidence matches actor/action/resource/project/request/correlation; denied/stale/mismatched evidence rejected; every injected failure rolls back review/task/contribution/award/audit/outbox together | REV-13 |
| Public contract | CON-11 readiness + REV-12A control + REV-13 activation | hidden routes absent before release; `/api/v1` only; dependency/fence/drain manifest exact; startup/preflight fail closed; no partial surface; deterministic shutdown/reactivation phase matrix | REV-13 |

The completed matrix must cover every normative invariant adopted into
`docs/spec_contribution_compensation.md`, including all candidate cases that are
retained after reconciliation. “All mismatch cases” is not an acceptable test
reference.
