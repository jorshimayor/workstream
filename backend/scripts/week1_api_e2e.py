"""Run a real HTTP Week 1 API flow against Postgres and local Flow tokens."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import os
import socket
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import httpx
from alembic import command
from alembic.config import Config

DEFAULT_FLOW_ISSUER = "https://auth.flow.local/e2e"
DEFAULT_FLOW_AUDIENCE = "workstream-api"


def base64url_json(payload: dict) -> str:
    """Encode a JSON payload as an unpadded base64url segment.

    Args:
        payload: JSON-serializable payload.

    Returns:
        Encoded JWT segment.
    """
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def base64url_bytes(payload: bytes) -> str:
    """Encode bytes as an unpadded base64url segment.

    Args:
        payload: Raw bytes to encode.

    Returns:
        Encoded JWT segment.
    """
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode()


def flow_settings(env: dict[str, str]) -> tuple[str, str, str]:
    """Resolve local Flow settings from the runtime environment.

    Args:
        env: Runtime environment used by the API server and client.

    Returns:
        Issuer, audience, and HMAC secret used for local Flow tokens.
    """
    return (
        env.get("WORKSTREAM_E2E_FLOW_ISSUER", DEFAULT_FLOW_ISSUER),
        env.get("WORKSTREAM_E2E_FLOW_AUDIENCE", DEFAULT_FLOW_AUDIENCE),
        env.get("WORKSTREAM_E2E_FLOW_SECRET", f"local-flow-e2e-{uuid4().hex}"),
    )


def issue_flow_token(
    subject: str,
    roles: list[str],
    *,
    issuer: str,
    audience: str,
    secret: str,
) -> str:
    """Issue a local Flow-compatible signed token for one QA actor.

    Args:
        subject: External Flow subject.
        roles: Workstream roles granted by Flow for this actor.
        issuer: Flow issuer claim.
        audience: Flow audience claim.
        secret: HMAC secret shared with the local Flow verifier.

    Returns:
        HMAC-signed bearer token consumed by ``FlowAuthVerifier``.
    """
    now = datetime.now(UTC)
    header = base64url_json({"alg": "HS256", "typ": "JWT"})
    payload = base64url_json(
        {
            "iss": issuer,
            "aud": audience,
            "sub": subject,
            "email": f"{subject}@flow.local",
            "name": subject.replace("-", " ").title(),
            "roles": roles,
            "iat": int(now.timestamp()),
            "nbf": int((now - timedelta(seconds=5)).timestamp()),
            "exp": int((now + timedelta(minutes=30)).timestamp()),
        }
    )
    signed_content = f"{header}.{payload}".encode()
    signature = hmac.new(secret.encode(), signed_content, hashlib.sha256).digest()
    return f"{header}.{payload}.{base64url_bytes(signature)}"


def auth_headers(token: str) -> dict[str, str]:
    """Build a bearer authorization header.

    Args:
        token: Flow bearer token.

    Returns:
        HTTP authorization header.
    """
    return {"Authorization": f"Bearer {token}"}


def project_root() -> Path:
    """Return the backend project root.

    Returns:
        Absolute backend project path.
    """
    return Path(__file__).resolve().parents[1]


def alembic_config() -> Config:
    """Create Alembic configuration for the backend project.

    Returns:
        Alembic configuration pointing at the local backend migration folder.
    """
    root = project_root()
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    return config


def find_free_port() -> int:
    """Find an available localhost TCP port.

    Returns:
        Available port number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def api_environment() -> dict[str, str]:
    """Build environment variables for the real API server.

    Returns:
        Environment configured for local Flow auth and Postgres.
    """
    env = os.environ.copy()
    env.setdefault(
        "WORKSTREAM_DATABASE_URL",
        "postgresql+asyncpg://workstream:workstream@localhost:5433/workstream",
    )
    flow_issuer, flow_audience, flow_secret = flow_settings(env)
    env["WORKSTREAM_E2E_FLOW_SECRET"] = flow_secret
    env["WORKSTREAM_AUTH_PROVIDER"] = "flow"
    env["WORKSTREAM_ENVIRONMENT"] = "local"
    env["WORKSTREAM_FLOW_AUTH_ISSUER"] = flow_issuer
    env["WORKSTREAM_FLOW_AUTH_AUDIENCE"] = flow_audience
    env["WORKSTREAM_FLOW_AUTH_LOCAL_HMAC_SECRET"] = flow_secret
    env["WORKSTREAM_ENABLE_DEMO_ROUTES"] = "true"
    env["PYTHONPATH"] = str(project_root())
    return env


