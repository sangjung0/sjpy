import ffmpeg
import io
import warnings
import tempfile
import subprocess
import numpy as np
import soundfile as sf

from scipy.io import wavfile
from scipy.signal import resample_poly


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


def s16le_bytes_to_array(
    pcm: bytes, channels: int = 1, dtype: np.dtype = np.float32
) -> np.ndarray:
    a = np.frombuffer(pcm, dtype="<i2")
    if a.size % channels != 0:
        raise ValueError("bytes not divisible by channels")
    a = a.reshape(-1, channels)
    if dtype == np.float32:
        return a.astype(np.float32) / 32768.0
    elif dtype == np.int16:
        return a
    else:
        raise ValueError("dtype must be np.float32 or np.int16")


def array_to_s16le(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x)
    if x.ndim == 1:
        x = x[:, None]
    if np.issubdtype(x.dtype, np.floating):
        x = np.clip(x, -1.0, 1.0).astype(np.float32)
        x = (x * 32767.0).round().astype("<i2")
    elif x.dtype != np.int16:
        x = x.astype("<i2", copy=False)
    else:
        x = x.astype("<i2", copy=False)
    return x.reshape(-1)


def resample_wav(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    audio = np.asarray(audio)

    if audio.ndim == 1:
        audio = audio[:, None]
    elif audio.ndim != 2:
        raise ValueError("audio must be 1D or 2D (T,) or (T,C)")

    if np.issubdtype(audio.dtype, np.floating):
        input_format = "f32le"
        in_bytes = audio.astype(np.float32).tobytes()
    elif np.issubdtype(audio.dtype, np.integer):
        input_format = "s16le"
        in_bytes = audio.astype(np.int16).tobytes()
    else:
        raise TypeError(f"Unsupported dtype {audio.dtype}")

    process = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-f",
            input_format,
            "-ac",
            str(audio.shape[1]),
            "-ar",
            str(orig_sr),
            "-i",
            "pipe:0",
            "-ac",
            str(audio.shape[1]),
            "-ar",
            str(target_sr),
            "-f",
            "f32le",  # 출력은 float32 raw PCM
            "-acodec",
            "pcm_f32le",
            "pipe:1",
        ],
        input=in_bytes,
        stdout=subprocess.PIPE,
        check=True,
    )

    out = np.frombuffer(process.stdout, dtype=np.float32)
    if out.size % audio.shape[1] != 0:
        raise ValueError("Output size not divisible by channel count")
    return out.reshape(-1, audio.shape[1])


def compress_to_opus(bytes: bytes):
    process = subprocess.Popen(
        ["ffmpeg", "-i", "pipe:0", "-c:a", "libopus", "-f", "opus", "pipe:1"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,  # subprocess.DEVNULL 하면 속도 조금 더 빨라짐
    )

    out, err = process.communicate(input=bytes)
    return out, err


def decompress_from_opus(bytes: bytes):
    process = subprocess.Popen(
        ["ffmpeg", "-i", "pipe:0", "-f", "wav", "pipe:1"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = process.communicate(input=bytes)
    return out, err


def np_to_wav(audio: np.ndarray, sample_rate: int) -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format="wav")
    return buffer.getvalue()


def audio_bytes_to_np(bt: bytes, sample_rate: int) -> np.ndarray:
    with io.BytesIO(bt) as buffer:
        audio, sr = sf.read(buffer, dtype="float32")
    if sr != sample_rate:
        audio = resample_poly(audio, sample_rate, sr)
    return audio


__all__ = [
    "generate_empty_chunk",
    "segment",
    "load_from_mp4_file",
    "mp4_bytes_to_ndarray",
    "ndarray_to_mp4_bytes",
    "s16le_bytes_to_array",
    "array_to_s16le",
    "resample_wav",
    "compress_to_opus",
    "decompress_from_opus",
    "np_to_wav",
    "audio_bytes_to_np",
]
