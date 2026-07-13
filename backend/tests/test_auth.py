from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import jwt
import httpx
import pytest
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient, MockTransport, Request, Response
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.adapters.auth.dev import DevelopmentAuthVerifier
from app.adapters.auth.flow import FlowAuthVerifier
from app.adapters.auth.metrics import InProcessAuthVerifierMetrics
from app.api.deps.auth import get_registered_actor
from app.core.auth import clear_auth_verifier_cache
from app.core.config import Settings, get_settings
from app.core.permissions import PermissionDenied, require_any_role
from app.db import session as db_session
from app.interfaces.auth import AuthVerificationError, AuthVerificationUnavailableError
from app.main import create_app
from app.modules.actors.service import ActorService
from app.schemas.auth import normalize_legacy_roles


def _application_paths(app) -> set[str]:
    """Return concrete application paths across FastAPI router representations."""
    paths = set(app.openapi()["paths"])
    for route in app.routes:
        path = getattr(route, "path", None)
        if path:
            paths.add(path)
        route_contexts = getattr(route, "effective_route_contexts", None)
        if route_contexts is not None:
            paths.update(context.path for context in route_contexts())
    return paths


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    clear_auth_verifier_cache()
    yield
    get_settings.cache_clear()
    clear_auth_verifier_cache()


@pytest.fixture
def auth_database_env(
    monkeypatch: pytest.MonkeyPatch,
    postgres_database_url: str,
    migration_lock,
) -> Iterator[str]:
    """Run auth route persistence tests against a migrated Postgres schema."""
    monkeypatch.setenv("WORKSTREAM_DATABASE_URL", postgres_database_url)
    get_settings.cache_clear()
    asyncio.run(db_session.dispose_engine())

    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    with migration_lock():
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        yield postgres_database_url
        command.downgrade(config, "base")
    asyncio.run(db_session.dispose_engine())
    get_settings.cache_clear()


def _base64url_int(value: int) -> str:
    size = (value.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(value.to_bytes(size, "big")).rstrip(b"=").decode()


@pytest.fixture(scope="module")
def rsa_signing_material() -> tuple[rsa.RSAPrivateKey, dict[str, Any]]:
    private_key = rsa.generate_private_key(public_exponent=65_537, key_size=2_048)
    return private_key, rsa_public_jwk(private_key, kid="issuer-key-1")


def rsa_public_jwk(
    private_key: rsa.RSAPrivateKey,
    *,
    kid: str,
) -> dict[str, Any]:
    numbers = private_key.public_key().public_numbers()
    return {
        "kty": "RSA",
        "kid": kid,
        "use": "sig",
        "key_ops": ["verify"],
        "alg": "RS256",
        "n": _base64url_int(numbers.n),
        "e": _base64url_int(numbers.e),
    }


def production_verifier_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "environment": "test",
        "auth_provider": "flow",
        "token_issuer": "https://issuer.example.test",
        "token_audience": "workstream",
        "token_jwks_url": "https://issuer.example.test/.well-known/jwks.json",
        "token_algorithms": "RS256",
        "token_introspection_mode": "disabled",
        "token_introspection_disabled_reason": "issuer uses short-lived final tokens",
    }
    values.update(overrides)
    return Settings(**values)


def issue_asymmetric_token(
    private_key: rsa.RSAPrivateKey,
    *,
    kid: str = "issuer-key-1",
    subject_kind: str = "human",
    scope: str = "workstream:access",
    claims: dict[str, Any] | None = None,
    remove_claims: set[str] | None = None,
    algorithm: str = "RS256",
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "iss": "https://issuer.example.test",
        "sub": "opaque-subject-1",
        "aud": "workstream",
        "exp": int((now + timedelta(minutes=10)).timestamp()),
        "iat": int(now.timestamp()),
        "nbf": int((now - timedelta(seconds=1)).timestamp()),
        "jti": "token-id-1",
        "subject_kind": subject_kind,
        "scope": scope,
        "roles": ["admin", "reviewer"],
        "email": "must-not-enter-canonical@example.test",
        "name": "Must Not Enter Canonical",
    }
    if claims:
        payload.update(claims)
    for claim in remove_claims or ():
        payload.pop(claim, None)
    return jwt.encode(payload, private_key, algorithm=algorithm, headers={"kid": kid, "typ": "JWT"})


def jwks_transport(jwk: dict[str, Any], requests: list[Request] | None = None) -> MockTransport:
    def handler(request: Request) -> Response:
        if requests is not None:
            requests.append(request)
        return Response(200, json={"keys": [jwk]})

    return MockTransport(handler)


def issue_local_hmac_token(secret: str, claims: dict[str, Any]) -> str:
    def segment(value: dict[str, Any]) -> str:
        encoded = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
        return base64.urlsafe_b64encode(encoded).rstrip(b"=").decode()

    header = segment({"alg": "HS256", "typ": "JWT"})
    payload = segment(claims)
    content = f"{header}.{payload}".encode()
    signature = (
        base64.urlsafe_b64encode(hmac.new(secret.encode(), content, hashlib.sha256).digest())
        .rstrip(b"=")
        .decode()
    )
    return f"{header}.{payload}.{signature}"


def replace_token_header(
    token: str,
    *,
    remove_headers: set[str] | None = None,
    **changes: Any,
) -> str:
    header_segment, payload_segment, signature_segment = token.split(".")
    header = json.loads(base64.urlsafe_b64decode(header_segment + "=" * (-len(header_segment) % 4)))
    header.update(changes)
    for name in remove_headers or ():
        header.pop(name, None)
    replacement = (
        base64.urlsafe_b64encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode())
        .rstrip(b"=")
        .decode()
    )
    return f"{replacement}.{payload_segment}.{signature_segment}"


