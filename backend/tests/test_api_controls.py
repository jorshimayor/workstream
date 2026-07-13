from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from hashlib import sha256
import logging
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response, StreamingResponse
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, Field, SecretStr, field_validator
import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.requests import Request

from app.api.deps.api_controls import (
    enforce_admin_mutation_rate_limit,
    enforce_first_access_rate_limit,
    get_rate_control_service,
)
from app.api.deps.auth import get_auth_verification_result
from app.core.api_controls import ApiErrorResponse, error_response
from app.core.config import Settings
from app.main import create_app
from app.modules.api_controls import service as rate_service_module
from app.modules.api_controls.repository import ApiRateControlRepository, ConsumedCounter
from app.modules.api_controls.service import (
    ADMIN_MUTATION_SCOPE,
    FIRST_ACCESS_SCOPE,
    RateControlDecision,
    RateControlService,
    RateControlUnavailableError,
    rate_key_digest,
)
from app.schemas.auth import AuthVerificationResult, VerifiedIssuerToken


def _assert_uuid(value: str) -> None:
    parsed = UUID(value)
    assert str(parsed) == value
    assert parsed.int != 0
    assert parsed.version in range(1, 9)


def test_error_response_fallback_ids_remain_consistent() -> None:
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})

    response = error_response(
        request,
        status_code=500,
        code="internal_error",
        message="Internal server error",
    )

    correlation_id = response.headers["x-correlation-id"]
    assert response.headers["x-request-id"] == correlation_id
    assert f'"correlation_id":"{correlation_id}"'.encode() in response.body


async def _get(app, path: str = "/health", **kwargs):
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as client:
        return await client.get(path, **kwargs)


async def test_missing_and_supplied_request_context_propagates() -> None:
    app = create_app()
    generated = await _get(app)
    request_id = str(uuid4())
    correlation_id = str(uuid4())
    supplied = await _get(
        app,
        headers={"X-Request-ID": request_id, "X-Correlation-ID": correlation_id},
    )
    request_only = await _get(app, headers={"X-Request-ID": request_id})
    correlation_only = await _get(app, headers={"X-Correlation-ID": correlation_id})

    _assert_uuid(generated.headers["x-request-id"])
    assert generated.headers["x-correlation-id"] == generated.headers["x-request-id"]
    assert supplied.headers["x-request-id"] == request_id
    assert supplied.headers["x-correlation-id"] == correlation_id
    assert request_only.headers["x-request-id"] == request_id
    assert request_only.headers["x-correlation-id"] == request_id
    _assert_uuid(correlation_only.headers["x-request-id"])
    assert correlation_only.headers["x-correlation-id"] == correlation_id


@pytest.mark.parametrize(
    "invalid_id",
    [
        str(uuid4()).upper(),
        str(uuid4()).replace("-", ""),
        "00000000-0000-0000-0000-000000000000",
        "00000000-0000-9000-8000-000000000001",
        f"{uuid4()}, {uuid4()}",
    ],
)
async def test_invalid_request_context_short_circuits_without_reflection(
    invalid_id: str,
) -> None:
    app = create_app()
    called = False

    @app.get("/_test/not-called")
    async def not_called() -> dict[str, bool]:
        nonlocal called
        called = True
        return {"called": True}

    response = await _get(app, "/_test/not-called", headers={"X-Request-ID": invalid_id})

    assert response.status_code == 400
    assert called is False
    assert response.headers["x-request-id"] == response.headers["x-correlation-id"]
    _assert_uuid(response.headers["x-request-id"])
    assert invalid_id not in response.text
    assert response.json() == {
        "detail": "Invalid request identifier",
        "error": {
            "code": "invalid_request",
            "message": "Invalid request identifier",
            "details": {},
            "correlation_id": response.headers["x-correlation-id"],
            "retryable": False,
        },
    }