def start_api_server(port: int, env: dict[str, str]) -> tuple[subprocess.Popen, Path]:
    """Start a real uvicorn server process.

    Args:
        port: Localhost port for the server.
        env: Environment variables for the server process.

    Returns:
        Server process and log path.
    """
    log_path = project_root() / ".week1_api_e2e_server.log"
    log_file = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=project_root(),
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_file.close()
    return process, log_path


async def wait_for_health(base_url: str, process: subprocess.Popen, log_path: Path) -> None:
    """Wait until the real API server responds to health checks.

    Args:
        base_url: API server base URL.
        process: Uvicorn subprocess.
        log_path: Server log path used for diagnostics.

    Raises:
        RuntimeError: If the server exits or does not become healthy.
    """
    deadline = time.monotonic() + 20
    async with httpx.AsyncClient(base_url=base_url, timeout=5) as client:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"API server exited early:\n{log_path.read_text()}")
            try:
                response = await client.get("/api/v1/health")
                if response.status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.25)
    raise RuntimeError(f"API server did not become healthy:\n{log_path.read_text()}")


async def request_json(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    token: str | None = None,
    payload: dict | None = None,
    expected_status: int = 200,
) -> dict | list:
    """Call one API endpoint and assert its status.

    Args:
        client: Real HTTP client.
        method: HTTP method.
        path: API path.
        token: Optional Flow bearer token.
        payload: Optional JSON payload.
        expected_status: Expected HTTP status code.

    Returns:
        Parsed JSON response body.

    Raises:
        AssertionError: If the response status does not match.
    """
    response = await client.request(
        method,
        path,
        headers={} if token is None else auth_headers(token),
        json=payload,
    )
    if response.status_code != expected_status:
        try:
            body = response.json()
        except ValueError:
            body = response.text
        raise AssertionError(
            f"{method} {path} expected {expected_status}, got {response.status_code}: {body}"
        )
    try:
        body = response.json()
    except ValueError as exc:
        raise AssertionError(
            f"{method} {path} returned non-JSON response: {response.text!r}"
        ) from exc
    if not isinstance(body, dict | list):
        raise AssertionError(f"{method} {path} returned non-JSON payload: {body!r}")
    print(f"PASS {method} {path} -> {response.status_code}")
    return body


def guide_payload(run_id: str) -> dict:
    """Build a complete project guide payload.

    Args:
        run_id: Unique QA run id.

    Returns:
        Project guide payload.
    """
    return {
        "version": "v1",
        "content_markdown": f"# Real API Guide {run_id}",
        "required_task_fields": [
            "title",
            "description",
            "acceptance_criteria",
            "required_evidence",
        ],
        "required_submission_fields": ["summary", "evidence", "worker_attestation"],
        "task_instructions": "Complete the real API task.",
        "output_requirements": "Submit artifact manifest and evidence.",
        "acceptance_criteria": "Submission packet is complete.",
        "rejection_criteria": "Evidence is missing.",
        "reviewer_rubric": "Review packet completeness.",
        "forbidden_actions": "No credentials or private source data.",
        "required_skills": ["stem"],
        "difficulty_scale": {"medium": 2},
        "estimated_time_policy": {"default_minutes": 45},
        "common_rejection_reasons": ["missing evidence"],
        "evidence_policy": {"required": ["log"]},
        "unacceptable_work_policy": "Copied or unverifiable work.",
        "change_summary": "Initial real API guide",
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
    }


