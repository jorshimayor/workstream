# Internal Review Evidence: WS-ART-001-02A2

## Chunk

`WS-ART-001-02A2`: Committed Source And Local Preparation

open sub-agent sessions: none

valid findings addressed: yes

## Reviewed Revision

Reviewed code SHA: d8b8c8abc7c6dd8cf254d0c8b3d5d7c066c01b46

Reviewed at: 2026-07-15T17:31:07Z

Reviewer run IDs: senior-engineering=019f66b1-e273-7971-a2d7-4db8c105d537; architecture=019f66b1-e898-7c51-8e7c-66352ac42be0; QA/test=019f66b1-f1bf-7561-bf41-23442b962212; security/auth=019f66b1-fe73-7372-9d50-4f19b9c3bb76; product/ops=019f66b2-09fc-7042-8e0c-f37b98dbed39; reuse/dedup=019f66b2-1b7e-7563-bebe-c482c388c002; CI-integrity=019f66b9-219b-7eb0-bcfd-8f511a5f5560; test-delta=019f66b9-29c5-7b61-a726-193235e1a67a; docs=019f66b9-326d-79a0-9c71-c5006b1e6152

After the reviewed SHA, only initiative review evidence and status files change.

## Reviewed Change

- Added the inactive, provider-neutral `PreparedArtifact` and
  `CommittedArtifactSource` boundary so a server-computed commitment cannot be
  detached from its exact second-pass bytes.
- Added a private, database-independent, cross-process scratch manager that
  reserves the full 512 MiB hard maximum, enforces aggregate/file/concurrency/
  free-space limits, and supports deterministic stale cleanup without runtime
  activation.
- Bound each scratch root to one canonical complete limit fingerprint and made
  release retryable until ledger cleanup succeeds.
- Refactored only LocalStorage private write internals; active ArtifactStore v1,
  factory wiring, routes, schema, providers, Celery ownership, auth, and product
  lifecycle behavior remain unchanged.
- Added exact configuration documentation and cumulative CI coverage proof.

## Reviewer Results

| Reviewer | Result | Blocking findings | Notes |
|---|---:|---|---|
| senior engineering | PASS | None | Bounded inactive boundary, conservative admission, and retryable cleanup passed. |
| qa/test | PASS | None | Acceptance criteria and 105 focused regression tests passed. |
| security/auth | PASS | None | No auth/authz surface or product data boundary was introduced; private filesystem handling passed. |
| product/ops | PASS | None | No operator, contributor, reviewer, payment, reputation, or lifecycle behavior changed. |
| architecture | PASS | None | Provider-neutral preparation remains separate from durable product state and active v1 wiring. |
| ci integrity | PASS | None | Repository 78 percent and cumulative scoped 90 percent gates remain fail closed. |
| docs | PASS | None | Exact settings, defaults, root separation, fingerprint, and reprovisioning rules are documented. |
| reuse/dedup | PASS | None | No missed abstraction remains; the reviewer-confirmed free-space defect was repaired. |
| test delta | PASS | None | Tests are additive; none were removed, skipped, xfailed, or weakened. |

## Valid Findings Addressed

- Failed root-directory durability could leave a published reservation after
  an error. Ledger rollback now covers root `fsync` failure.
- Existing or rejected scratch roots could be mutated. Initialization no longer
  changes existing permissions and rejects invalid layouts before mutation.
- Concurrent root initialization and temporary-ledger publication could race.
  Initialization, validation, temporary cleanup, and publication are lock-safe.
- Prepared handles and sources were forgeable or could yield bytes before full
  commitment verification. Construction is preparation-service-owned and the
  complete commitment is verified before the first provider byte is yielded.
- Constructor and failure paths could leak file descriptors or reservations.
  Descriptor and ledger rollback are explicit and covered by fault injection.
- A transient release failure made cleanup non-retryable. The handle remains
  open and service-owned until ledger release succeeds.
- Processes could share a root with different limit settings. The root marker
  now binds a canonical fingerprint of the complete limit set.
- Exact scratch environment names/defaults and mixed-rollout behavior were not
  documented. The canonical artifact spec now contains the operator inventory.
- Free-space admission ignored outstanding logical reservations. Admission now
  requires existing reserved bytes plus the new full reservation plus the
  configured floor while holding the cross-process ledger lock.

## Cross-Initiative Compatibility

- The current authorization implementation remains the sole owner of canonical
  `ActorProfile.id`, `ActionId`, `PermissionId`, service identities, and live
  authorization decisions. This inactive chunk consumes none of them.
- WS-REV continues to own review packet/evidence records and will consume only
  future narrow artifact capabilities and verified `ArtifactBinding` values.
- WS-CON contribution-evidence capabilities remain a separately approved future
  ART prerequisite; no contribution or compensation contract was invented here.

## Commands Run

```bash
cd backend && .venv/bin/ruff check app tests
cd backend && .venv/bin/pytest \
  tests/test_artifact_preparation.py \
  tests/test_local_artifact_store.py \
  tests/test_config.py -q \
  --cov=app.modules.artifacts.preparation \
  --cov=app.modules.artifacts.sources \
  --cov=app.core.config \
  --cov-report=term-missing --cov-fail-under=90
cd backend && .venv/bin/docstr-coverage --config .docstr.yaml
python3 scripts/test_agent_gates.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_markdown_links.py
python3 scripts/update_post_merge_memory.py validate-merge-intent \
  --base-ref origin/main
git diff --check
```

Results: Ruff passed; 105 focused tests passed at 94.24 percent changed-scope
coverage; repository docstring coverage passed at 92.3 percent; 71 agent-gate
tests passed; stale artifact, stale wording, Markdown link, merge-intent, and
diff checks passed.

The full isolated PostgreSQL suite is intentionally delegated to GitHub Backend
CI because the user directed repository-wide execution away from the contended
local workstation. CI retains the exact 78 percent repository floor.

## Remaining Risks

- This chunk is inactive preparation infrastructure. `WS-ART-001-02A3` must
  atomically cut ArtifactStore to v2 and explicitly activate cleanup ownership.
- GitHub Backend CI must prove the exact published head and repository-wide 78
  percent floor before merge.
- No later artifact, review, contribution, or authorization chunk starts from
  this evidence automatically.

## Stop Condition

Publish this chunk for external and human review, then stop. Do not start
`WS-ART-001-02A3` and do not merge without explicit user approval.
