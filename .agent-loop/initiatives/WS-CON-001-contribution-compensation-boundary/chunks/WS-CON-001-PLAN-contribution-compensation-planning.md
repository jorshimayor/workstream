# Chunk Contract: WS-CON-001-PLAN - Contribution And Compensation Planning

## Parent initiative

`WS-CON-001` - Contribution Record And Compensation Boundary

## Goal

Reconcile the supplied WS-CON pair with current code and parallel AUTH/REV
contracts, then produce a human-reviewable initiative plan without implementing
runtime behavior.

## Why this chunk exists

The candidate spans architecture, permissions, payment, artifacts, lifecycle,
workers, APIs, and migrations and contains conflicts with accepted repository
decisions. Implementation cannot safely begin from the candidate alone.

## Approved plan reference

This chunk creates the parent `INTENT.md`, `DISCOVERY.md`, `PLAN.md`, and
`CHUNK_MAP.md`; no prior implementation plan exists.

## Risk class

L0 architecture/payment/authorization direction; P1 planning priority.

## Allowed files

```text
.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/**
```

## Not allowed

```text
backend application, migrations, tests, workflows, dependencies
AUTH/ART/REV sibling worktree edits
reference-spec byte edits or archival replacement
active runtime documentation adoption
```

## Acceptance criteria

- [x] Candidate Markdown/PDF and original PDF are inventoried by hash/status.
- [x] Current code, tests, docs, AUTH catalogue, REV plan, and ART contract are
  cited concretely.
- [x] ActionIds and PermissionIds are separated and incorrect candidate IDs are
  rejected.
- [x] `/api/v1`, Submission identity, provider, artifact capability, payment
  model, outbox, and review integration conflicts are explicit.
- [x] Required initiative artifacts and bounded chunk contracts exist.
- [x] First implementation/spec chunk remains proposed until human approval.
- [x] Required plan reviewers complete and all valid findings are resolved or
  recorded for human decision.
- [x] AUTH-07B refresh records the two-active/48-planned runtime, separates AUTH
  registration from post-feature AUTH activation, adds the prepared `T`
  protocol and absent upstream `task.claim` gate, and receives fresh required
  review/evidence against current trusted main.
- [x] AUTH-08 refresh records the 74/57 and nine-active/48-planned runtime,
  eight resource variants, two matched-authority kinds, resource/grant/scope
  decision evidence and explicit feature commit ownership; reconciles D11's
  cross-spec role choices and conditional AUTH changes; adds D12's exact
  proposed ActionOwner/custody map; refreshes the clean/non-consumable REV
  dependency; and receives fresh required review/evidence against `aa0fdcd`.

## Verification commands

