"""Cancellation-resistant async ownership handoffs."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar


CancellationResult = TypeVar("CancellationResult")


async def await_cancellation_resistant(
    awaitable: Awaitable[CancellationResult],
) -> CancellationResult:
    """Finish an ownership handoff despite repeated caller cancellation."""
    task = asyncio.ensure_future(awaitable)
    while True:
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            if task.done():
                return task.result()
