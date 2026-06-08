"""Flow auth verifier boundary for external authentication tokens."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
from datetime import UTC, datetime
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from app.core.config import Settings
from app.interfaces.auth import AuthVerificationError
from app.schemas.auth import ActorContext

LOCAL_FLOW_AUTH_ENVIRONMENTS = {"local", "dev", "development", "test"}


def actor_id_from_flow_identity(external_issuer: str, external_subject: str) -> str:
    """Build a stable Workstream actor id from Flow issuer and subject.

    Args:
        external_issuer: Issuer that signed the Flow token.
        external_subject: Subject inside the Flow token.

    Returns:
        Deterministic actor id for the issuer and subject pair.
    """
    return str(uuid5(NAMESPACE_URL, f"{external_issuer}:{external_subject}"))


def _decode_base64url(value: str) -> bytes:
    """Decode one unpadded base64url token segment.

    Args:
        value: JWT segment to decode.

    Returns:
        Decoded bytes.

    Raises:
        AuthVerificationError: If the segment is malformed.
    """
    try:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(f"{value}{padding}")
    except (binascii.Error, ValueError) as exc:
        raise AuthVerificationError("malformed Flow token segment") from exc


def _decode_json_segment(value: str) -> dict[str, Any]:
    """Decode a JSON object from one base64url token segment.

    Args:
        value: JWT segment containing a JSON object.

    Returns:
        Decoded JSON object.

    Raises:
        AuthVerificationError: If the segment is not a JSON object.
    """
    try:
        decoded = json.loads(_decode_base64url(value))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AuthVerificationError("malformed Flow token JSON") from exc
    if not isinstance(decoded, dict):
        raise AuthVerificationError("malformed Flow token JSON")
    return decoded


def _normalize_roles(value: Any) -> tuple[str, ...]:
    """Normalize Flow role claims into a role tuple.

    Args:
        value: Role claim supplied as a list, tuple, set, or comma-separated
            string.

    Returns:
        Normalized non-empty role names.
    """
    if isinstance(value, str):
        raw_roles = value.split(",")
    elif isinstance(value, list | tuple | set):
        raw_roles = value
    else:
        raw_roles = ()
    return tuple(str(role).strip() for role in raw_roles if str(role).strip())


class FlowAuthVerifier:
    """Production Flow token verifier boundary.

    Chunk 2 defines the adapter boundary without adding network verification. The
    concrete Flow verification client is added when Flow auth details are wired.
    """

    def __init__(self, settings: Settings) -> None:
        """Create the Flow verifier boundary from application settings.

        Args:
            settings: Application settings containing Flow auth configuration.
        """
        self._issuer = settings.flow_auth_issuer
        self._audience = settings.flow_auth_audience
        self._local_hmac_secret = settings.flow_auth_local_hmac_secret
        if (
            self._local_hmac_secret
            and settings.environment.strip().lower() not in LOCAL_FLOW_AUTH_ENVIRONMENTS
        ):
            raise RuntimeError("local Flow auth verifier cannot run outside local/test")

    async def verify(self, token: str) -> ActorContext:
        """Verify a Flow bearer token.

        Args:
            token: Bearer token from the incoming request.

        Raises:
            AuthVerificationError: If Flow verification is not configured or
                the token is invalid.
        """
        if self._local_hmac_secret:
            return self._verify_local_hmac_token(token)
        raise AuthVerificationError(
            f"Flow token verification is not configured for issuer {self._issuer}"
        )

    def _verify_local_hmac_token(self, token: str) -> ActorContext:
        """Verify a local Flow-compatible HMAC token for real API QA runs.

        Args:
            token: Bearer token supplied by an HTTP client.

        Returns:
            Trusted actor context derived from the token claims.

        Raises:
            AuthVerificationError: If token shape, signature, or claims fail.
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise AuthVerificationError("malformed Flow token")

        header_segment, payload_segment, signature_segment = parts
        header = _decode_json_segment(header_segment)
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            raise AuthVerificationError("unsupported Flow token header")

        signed_content = f"{header_segment}.{payload_segment}".encode()
        expected_signature = hmac.new(
            self._local_hmac_secret.encode(),
            signed_content,
            hashlib.sha256,
        ).digest()
        supplied_signature = _decode_base64url(signature_segment)
        if not hmac.compare_digest(expected_signature, supplied_signature):
            raise AuthVerificationError("invalid Flow token signature")

        claims = _decode_json_segment(payload_segment)
        subject = claims.get("sub")
        issuer = claims.get("iss")
        audience = claims.get("aud")
        if not isinstance(subject, str) or not subject:
            raise AuthVerificationError("Flow token subject is required")
        if issuer != self._issuer:
            raise AuthVerificationError("Flow token issuer is invalid")
        if audience != self._audience:
            raise AuthVerificationError("Flow token audience is invalid")

        now = datetime.now(UTC).timestamp()
        expires_at = claims.get("exp")
        not_before = claims.get("nbf")
        if not isinstance(expires_at, int | float):
            raise AuthVerificationError("Flow token expiry is required")
        if expires_at <= now:
            raise AuthVerificationError("Flow token is expired")
        if not_before is not None and not isinstance(not_before, int | float):
            raise AuthVerificationError("Flow token not-before claim is invalid")
        if isinstance(not_before, int | float) and not_before > now:
            raise AuthVerificationError("Flow token is not active")

        return ActorContext(
            actor_id=actor_id_from_flow_identity(issuer, subject),
            external_subject=subject,
            external_issuer=issuer,
            email=claims.get("email") if isinstance(claims.get("email"), str) else None,
            display_name=claims.get("name") if isinstance(claims.get("name"), str) else None,
            roles=_normalize_roles(claims.get("roles", ())),
            claim_snapshot=claims,
            auth_source="flow",
            is_dev_auth=False,
        )
