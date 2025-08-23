import ffmpeg
import io
import warnings
import numpy as np

from scipy.io import wavfile


def generate_empty_chunk(dtype=np.float32) -> np.ndarray:
    return np.zeros((0,), dtype=dtype)


def segment_audio(
    audio: np.ndarray,
    mean: int = 48000,
    std: int = 400,
    max_div: int = 4800,
    rng: np.random.Generator | np.random.RandomState = np.random,
):
    segments = []
    length = len(audio)

    start = 0
    while start < length:
        read_len = np.clip(int(rng.normal(mean, std)), mean - max_div, mean + max_div)
        end = min(start + read_len, length)
        segments.append(audio[start:end])
        start = end

    return segments


def load_audio_from_mp4(
    mp4_path: str, sr: int = 16000, dtype: type | np.dtype = np.float32
) -> tuple[np.ndarray, int]:

    out, _ = (
        ffmpeg.input(mp4_path)
        .output("pipe:", format="wav", ac=1, ar=sr)  # mono, target sr
        .run(capture_stdout=True, capture_stderr=True)
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=wavfile.WavFileWarning)
        sample_rate, waveform = wavfile.read(io.BytesIO(out))  # may return int or float

    desired = np.dtype(dtype)

    if np.issubdtype(desired, np.floating):
        if np.issubdtype(waveform.dtype, np.integer):
            info = np.iinfo(waveform.dtype)
            scale = max(abs(info.min), info.max)
            waveform = waveform.astype(np.float32) / float(scale)
        elif not np.issubdtype(waveform.dtype, np.floating):
            waveform = waveform.astype(np.float32)
        waveform = waveform.astype(desired, copy=False)

    elif np.issubdtype(desired, np.integer):
        if np.issubdtype(waveform.dtype, np.floating):
            info = np.iinfo(desired)
            scale = float(info.max)
            waveform = np.clip(waveform, -1.0, 1.0)
            waveform = (waveform * scale).round().astype(desired)
        else:
            dst_info = np.iinfo(desired)
            waveform = np.clip(waveform, dst_info.min, dst_info.max).astype(desired)

    else:
        waveform = waveform.astype(desired)

    return waveform, sample_rate


__all__ = [
    "generate_empty_chunk",
    "segment_audio",
    "load_audio_from_mp4",
]

