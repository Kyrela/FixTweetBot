"""Bounded helpers for work that must not block the Discord event loop."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from typing import TypeVar


T = TypeVar('T')


class RuntimeBusyError(RuntimeError):
    """Raised when bounded blocking work cannot start before its deadline."""


_database_concurrency = max(1, int(os.getenv('DATABASE_WORKER_CONCURRENCY', '8')))
_database_wait_timeout = max(0.01, float(os.getenv('DATABASE_WORKER_WAIT_TIMEOUT', '0.5')))
_database_semaphore = asyncio.Semaphore(_database_concurrency)


async def run_database(func: Callable[..., T], *args, **kwargs) -> T:
    """Run synchronous ORM work off-loop with bounded concurrency and wait time."""

    try:
        await asyncio.wait_for(_database_semaphore.acquire(), timeout=_database_wait_timeout)
    except asyncio.TimeoutError as exc:
        raise RuntimeBusyError('database worker capacity exhausted') from exc

    try:
        return await asyncio.to_thread(func, *args, **kwargs)
    finally:
        _database_semaphore.release()