```bash
python3 scripts/check_markdown_links.py
python3 scripts/check_stale_workstream_wording.py
python3 scripts/check_stale_artifact_contracts.py
python3 scripts/check_loop_memory_state.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q scripts/test_agent_gates.py
git diff --check
test "$(git rev-parse origin/main)" = aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3
git merge-base --is-ancestor aa0fdcd6912e66609e39a2fbd7b65f67be6c62f3 HEAD
test "$(sha256sum docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.md | cut -d' ' -f1)" = cddbe20f4fadf5307f68519347bdd9520ef49b23fb0b92cad24c31fc9b34c640
test "$(sha256sum 'docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification(2).pdf' | cut -d' ' -f1)" = ce65e208076769f0bafb09779d60ab6f5fc0c596514d4e8f4cc03690c6e6d457
test "$(git show origin/main:docs/reference_specs/WS-CON-001-contribution-record-and-compensation-boundary-specification.pdf | sha256sum | cut -d' ' -f1)" = 34c4337f27e42a5b0ed5e153fe8ccd492ecede202c2764506a930d109aef66c1
test "$(git -C /home/abiorh/flow/workstream-rev-001 rev-parse HEAD)" = a13bf352147cbb2c65742802e7c74a9478e5013b
test -z "$(git -C /home/abiorh/flow/workstream-rev-001 status --porcelain)"
(cd backend && python3 - <<'PY'
import re
from pathlib import Path

from app.modules.authorization.catalogue import (
    ACTION_DEFINITIONS, ActionAvailability, ActionId, PermissionId,
)
from app.modules.authorization.policy import ADMIN_ROLE_PERMISSIONS
from app.modules.authorization.runtime import AuthorizationResourceContext, MatchedAuthorityKind
from app.modules.authorization.schemas import AdminRole

actions = {item.value for item in ActionId}
permissions = {item.value for item in PermissionId}
active = {
    row.action_id.value
    for row in ACTION_DEFINITIONS
    if row.availability is ActionAvailability.ACTIVE
}
ws_con_actions = {
    "contribution.read_self", "contribution.read_project",
    "compensation.policy.read", "compensation.policy.create_draft",
    "compensation.policy.update_draft", "compensation.policy.publish",
    "compensation.policy.retire", "compensation.adapter_binding.read",
    "compensation.adapter_binding.create", "compensation.adapter_binding.suspend",
    "compensation.adapter_binding.resume", "compensation.adapter_binding.retire",
    "compensation.award.read_self", "compensation.award.read_project",
    "compensation.delivery.reconcile", "compensation.status.read",
    "compensation.reconcile.run", "contribution.projection.rebuild",
    "audit.read", "audit.export", "compensation.fulfillment.report",
    "outbox.dispatch", "artifact.contribution_evidence.binding.create",
}
operator = {item.value for item in ADMIN_ROLE_PERMISSIONS[AdminRole.OPERATOR]}
finance = {item.value for item in ADMIN_ROLE_PERMISSIONS[AdminRole.FINANCE_AUTHORITY]}
manager = {item.value for item in ADMIN_ROLE_PERMISSIONS[AdminRole.PROJECT_MANAGER]}
assert (len(permissions), len(actions), len(active)) == (74, 57, 9)
assert len(ACTION_DEFINITIONS) - len(active) == 48
assert len(AuthorizationResourceContext.__args__) == 8
assert {item.value for item in MatchedAuthorityKind} == {"actor_self", "admin_role_grant"}
assert not (ws_con_actions & actions)
assert "task.claim" in permissions and "task.claim" not in actions
assert not ({"outbox.dispatch", "compensation.fulfillment.report"} & permissions)
assert "compensation.delivery.reconcile" in finance
assert "compensation.delivery.reconcile" not in operator
assert "compensation.award.read" in manager
handoff = Path("../.agent-loop/initiatives/WS-CON-001-contribution-compensation-boundary/AUTHORIZATION_HANDOFF.md").read_text()
owner_section = handoff.split("## Proposed AUTH-owned ActionOwner custody", 1)[1].split("## Proposed closed handoff", 1)[0]
owner_actions = []
for line in owner_section.splitlines():
    if line.startswith("| `AUTH_CON_"):
        owner_actions.extend(re.findall(r"`([^`]+)`", line.split("|")[3]))
assert len(owner_actions) == len(set(owner_actions)) == 23
assert set(owner_actions) == ws_con_actions
PY
)
```

## Required reviewers

Senior engineering, QA/test, security/auth, product/ops, architecture, docs,
and reuse/dedup. CI integrity and test-delta are N/A because this chunk changes
only planning Markdown and no CI/tests.

## Human review focus

Review unresolved D1/D4/D7/D8/D10/D11/D12, confirm accepted D3/D5/D6/D9 and
approved D2, and assess D2's unresolved legacy-row handling rule, exact
authorization dependencies and role candidates, artifact boundary, cross-
initiative gates, and whether every runtime chunk is independently reviewable.

## Stop conditions

Stop after presenting the reviewed plan. Do not start `WS-CON-001-01` without
explicit human approval.
