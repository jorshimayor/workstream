from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import inspect, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex

from app.core.config import get_settings
from app.db import models as db_models
from app.db import session as db_session
from app.db.base import Base
from app.main import create_app
from app.modules.checkers.models import CheckerResult, CheckerRun
from app.modules.checkers.runner import canonical_artifact_manifest_hash
from app.modules.checkers.schemas import CheckerRoutingRecommendation
from app.modules.tasks.models import AuditEvent, Submission
from tests.test_tasks import (
    auth_headers,
    complete_guide_payload,
    complete_submission_payload,
    create_active_project,
    create_started_task,
    seed_worker_profile,
    set_dev_actor,
)


@pytest.fixture
def checker_database_env(
    monkeypatch: pytest.MonkeyPatch,
    postgres_database_url: str,
    migration_lock,
) -> Iterator[str]:
    monkeypatch.setenv("WORKSTREAM_DATABASE_URL", postgres_database_url)
    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    get_settings.cache_clear()
    asyncio.run(db_session.dispose_engine())

    config = alembic_config()
    with migration_lock():
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        yield postgres_database_url
        command.downgrade(config, "base")
    asyncio.run(db_session.dispose_engine())
    get_settings.cache_clear()


@pytest.fixture
async def checker_client(checker_database_env: str) -> AsyncIterator[AsyncClient]:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


def alembic_config() -> Config:
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    return config


def test_checker_models_are_registered_for_alembic_metadata() -> None:
    expected_tables = {"checker_runs", "checker_results"}

    assert expected_tables.issubset(Base.metadata.tables)
    assert db_models.CheckerRun is CheckerRun
    assert db_models.CheckerResult is CheckerResult


def test_checker_routing_recommendation_schema_uses_checker_retry_token() -> None:
    adapter = TypeAdapter(CheckerRoutingRecommendation)

    assert adapter.validate_python("checker_retry") == "checker_retry"
    with pytest.raises(ValidationError):
        adapter.validate_python("operator" + "_retry")


async def test_checker_migration_creates_expected_tables(checker_database_env: str) -> None:
    async with db_session.get_engine().connect() as connection:
        table_names = await connection.run_sync(
            lambda sync_connection: set(inspect(sync_connection).get_table_names())
        )

    assert {"checker_runs", "checker_results"}.issubset(table_names)


def test_checker_run_current_partial_unique_index_metadata_compiles() -> None:
    index = next(
        index
        for index in CheckerRun.__table__.indexes
        if index.name == "uq_checker_runs_current_per_submission"
    )

    postgres_compiled = str(CreateIndex(index).compile(dialect=postgresql.dialect()))

    assert "is_current_for_submission = true" in postgres_compiled


def test_artifact_manifest_hash_is_stable_and_rejects_duplicates() -> None:
    first = [
        {"artifact": "b.txt", "hash": "sha256:b", "size_bytes": 2, "notes": None},
        {"hash": "sha256:a", "artifact": "a.txt", "notes": "main", "size_bytes": 1},
    ]
    second = [
        {"size_bytes": 1, "notes": "main", "artifact": "a.txt", "hash": "sha256:a"},
        {"notes": None, "artifact": "b.txt", "hash": "sha256:b", "size_bytes": 2},
    ]

    assert canonical_artifact_manifest_hash(first) == canonical_artifact_manifest_hash(second)

    with pytest.raises(ValueError, match="duplicate artifact"):
        canonical_artifact_manifest_hash(
            [
                {"artifact": "a.txt", "hash": "sha256:a"},
                {"artifact": "a.txt", "hash": "sha256:b"},
            ]
        )


