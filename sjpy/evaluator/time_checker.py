from __future__ import annotations

import time

from contextlib import contextmanager
from collections.abc import Generator

from sjpy.statistics import summarize_distribution, DistributionSummary


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

    def metric(self) -> DistributionSummary:
        return summarize_distribution(self.__times)


__all__ = ["TimeChecker"]