@pytest.mark.parametrize(
    "headers",
    [
        [(b"x-request-id", str(uuid4()).encode())] * 2,
        [
            (b"x-request-id", str(uuid4()).encode()),
            (b"X-Request-ID", str(uuid4()).encode()),
        ],
        [(b"x-correlation-id", str(uuid4()).encode())] * 2,
        [(b"x-request-id", b"\xff" * 36)],
    ],
)
async def test_duplicate_and_non_ascii_request_context_is_rejected(
    headers: list[tuple[bytes, bytes]],
) -> None:
    response = await _get(create_app(), headers=headers)

    assert response.status_code == 400
    assert response.headers["x-request-id"] == response.headers["x-correlation-id"]
    assert response.json()["error"]["code"] == "invalid_request"


async def test_concurrent_request_context_remains_isolated() -> None:
    app = create_app()
    identifiers = [(str(uuid4()), str(uuid4())) for _ in range(12)]

    async def call(request_id: str, correlation_id: str):
        return await _get(
            app,
            headers={"X-Request-ID": request_id, "X-Correlation-ID": correlation_id},
        )

    responses = await asyncio.gather(*(call(*pair) for pair in identifiers))

    assert [
        (response.headers["x-request-id"], response.headers["x-correlation-id"])
        for response in responses
    ] == identifiers


async def test_response_context_overwrites_ids_and_preserves_headers() -> None:
    app = create_app()
    request_id = str(uuid4())
    correlation_id = str(uuid4())

    @app.get("/_test/headers")
    async def headers() -> Response:
        response = Response(
            "ok",
            headers={
                "X-Request-ID": str(uuid4()),
                "X-Correlation-ID": str(uuid4()),
                "Retry-After": "7",
            },
        )
        response.raw_headers.extend(
            [(b"set-cookie", b"first=1"), (b"set-cookie", b"second=2")]
        )
        return response

    response = await _get(
        app,
        "/_test/headers",
        headers={"X-Request-ID": request_id, "X-Correlation-ID": correlation_id},
    )

    assert response.status_code == 200
    assert response.content == b"ok"
    assert response.headers["content-length"] == "2"
    assert response.headers["retry-after"] == "7"
    assert response.headers.get_list("set-cookie") == ["first=1", "second=2"]
    assert response.headers["x-request-id"] == request_id
    assert response.headers["x-correlation-id"] == correlation_id


async def test_streaming_and_background_responses_keep_context() -> None:
    app = create_app()
    completed: list[str] = []

    @app.get("/_test/stream")
    async def stream(background_tasks: BackgroundTasks) -> StreamingResponse:
        async def content():
            yield b"first"
            yield b"second"

        background_tasks.add_task(completed.append, "done")
        return StreamingResponse(content(), background=background_tasks)

    response = await _get(app, "/_test/stream")

    assert response.status_code == 200
    assert response.content == b"firstsecond"
    _assert_uuid(response.headers["x-request-id"])
    assert response.headers["x-correlation-id"] == response.headers["x-request-id"]
    assert completed == ["done"]


