import asyncio

from logging import Logger
from typing import Callable, TypeVar, Awaitable

T = TypeVar("T")


def callback_waiter(
    task: Awaitable,
    callback: Callable[[T | None, Exception | None], Awaitable[None]],
    logger: Logger | None = None,
) -> None:
    async def _run() -> None:
        try:
            result = await task
            await callback(result, None)
        except Exception as e:
            # 흠 필요할까
            logger and logger.error(f"Error in callback: {e}")
            await callback(None, e)

    asyncio.create_task(_run())


__all__ = ["callback_waiter"]
