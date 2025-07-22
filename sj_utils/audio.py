import numpy as np
import ffmpeg
import io

from scipy.io import wavfile


def generate_empty_chunk(dtype=np.float32) -> np.ndarray:
    return np.zeros((0,), dtype=dtype)


def segment_audio(
    audio: np.ndarray,
    mean: int = 48000,
    std: int = 400,
    ratio: float = 0.1,
    rng: np.random.Generator | np.random.RandomState = np.random,
):
    min_len = int(mean * (1 - ratio))
    max_len = int(mean * (1 + ratio))
    segments = []
    length = len(audio)

    start = 0
    while start < length:
        read_len = np.clip(int(rng.normal(mean, std)), min_len, max_len)
        end = min(start + read_len, length)
        segments.append(audio[start:end])
        start = end

    return segments


def load_audio_from_mp4(mp4_path: str, sr: int = 16000) -> tuple[np.ndarray, int]:

    out, _ = (
        ffmpeg.input(mp4_path)
        .output("pipe:", format="wav", ac=1, ar=sr)
        .run(capture_stdout=True, capture_stderr=True)
    )

    sample_rate, waveform = wavfile.read(io.BytesIO(out))

    if waveform.dtype != np.float32:
        waveform = waveform.astype(np.float32) / np.iinfo(waveform.dtype).max

    return waveform, sample_rate


__all__ = [
    "generate_empty_chunk",
    "segment_audio",
    "load_audio_from_mp4",
]
