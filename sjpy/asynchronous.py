import asyncio

from logging import Logger
from typing import Callable, TypeVar, Awaitable

from sjpy.excptn import exc_to_str

T = TypeVar("T")


def task_with_callback(
    task: Awaitable[T],
    callback: Callable[[T | None, Exception | None], Awaitable[None]],
    logger: Logger | None = None,
) -> Awaitable[None]:
    async def _run() -> None:
        try:
            result = await task
            await callback(result, None)
        except Exception as e:
            # NOTE 필요할까
            logger and logger.error(f"Error in callback:\n{exc_to_str(e)}")
            await callback(None, e)

    return _run()


def task_with_callback_guarded(
    task: Awaitable[T],
    callback: Callable[[T | None, Exception | None], Awaitable[None]],
    lock: asyncio.Lock,
    stop_event: asyncio.Event,
    logger: Logger | None = None,
) -> Awaitable[None]:
    async def _run() -> None:
        try:
            async with lock:
                if stop_event.is_set():
                    await callback(
                        None, Exception("Operation cancelled due to stop event")
                    )
                else:
                    result = await task
                    await callback(result, None)
        except Exception as e:
            logger and logger.error(f"Error in callback:\n{exc_to_str(e)}")
            await callback(None, e)

    return _run()


def spawn_task_with_callback(
    task: Awaitable[T],
    callback: Callable[[T | None, Exception | None], Awaitable[None]],
    logger: Logger | None = None,
) -> None:
    task = task_with_callback(task, callback, logger)
    asyncio.create_task(task)


def spawn_task_with_callback_guarded(
    task: Awaitable[T],
    callback: Callable[[T | None, Exception | None], Awaitable[None]],
    lock: asyncio.Lock,
    stop_event: asyncio.Event,
    logger: Logger | None = None,
):
    task = task_with_callback_guarded(task, callback, lock, stop_event, logger)
    asyncio.create_task(task)


def spawn_task_queue_worker(
    queue: asyncio.Queue[Awaitable | None],
    lock: asyncio.Lock,
    stop_event: asyncio.Event,
    logger: Logger | None = None,
) -> None:
    async def _run() -> None:
        while True:
            task = await queue.get()
            if task is None:
                break
            try:
                async with lock:
                    if stop_event.is_set():
                        break
                    await task
            except Exception as e:
                print(exc_to_str(e))
                logger and logger.error(f"Error in queued task:\n{exc_to_str(e)}")

    asyncio.create_task(_run())


__all__ = [
    "task_with_callback",
    "task_with_callback_guarded",
    "spawn_task_with_callback",
    "spawn_task_with_callback_guarded",
    "spawn_task_queue_worker",
]