async def test_pre_submit_check_returns_feedback_without_durable_run(
    checker_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = await create_active_project(checker_client)
    started_task = await create_started_task(checker_client, project["id"], monkeypatch)
    payload = complete_submission_payload()
    payload["artifact_hash_manifest"].append(
        {
            "artifact": "answer.md",
            "hash": "sha256:duplicate",
            "size_bytes": 129,
            "notes": "duplicate",
        }
    )

    response = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submission-precheck",
        headers=auth_headers(),
        json={"submission": payload},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["authoritative"] is False
    assert body["status"] == "failed"
    assert body["eligible_to_submit"] is False
    assert any(
        result["checker_name"] == "check_artifact_manifest_integrity"
        and result["would_block_if_submitted"] is True
        for result in body["results"]
    )

    async with db_session.get_session_factory()() as session:
        rows = (await session.execute(CheckerRun.__table__.select())).all()
    assert rows == []


async def test_locked_submission_checker_run_persists_results_and_allows_review(
    checker_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = await create_active_project(checker_client)
    started_task = await create_started_task(checker_client, project["id"], monkeypatch)
    created = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submissions",
        headers=auth_headers(),
        json=complete_submission_payload(),
    )
    assert created.status_code == 201, created.text

    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    locked = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/lock",
        headers=auth_headers(),
    )
    assert locked.status_code == 200, locked.text

    run = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "manual checker dry run"},
    )

    assert run.status_code == 200, run.text
    body = run.json()
    assert body["status"] == "completed"
    assert body["trigger_source"] == "manual_checker_trigger"
    assert body["routing_recommendation"] == "allow_review"
    assert body["outcome_source"] == "none"
    assert body["submission_version"] == 1
    assert body["locked_checker_policy_version"] == "v1"
    assert body["artifact_manifest_hash"].startswith("sha256:")
    assert body["audit_event_id"]
    assert body["passed_count"] >= 4
    assert body["blocking_count"] == 0
    assert {
        "check_submission_packet",
        "check_policy_context_present",
        "check_artifact_manifest_integrity",
        "check_evidence_references_present",
    }.issubset({result["checker_name"] for result in body["results"]})

    listed = await checker_client.get(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
    )
    assert listed.status_code == 200, listed.text
    assert [item["id"] for item in listed.json()] == [body["id"]]

    async with db_session.get_session_factory()() as session:
        audit = await session.get(AuditEvent, body["audit_event_id"])
    assert audit is not None
    assert audit.event_type == "checker_run_triggered"
    assert audit.entity_id == created.json()["id"]
    assert audit.reason == "manual checker dry run"
    assert audit.event_payload["submission_version"] == 1


async def test_checker_run_retry_supersedes_previous_current_run(
    checker_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = await create_active_project(checker_client)
    started_task = await create_started_task(checker_client, project["id"], monkeypatch)
    created = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submissions",
        headers=auth_headers(),
        json=complete_submission_payload(),
    )
    assert created.status_code == 201, created.text
    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    locked = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/lock",
        headers=auth_headers(),
    )
    assert locked.status_code == 200, locked.text
    first = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "first run"},
    )
    assert first.status_code == 200, first.text

    second = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "retry run"},
    )

    assert second.status_code == 200, second.text
    assert second.json()["attempt_number"] == 2
    assert second.json()["supersedes_checker_run_id"] == first.json()["id"]
    listed = await checker_client.get(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
    )
    assert listed.status_code == 200, listed.text
    assert [item["attempt_number"] for item in listed.json()] == [1, 2]
    assert listed.json()[0]["is_current_for_submission"] is False
    assert listed.json()[1]["is_current_for_submission"] is True


async def test_checker_run_with_duplicate_artifact_persists_needs_revision_result(
    checker_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = await create_active_project(checker_client)
    started_task = await create_started_task(checker_client, project["id"], monkeypatch)
    payload = complete_submission_payload()
    payload["artifact_hash_manifest"].append(
        {
            "artifact": "answer.md",
            "hash": "sha256:duplicate",
            "size_bytes": 129,
            "notes": "duplicate",
        }
    )
    created = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submissions",
        headers=auth_headers(),
        json=payload,
    )
    assert created.status_code == 201, created.text

    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    locked = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/lock",
        headers=auth_headers(),
    )
    assert locked.status_code == 200, locked.text

    run = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "manual checker dry run"},
    )

    assert run.status_code == 200, run.text
    body = run.json()
    assert body["routing_recommendation"] == "needs_revision"
    assert body["outcome_source"] == "auto_checker"
    assert body["artifact_manifest_hash"] == "invalid:artifact_manifest"
    duplicate_result = next(
        result
        for result in body["results"]
        if result["checker_name"] == "check_artifact_manifest_integrity"
    )
    assert duplicate_result["status"] == "failed"
    assert duplicate_result["blocks_review"] is True
    assert "duplicate artifact" in duplicate_result["worker_message"]


