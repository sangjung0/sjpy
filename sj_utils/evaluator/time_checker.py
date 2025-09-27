import time

from contextlib import contextmanager

from sj_utils.statistics import summarize_distribution


class TimeChecker:
    def __init__(self):
        self.__times = []

    @contextmanager
    def timeit(self):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.__times.append(elapsed)

    def metric(self):
        return summarize_distribution(self.__times)


__all__ = ["TimeChecker"]