async def test_local_hmac_fixture_uses_final_claim_shape() -> None:
    secret = "local-test-secret"
    now = int(datetime.now(UTC).timestamp())
    verifier = FlowAuthVerifier(
        Settings(
            environment="test",
            auth_provider="flow",
            flow_auth_issuer="https://issuer.local.test",
            flow_auth_audience="workstream",
            flow_auth_local_hmac_secret=secret,
        )
    )
    token = issue_local_hmac_token(
        secret,
        {
            "iss": "https://issuer.local.test",
            "sub": "local-subject",
            "aud": "workstream",
            "exp": now + 300,
            "iat": now,
            "jti": "local-token-id",
            "subject_kind": "human",
            "scope": "workstream:access",
            "roles": ["reviewer"],
        },
    )

    result = await verifier.verify(token)

    assert result.token.token_id == "local-token-id"
    assert result.legacy is not None
    assert result.legacy.roles == ("reviewer",)


@pytest.mark.parametrize("environment", ["staging", "preview", "prod", "production"])
def test_local_hmac_fixture_is_impossible_in_production(environment: str) -> None:
    with pytest.raises(RuntimeError, match="cannot run outside local/test"):
        FlowAuthVerifier(
            Settings(
                environment=environment,
                auth_provider="flow",
                flow_auth_local_hmac_secret="forbidden-secret",
            )
        )


async def test_asymmetric_token_returns_minimal_canonical_contract(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    requests: list[Request] = []
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk, requests),
    )

    result = await verifier.verify(issue_asymmetric_token(private_key))

    assert result.token.model_dump().keys() == {
        "issuer",
        "subject",
        "audience",
        "expires_at",
        "issued_at",
        "not_before",
        "token_id",
        "subject_kind",
        "scopes",
    }
    assert result.token.subject == "opaque-subject-1"
    assert not hasattr(result.token, "roles")
    assert not hasattr(result.token, "email")
    assert result.legacy is not None
    assert result.legacy.roles == ("admin", "reviewer")
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].headers.get("authorization") is None
    assert requests[0].content == b""


@pytest.mark.parametrize(
    "header_changes",
    [
        {"alg": "none"},
        {"alg": "HS256"},
        {"kid": ""},
        {"jku": "https://attacker.test/jwks"},
        {"x5u": "https://attacker.test/certificate"},
        {"crit": ["unrecognized"]},
    ],
)
async def test_untrusted_or_remote_key_headers_fail_before_jwks(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
    header_changes: dict[str, Any],
) -> None:
    private_key, jwk = rsa_signing_material
    requests: list[Request] = []
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk, requests),
    )
    token = replace_token_header(issue_asymmetric_token(private_key), **header_changes)

    with pytest.raises(AuthVerificationError):
        await verifier.verify(token)

    assert requests == []


async def test_missing_kid_fails_before_jwks(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    requests: list[Request] = []
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk, requests),
    )
    token = replace_token_header(
        issue_asymmetric_token(private_key),
        remove_headers={"kid"},
    )

    with pytest.raises(AuthVerificationError, match="key identifier"):
        await verifier.verify(token)

    assert requests == []


async def test_jwks_cache_hit_avoids_second_network_request(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    requests: list[Request] = []
    metrics = InProcessAuthVerifierMetrics()
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk, requests),
        metrics=metrics,
    )

    await verifier.verify(issue_asymmetric_token(private_key))
    await verifier.verify(issue_asymmetric_token(private_key, claims={"jti": "token-id-2"}))

    assert len(requests) == 1
    assert any(
        name == "workstream_auth_jwks_cache_total" and ("result", "hit") in labels
        for name, labels in metrics.snapshot()
    )


def test_verifier_metrics_enforce_closed_labels_without_identity_values() -> None:
    metrics = InProcessAuthVerifierMetrics()
    for result in ("success", "invalid", "unsupported_kind", "unavailable"):
        metrics.verification(result)  # type: ignore[arg-type]
    for result in ("hit", "miss", "negative_hit", "expired"):
        metrics.jwks_cache(result)  # type: ignore[arg-type]
    for result in ("success", "failure"):
        metrics.jwks_refresh(result)  # type: ignore[arg-type]
    for mode in ("disabled", "required"):
        for result in ("success", "inactive", "invalid", "unavailable", "skipped"):
            metrics.introspection(mode, result)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="not allowed"):
        metrics.verification("opaque-subject-token-id")  # type: ignore[arg-type]

    snapshot = repr(metrics.snapshot())
    for forbidden in ("opaque-subject", "token-id", "https://", "client-secret", "BEGIN"):
        assert forbidden not in snapshot


async def test_unknown_kid_refreshes_once_then_uses_bounded_negative_cache(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    requests: list[Request] = []
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk, requests),
    )
    token = issue_asymmetric_token(private_key, kid="unknown-key")

    with pytest.raises(AuthVerificationError, match="unknown"):
        await verifier.verify(token)
    with pytest.raises(AuthVerificationError, match="unknown"):
        await verifier.verify(token)

    assert len(requests) == 1


async def test_unknown_kid_refresh_is_single_flight(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    requests: list[Request] = []
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk, requests),
    )
    token = issue_asymmetric_token(private_key, kid="concurrent-unknown-key")

    results = await asyncio.gather(
        verifier.verify(token),
        verifier.verify(token),
        return_exceptions=True,
    )

    assert all(isinstance(result, AuthVerificationError) for result in results)
    assert len(requests) == 1


