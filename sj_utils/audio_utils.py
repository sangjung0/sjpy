import numpy as np


def get_empty_chunk(dtype=np.float32) -> np.ndarray:
    return np.zeros((0,), dtype=dtype)
