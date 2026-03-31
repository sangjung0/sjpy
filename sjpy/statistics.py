from __future__ import annotations

import math
import numpy as np

from typing import Any
from collections.abc import Sequence

from scipy.stats import skew, kurtosis


def update_mean_std(
    old_mean: float,
    old_std: float,
    old_count: int,
    new_mean: float,
    new_std: float,
    new_count: int,
) -> tuple[float, float]:
    if old_count == 0:
        return new_mean, new_std
    if new_count == 0:
        return old_mean, old_std

    total_count = old_count + new_count
    updated_mean = (old_mean * old_count + new_mean * new_count) / total_count

    updated_std = math.sqrt(
        (
            old_count * (old_std**2 + (old_mean - updated_mean) ** 2)
            + new_count * (new_std**2 + (new_mean - updated_mean) ** 2)
        )
        / total_count
    )

    return updated_mean, updated_std


def summarize_distribution(
    data: Sequence[int | float],
    hist_bins: int = 10,
) -> dict[str, Any]:
    if len(data) == 0:
        return {
            "n": 0,
            "mean": None,
            "std": None,
            "min": None,
            "q1": None,
            "q2": None,
            "q3": None,
            "max": None,
            "iqr": None,
            "skew": None,
            "kurtosis": None,
            "histogram": {
                "bin_edges": [],
                "bin_probs": [],
            },
        }

    array = np.array(data, dtype=np.float64)
    n = len(array)
    mean = float(np.mean(array))
    std = float(np.std(array))
    _min = float(np.min(array))
    q1 = float(np.percentile(array, 25))
    q2 = float(np.percentile(array, 50))
    q3 = float(np.percentile(array, 75))
    _max = float(np.max(array))
    iqr = q3 - q1
    _skew = float(skew(array))
    _kurtosis = float(kurtosis(array))

    hist, bin_edges = np.histogram(array, bins=hist_bins, density=True)
    bin_probs = hist / hist.sum()

    return {
        "n": n,
        "mean": mean,
        "std": std,
        "min": _min,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "max": _max,
        "iqr": iqr,
        "skew": _skew,
        "kurtosis": _kurtosis,
        "histogram": {
            "bin_edges": bin_edges.tolist(),
            "bin_probs": bin_probs.tolist(),
        },
    }


__all__ = [
    "update_mean_std",
    "summarize_distribution",
]