async def test_distinct_unknown_kids_share_one_refresh_generation(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    requests: list[Request] = []
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk, requests),
    )

    results = await asyncio.gather(
        verifier.verify(issue_asymmetric_token(private_key, kid="unknown-a")),
        verifier.verify(issue_asymmetric_token(private_key, kid="unknown-b")),
        return_exceptions=True,
    )

    assert all(isinstance(result, AuthVerificationError) for result in results)
    assert len(requests) == 1


async def test_jwks_lock_wait_is_inside_total_deadline(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material

    async def slow_jwks(request: Request) -> Response:
        await asyncio.sleep(0.6)
        return Response(200, json={"keys": [jwk]})

    verifier = FlowAuthVerifier(
        production_verifier_settings(token_jwks_total_timeout_seconds=0.5),
        jwks_transport=MockTransport(slow_jwks),
    )

    with pytest.raises(AuthVerificationUnavailableError, match="unavailable|timed out"):
        await verifier.verify(issue_asymmetric_token(private_key))


async def test_rotation_clears_matching_negative_kid() -> None:
    first_key = rsa.generate_private_key(public_exponent=65_537, key_size=2_048)
    rotated_key = rsa.generate_private_key(public_exponent=65_537, key_size=2_048)
    first_jwk = rsa_public_jwk(first_key, kid="first-key")
    rotated_jwk = rsa_public_jwk(rotated_key, kid="rotated-key")
    clock = [0.0]
    requests: list[Request] = []

    def rotating_jwks(request: Request) -> Response:
        requests.append(request)
        keys = [first_jwk] if len(requests) < 3 else [first_jwk, rotated_jwk]
        return Response(200, json={"keys": keys})

    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=MockTransport(rotating_jwks),
        monotonic=lambda: clock[0],
    )
    await verifier.verify(issue_asymmetric_token(first_key, kid="first-key"))
    clock[0] = 31.0
    rotated_token = issue_asymmetric_token(rotated_key, kid="rotated-key")
    with pytest.raises(AuthVerificationError, match="unknown"):
        await verifier.verify(rotated_token)
    clock[0] = 62.0
    with pytest.raises(AuthVerificationError, match="unknown"):
        await verifier.verify(issue_asymmetric_token(rotated_key, kid="rotation-trigger"))

    result = await verifier.verify(rotated_token)

    assert result.token.subject == "opaque-subject-1"
    assert len(requests) == 3


async def test_negative_kid_cache_is_ttl_and_size_bounded(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    clock = [0.0]
    verifier = FlowAuthVerifier(
        production_verifier_settings(token_unknown_kid_cache_max_entries=1),
        jwks_transport=jwks_transport(jwk),
        monotonic=lambda: clock[0],
    )
    await verifier.verify(issue_asymmetric_token(private_key))
    for kid in ("unknown-a", "unknown-b"):
        with pytest.raises(AuthVerificationError):
            await verifier.verify(issue_asymmetric_token(private_key, kid=kid))
    assert tuple(verifier._negative_kids) == ("unknown-b",)

    clock[0] = 31.0
    verifier._prune_negative_kids(clock[0])
    assert not verifier._negative_kids


async def test_expired_jwks_cache_refreshes_during_longer_unknown_kid_cooldown(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    clock = [0.0]
    requests: list[Request] = []

    def outage_after_prime(request: Request) -> Response:
        requests.append(request)
        if len(requests) == 1:
            return Response(200, json={"keys": [jwk]})
        return Response(503)

    verifier = FlowAuthVerifier(
        production_verifier_settings(
            token_jwks_cache_ttl_seconds=30,
            token_unknown_kid_cache_ttl_seconds=300,
        ),
        jwks_transport=MockTransport(outage_after_prime),
        monotonic=lambda: clock[0],
    )
    token = issue_asymmetric_token(private_key)
    await verifier.verify(token)
    clock[0] = 31.0

    with pytest.raises(AuthVerificationUnavailableError):
        await verifier.verify(token)
    clock[0] = 32.0
    with pytest.raises(AuthVerificationUnavailableError, match="cooling down"):
        await verifier.verify(token)

    assert len(requests) == 2


async def test_refresh_failure_cooldown_preserves_valid_cached_key_hits(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    clock = [0.0]
    requests: list[Request] = []

    def outage_after_prime(request: Request) -> Response:
        requests.append(request)
        if len(requests) == 1:
            return Response(200, json={"keys": [jwk]})
        return Response(503)

    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=MockTransport(outage_after_prime),
        monotonic=lambda: clock[0],
    )
    valid_token = issue_asymmetric_token(private_key)
    await verifier.verify(valid_token)
    clock[0] = 31.0
    with pytest.raises(AuthVerificationUnavailableError):
        await verifier.verify(issue_asymmetric_token(private_key, kid="unknown-during-outage"))

    clock[0] = 32.0
    assert (await verifier.verify(valid_token)).token.token_id == "token-id-1"
    with pytest.raises(AuthVerificationUnavailableError, match="cooling down"):
        await verifier.verify(issue_asymmetric_token(private_key, kid="another-unknown"))
    assert len(requests) == 2


@pytest.mark.parametrize(
    ("claims", "message"),
    [
        ({"aud": "other"}, "signature or claims"),
        ({"iss": "https://other.example.test"}, "signature or claims"),
        ({"exp": 1}, "signature or claims"),
        ({"iat": int((datetime.now(UTC) + timedelta(hours=1)).timestamp())}, "signature or claims"),
        ({"jti": ""}, "identifier"),
        ({"subject_kind": "Human"}, "subject kind"),
        ({"scope": "unrelated"}, "human scope"),
    ],
)
async def test_verified_token_claim_failures_are_closed(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
    claims: dict[str, Any],
    message: str,
) -> None:
    private_key, jwk = rsa_signing_material
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk),
    )

    with pytest.raises(AuthVerificationError, match=message):
        await verifier.verify(issue_asymmetric_token(private_key, claims=claims))


