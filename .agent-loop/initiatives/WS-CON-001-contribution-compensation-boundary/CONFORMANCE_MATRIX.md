# Conformance Matrix: WS-CON-001

| Family | Owning chunks | Required proof | Final gate |
|---|---|---|---|
| Canonical policy model | 01,03B,04B | ContributionPolicy/version/rules/definitions; explicit unpaid; immutable publish; one active policy; stable binding references | CON-11 |
| Legacy clean cut | 05A,05B | zero semantic consumers before schema removal; deterministic row treatment; no alias/fallback; migration upgrade/downgrade | CON-11 |
| Authorization | AUTH + each feature | 74/57 baseline refreshed; proposed mappings exact; full ART/REV custody referenced; one AUTH custodian; planned denial; exact grant/static row; AUTH-09E; prepared handle misuse; no local role logic | AUTH activation + CON-11 |
| Final acceptance | REV + 03C,07 | accept creates one immutable FinalAcceptance per task/Review/Submission; needs_revision/reject create none; no create API/action, reopen, replacement, or adjudication path | joint live drill |
| Contribution cardinality | 03C,07 + REV | one completed_review per valid Review with direct Review/lease lineage; one accepted_submission per FinalAcceptance with assignment lineage; mutually exclusive sources; revision Reviews distinct; automated outcomes create none | joint live drill |
| Policy freeze | 05A,06 + task/REV | exact submitter/reviewer fields; published version; no drift; publish/suspend races both orders | joint live drill |
| Award evaluation | 03C,07 | matching frozen ContributionRule; unpaid creates none; at most one money/points; exact decimal; replay stable | joint live drill |
| Atomic REV/CON | 07 + REV | exact locked request and stabilized digest; REV creates accept-only FinalAcceptance and stages audit/outbox; CON copies artifact_hash and flushes contributions/awards; zero ART calls; every injected failure rolls back Review/FinalAcceptance/task/contribution/award/audit/outbox | joint live drill |
| Outbox isolation | 02A,02B | stable event/task IDs; claim fencing; retry/dead-letter/replay; dispatcher cannot inherit feature authority; handler returns typed outcome | CON-11 |
| Delivery and callback | 08A,08R,08B | exact feature service authority; no I/O under locks; callback/binding/award match; replay and callback-before-ack; immutable receipts | joint live drill |
| Product reads | 10A | PostgreSQL contribution/award truth; D11 exact role sets; stable pagination/concealment; no ART/provider data | AUTH activation + joint drill |
| Operations requests and observation | 10B | bounded durable requests; AdminRole and prepared-protocol proof; audit redaction; stable drain observation; no executor authority | AUTH activation + joint drill |
| Operations executors | 10C | exact independent fixed-service authority; dispatcher/cross-executor denial; retry/replay/finding proof; projection-only rebuild mutation; immutable contribution/award/receipt truth | AUTH activation + joint drill |
| Public release | 11 + REV | hidden before release; exact `/api/v1` manifest; provisioning-aware readiness; no optional evidence/ART gate | joint live drill |
| Optional evidence | 09A,09B only if approved | separately reviewed ART/AUTH capability; independent status/failure; no effect on canonical truth or core release | separate optional release |
| No adjudication | all core | only accept/needs_revision/reject; no adjudication grant/action/state/queue/lease/decision/contribution/branch/readiness or initiative dependency | CON-11 + joint drill |

Executable node IDs and retained evidence are added by each implementation
chunk. Planning rows are contracts, not claims that tests already ran.