async def test_background_failure_is_bounded_after_response_start(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logger = logging.getLogger("app.core.api_controls")
    # In-process Alembic tests disable existing loggers through fileConfig.
    monkeypatch.setattr(logger, "disabled", False)
    caplog.set_level(logging.ERROR, logger=logger.name)
    app = create_app()

    @app.get("/_test/background-failure")
    async def background_failure(background_tasks: BackgroundTasks) -> dict[str, bool]:
        def fail() -> None:
            raise RuntimeError("token=secret-background-value")

        background_tasks.add_task(fail)
        return {"accepted": True}

    response = await _get(app, "/_test/background-failure")

    assert response.status_code == 200
    assert response.json() == {"accepted": True}
    assert response.headers["x-request-id"]
    assert "request_failed_after_response_start" in caplog.text
    assert "secret-background-value" not in caplog.text


@pytest.mark.parametrize(
    ("status_code", "code", "message", "retryable"),
    [
        (400, "invalid_request", "Invalid request", False),
        (401, "invalid_token", "Invalid bearer token", False),
        (403, "permission_not_granted", "Permission not granted", False),
        (409, "conflict", "Request conflict", False),
        (422, "invalid_request", "Invalid request", False),
        (429, "rate_limit_exceeded", "Rate limit exceeded", True),
        (503, "service_unavailable", "Service unavailable", True),
    ],
)
async def test_http_errors_use_stable_mapping_and_preserve_legacy_detail(
    status_code: int, code: str, message: str, retryable: bool
) -> None:
    app = create_app()

    async def fail() -> None:
        headers = {"Retry-After": "9"} if status_code == 429 else None
        raise HTTPException(status_code=status_code, detail="legacy detail", headers=headers)

    app.add_api_route(f"/_test/error/{status_code}", fail, methods=["GET"])
    response = await _get(app, f"/_test/error/{status_code}")

    assert response.status_code == status_code
    assert response.json()["detail"] == "legacy detail"
    assert response.json()["error"] == {
        "code": code,
        "message": message,
        "details": {},
        "correlation_id": response.headers["x-correlation-id"],
        "retryable": retryable,
    }
    ApiErrorResponse.model_validate(response.json())
    if status_code == 429:
        assert response.headers["retry-after"] == "9"


@pytest.mark.parametrize("debug", [False, True])
async def test_not_found_method_not_allowed_and_unhandled_errors_are_private(
    debug: bool,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logger = logging.getLogger("app.core.api_controls")
    monkeypatch.setattr(logger, "disabled", False)
    caplog.set_level(logging.ERROR, logger=logger.name)
    app = create_app(Settings(debug=debug))

    @app.get("/_test/boom")
    async def boom() -> None:
        raise RuntimeError("token=secret database failure")

    not_found = await _get(app, "/_test/missing")
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as client:
        method_not_allowed = await client.post("/health")
    failed = await _get(app, "/_test/boom")

    for response, status_code, detail, code, message in [
        (not_found, 404, "Not Found", "resource_not_found", "Resource not found"),
        (
            method_not_allowed,
            405,
            "Method Not Allowed",
            "method_not_allowed",
            "Method not allowed",
        ),
        (
            failed,
            500,
            "Internal server error",
            "internal_error",
            "Internal server error",
        ),
    ]:
        assert response.status_code == status_code
        assert response.json() == {
            "detail": detail,
            "error": {
                "code": code,
                "message": message,
                "details": {},
                "correlation_id": response.headers["x-correlation-id"],
                "retryable": False,
            },
        }
        ApiErrorResponse.model_validate(response.json())

    failure_record = next(
        record
        for record in caplog.records
        if record.message == "request_failed_before_response_start"
    )
    assert failure_record.correlation_id == failed.headers["x-correlation-id"]
    assert "secret" not in failed.text
    assert "secret" not in caplog.text


class ManyInvalidValues(BaseModel):
    """Request fixture that can produce more errors than the response cap."""

    values: list[Annotated[int, Field(gt=0)]]


class SafeValidatorMessage(BaseModel):
    """Request fixture for legacy sanitized validator compatibility."""

    value: str

    @field_validator("value")
    @classmethod
    def reject_value(cls, _value: str) -> str:
        raise ValueError("safe compatibility message")


async def test_validation_summary_is_bounded_and_legacy_messages_remain() -> None:
    app = create_app()

    @app.post("/_test/many-values")
    async def many_values(_payload: ManyInvalidValues) -> None:
        return None

    @app.post("/_test/safe-message")
    async def safe_message(_payload: SafeValidatorMessage) -> None:
        return None

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        many = await client.post("/_test/many-values", json={"values": [-1] * 25})
        safe = await client.post("/_test/safe-message", json={"value": "rejected"})

    assert many.status_code == 422
    assert len(many.json()["detail"]) == 20
    assert len(many.json()["error"]["details"]["errors"]) == 20
    assert many.json()["error"]["details"]["truncated"] is True
    assert set(many.json()["error"]["details"]["errors"][0]) == {"type", "loc"}
    assert safe.status_code == 422
    assert "safe compatibility message" in safe.text
    assert "safe compatibility message" not in str(safe.json()["error"]["details"])
    assert safe.json()["detail"][0]["input"] == "redacted"


async def test_validation_summary_redacts_unsupported_location_parts() -> None:
    app = create_app()

    @app.get("/_test/unsupported-location")
    async def unsupported_location() -> None:
        raise RequestValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ("query", None),
                    "input": "secret",
                    "ctx": "bounded context",
                }
            ]
        )

    response = await _get(app, "/_test/unsupported-location")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", None]
    assert response.json()["detail"][0]["ctx"] == "bounded context"
    assert response.json()["error"]["details"]["errors"][0]["loc"] == [
        "query",
        "redacted",
    ]


