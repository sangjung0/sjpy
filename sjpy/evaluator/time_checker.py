from __future__ import annotations

import time

from typing import Any
from contextlib import contextmanager
from collections.abc import Generator

from sjpy.statistics import summarize_distribution


class TimeChecker:
    def __init__(self) -> None:
        self.__times: list[float] = []

    def get_times(self) -> list[float]:
        return self.__times.copy()

    @contextmanager
    def timeit(self) -> Generator[None, None, None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.__times.append(elapsed)

    def metric(self) -> dict[str, Any]:
        return summarize_distribution(self.__times)


__all__ = ["TimeChecker"]
