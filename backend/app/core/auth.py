from __future__ import annotations

from app.adapters.auth.dev import DevelopmentAuthVerifier
from app.adapters.auth.flow import FlowAuthVerifier
from app.core.config import Settings, get_settings
from app.interfaces.auth import AuthVerifier


def build_auth_verifier(settings: Settings) -> AuthVerifier:
    if settings.auth_provider == "dev":
        return DevelopmentAuthVerifier(settings)
    return FlowAuthVerifier(settings)


def get_auth_verifier() -> AuthVerifier:
    return build_auth_verifier(get_settings())