def test_openapi_documents_request_error_and_response_context() -> None:
    schema = create_app().openapi()
    error_schema = schema["components"]["schemas"]["ApiError"]
    validation_schema = schema["components"]["schemas"]["HTTPValidationError"]

    assert set(error_schema["required"]) == {
        "code",
        "message",
        "details",
        "correlation_id",
        "retryable",
    }
    assert "error" in validation_schema["required"]
    response_schema = schema["components"]["schemas"]["ApiErrorResponse"]
    assert response_schema["required"] == ["error"]
    assert set(response_schema["properties"]) == {"error", "detail"}
    assert response_schema["additionalProperties"] is False
    methods = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
    route_inventory = sorted(
        f"{method.upper()} {path}"
        for path, path_item in schema["paths"].items()
        for method in path_item
        if method in methods
    )
    protected_inventory = sorted(
        f"{method.upper()} {path}"
        for path, path_item in schema["paths"].items()
        for method, operation in path_item.items()
        if method in methods and operation.get("security")
    )
    assert len(route_inventory) == 46
    assert sha256("\n".join(route_inventory).encode()).hexdigest() == (
        "991f50d0dd6009e96c1cd8d0a8b6f403d6f48d81bb247075c103a9d74341425b"
    )
    assert len(protected_inventory) == 44
    assert sha256("\n".join(protected_inventory).encode()).hexdigest() == (
        "ae15e39df8b1710e16b9c20cfa588a8ee8f96a98505f34e1cbcc5fe4c96a17d4"
    )
    assert set(schema["paths"]["/health"]["get"]["responses"]) == {"200", "400", "500"}
    assert {"401", "403", "503"} <= set(
        schema["paths"]["/api/v1/auth/me"]["get"]["responses"]
    )
    assert {"404"} <= set(
        schema["paths"]["/api/v1/tasks/{task_id}"]["get"]["responses"]
    )
    assert {"404", "409"} <= set(
        schema["paths"]["/api/v1/tasks/{task_id}/claim"]["post"]["responses"]
    )
    assert {"404", "409"} <= set(
        schema["paths"]["/api/v1/projects/{project_id}/guides/{guide_id}/activate"][
            "post"
        ]["responses"]
    )
    for path_item in schema["paths"].values():
        for method, operation in path_item.items():
            if method not in {"get", "put", "post", "delete", "options", "head", "patch"}:
                continue
            request_headers = {
                parameter["name"] for parameter in operation["parameters"]
            }
            assert {"X-Request-ID", "X-Correlation-ID"} <= request_headers
            for response in operation["responses"].values():
                assert {"X-Request-ID", "X-Correlation-ID"} <= set(response["headers"])
                assert response["headers"]["X-Request-ID"]["required"] is True
                assert response["headers"]["X-Correlation-ID"]["required"] is True


RATE_SECRET_TEXT = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="
RATE_SECRET = SecretStr(RATE_SECRET_TEXT)
RATE_ISSUER = "https://issuer.example.test"
RATE_SUBJECT = "opaque-subject"