@pytest.mark.parametrize(
    "missing_claim", ["iss", "sub", "aud", "exp", "iat", "jti", "subject_kind", "scope"]
)
async def test_missing_mandatory_claims_fail_closed(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
    missing_claim: str,
) -> None:
    private_key, jwk = rsa_signing_material
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk),
    )

    with pytest.raises(AuthVerificationError):
        await verifier.verify(issue_asymmetric_token(private_key, remove_claims={missing_claim}))


@pytest.mark.parametrize(
    "token",
    [
        "not-a-jwt",
        "a.b.c",
        "eyJhbGciOiJSUzI1NiJ9.not-json.signature",
        "....",
    ],
)
async def test_malformed_tokens_fail_without_network(token: str) -> None:
    requests: list[Request] = []
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=MockTransport(lambda request: requests.append(request) or Response(500)),
    )

    with pytest.raises(AuthVerificationError):
        await verifier.verify(token)

    assert requests == []


@pytest.mark.parametrize("limit", ["total", "header", "payload"])
async def test_token_size_limits_fail_before_network(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
    limit: str,
) -> None:
    private_key, jwk = rsa_signing_material
    requests: list[Request] = []
    overrides: dict[str, int] = {
        "token_max_bytes": 4_096,
        "token_header_max_bytes": 512,
        "token_payload_max_bytes": 2_048,
    }
    token = issue_asymmetric_token(private_key)
    if limit == "total":
        overrides.update(
            token_max_bytes=512,
            token_header_max_bytes=128,
            token_payload_max_bytes=256,
        )
        token = "x" * 513
    elif limit == "header":
        overrides["token_header_max_bytes"] = 128
        token = replace_token_header(token, padding="x" * 200)
    else:
        overrides["token_payload_max_bytes"] = 256
        token = issue_asymmetric_token(private_key, claims={"padding": "x" * 400})
    verifier = FlowAuthVerifier(
        production_verifier_settings(**overrides),
        jwks_transport=jwks_transport(jwk, requests),
    )

    with pytest.raises(AuthVerificationError):
        await verifier.verify(token)

    assert requests == []


@pytest.mark.parametrize(
    ("claim", "within_delta", "beyond_delta"),
    [("exp", -10, -60), ("iat", 10, 60), ("nbf", 10, 60)],
)
async def test_temporal_claims_honor_configured_skew(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
    claim: str,
    within_delta: int,
    beyond_delta: int,
) -> None:
    private_key, jwk = rsa_signing_material
    verifier = FlowAuthVerifier(
        production_verifier_settings(token_clock_skew_seconds=30),
        jwks_transport=jwks_transport(jwk),
    )
    now = datetime.now(UTC)

    within_skew = issue_asymmetric_token(
        private_key,
        claims={claim: int((now + timedelta(seconds=within_delta)).timestamp())},
    )
    beyond_skew = issue_asymmetric_token(
        private_key,
        claims={claim: int((now + timedelta(seconds=beyond_delta)).timestamp())},
    )

    assert (await verifier.verify(within_skew)).token.token_id == "token-id-1"
    with pytest.raises(AuthVerificationError):
        await verifier.verify(beyond_skew)


async def test_service_and_agent_tokens_receive_no_legacy_authority(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(jwk),
    )

    service = await verifier.verify(
        issue_asymmetric_token(
            private_key,
            subject_kind="service",
            scope="workstream:service",
        )
    )
    agent = await verifier.verify(
        issue_asymmetric_token(private_key, subject_kind="agent", scope="agent:identity")
    )
    space = await verifier.verify(
        issue_asymmetric_token(private_key, subject_kind="space", scope="space:identity")
    )

    assert service.legacy is None
    assert agent.legacy is None
    assert space.legacy is None
    with pytest.raises(HTTPException) as exc_info:
        await get_registered_actor(agent, None)  # type: ignore[arg-type]
    assert exc_info.value.status_code == 403
    assert exc_info.value.error_code == "unsupported_subject_kind"

    with pytest.raises(AuthVerificationError, match="service scope"):
        await verifier.verify(
            issue_asymmetric_token(
                private_key,
                subject_kind="service",
                scope="workstream:access",
            )
        )


async def test_jwks_unavailability_is_typed_and_redacted() -> None:
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=MockTransport(lambda request: Response(503, text="secret issuer body")),
    )
    private_key = rsa.generate_private_key(public_exponent=65_537, key_size=2_048)
    bearer = issue_asymmetric_token(private_key)

    with pytest.raises(AuthVerificationUnavailableError) as exc_info:
        await verifier.verify(bearer)

    assert bearer not in str(exc_info.value)
    assert "secret issuer body" not in str(exc_info.value)


@pytest.mark.parametrize(
    "jwks_payload",
    [
        {"keys": []},
        {"keys": [{"kid": "duplicate"}, {"kid": "duplicate"}]},
        {"keys": [{"kid": "wrong-use", "alg": "RS256", "kty": "RSA", "use": "enc"}]},
    ],
)
async def test_invalid_jwks_documents_fail_closed(jwks_payload: dict[str, Any]) -> None:
    private_key = rsa.generate_private_key(public_exponent=65_537, key_size=2_048)
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=MockTransport(lambda request: Response(200, json=jwks_payload)),
    )

    with pytest.raises(AuthVerificationUnavailableError):
        await verifier.verify(issue_asymmetric_token(private_key))


