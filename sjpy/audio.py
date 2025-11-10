import ffmpeg
import io
import warnings
import tempfile
import subprocess
import numpy as np

from scipy.io import wavfile


def generate_empty_chunk(dtype=np.float32) -> np.ndarray:
    return np.zeros((0,), dtype=dtype)


def segment(
    audio: np.ndarray,
    mean: int = 48000,
    std: int = 0,
    max_div: int = 0,
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


def load_from_mp4_file(
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


def mp4_bytes_to_ndarray(mp4_bytes: bytes, sr: int = 16000) -> np.ndarray:
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_in:
        tmp_in.write(mp4_bytes)
        tmp_in.flush()

        process = subprocess.Popen(
            [
                "ffmpeg",
                "-i",
                tmp_in.name,  # ← 파일 기반 입력
                "-f",
                "f32le",  # 출력 포맷: float32 PCM
                "-acodec",
                "pcm_f32le",  # codec: float32 PCM
                "-ac",
                "1",  # mono
                "-ar",
                str(sr),  # sample rate
                "pipe:1",  # 출력: stdout
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        out, _ = process.communicate()
        return np.frombuffer(out, dtype=np.float32)


def ndarray_to_mp4_bytes(audio: np.ndarray, sr: int = 16000) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_out:
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-f",
                "f32le",
                "-ac",
                "1",
                "-ar",
                str(sr),
                "-i",
                "pipe:0",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-y",  # overwrite
                tmp_out.name,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        in_bytes = audio.astype(np.float32).tobytes()
        process.communicate(input=in_bytes)
        tmp_out.seek(0)
        return tmp_out.read()


def pcm_s16le_resample_ffmpeg(
    pcm_bytes: bytes,
    orig_sr: int,
    target_sr: int,
    channels: int = 1,
) -> np.ndarray | bytes:
    proc = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-f",
            "s16le",
            "-ar",
            str(orig_sr),
            "-ac",
            str(channels),
            "-i",
            "pipe:0",
            "-ac",
            str(channels),
            "-ar",
            str(target_sr),
            "-f",
            "f32le",
            "-acodec",
            "pcm_f32le",
            "pipe:1",
        ],
        input=pcm_bytes,
        stdout=subprocess.PIPE,
        check=True,
    )
    out = proc.stdout
    arr = np.frombuffer(out, dtype=np.float32)
    # (T, C)로 reshape
    if arr.size % channels != 0:
        raise ValueError("ffmpeg output size not divisible by channels")
    return arr.reshape(-1, channels)


__all__ = [
    "generate_empty_chunk",
    "segment",
    "load_from_mp4_file",
    "mp4_bytes_to_ndarray",
    "ndarray_to_mp4_bytes",
    "pcm_s16le_resample_ffmpeg",
]