async def test_worker_can_read_only_worker_visible_checker_result_fields(
    checker_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = await create_active_project(checker_client)
    started_task = await create_started_task(checker_client, project["id"], monkeypatch)
    created = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submissions",
        headers=auth_headers(),
        json=complete_submission_payload(),
    )
    assert created.status_code == 201, created.text
    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    locked = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/lock",
        headers=auth_headers(),
    )
    assert locked.status_code == 200, locked.text
    run = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "manual checker dry run"},
    )
    assert run.status_code == 200, run.text

    set_dev_actor(monkeypatch, roles="worker", subject="worker-one")
    read = await checker_client.get(
        f"/api/v1/checker-runs/{run.json()['id']}",
        headers=auth_headers(),
    )

    assert read.status_code == 200, read.text
    body = read.json()
    assert body["failure_message"] is None
    assert body["triggered_by"] is None
    assert body["triggered_by_subject"] is None
    assert body["triggered_by_issuer"] is None
    assert body["trigger_auth_source"] is None
    assert body["trigger_reason"] is None
    assert body["audit_event_id"] is None
    assert body["locked_guide_version"] is None
    assert body["locked_checker_policy_version"] is None
    assert body["locked_review_policy_version"] is None
    assert body["locked_revision_policy_version"] is None
    assert body["locked_payment_policy_version"] is None
    assert body["package_hash"] is None
    assert body["artifact_hash_manifest"] == []
    assert body["artifact_manifest_hash"] is None
    assert body["results"]
    assert all(result["message"] is None for result in body["results"])
    assert all(result["metadata"] == {} for result in body["results"])
    assert all(result["worker_visible"] is True for result in body["results"])


async def test_worker_cannot_see_hidden_checker_results(
    checker_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = await create_active_project(checker_client)
    started_task = await create_started_task(checker_client, project["id"], monkeypatch)
    created = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submissions",
        headers=auth_headers(),
        json=complete_submission_payload(),
    )
    assert created.status_code == 201, created.text
    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    locked = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/lock",
        headers=auth_headers(),
    )
    assert locked.status_code == 200, locked.text
    run = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "manual checker dry run"},
    )
    assert run.status_code == 200, run.text

    async with db_session.get_session_factory()() as session:
        session.add(
            CheckerResult(
                id="hidden-result",
                checker_run_id=run.json()["id"],
                task_id=started_task["id"],
                submission_id=created.json()["id"],
                checker_name="internal_hidden_checker",
                status="failed",
                severity="high",
                blocks_review=True,
                message="internal stack and private path",
                worker_message=None,
                worker_suggested_fix=None,
                worker_evidence_refs=[],
                worker_visible=False,
                metadata_json={"private_path": "local://private/hidden"},
            )
        )
        await session.commit()

    manager_read = await checker_client.get(
        f"/api/v1/checker-runs/{run.json()['id']}",
        headers=auth_headers(),
    )
    assert manager_read.status_code == 200, manager_read.text
    assert "internal_hidden_checker" in {
        result["checker_name"] for result in manager_read.json()["results"]
    }

    set_dev_actor(monkeypatch, roles="worker", subject="worker-one")
    worker_read = await checker_client.get(
        f"/api/v1/checker-runs/{run.json()['id']}",
        headers=auth_headers(),
    )
    assert worker_read.status_code == 200, worker_read.text
    worker_names = {result["checker_name"] for result in worker_read.json()["results"]}
    assert "internal_hidden_checker" not in worker_names


