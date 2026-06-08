"""Run the Week 1 backend lifecycle dry run against a configured database."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient

from app.adapters.auth.dev import actor_id_from_external_identity
from app.core.config import get_settings
from app.db import session as db_session
from app.main import create_app
from app.modules.tasks.models import WorkerProfile

TOKEN = "week1-dry-run-token"
ISSUER = "flow-dry-run"


def set_actor(*, subject: str, roles: str) -> None:
    """Set dev-auth actor environment for the next in-process API request.

    Args:
        subject: External Flow subject represented by the dev verifier.
        roles: Comma-separated Workstream roles for the actor.
    """
    os.environ["WORKSTREAM_AUTH_PROVIDER"] = "dev"
    os.environ["WORKSTREAM_ENVIRONMENT"] = "local"
    os.environ["WORKSTREAM_DEV_AUTH_TOKEN"] = TOKEN
    os.environ["WORKSTREAM_DEV_AUTH_SUBJECT"] = subject
    os.environ["WORKSTREAM_DEV_AUTH_ISSUER"] = ISSUER
    os.environ["WORKSTREAM_DEV_AUTH_EMAIL"] = f"{subject}@flow.local"
    os.environ["WORKSTREAM_DEV_AUTH_DISPLAY_NAME"] = subject.replace("-", " ").title()
    os.environ["WORKSTREAM_DEV_AUTH_ROLES"] = roles
    get_settings.cache_clear()


def auth_headers() -> dict[str, str]:
    """Build the bearer token header used by the dev verifier.

    Returns:
        Authorization header for dry-run requests.
    """
    return {"Authorization": f"Bearer {TOKEN}"}


def alembic_config() -> Config:
    """Create Alembic configuration for the backend project.

    Returns:
        Alembic configuration pointing at the local backend migration folder.
    """
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    return config


async def seed_worker_profile(subject: str) -> str:
    """Create the active worker profile required before claim.

    Args:
        subject: External Flow subject for the worker.

    Returns:
        Stable Workstream actor id for the worker.
    """
    worker_actor_id = actor_id_from_external_identity(ISSUER, subject)
    async with db_session.get_session_factory()() as session:
        session.add(
            WorkerProfile(
                id=str(uuid4()),
                actor_id=worker_actor_id,
                external_subject=subject,
                external_issuer=ISSUER,
                display_name=subject.replace("-", " ").title(),
                email=f"{subject}@flow.local",
                skill_tags=["stem", "proofs"],
                status="active",
            )
        )
        await session.commit()
    return worker_actor_id


async def post_ok(client: AsyncClient, url: str, payload: dict | None = None) -> dict:
    """POST JSON and return a successful response body.

    Args:
        client: In-process HTTP client.
        url: API route to call.
        payload: Optional JSON body.

    Returns:
        Parsed JSON response.
    """
    response = await client.post(url, headers=auth_headers(), json=payload)
    response.raise_for_status()
    return response.json()


async def main() -> None:
    """Execute Project -> Guide -> Task -> Submit -> Lock dry run."""
    await db_session.dispose_engine()

    run_id = uuid4().hex[:8]
    worker_subject = f"dry-run-worker-{run_id}"
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://week1-dry-run",
    ) as client:
        project = await post_ok(
            client,
            "/api/v1/projects",
            {
                "name": f"Week 1 Dry Run {run_id}",
                "slug": f"week1-dry-run-{run_id}",
                "description": "Week 1 backend closure dry run",
                "base_amount": "25.00",
                "currency": "USD",
            },
        )
        guide = await post_ok(
            client,
            f"/api/v1/projects/{project['id']}/guides",
            {
                "version": "v1",
                "content_markdown": "# Week 1 Dry Run Guide",
                "required_task_fields": [
                    "title",
                    "description",
                    "acceptance_criteria",
                    "required_evidence",
                ],
                "required_submission_fields": ["summary", "evidence", "worker_attestation"],
                "task_instructions": "Complete the dry-run task.",
                "output_requirements": "Submit an artifact manifest and evidence item.",
                "acceptance_criteria": "The packet is complete.",
                "rejection_criteria": "The packet is missing evidence.",
                "reviewer_rubric": "Review packet completeness.",
                "forbidden_actions": "No credentials or private source data.",
                "required_skills": ["stem"],
                "difficulty_scale": {"medium": 2},
                "estimated_time_policy": {"default_minutes": 45},
                "common_rejection_reasons": ["missing evidence"],
                "evidence_policy": {"required": ["log"]},
                "unacceptable_work_policy": "Copied or unverifiable work.",
                "change_summary": "Initial dry-run guide",
                "checker_policy": {
                    "required_checkers": ["check_policy_context_present"],
                    "warning_checkers": [],
                    "blocking_severities": ["high"],
                },
                "review_policy": {
                    "requires_second_review": False,
                    "allowed_decisions": ["accept", "needs_revision", "reject"],
                    "minimum_finding_fields": ["issue", "required_fix"],
                    "sla_hours": 24,
                },
                "revision_policy": {
                    "max_revision_rounds": 7,
                    "revision_deadline_hours": 48,
                    "auto_reject_after_limit": True,
                    "allowed_resubmission_states": ["needs_revision"],
                    "reviewer_reassignment_rule": "same reviewer preferred",
                },
                "payment_policy": {
                    "base_amount": "25.00",
                    "currency": "USD",
                    "payout_type": "fixed",
                    "revision_payment_rule": "none",
                    "rejection_payment_rule": "none",
                    "accepted_payment_rule": "pay base amount",
                },
            },
        )
        await post_ok(client, f"/api/v1/projects/{project['id']}/guides/{guide['id']}/activate")
        task = await post_ok(
            client,
            f"/api/v1/projects/{project['id']}/tasks",
            {
                "title": "Week 1 dry-run task",
                "description": "Prove the backend lifecycle through submission.",
                "task_type": "evaluation",
                "difficulty": "medium",
                "skill_tags": ["stem", "proofs"],
                "estimated_time_minutes": 45,
                "source_type": "manual",
                "source_ref": f"dry-run-{run_id}",
                "source_payload_hash": f"sha256:source-{run_id}",
                "acceptance_criteria": "The submission packet is complete.",
                "rejection_criteria": "Evidence is missing.",
                "required_files": ["answer.md"],
                "required_evidence": ["checker log"],
            },
        )
        await post_ok(
            client,
            f"/api/v1/tasks/{task['id']}/screen",
            {"reason": "dry-run screening passed"},
        )
        await post_ok(
            client,
            f"/api/v1/tasks/{task['id']}/release",
            {"reason": "dry-run release decision"},
        )

        await seed_worker_profile(worker_subject)
        set_actor(subject=worker_subject, roles="worker")
        claim = await post_ok(
            client,
            f"/api/v1/tasks/{task['id']}/claim",
            {"reason": "dry-run claim"},
        )
        await post_ok(
            client,
            f"/api/v1/tasks/{task['id']}/start",
            {"reason": "dry-run start"},
        )
        submission = await post_ok(
            client,
            f"/api/v1/tasks/{task['id']}/submissions",
            {
                "summary": "Dry-run packet completed.",
                "package_uri": f"local://dry-run/{run_id}/package.tar.zst",
                "package_hash": f"sha256:package-{run_id}",
                "artifact_hash_manifest": [
                    {
                        "artifact": "answer.md",
                        "hash": f"sha256:answer-{run_id}",
                        "size_bytes": 128,
                        "notes": "dry-run artifact",
                    }
                ],
                "worker_attestation": "I confirm this dry-run packet follows the locked guide.",
                "evidence_items": [
                    {
                        "type": "log",
                        "label": "dry-run evidence",
                        "uri": f"local://dry-run/{run_id}/evidence.log",
                        "hash": f"sha256:evidence-{run_id}",
                        "size_bytes": 256,
                        "metadata": {"command": "week1_dry_run"},
                    }
                ],
            },
        )

        set_actor(subject="dry-run-project-manager", roles="project_manager")
        locked = await post_ok(client, f"/api/v1/submissions/{submission['id']}/lock")

    print("Week 1 dry run passed")
    print(f"project_id={project['id']}")
    print(f"guide_id={guide['id']}")
    print(f"task_id={task['id']}")
    print(f"assignment_id={claim['assignment']['id']}")
    print(f"submission_id={submission['id']}")
    print(f"submission_locked_at={locked['locked_at']}")


if __name__ == "__main__":
    if not os.environ.get("WORKSTREAM_DATABASE_URL"):
        os.environ["WORKSTREAM_DATABASE_URL"] = (
            "postgresql+asyncpg://workstream:workstream@localhost:5433/workstream"
        )
    set_actor(subject="dry-run-project-manager", roles="project_manager")
    command.upgrade(alembic_config(), "head")
    asyncio.run(main())