@pytest.fixture
async def rate_control_factory(postgres_database_url: str):
    """Provide independent sessions over a clean, migrated rate-control table."""
    engine = create_async_engine(postgres_database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.execute(text("delete from api_rate_control_counters"))
    try:
        yield factory
    finally:
        async with engine.begin() as connection:
            await connection.execute(text("delete from api_rate_control_counters"))
        await engine.dispose()


def test_rate_key_digest_matches_literal_vector_and_separates_boundaries() -> None:
    expected = bytes.fromhex(
        "35b4fb3e6a647a52596a5240b0b3ad5c2976d91771f95e2497be247081e53b31"
    )

    assert rate_key_digest(
        RATE_SECRET, FIRST_ACCESS_SCOPE, RATE_ISSUER, RATE_SUBJECT
    ) == expected
    assert rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, "ab", "c") != (
        rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, "a", "bc")
    )
    assert rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, "Issuer", "subject") != (
        rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, "issuer", "subject")
    )
    assert rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, "issuer", "e\u0301") != (
        rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, "issuer", "\u00e9")
    )
    assert rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, "issuer", "subject") != (
        rate_key_digest(RATE_SECRET, ADMIN_MUTATION_SCOPE, "issuer", "subject")
    )


@pytest.mark.parametrize("identity", ["", "x" * 4_097, "\u00e9" * 2_049])
def test_rate_key_digest_rejects_unbounded_identity_without_echo(identity: str) -> None:
    with pytest.raises(RateControlUnavailableError) as caught:
        rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, identity, "subject")
    assert str(caught.value) == "rate control unavailable"


async def _stored_rate_row(factory, scope: str, digest: bytes):
    async with factory() as session:
        return (
            await session.execute(
                text(
                    "select window_started_at, window_expires_at, request_count "
                    "from api_rate_control_counters "
                    "where control_scope = :scope and key_digest = :digest"
                ),
                {"scope": scope, "digest": digest},
            )
        ).one()


async def test_rate_control_commits_fixed_window_denials_and_resets_expiry(
    rate_control_factory,
) -> None:
    service = RateControlService(rate_control_factory)
    decisions = [
        await service.consume(
            control_scope=FIRST_ACCESS_SCOPE,
            issuer=RATE_ISSUER,
            subject=RATE_SUBJECT,
            limit=2,
            window_seconds=60,
            secret=RATE_SECRET,
        )
        for _ in range(4)
    ]
    digest = rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, RATE_ISSUER, RATE_SUBJECT)
    original = await _stored_rate_row(rate_control_factory, FIRST_ACCESS_SCOPE, digest)

    assert [decision.allowed for decision in decisions] == [True, True, False, False]
    assert [decision.request_count for decision in decisions] == [1, 2, 3, 4]
    assert all(1 <= decision.retry_after <= 60 for decision in decisions)
    assert original.request_count == 4

    async with rate_control_factory() as session:
        await session.execute(
            text(
                "update api_rate_control_counters set "
                "window_started_at = statement_timestamp() - interval '2 seconds', "
                "window_expires_at = statement_timestamp() - interval '1 second' "
                "where control_scope = :scope and key_digest = :digest"
            ),
            {"scope": FIRST_ACCESS_SCOPE, "digest": digest},
        )
        await session.commit()

    reset = await service.consume(
        control_scope=FIRST_ACCESS_SCOPE,
        issuer=RATE_ISSUER,
        subject=RATE_SUBJECT,
        limit=2,
        window_seconds=60,
        secret=RATE_SECRET,
    )
    persisted = await _stored_rate_row(rate_control_factory, FIRST_ACCESS_SCOPE, digest)
    assert reset == RateControlDecision(allowed=True, request_count=1, retry_after=60)
    assert persisted.request_count == 1
    assert persisted.window_started_at > original.window_started_at


