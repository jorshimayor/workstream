"""Shared deep assertions for security-sensitive test object graphs."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import SecretStr, ValidationError


def assert_secret_not_retained(
    value: object,
    secret: str,
    seen: set[int] | None = None,
) -> None:
    """Assert a secret is unreachable through an error's public object graph."""
    if seen is None:
        seen = set()
    if id(value) in seen:
        return
    seen.add(id(value))
    if isinstance(value, str):
        assert secret not in value
    elif isinstance(value, SecretStr):
        assert secret not in value.get_secret_value()
    elif isinstance(value, BaseException):
        if isinstance(value, ValidationError):
            assert_secret_not_retained(value.errors(), secret, seen)
        assert_secret_not_retained(value.args, secret, seen)
        assert_secret_not_retained(vars(value), secret, seen)
        assert_secret_not_retained(value.__cause__, secret, seen)
        assert_secret_not_retained(value.__context__, secret, seen)
    elif isinstance(value, Mapping):
        for key, item in value.items():
            assert_secret_not_retained(key, secret, seen)
            assert_secret_not_retained(item, secret, seen)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            assert_secret_not_retained(item, secret, seen)
