import time
import numpy as np

from contextlib import contextmanager

from sj_utils.statistics import summarize_distribution


def compute_average_lagging(coverage: np.ndarray, L: float) -> float | None:
    coverage = np.asarray(coverage, dtype=np.float32)
    if coverage.ndim != 1:
        raise ValueError("coverage must be a 1-dimensional array")
    if not np.isfinite(coverage).all():
        raise ValueError("coverage must contain only finite values")
    if not np.isfinite(L):
        raise ValueError("L must be a finite value")
    if L <= 0:
        raise ValueError("L must be a positive value")
    if np.any(coverage > L):
        raise ValueError("all elements in coverage must be less than or equal to L")
    if not np.all(coverage[1:] >= coverage[:-1]):  # 단조 비감소
        raise ValueError("coverage must be a non-decreasing sequence")

    if coverage.size == 0:
        return None

    J = coverage.size
    idx = int(np.searchsorted(coverage, L, side="left"))
    tau = int(idx + 1) if idx < J else J
    j = np.arange(1, tau + 1, dtype=np.float32)
    return float(np.mean(coverage[:tau] - (j - 1) * (L / J)))


def compute_average_proportion(coverage: np.ndarray, L: float) -> float | None:
    coverage = np.asarray(coverage, dtype=np.float32)
    if coverage.ndim != 1:
        raise ValueError("coverage must be a 1-dimensional array")
    if not np.isfinite(coverage).all():
        raise ValueError("coverage must contain only finite values")
    if not np.isfinite(L):
        raise ValueError("L must be a finite value")
    if L <= 0:
        raise ValueError("L must be a positive value")
    if np.any(coverage > L):
        raise ValueError("all elements in coverage must be less than or equal to L")
    if not np.all(coverage[1:] >= coverage[:-1]):  # 단조 비감소
        raise ValueError("coverage must be a non-decreasing sequence")

    if coverage.size == 0:
        return None

    J = coverage.size
    ap = float(coverage.sum() / (L * J))
    return ap


class TimeEvaluator:
    def __init__(self, L: float):
        self.times = []
        self.coverages = np.asarray([], dtype=np.float32)
        self.L = L

    @contextmanager
    def timeit(self):
        start = time.time()
        try:
            yield
        finally:
            self.times.append(time.time() - start)

    def add_coverage(self, coverage: np.ndarray):
        coverage = np.asarray(coverage, dtype=np.float32)
        self.coverages = np.concatenate([self.coverages, coverage], axis=0)

    def metric(self):
        return {
            "average_lagging": self.get_avg_lagging(),
            "average_proportion": self.get_avg_proportion(),
            "time_stats": summarize_distribution(self.times),
        }

    def get_avg_lagging(self):
        return compute_average_lagging(self.coverages, self.L)

    def get_avg_proportion(self):
        return compute_average_proportion(self.coverages, self.L)


class TimeEvaluatorSummary:
    def __init__(self):
        self.times = []
        self.als = []
        self.aps = []

    def add(self, evaluator: TimeEvaluator):
        self.times.extend(evaluator.times)
        self.als.append(evaluator.get_avg_lagging())
        self.aps.append(evaluator.get_avg_proportion())

    def metric(self):
        als = [x for x in self.als if x is not None]
        aps = [x for x in self.aps if x is not None]
        average_lagging_stats = summarize_distribution(als)
        average_proportion_stats = summarize_distribution(aps)
        average_lagging_stats["count_null"] = len(self.als) - len(als)
        average_proportion_stats["count_null"] = len(self.aps) - len(aps)
        return {
            "average_lagging_stats": average_lagging_stats,
            "average_proportion_stats": average_proportion_stats,
            "time_stats": summarize_distribution(self.times),
        }


__all__ = [
    "compute_average_lagging",
    "compute_average_proportion",
    "TimeEvaluator",
    "TimeEvaluatorSummary",
]