async def test_rate_control_concurrency_has_no_lost_or_rolled_back_consumption(
    rate_control_factory,
) -> None:
    service = RateControlService(rate_control_factory)

    async def consume_once():
        return await service.consume(
            control_scope=ADMIN_MUTATION_SCOPE,
            issuer=RATE_ISSUER,
            subject="concurrent-subject",
            limit=7,
            window_seconds=30,
            secret=RATE_SECRET,
        )

    decisions = await asyncio.gather(*(consume_once() for _ in range(20)))
    digest = rate_key_digest(
        RATE_SECRET, ADMIN_MUTATION_SCOPE, RATE_ISSUER, "concurrent-subject"
    )
    persisted = await _stored_rate_row(rate_control_factory, ADMIN_MUTATION_SCOPE, digest)

    assert sum(decision.allowed for decision in decisions) == 7
    assert sorted(decision.request_count for decision in decisions) == list(range(1, 21))
    assert persisted.request_count == 20

    async with rate_control_factory() as downstream:
        await downstream.execute(
            text(
                "update api_rate_control_counters set request_count = 21 "
                "where control_scope = :scope and key_digest = :digest"
            ),
            {"scope": ADMIN_MUTATION_SCOPE, "digest": digest},
        )
        await downstream.rollback()
    assert (
        await _stored_rate_row(rate_control_factory, ADMIN_MUTATION_SCOPE, digest)
    ).request_count == 20


async def test_rate_control_saturates_bigint_and_prunes_only_bounded_other_rows(
    rate_control_factory,
) -> None:
    service = RateControlService(rate_control_factory)
    digest = rate_key_digest(RATE_SECRET, FIRST_ACCESS_SCOPE, RATE_ISSUER, "saturated")
    async with rate_control_factory() as session:
        await session.execute(
            text(
                "insert into api_rate_control_counters "
                "(control_scope, key_digest, window_started_at, window_expires_at, "
                "request_count, updated_at) values "
                "(:scope, :digest, statement_timestamp(), "
                "statement_timestamp() + interval '1 minute', 9223372036854775807, "
                "statement_timestamp())"
            ),
            {"scope": FIRST_ACCESS_SCOPE, "digest": digest},
        )
        for value in range(125):
            await session.execute(
                text(
                    "insert into api_rate_control_counters "
                    "(control_scope, key_digest, window_started_at, window_expires_at, "
                    "request_count, updated_at) values "
                    "(:scope, :digest, statement_timestamp() - interval '2 minutes', "
                    "statement_timestamp() - interval '1 minute', 1, "
                    "statement_timestamp() - interval '1 minute')"
                ),
                {
                    "scope": ADMIN_MUTATION_SCOPE,
                    "digest": value.to_bytes(32, "big"),
                },
            )
        await session.commit()

    decision = await service.consume(
        control_scope=FIRST_ACCESS_SCOPE,
        issuer=RATE_ISSUER,
        subject="saturated",
        limit=10_000,
        window_seconds=60,
        secret=RATE_SECRET,
    )
    async with rate_control_factory() as session:
        expired = await session.scalar(
            text(
                "select count(*) from api_rate_control_counters "
                "where window_expires_at <= statement_timestamp()"
            )
        )
    assert decision.request_count == 9_223_372_036_854_775_807
    assert decision.allowed is False
    assert expired == 25


async def test_concurrent_expired_keys_do_not_deadlock_during_pruning(
    rate_control_factory,
) -> None:
    subjects = ("expired-a", "expired-b")
    async with rate_control_factory() as session:
        for subject in subjects:
            await session.execute(
                text(
                    "insert into api_rate_control_counters "
                    "(control_scope, key_digest, window_started_at, window_expires_at, "
                    "request_count, updated_at) values "
                    "(:scope, :digest, statement_timestamp() - interval '2 seconds', "
                    "statement_timestamp() - interval '1 second', 5, "
                    "statement_timestamp() - interval '1 second')"
                ),
                {
                    "scope": FIRST_ACCESS_SCOPE,
                    "digest": rate_key_digest(
                        RATE_SECRET, FIRST_ACCESS_SCOPE, RATE_ISSUER, subject
                    ),
                },
            )
        await session.commit()

    service = RateControlService(rate_control_factory)
    decisions = await asyncio.wait_for(
        asyncio.gather(
            *(
                service.consume(
                    control_scope=FIRST_ACCESS_SCOPE,
                    issuer=RATE_ISSUER,
                    subject=subject,
                    limit=1,
                    window_seconds=60,
                    secret=RATE_SECRET,
                )
                for subject in subjects
            )
        ),
        timeout=5,
    )
    assert decisions == [
        RateControlDecision(allowed=True, request_count=1, retry_after=60),
        RateControlDecision(allowed=True, request_count=1, retry_after=60),
    ]


