"""Tests for shared security-sensitive assertion helpers."""

from pydantic import SecretStr
import pytest

from tests.assertion_helpers import assert_secret_not_retained


def test_secret_str_rejects_embedded_forbidden_value() -> None:
    """Reject a forbidden value even when wrapped by other secret text."""
    with pytest.raises(AssertionError):
        assert_secret_not_retained(SecretStr("prefix-forbidden-suffix"), "forbidden")
