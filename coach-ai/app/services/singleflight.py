import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")
_tasks: dict[str, asyncio.Task] = {}
_lock = asyncio.Lock()


async def run_singleflight(key: str, factory: Callable[[], Awaitable[T]]) -> T:
    """Share one in-process calculation among concurrent requests for the same key."""
    async with _lock:
        task = _tasks.get(key)
        if task is None:
            task = asyncio.create_task(factory())
            _tasks[key] = task

    try:
        return await asyncio.shield(task)
    finally:
        if task.done():
            async with _lock:
                if _tasks.get(key) is task:
                    _tasks.pop(key, None)
