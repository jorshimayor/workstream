"""Auth verifier factory functions."""

from __future__ import annotations

from threading import Lock

from app.adapters.auth.dev import DevelopmentAuthVerifier
from app.adapters.auth.flow import FlowAuthVerifier
from app.core.config import Settings, get_settings
from app.interfaces.auth import AuthVerificationUnavailableError, AuthVerifier
from app.schemas.auth import AuthVerificationResult


class _UnavailableAuthVerifier:
    """Fail-closed verifier returned when production configuration is invalid."""

    async def verify(self, token: str) -> AuthVerificationResult:
        raise AuthVerificationUnavailableError("token verification is unavailable")


_cached_flow_settings: Settings | None = None
_cached_flow_verifier: AuthVerifier | None = None
_flow_cache_lock = Lock()


def build_auth_verifier(settings: Settings) -> AuthVerifier:
    """Build the configured auth verifier.

    Args:
        settings: Application settings selecting the auth provider.

    Returns:
        Auth verifier implementation for the selected provider.
    """
    if settings.auth_provider == "dev":
        return DevelopmentAuthVerifier(settings)
    return FlowAuthVerifier(settings)


def get_auth_verifier() -> AuthVerifier:
    """Return the process-lifetime auth verifier dependency.

    Returns:
        Auth verifier built from cached application settings.
    """
    global _cached_flow_settings, _cached_flow_verifier

    settings = get_settings()
    if settings.auth_provider == "dev":
        try:
            return build_auth_verifier(settings)
        except RuntimeError:
            return _UnavailableAuthVerifier()
    with _flow_cache_lock:
        if settings is _cached_flow_settings and _cached_flow_verifier is not None:
            return _cached_flow_verifier
        try:
            verifier = build_auth_verifier(settings)
        except RuntimeError:
            verifier = _UnavailableAuthVerifier()
        _cached_flow_settings = settings
        _cached_flow_verifier = verifier
        return verifier


def clear_auth_verifier_cache() -> None:
    """Clear process verifier state for deterministic configuration tests."""
    global _cached_flow_settings, _cached_flow_verifier

    with _flow_cache_lock:
        _cached_flow_settings = None
        _cached_flow_verifier = None