async def test_weak_rsa_signing_key_is_rejected() -> None:
    weak_key = rsa.generate_private_key(public_exponent=65_537, key_size=1_024)
    weak_jwk = rsa_public_jwk(weak_key, kid="weak-key")
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport(weak_jwk),
    )

    with pytest.warns(jwt.InsecureKeyLengthWarning):
        token = issue_asymmetric_token(weak_key, kid="weak-key")
    with pytest.raises(AuthVerificationUnavailableError, match="invalid"):
        await verifier.verify(token)


@pytest.mark.parametrize(
    "jwk_override",
    [
        {"kty": "EC"},
        {"alg": "RS512"},
        {"key_ops": ["sign"]},
        {"use": "enc"},
    ],
)
async def test_incompatible_jwk_metadata_is_rejected(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
    jwk_override: dict[str, Any],
) -> None:
    private_key, jwk = rsa_signing_material
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=jwks_transport({**jwk, **jwk_override}),
    )

    with pytest.raises(AuthVerificationUnavailableError):
        await verifier.verify(issue_asymmetric_token(private_key))


async def test_malformed_and_excessive_jwks_fail_closed(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    responses = [
        Response(200, content=b"not-json"),
        Response(200, json={"keys": [jwk, {**jwk, "kid": "second"}]}),
    ]
    for response, settings in (
        (responses[0], production_verifier_settings()),
        (responses[1], production_verifier_settings(token_jwks_max_keys=1)),
    ):
        verifier = FlowAuthVerifier(
            settings,
            jwks_transport=MockTransport(lambda request, response=response: response),
        )
        with pytest.raises(AuthVerificationUnavailableError):
            await verifier.verify(issue_asymmetric_token(private_key))


async def test_jwks_redirect_does_not_receive_or_forward_bearer(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, _ = rsa_signing_material
    requests: list[Request] = []

    def redirect(request: Request) -> Response:
        requests.append(request)
        return Response(302, headers={"location": "https://attacker.test/jwks"})

    bearer = issue_asymmetric_token(private_key)
    verifier = FlowAuthVerifier(
        production_verifier_settings(),
        jwks_transport=MockTransport(redirect),
    )

    with pytest.raises(AuthVerificationUnavailableError):
        await verifier.verify(bearer)

    assert len(requests) == 1
    assert requests[0].url.host == "issuer.example.test"
    assert requests[0].headers.get("authorization") is None
    assert requests[0].content == b""
    assert all(request.url.host != "attacker.test" for request in requests)


async def test_oversized_jwks_response_fails_before_json_buffering() -> None:
    private_key = rsa.generate_private_key(public_exponent=65_537, key_size=2_048)
    verifier = FlowAuthVerifier(
        production_verifier_settings(token_jwks_max_response_bytes=1_024),
        jwks_transport=MockTransport(
            lambda request: Response(200, content=b"{" + b'"padding":"' + b"x" * 2_000 + b'"}')
        ),
    )

    with pytest.raises(AuthVerificationUnavailableError, match="exceeds"):
        await verifier.verify(issue_asymmetric_token(private_key))


async def test_required_introspection_is_separate_bound_and_no_redirect(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    jwks_requests: list[Request] = []
    introspection_requests: list[Request] = []

    def introspection_handler(request: Request) -> Response:
        introspection_requests.append(request)
        return Response(
            200,
            json={
                "active": True,
                "iss": "https://issuer.example.test",
                "sub": "opaque-subject-1",
                "aud": "workstream",
                "jti": "token-id-1",
            },
        )

    verifier = FlowAuthVerifier(
        production_verifier_settings(
            token_introspection_mode="required",
            token_introspection_disabled_reason=None,
            token_introspection_url="https://introspection.example.test/oauth/introspect",
            token_introspection_client_id="workstream-client",
            token_introspection_client_secret="client-secret",
        ),
        jwks_transport=jwks_transport(jwk, jwks_requests),
        introspection_transport=MockTransport(introspection_handler),
    )
    bearer = issue_asymmetric_token(private_key)

    result = await verifier.verify(bearer)

    assert result.token.token_id == "token-id-1"
    assert len(jwks_requests) == 1
    assert jwks_requests[0].headers.get("authorization") is None
    assert bearer.encode() not in jwks_requests[0].content
    assert len(introspection_requests) == 1
    assert introspection_requests[0].method == "POST"
    assert introspection_requests[0].url.host == "introspection.example.test"
    assert introspection_requests[0].headers["authorization"].startswith("Basic ")
    assert bearer.encode() in introspection_requests[0].content

    redirect_requests: list[Request] = []

    def introspection_redirect(request: Request) -> Response:
        redirect_requests.append(request)
        return Response(302, headers={"location": "https://attacker.test/collect"})

    redirecting = FlowAuthVerifier(
        production_verifier_settings(
            token_introspection_mode="required",
            token_introspection_disabled_reason=None,
            token_introspection_url="https://introspection.example.test/oauth/introspect",
            token_introspection_client_id="workstream-client",
            token_introspection_client_secret="client-secret",
        ),
        jwks_transport=jwks_transport(jwk),
        introspection_transport=MockTransport(introspection_redirect),
    )
    with pytest.raises(AuthVerificationUnavailableError):
        await redirecting.verify(bearer)
    assert len(redirect_requests) == 1
    assert redirect_requests[0].url.host == "introspection.example.test"
    assert bearer.encode() in redirect_requests[0].content
    assert all(request.url.host != "attacker.test" for request in redirect_requests)


async def test_jwks_and_introspection_use_distinct_owned_client_factories(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    clients: dict[str, list[AsyncClient]] = {"jwks": [], "introspection": []}

    def factory(name: str, transport: MockTransport):
        def build_client(**kwargs: Any) -> AsyncClient:
            client = AsyncClient(transport=transport, **kwargs)
            clients[name].append(client)
            return client

        return build_client

    introspection_transport = MockTransport(
        lambda request: Response(
            200,
            json={
                "active": True,
                "iss": "https://issuer.example.test",
                "sub": "opaque-subject-1",
                "aud": "workstream",
                "jti": "token-id-1",
            },
        )
    )
    verifier = FlowAuthVerifier(
        production_verifier_settings(
            token_introspection_mode="required",
            token_introspection_disabled_reason=None,
            token_introspection_url="https://introspection.example.test/oauth/introspect",
            token_introspection_client_id="workstream-client",
            token_introspection_client_secret="client-secret",
        ),
        jwks_client_factory=factory("jwks", jwks_transport(jwk)),
        introspection_client_factory=factory("introspection", introspection_transport),
    )

    await verifier.verify(issue_asymmetric_token(private_key))

    assert len(clients["jwks"]) == 1
    assert len(clients["introspection"]) == 1
    assert clients["jwks"][0] is not clients["introspection"][0]
    assert clients["jwks"][0].is_closed
    assert clients["introspection"][0].is_closed

@pytest.mark.parametrize(
    "response_override",
    [
        {"active": False},
        {"iss": "https://other.example.test"},
        {"sub": "other-subject"},
        {"aud": "other-audience"},
        {"jti": "other-token-id"},
    ],
)
async def test_required_introspection_fails_closed_on_inactive_or_mismatch(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
    response_override: dict[str, Any],
) -> None:
    private_key, jwk = rsa_signing_material
    response = {
        "active": True,
        "iss": "https://issuer.example.test",
        "sub": "opaque-subject-1",
        "aud": "workstream",
        "jti": "token-id-1",
    }
    response.update(response_override)
    verifier = FlowAuthVerifier(
        production_verifier_settings(
            token_introspection_mode="required",
            token_introspection_disabled_reason=None,
            token_introspection_url="https://introspection.example.test/oauth/introspect",
            token_introspection_client_id="workstream-client",
            token_introspection_client_secret="client-secret",
        ),
        jwks_transport=jwks_transport(jwk),
        introspection_transport=MockTransport(lambda request: Response(200, json=response)),
    )

    with pytest.raises(AuthVerificationError):
        await verifier.verify(issue_asymmetric_token(private_key))


@pytest.mark.parametrize("missing_field", ["iss", "sub", "aud", "jti"])
async def test_required_introspection_rejects_missing_identity_fields(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
    missing_field: str,
) -> None:
    private_key, jwk = rsa_signing_material
    response = {
        "active": True,
        "iss": "https://issuer.example.test",
        "sub": "opaque-subject-1",
        "aud": "workstream",
        "jti": "token-id-1",
    }
    response.pop(missing_field)
    verifier = FlowAuthVerifier(
        production_verifier_settings(
            token_introspection_mode="required",
            token_introspection_disabled_reason=None,
            token_introspection_url="https://introspection.example.test/oauth/introspect",
            token_introspection_client_id="workstream-client",
            token_introspection_client_secret="client-secret",
        ),
        jwks_transport=jwks_transport(jwk),
        introspection_transport=MockTransport(lambda request: Response(200, json=response)),
    )

    with pytest.raises(AuthVerificationError):
        await verifier.verify(issue_asymmetric_token(private_key))


@pytest.mark.parametrize(
    "response",
    [
        Response(200, content=b"not-json-secret-response"),
        Response(200, content=b"x" * 300),
        Response(503, content=b"issuer-secret-response"),
    ],
)
async def test_introspection_response_failures_are_redacted(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
    response: Response,
) -> None:
    private_key, jwk = rsa_signing_material
    bearer = issue_asymmetric_token(private_key)
    verifier = FlowAuthVerifier(
        production_verifier_settings(
            token_introspection_mode="required",
            token_introspection_disabled_reason=None,
            token_introspection_url="https://introspection.example.test/oauth/introspect",
            token_introspection_client_id="workstream-client",
            token_introspection_client_secret="client-secret",
            token_introspection_max_response_bytes=256,
        ),
        jwks_transport=jwks_transport(jwk),
        introspection_transport=MockTransport(lambda request: response),
    )

    with pytest.raises(AuthVerificationUnavailableError) as exc_info:
        await verifier.verify(bearer)

    error = exc_info.value
    assert error.__cause__ is None
    assert error.__context__ is None
    serialized_error = repr(vars(error)) + repr(error.args)
    for forbidden in (
        bearer,
        "client-secret",
        "not-json-secret-response",
        "issuer-secret-response",
    ):
        assert forbidden not in serialized_error


async def test_introspection_transport_error_drops_credential_bearing_exception(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material
    bearer = issue_asymmetric_token(private_key)

    def fail_with_request(request: Request) -> Response:
        raise httpx.ReadTimeout("transport-secret", request=request)

    verifier = FlowAuthVerifier(
        production_verifier_settings(
            token_introspection_mode="required",
            token_introspection_disabled_reason=None,
            token_introspection_url="https://introspection.example.test/oauth/introspect",
            token_introspection_client_id="workstream-client",
            token_introspection_client_secret="client-secret",
        ),
        jwks_transport=jwks_transport(jwk),
        introspection_transport=MockTransport(fail_with_request),
    )

    with pytest.raises(AuthVerificationUnavailableError) as exc_info:
        await verifier.verify(bearer)

    error = exc_info.value
    assert error.__cause__ is None
    assert error.__context__ is None
    assert bearer not in repr(vars(error))
    assert "client-secret" not in repr(vars(error))


async def test_introspection_total_timeout_fails_closed(
    rsa_signing_material: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_signing_material

    async def slow_introspection(request: Request) -> Response:
        await asyncio.sleep(0.6)
        return Response(200, json={"active": True})

    verifier = FlowAuthVerifier(
        production_verifier_settings(
            token_introspection_mode="required",
            token_introspection_disabled_reason=None,
            token_introspection_url="https://introspection.example.test/oauth/introspect",
            token_introspection_client_id="workstream-client",
            token_introspection_client_secret="client-secret",
            token_introspection_total_timeout_seconds=0.5,
        ),
        jwks_transport=jwks_transport(jwk),
        introspection_transport=MockTransport(slow_introspection),
    )

    with pytest.raises(AuthVerificationUnavailableError):
        await verifier.verify(issue_asymmetric_token(private_key))


def test_legacy_compatibility_dependency_has_fixed_consumer_allowlist() -> None:
    app_root = Path(__file__).resolve().parents[1] / "app"
    sources = {
        path.relative_to(app_root).as_posix(): path.read_text() for path in app_root.rglob("*.py")
    }

    assert {path for path, source in sources.items() if "get_registered_actor" in source} == {
        "api/deps/auth.py",
        "api/routes/auth.py",
        "modules/checkers/router.py",
        "modules/projects/router.py",
        "modules/tasks/router.py",
    }
    assert {
        path for path, source in sources.items() if "get_auth_verification_result" in source
    } == {"api/deps/auth.py"}
    assert {path for path, source in sources.items() if "AuthVerificationResult" in source} == {
        "adapters/auth/dev.py",
        "adapters/auth/flow.py",
        "api/deps/auth.py",
        "core/auth.py",
        "interfaces/auth.py",
        "schemas/auth.py",
    }
    assert {
        path
        for path, source in sources.items()
        if "LegacyAuthorizationCompatibilityContext" in source
    } == {
        "adapters/auth/dev.py",
        "adapters/auth/flow.py",
        "schemas/auth.py",
    }
    assert {path for path, source in sources.items() if "result.legacy" in source} == {
        "api/deps/auth.py"
    }


async def test_missing_bearer_token_is_rejected() -> None:
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["error"] == {
        "code": "missing_token",
        "message": "Missing bearer token",
        "details": {},
        "correlation_id": response.headers["x-correlation-id"],
        "retryable": False,
    }


async def test_invalid_bearer_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKSTREAM_AUTH_PROVIDER", "dev")
    monkeypatch.setenv("WORKSTREAM_ENVIRONMENT", "test")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_TOKEN", "expected-token")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_SUBJECT", "subject")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_ISSUER", "issuer")
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer wrong-token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid bearer token"
    assert response.json()["error"]["code"] == "invalid_token"
    assert response.json()["error"]["retryable"] is False


async def test_invalid_production_verifier_configuration_is_service_unavailable() -> None:
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer opaque-token"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "Identity verification unavailable"
    assert response.json()["error"]["code"] == "identity_verification_unavailable"
    assert response.json()["error"]["retryable"] is True


async def test_valid_dev_token_resolves_actor_context(
    monkeypatch: pytest.MonkeyPatch,
    auth_database_env: str,
) -> None:
    monkeypatch.setenv("WORKSTREAM_AUTH_PROVIDER", "dev")
    monkeypatch.setenv("WORKSTREAM_ENVIRONMENT", "local")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_TOKEN", "local-token")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_SUBJECT", "flow-subject-1")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_ISSUER", "flow-dev-issuer")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_EMAIL", "worker@example.test")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_DISPLAY_NAME", "Worker One")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_ROLES", "worker,reviewer")
    get_settings.cache_clear()
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer local-token"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["actor_id"]
    assert body["external_subject"] == "flow-subject-1"
    assert body["external_issuer"] == "flow-dev-issuer"
    assert body["email"] is None
    assert body["display_name"] is None
    assert body["roles"] == ["worker", "reviewer"]
    assert body["auth_source"] == "dev_mock"
    assert body["is_dev_auth"] is True
    assert body["audit_context"]["actor_id"] == body["actor_id"]
    assert body["audit_context"]["external_subject"] == "flow-subject-1"
    assert body["audit_context"]["external_issuer"] == "flow-dev-issuer"
    assert body["audit_context"]["auth_source"] == "dev_mock"
    assert body["audit_context"]["is_dev_auth"] is True


async def test_auth_me_maps_actor_registry_failure_to_service_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    auth_database_env: str,
) -> None:
    monkeypatch.setenv("WORKSTREAM_AUTH_PROVIDER", "dev")
    monkeypatch.setenv("WORKSTREAM_ENVIRONMENT", "local")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_TOKEN", "local-token")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_SUBJECT", "registry-failure-subject")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_ISSUER", "flow-dev-issuer")
    monkeypatch.setenv("WORKSTREAM_DEV_AUTH_ROLES", "worker")
    get_settings.cache_clear()

    async def fail_register_actor(self, actor):
        raise SQLAlchemyError("registry unavailable")

    monkeypatch.setattr(ActorService, "register_actor", fail_register_actor)
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer local-token"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "Actor registry unavailable"
    assert response.json()["error"]["code"] == "service_unavailable"
    assert response.json()["error"]["message"] == "Service unavailable"
    assert response.json()["error"]["retryable"] is True


