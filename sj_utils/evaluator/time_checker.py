import time

from sj_utils.statistics import summarize_distribution


class TimeChecker:
    def __init__(self):
        self.__time = 0
        self.__times = []

    def start(self):
        self.__time = time.perf_counter()

    def check(self):
        elapsed = time.perf_counter() - self.__time
        self.__times.append(elapsed)
        return elapsed

    def metric(self):
        return summarize_distribution(self.__times)
