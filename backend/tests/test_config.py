from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_default_settings_are_fail_closed() -> None:
    settings = Settings()

    assert settings.app_name == "Workstream API"
    assert settings.environment == "production"
    assert settings.auth_provider == "flow"
    assert settings.database_url is None
    assert settings.dev_auth_token is None


def test_settings_reject_unknown_environment() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="unknown")
