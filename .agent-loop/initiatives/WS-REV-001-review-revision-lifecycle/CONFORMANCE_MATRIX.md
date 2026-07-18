# Conformance Matrix: WS-REV-001

Chunk starts replace proposed test descriptions with exact collected node IDs.
No row is complete from prose or an unmerged owner contract.

| Area | Owning chunks | Required executable proof | Release proof |
|---|---|---|---|
| Authority | 05B, 06A-C, 07A-B, 08, 02A2, 09A2-A5, 10, 11A-D, 12P2, 12A1-A4, 13C | Exact active/project reviewer grant; canonical human actors; AUTH-first prepared mutations; opaque one-use bindings; clean denial/restaging; service identity isolation; no direct grant reads; no adjudication authority | Exact merged feature manifests -> AUTH activation -> phase-enabled HTTP denial/allow matrix |
| Guide chronology | 02A, 02A2 | Positive immutable per-project sequence; exact status/provenance; Project-first publication/screening; immutable Task triplet; hidden prepared If-Match reactivation; both-order races | Forward/backward active guide changes without reviewer-side rebase or stale retry |
| Queue routing | 03A-B, 05A-B, 06A-C, 09B, 11A/C | Exact checker admission; one open/preferred entry; normalized packet membership; current returns lease/offer/none; duplicate/supersession races; authorized batched historical classification | New and historical eligible rows, preferred return, takeover, counts/age evidence |
| Leases | 03A-B, 06A-C, 11A/C | One active lease globally; canonical reviewer; packet manifest; reviewer ContributionPolicyVersion freeze; release/decline/expiry/revocation/lazy recovery and both-order races | Claim/release/expiry/reclaim/revocation through exact admitted service identities |
| Review history | 04A-B, 08, 10 | Every decision/finding/resolution immutable; exact predecessor/assignment lineage; reviewer CON operation before branch; accept-only FinalAcceptance and submitter operation; reject exact assignment; atomic rollback | Real accept/needs_revision/reject HTTP/database/audit/CON agreement and changed replay denial |
| Revision origins | 09A1-A2, 10, 11B-D | RevisionObligation XOR `human_review`/`checker_run`; exact source lineage; one obligation per source/prior Submission; no checker synthetic Review; atomic initial preparation | Checker and human revision drills both reach corrected N+1 without lineage drift |
| Revision context | 02A-C, 09A1-A5, 09B | Immutable non-branching task-owned preparation; kept/forward/backward/blocked; exact head acknowledgement; one winner per head; replacement successor; no contribution-policy rebase | Context display, checker rerun, prior-reviewer preference, resolution, final decision |
| Limits/deadlines | 09A1-A4, 11B | Round counts both origin kinds; DB time strictly before per-obligation deadline; equality expired; repair cannot bypass exhaustion; D6 close only | Before/equal/after, exact replay/races, no synthetic Review/CON record |
| Reject/admin close | 10, 11B/D | Human reject only from Review; exact assignment blocked/task rejected. PM/Operator closes use canonical cancelled reasons and create no Review/CON | Authorized/denied/cross-project/rollback proof; no `closed` token |
| Artifact evidence | 03B, 07A-B, 09A3, 11D | Active-exact-lease bytes; metadata-only history; ART candidate/finalize; immutable slot plus append-only attachment; orphan-only failed finalization; no raw store/provider path | Local/MinIO/S3 owner conformance plus outage/integrity no-adverse-outcome drill |
| Projection | 04B, 10, 12P1-P3 | Shared outbox only; deterministic handler/receipt; reauthorized reads; independent projection/reconciliation services; no canonical truth change on failure | Forced post-commit failure/retry and one immutable receipt |
| Release control | 12P3, 12A1-A4, 13A-C | Persisted phase history; read/mutation classes; checker revision routing allowed with checker completion through revision-cutover fence; human preparation inside leased decision; REV/task/checker/CON fences; bounded drain/cutoff/crash resume | Static routes/AUTH mappings, phase-denied execution, scheduler runbook, forward reactivation, final real-HTTP drill |

## Concurrency invariants

- Concurrent initial creates produce one v1; loser exact replay or stable
  conflict. They never produce v2.
- Concurrent creates against one preparation head produce one N+1; loser exact
  replay or conflict. N+2 requires a later committed revision obligation/head.
- Every mutation race uses independent PostgreSQL sessions and both lock/commit
  orders.

## Closure rule

13C validates all rows against fresh real-PostgreSQL evidence, exact merged owner
SHAs, AUTH-active actions, mandatory phase fences, privacy-safe HTTP proof, and
active docs generated from the released behavior. Missing/skipped proof, direct
database fabrication, or an unavailable owner participant blocks release.