async def test_actor_id_uses_subject_and_issuer_not_email() -> None:
    first = Settings(
        environment="local",
        auth_provider="dev",
        dev_auth_token="local-token",
        dev_auth_subject="same-subject",
        dev_auth_issuer="same-issuer",
        dev_auth_email="first@example.test",
    )
    second = Settings(
        environment="local",
        auth_provider="dev",
        dev_auth_token="local-token",
        dev_auth_subject="same-subject",
        dev_auth_issuer="same-issuer",
        dev_auth_email="second@example.test",
    )

    first_actor = (await DevelopmentAuthVerifier(first).verify(first.dev_auth_token)).legacy_actor()
    second_actor = (
        await DevelopmentAuthVerifier(second).verify(second.dev_auth_token)
    ).legacy_actor()

    assert first_actor.actor_id == second_actor.actor_id
    assert first_actor.email is None
    assert second_actor.email is None


@pytest.mark.parametrize("environment", ["production", "prod", "staging", "preview"])
def test_dev_auth_requires_explicit_development_environment(environment: str) -> None:
    settings = Settings(
        environment=environment,
        auth_provider="dev",
        dev_auth_token="local-token",
        dev_auth_subject="subject",
        dev_auth_issuer="issuer",
    )

    with pytest.raises(RuntimeError, match="development auth cannot run in production"):
        DevelopmentAuthVerifier(settings)