class _FakeSession:
    """Minimal async-session context for deterministic failure tests."""

    def __init__(self, *, commit_error: bool = False) -> None:
        self.commit_error = commit_error
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args) -> None:
        return None

    async def commit(self) -> None:
        if self.commit_error:
            raise SQLAlchemyError("private commit detail")

    async def rollback(self) -> None:
        self.rolled_back = True


async def test_rate_control_maps_only_database_failures_and_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = datetime.now(UTC)
    session = _FakeSession()

    async def fail_execute(*_args, **_kwargs):
        raise SQLAlchemyError("private execute detail")

    monkeypatch.setattr(ApiRateControlRepository, "consume", fail_execute)
    with pytest.raises(RateControlUnavailableError, match="^rate control unavailable$"):
        await RateControlService(lambda: session).consume(
            control_scope=FIRST_ACCESS_SCOPE,
            issuer=RATE_ISSUER,
            subject=RATE_SUBJECT,
            limit=1,
            window_seconds=60,
            secret=RATE_SECRET,
        )
    assert session.rolled_back is True

    async def successful_consume(*_args, **_kwargs):
        return ConsumedCounter(now, now, now + timedelta(seconds=60), 1)

    async def successful_prune(*_args, **_kwargs):
        return None

    commit_session = _FakeSession(commit_error=True)
    monkeypatch.setattr(ApiRateControlRepository, "consume", successful_consume)
    monkeypatch.setattr(ApiRateControlRepository, "prune_expired", successful_prune)
    with pytest.raises(RateControlUnavailableError, match="^rate control unavailable$"):
        await RateControlService(lambda: commit_session).consume(
            control_scope=FIRST_ACCESS_SCOPE,
            issuer=RATE_ISSUER,
            subject=RATE_SUBJECT,
            limit=1,
            window_seconds=60,
            secret=RATE_SECRET,
        )
    assert commit_session.rolled_back is True


async def test_rate_control_narrowly_maps_missing_database_and_propagates_cancel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_database():
        raise RuntimeError("WORKSTREAM_DATABASE_URL must be set before database access")

    monkeypatch.setattr(rate_service_module, "get_session_factory", missing_database)
    with pytest.raises(RateControlUnavailableError, match="^rate control unavailable$"):
        await RateControlService().consume(
            control_scope=FIRST_ACCESS_SCOPE,
            issuer=RATE_ISSUER,
            subject=RATE_SUBJECT,
            limit=1,
            window_seconds=60,
            secret=RATE_SECRET,
        )

    def unrelated_failure():
        raise RuntimeError("unrelated runtime failure")

    monkeypatch.setattr(rate_service_module, "get_session_factory", unrelated_failure)
    with pytest.raises(RuntimeError, match="unrelated runtime failure"):
        await RateControlService().consume(
            control_scope=FIRST_ACCESS_SCOPE,
            issuer=RATE_ISSUER,
            subject=RATE_SUBJECT,
            limit=1,
            window_seconds=60,
            secret=RATE_SECRET,
        )

    async def cancel(*_args, **_kwargs):
        raise asyncio.CancelledError

    monkeypatch.setattr(ApiRateControlRepository, "consume", cancel)
    with pytest.raises(asyncio.CancelledError):
        await RateControlService(lambda: _FakeSession()).consume(
            control_scope=FIRST_ACCESS_SCOPE,
            issuer=RATE_ISSUER,
            subject=RATE_SUBJECT,
            limit=1,
            window_seconds=60,
            secret=RATE_SECRET,
        )


def _verified_rate_identity(subject: str = RATE_SUBJECT) -> AuthVerificationResult:
    return AuthVerificationResult(
        token=VerifiedIssuerToken(
            issuer=RATE_ISSUER,
            subject=subject,
            audience=("workstream",),
            expires_at=2_000_000_000,
            issued_at=1_999_999_000,
            token_id="rate-token",
            subject_kind="human",
            scopes=frozenset({"workstream:access"}),
        )
    )


