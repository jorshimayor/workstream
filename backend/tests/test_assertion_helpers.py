"""Tests for shared security-sensitive assertion helpers."""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pydantic import SecretStr
import pytest
from types import SimpleNamespace

from tests.assertion_helpers import assert_secret_not_retained


def test_secret_str_rejects_embedded_forbidden_value() -> None:
    """Reject a forbidden value even when wrapped by other secret text."""
    with pytest.raises(AssertionError):
        assert_secret_not_retained(SecretStr("prefix-forbidden-suffix"), "forbidden")


@pytest.mark.parametrize(
    "value",
    [b"prefix-forbidden-suffix", bytearray(b"forbidden"), memoryview(b"forbidden")],
)
def test_byte_buffers_reject_embedded_forbidden_value(value: object) -> None:
    """Reject a forbidden value retained in any supported byte buffer."""
    with pytest.raises(AssertionError):
        assert_secret_not_retained(value, "forbidden")


def test_public_object_state_rejects_nested_forbidden_value() -> None:
    """Reject a forbidden value reachable through public object state."""
    value = SimpleNamespace(payload={"body": b"prefix-forbidden-suffix"})

    with pytest.raises(AssertionError):
        assert_secret_not_retained(value, "forbidden")


def test_builtin_container_subclasses_cannot_hide_forbidden_values() -> None:
    """Inspect builtin storage without invoking hostile iteration overrides."""

    class HostileDict(dict[str, str]):
        def items(self):
            raise RuntimeError("hostile items")

    class HostileList(list[str]):
        def __iter__(self):
            raise RuntimeError("hostile iterator")

    class HostileString(str):
        def __contains__(self, item: object) -> bool:
            raise RuntimeError("hostile membership")

    for value in (
        HostileDict(value="forbidden"),
        HostileList(["forbidden"]),
        HostileString("forbidden"),
    ):
        with pytest.raises(AssertionError):
            assert_secret_not_retained(value, "forbidden")


def test_slotted_dataclass_state_rejects_forbidden_value() -> None:
    """Inspect slotted reservation-style records without requiring __dict__."""

    @dataclass(frozen=True, slots=True)
    class SlottedRecord:
        payload: str

    with pytest.raises(AssertionError):
        assert_secret_not_retained(SlottedRecord(payload="forbidden"), "forbidden")


def test_raising_mapping_falls_back_to_inspecting_object_state() -> None:
    """Fail closed on retained secrets when a framework mapping cannot iterate."""

    class RaisingMapping(Mapping[str, str]):
        def __init__(self, payload: str) -> None:
            self.payload = payload

        def __getitem__(self, key: str) -> str:
            raise RuntimeError(key)

        def __iter__(self) -> Iterator[str]:
            raise RuntimeError("opaque framework mapping")

        def __len__(self) -> int:
            return 1

    with pytest.raises(AssertionError):
        assert_secret_not_retained(RaisingMapping("forbidden"), "forbidden")