@pytest.mark.parametrize("environment", ["local", "dev", "development", "test"])
def test_dev_auth_allows_only_development_environments(environment: str) -> None:
    verifier = DevelopmentAuthVerifier(
        Settings(
            environment=environment,
            auth_provider="dev",
            dev_auth_token="local-token",
            dev_auth_subject="subject",
            dev_auth_issuer="issuer",
        )
    )

    assert verifier


@pytest.mark.parametrize(
    ("field_name", "error_message"),
    [
        ("dev_auth_token", "WORKSTREAM_DEV_AUTH_TOKEN must be set"),
        ("dev_auth_subject", "WORKSTREAM_DEV_AUTH_SUBJECT must be set"),
        ("dev_auth_issuer", "WORKSTREAM_DEV_AUTH_ISSUER must be set"),
    ],
)
def test_dev_auth_requires_explicit_identity_fields(
    field_name: str,
    error_message: str,
) -> None:
    values = {
        "environment": "local",
        "auth_provider": "dev",
        "dev_auth_token": "local-token",
        "dev_auth_subject": "subject",
        "dev_auth_issuer": "issuer",
    }
    values[field_name] = None
    settings = Settings(**values)

    with pytest.raises(RuntimeError, match=error_message):
        DevelopmentAuthVerifier(settings)