class _DecisionService:
    def __init__(self, decisions: list[RateControlDecision] | None = None) -> None:
        self.decisions = decisions or []
        self.calls: list[dict] = []

    async def consume(self, **kwargs) -> RateControlDecision:
        self.calls.append(kwargs)
        if not self.decisions:
            raise RateControlUnavailableError("private database detail")
        return self.decisions.pop(0)


async def test_unattached_dependencies_emit_canonical_429_and_use_token_identity() -> None:
    service = _DecisionService(
        [
            RateControlDecision(True, 1, 60),
            RateControlDecision(False, 31, 17),
        ]
    )
    app = create_app(
        Settings(environment="test", api_rate_limit_key_secret=RATE_SECRET_TEXT)
    )
    app.dependency_overrides[get_auth_verification_result] = _verified_rate_identity
    app.dependency_overrides[get_rate_control_service] = lambda: service

    @app.post(
        "/_test/first-access-rate",
        dependencies=[Depends(enforce_first_access_rate_limit)],
    )
    async def first_access() -> dict[str, bool]:
        return {"allowed": True}

    @app.post(
        "/_test/admin-mutation-rate",
        dependencies=[Depends(enforce_admin_mutation_rate_limit)],
    )
    async def admin_mutation() -> dict[str, bool]:
        return {"allowed": True}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        allowed = await client.post("/_test/first-access-rate")
        denied = await client.post("/_test/admin-mutation-rate")

    assert allowed.status_code == 200
    assert denied.status_code == 429
    assert denied.headers["retry-after"] == "17"
    assert denied.json() == {
        "detail": "Rate limit exceeded",
        "error": {
            "code": "rate_limit_exceeded",
            "message": "Rate limit exceeded",
            "details": {},
            "correlation_id": denied.headers["x-correlation-id"],
            "retryable": True,
        },
    }
    assert [call["control_scope"] for call in service.calls] == [
        FIRST_ACCESS_SCOPE,
        ADMIN_MUTATION_SCOPE,
    ]
    assert all(call["issuer"] == RATE_ISSUER for call in service.calls)
    assert all(call["subject"] == RATE_SUBJECT for call in service.calls)


@pytest.mark.parametrize(
    ("settings", "subject", "service"),
    [
        (Settings(environment="test"), RATE_SUBJECT, RateControlService()),
        (
            Settings(environment="test", api_rate_limit_key_secret=RATE_SECRET_TEXT),
            "x" * 4_097,
            RateControlService(),
        ),
        (
            Settings(environment="test", api_rate_limit_key_secret=RATE_SECRET_TEXT),
            RATE_SUBJECT,
            _DecisionService(),
        ),
    ],
)
async def test_rate_dependency_unavailability_is_private_503(
    settings: Settings,
    subject: str,
    service,
) -> None:
    app = create_app(settings)
    app.dependency_overrides[get_auth_verification_result] = lambda: _verified_rate_identity(
        subject
    )
    app.dependency_overrides[get_rate_control_service] = lambda: service

    @app.post(
        "/_test/rate-unavailable",
        dependencies=[Depends(enforce_first_access_rate_limit)],
    )
    async def unavailable() -> None:
        return None

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post("/_test/rate-unavailable")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Service unavailable",
        "error": {
            "code": "service_unavailable",
            "message": "Service unavailable",
            "details": {},
            "correlation_id": response.headers["x-correlation-id"],
            "retryable": True,
        },
    }
    assert subject not in response.text


def test_rate_dependencies_are_not_attached_to_production_routes() -> None:
    forbidden = {
        enforce_first_access_rate_limit,
        enforce_admin_mutation_rate_limit,
    }

    def dependency_calls(dependant) -> set:
        calls = {dependant.call}
        for dependency in dependant.dependencies:
            calls.update(dependency_calls(dependency))
        return calls

    app = create_app()
    assert all(
        forbidden.isdisjoint(dependency_calls(route.dependant))
        for route in app.routes
        if hasattr(route, "dependant")
    )
