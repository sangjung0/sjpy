import time


class TimeChecker:
    def __init__(self):
        self.__time = 0
        self.__count = 0
        self.__total_time = 0

        self.__mean = 0
        self.__max = 0
        self.__min = float("inf")

    def start(self):
        self.__time = time.perf_counter()

    def check(self):
        elapsed = time.perf_counter() - self.__time
        self.__count += 1
        self.__total_time += elapsed

        if elapsed > self.__max:
            self.__max = elapsed
        if elapsed < self.__min:
            self.__min = elapsed

        self.__mean = self.__total_time / self.__count

        return elapsed

    def metric(self):
        return {
            "mean": self.__mean,
            "max": self.__max,
            "min": self.__min,
            "count": self.__count,
            "total_time": self.__total_time,
        }
