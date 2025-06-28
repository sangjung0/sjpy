import numpy as np


def generate_empty_chunk(dtype=np.float32) -> np.ndarray:
    return np.zeros((0,), dtype=dtype)

def segment_audio(
    audio:np.ndarray, mean:int = 48000, std:int = 400, ratio:float = 0.1
):
    min_len = int(mean * (1 - ratio))
    max_len = int(mean * (1 + ratio))
    segments = []
    length = len(audio)

    start = 0
    while start < length:
        read_len = np.clip(
            int(np.random.normal(mean, std)), min_len, max_len
        )
        end = min(start + read_len, length)
        segments.append(audio[start:end])
        start = end

    return segments