async def test_checker_endpoints_reject_unassigned_worker_and_fake_result_payloads(
    checker_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = await create_active_project(checker_client)
    started_task = await create_started_task(checker_client, project["id"], monkeypatch)
    payload = complete_submission_payload()
    payload["status"] = "completed"
    payload["routing_recommendation"] = "allow_review"
    payload["results"] = [{"checker_name": "fake", "status": "passed"}]

    fake_precheck = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submission-precheck",
        headers=auth_headers(),
        json={"submission": payload},
    )
    assert fake_precheck.status_code == 422

    created = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submissions",
        headers=auth_headers(),
        json=complete_submission_payload(),
    )
    assert created.status_code == 201, created.text
    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    locked = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/lock",
        headers=auth_headers(),
    )
    assert locked.status_code == 200, locked.text
    fake_run = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={
            "trigger_reason": "manual checker dry run",
            "status": "completed",
            "routing_recommendation": "allow_review",
            "results": [{"checker_name": "fake", "status": "passed"}],
        },
    )
    assert fake_run.status_code == 422
    blank_reason = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "   "},
    )
    assert blank_reason.status_code == 422

    set_dev_actor(monkeypatch, roles="worker", subject="worker-one")
    worker_run = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "worker tries to trigger"},
    )
    assert worker_run.status_code == 403

    await seed_worker_profile("worker-two")
    set_dev_actor(monkeypatch, roles="worker", subject="worker-two")
    denied = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submission-precheck",
        headers=auth_headers(),
        json={"submission": complete_submission_payload()},
    )
    assert denied.status_code == 404

    set_dev_actor(monkeypatch, roles="auditor", subject="auditor-subject")
    no_role_existing = await checker_client.get(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
    )
    no_role_missing = await checker_client.get(
        "/api/v1/submissions/00000000-0000-0000-0000-000000000000/checker-runs",
        headers=auth_headers(),
    )
    assert no_role_existing.status_code == 403
    assert no_role_missing.status_code == 403

    async with db_session.get_session_factory()() as session:
        rows = (await session.execute(select(CheckerRun))).scalars().all()
    assert rows == []


async def test_stale_locked_submission_cannot_receive_checker_run(
    checker_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = await create_active_project(checker_client)
    started_task = await create_started_task(checker_client, project["id"], monkeypatch)
    first = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submissions",
        headers=auth_headers(),
        json=complete_submission_payload(),
    )
    assert first.status_code == 201, first.text
    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    locked_first = await checker_client.post(
        f"/api/v1/submissions/{first.json()['id']}/lock",
        headers=auth_headers(),
    )
    assert locked_first.status_code == 200, locked_first.text
    set_dev_actor(monkeypatch, roles="worker", subject="worker-one")
    second_payload = complete_submission_payload("sha256:package-v2")
    second_payload["artifact_hash_manifest"][0]["hash"] = "sha256:answer-v2"
    second = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submissions",
        headers=auth_headers(),
        json=second_payload,
    )
    assert second.status_code == 201, second.text

    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    stale_run = await checker_client.post(
        f"/api/v1/submissions/{first.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "stale run"},
    )

    assert stale_run.status_code == 409
    assert "latest submission" in stale_run.json()["detail"]

    async with db_session.get_session_factory()() as session:
        submissions = (
            await session.execute(
                select(Submission).where(Submission.id == first.json()["id"])
            )
        ).scalars().all()
    assert submissions[0].version == 1


async def test_unknown_policy_checker_blocks_durable_run_without_fake_results(
    checker_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_response = await checker_client.post(
        "/api/v1/projects",
        headers=auth_headers(),
        json={
            "name": "Unknown Checker Project",
            "slug": "unknown-checker-project",
            "base_amount": "25.00",
            "currency": "USD",
        },
    )
    assert project_response.status_code == 201, project_response.text
    project = project_response.json()
    guide_payload = complete_guide_payload()
    guide_payload["checker_policy"]["required_checkers"] = ["check_missing_registered_checker"]
    guide_response = await checker_client.post(
        f"/api/v1/projects/{project['id']}/guides",
        headers=auth_headers(),
        json=guide_payload,
    )
    assert guide_response.status_code == 201, guide_response.text
    activation_response = await checker_client.post(
        f"/api/v1/projects/{project['id']}/guides/{guide_response.json()['id']}/activate",
        headers=auth_headers(),
    )
    assert activation_response.status_code == 200, activation_response.text
    started_task = await create_started_task(checker_client, project["id"], monkeypatch)
    created = await checker_client.post(
        f"/api/v1/tasks/{started_task['id']}/submissions",
        headers=auth_headers(),
        json=complete_submission_payload(),
    )
    assert created.status_code == 201, created.text
    set_dev_actor(monkeypatch, roles="project_manager", subject="project-manager-subject")
    locked = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/lock",
        headers=auth_headers(),
    )
    assert locked.status_code == 200, locked.text

    run = await checker_client.post(
        f"/api/v1/submissions/{created.json()['id']}/checker-runs",
        headers=auth_headers(),
        json={"trigger_reason": "manual checker dry run"},
    )

    assert run.status_code == 422
    assert "unregistered checker policy names" in run.json()["detail"]

    async with db_session.get_session_factory()() as session:
        rows = (await session.execute(CheckerRun.__table__.select())).all()
    assert rows == []