async def test_flow_auth_verifier_boundary_rejects_unconfigured_verification() -> None:
    with pytest.raises(RuntimeError, match="WORKSTREAM_TOKEN_ISSUER"):
        FlowAuthVerifier(Settings(auth_provider="flow"))


async def test_flow_role_normalization_ignores_non_string_values() -> None:
    assert normalize_legacy_roles(
        [
            "worker",
            {"api_key": "must-not-persist"},
            42,
            " reviewer ",
            "",
        ]
    ) == ("worker", "reviewer")


async def test_dev_role_normalization_uses_bounded_compatibility_contract() -> None:
    long_role = "x" * 129
    roles = ",".join([*(f"role-{index}" for index in range(35)), long_role])
    result = await DevelopmentAuthVerifier(
        Settings(
            environment="local",
            auth_provider="dev",
            dev_auth_token="local-token",
            dev_auth_subject="subject",
            dev_auth_issuer="issuer",
            dev_auth_roles=roles,
        )
    ).verify("local-token")

    assert result.legacy is not None
    assert result.legacy.roles == tuple(f"role-{index}" for index in range(32))


async def test_permission_policy_allows_required_role() -> None:
    actor = (
        await DevelopmentAuthVerifier(
            Settings(
                environment="local",
                auth_provider="dev",
                dev_auth_token="local-token",
                dev_auth_subject="subject",
                dev_auth_issuer="issuer",
                dev_auth_roles="worker,reviewer",
            )
        ).verify("local-token")
    ).legacy_actor()

    require_any_role(actor, {"reviewer"})


async def test_permission_policy_rejects_missing_role() -> None:
    actor = (
        await DevelopmentAuthVerifier(
            Settings(
                environment="local",
                auth_provider="dev",
                dev_auth_token="local-token",
                dev_auth_subject="subject",
                dev_auth_issuer="issuer",
                dev_auth_roles="worker",
            )
        ).verify("local-token")
    ).legacy_actor()

    with pytest.raises(PermissionDenied, match="actor lacks required role"):
        require_any_role(actor, {"finance"})


async def test_no_local_login_password_or_session_routes() -> None:
    app = create_app()
    paths = {path.lower() for path in _application_paths(app)}
    forbidden_segments = {
        "login",
        "signup",
        "register",
        "password",
        "password-reset",
        "session",
        "sessions",
    }

    assert "/api/v1/auth/me" in paths
    assert "/api/v1/demo/worker-profile" not in paths
    assert not any(
        segment in forbidden_segments for path in paths for segment in path.strip("/").split("/")
    )