async def exercise_week1_api(base_url: str, env: dict[str, str]) -> None:
    """Run the real Project -> Task -> Submission Week 1 API flow.

    Args:
        base_url: Real API server base URL.
        env: Runtime environment shared by the API server and token issuer.
    """
    flow_issuer, flow_audience, flow_secret = flow_settings(env)
    run_id = uuid4().hex[:8]
    manager_token = issue_flow_token(
        f"real-api-project-manager-{run_id}",
        ["project_manager"],
        issuer=flow_issuer,
        audience=flow_audience,
        secret=flow_secret,
    )
    worker_subject = f"real-api-worker-{run_id}"
    worker_token = issue_flow_token(
        worker_subject,
        ["worker"],
        issuer=flow_issuer,
        audience=flow_audience,
        secret=flow_secret,
    )
    reviewer_token = issue_flow_token(
        f"real-api-reviewer-{run_id}",
        ["reviewer"],
        issuer=flow_issuer,
        audience=flow_audience,
        secret=flow_secret,
    )
    invalid_token = (
        issue_flow_token(
            f"real-api-invalid-{run_id}",
            ["worker"],
            issuer=flow_issuer,
            audience=flow_audience,
            secret=flow_secret,
        )[:-8]
        + "tampered"
    )

    async with httpx.AsyncClient(base_url=base_url, timeout=10) as client:
        await request_json(client, "GET", "/health")
        await request_json(client, "GET", "/api/v1/health")
        await request_json(client, "GET", "/api/v1/auth/me", invalid_token, expected_status=401)
        manager = await request_json(client, "GET", "/api/v1/auth/me", manager_token)
        assert manager["auth_source"] == "flow"
        assert manager["is_dev_auth"] is False
        assert manager["roles"] == ["project_manager"]

        project = await request_json(
            client,
            "POST",
            "/api/v1/projects",
            manager_token,
            {
                "name": f"Week 1 Real API {run_id}",
                "slug": f"week1-real-api-{run_id}",
                "description": "Real Week 1 API lifecycle QA",
                "base_amount": "25.00",
                "currency": "USD",
            },
            201,
        )
        await request_json(client, "GET", f"/api/v1/projects/{project['id']}", manager_token)

        guide = await request_json(
            client,
            "POST",
            f"/api/v1/projects/{project['id']}/guides",
            manager_token,
            guide_payload(run_id),
            201,
        )
        patched_guide = await request_json(
            client,
            "PATCH",
            f"/api/v1/projects/{project['id']}/guides/{guide['id']}",
            manager_token,
            {"change_summary": "Patched before activation through real API"},
        )
        assert patched_guide["change_summary"] == "Patched before activation through real API"
        active = await request_json(
            client,
            "POST",
            f"/api/v1/projects/{project['id']}/guides/{guide['id']}/activate",
            manager_token,
        )
        assert active["guide"]["version"] == "v1"
        await request_json(client, "GET", f"/api/v1/projects/{project['id']}/active-guide", manager_token)

        task = await request_json(
            client,
            "POST",
            f"/api/v1/projects/{project['id']}/tasks",
            manager_token,
            {
                "title": "Real API task",
                "description": "Exercise the full Week 1 API lifecycle over HTTP.",
                "task_type": "evaluation",
                "difficulty": "medium",
                "skill_tags": ["stem", "proofs"],
                "estimated_time_minutes": 45,
                "source_type": "manual",
                "source_ref": f"real-api-{run_id}",
                "source_payload_hash": f"sha256:source-{run_id}",
                "acceptance_criteria": "Submission packet is complete.",
                "rejection_criteria": "Evidence is missing.",
                "required_files": ["answer.md"],
                "required_evidence": ["checker log"],
            },
            201,
        )
        await request_json(client, "GET", f"/api/v1/tasks/{task['id']}", manager_token)
        await request_json(
            client,
            "POST",
            f"/api/v1/tasks/{task['id']}/screen",
            manager_token,
            {"reason": "real API screening passed"},
        )
        await request_json(
            client,
            "POST",
            f"/api/v1/tasks/{task['id']}/release",
            manager_token,
            {"reason": "real API release"},
        )

        worker = await request_json(client, "GET", "/api/v1/auth/me", worker_token)
        assert worker["roles"] == ["worker"]
        worker_profile = await request_json(
            client,
            "POST",
            "/api/v1/demo/worker-profile",
            worker_token,
            {"skill_tags": ["stem", "proofs"]},
            201,
        )
        assert worker_profile["external_subject"] == worker_subject
        assert worker_profile["external_issuer"] == flow_issuer
        assert worker_profile["status"] == "active"
        assert set(worker_profile["skill_tags"]) == {"stem", "proofs"}
        await request_json(client, "GET", f"/api/v1/tasks/{task['id']}", worker_token)
        claim = await request_json(
            client,
            "POST",
            f"/api/v1/tasks/{task['id']}/claim",
            worker_token,
            {"reason": "real worker claim"},
        )
        await request_json(
            client,
            "POST",
            f"/api/v1/tasks/{task['id']}/start",
            worker_token,
            {"reason": "real worker start"},
        )
        submission = await request_json(
            client,
            "POST",
            f"/api/v1/tasks/{task['id']}/submissions",
            worker_token,
            {
                "summary": "Real API packet completed.",
                "package_uri": f"local://packages/token=build-{run_id}.tar.zst",
                "package_hash": f"sha256:package-{run_id}",
                "artifact_hash_manifest": [
                    {
                        "artifact": "answer.md",
                        "hash": f"sha256:answer-{run_id}",
                        "size_bytes": 128,
                        "notes": "real API artifact",
                    }
                ],
                "worker_attestation": "I confirm this packet follows the locked guide.",
                "evidence_items": [
                    {
                        "type": "log",
                        "label": "real API evidence",
                        "uri": f"s3://workstream-e2e/reports/user@team-{run_id}.log",
                        "hash": f"sha256:evidence-{run_id}",
                        "size_bytes": 256,
                        "metadata": {"command": "week1_api_e2e"},
                    }
                ],
            },
            201,
        )
        assert submission["locked_guide_version"] == "v1"
        await request_json(client, "GET", f"/api/v1/tasks/{task['id']}/submissions", worker_token)
        await request_json(client, "GET", f"/api/v1/submissions/{submission['id']}", worker_token)
        await request_json(
            client,
            "POST",
            f"/api/v1/submissions/{submission['id']}/lock",
            worker_token,
            expected_status=403,
        )
        locked = await request_json(
            client,
            "POST",
            f"/api/v1/submissions/{submission['id']}/lock",
            manager_token,
        )
        assert locked["locked_at"] is not None
        audit_events = await request_json(
            client,
            "GET",
            f"/api/v1/tasks/{task['id']}/audit-events",
            manager_token,
        )
        assert len(audit_events) >= 6
        await request_json(
            client,
            "GET",
            f"/api/v1/tasks/{task['id']}",
            reviewer_token,
            expected_status=403,
        )

    print("Week 1 real API e2e passed")
    print(f"project_id={project['id']}")
    print(f"guide_id={guide['id']}")
    print(f"task_id={task['id']}")
    print(f"assignment_id={claim['assignment']['id']}")
    print(f"submission_id={submission['id']}")
    print(f"submission_locked_at={locked['locked_at']}")


async def main(env: dict[str, str]) -> None:
    """Start the API server and exercise every Week 1 API.

    Args:
        env: Environment variables for the API server.
    """
    from app.db import session as db_session

    await db_session.dispose_engine()

    port = find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    process, log_path = start_api_server(port, env)
    try:
        await wait_for_health(base_url, process, log_path)
        await exercise_week1_api(base_url, env)
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


if __name__ == "__main__":
    api_env = api_environment()
    os.environ.update(api_env)
    command.upgrade(alembic_config(), "head")
    asyncio.run(main(api_env))
