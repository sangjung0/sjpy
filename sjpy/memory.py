from __future__ import annotations
from typing import TYPE_CHECKING

import os
import time
import gc
import threading
import psutil
import multiprocessing as mp

from contextlib import ContextDecorator
from queue import Queue
from logging import Logger

from sjpy.logger import generate

if TYPE_CHECKING:
    from multiprocessing import synchronize


def _sampler_proc(
    pid: int,
    sample_ms: int,
    include_children: bool,
    stop_evt: synchronize.Event | threading.Event,
    out_q: mp.Queue | Queue,
):
    peak_rss = 0
    peak_uss = 0
    samples = 0
    start_t = time.perf_counter()
    sleep_s = max(sample_ms, 1) / 1000.0
    while not stop_evt.is_set():
        m = _mem_of(pid, include_children)
        if m["rss"] > peak_rss:
            peak_rss = m["rss"]
        if m["uss"] > peak_uss:
            peak_uss = m["uss"]
        samples += 1
        time.sleep(sleep_s)
    duration = time.perf_counter() - start_t
    out_q.put(
        {
            "peak_rss": peak_rss,
            "peak_uss": peak_uss,
            "samples": samples,
            "duration": duration,
        },
        block=False,
    )


def _mem_of(pid: int, include_children: bool = False) -> dict[str, int]:
    rss = 0
    uss = 0
    try:
        p = psutil.Process(pid)
        procs = [p] + (p.children(recursive=True) if include_children else [])
        for q in procs:
            try:
                mi = q.memory_full_info()  # rss, uss
                rss += getattr(mi, "rss", 0) or 0
                uss += getattr(mi, "uss", 0) or 0
            except psutil.Error:
                pass
    except psutil.Error:
        pass
    return {"rss": rss, "uss": uss}


class MemScope(ContextDecorator):
    def __init__(
        self,
        sample_ms: int = 50,
        include_children: bool = False,
        backend: str = "process",
        logger: Logger | None = None,
    ):
        assert backend in ("process", "thread")

        if logger is None:
            logger = generate(__name__)

        self.logger = logger
        self.sample_ms = sample_ms
        self.include_children = include_children
        self.backend = backend

        self._target_pid = os.getpid()
        self._stop_evt: synchronize.Event | threading.Event | None = None
        self._queue: mp.Queue | Queue | None = None
        self._worker: mp.Process | threading.Thread | None = None

        self._t0: float | None = None
        self.stats: dict[str, float | int] = {}

    def _proc_work(self):
        self._stop_evt = mp.Event()
        self._queue = mp.Queue(maxsize=1)
        self._worker = mp.Process(
            target=_sampler_proc,
            args=(
                self._target_pid,
                self.sample_ms,
                self.include_children,
                self._stop_evt,
                self._queue,
            ),
            daemon=True,
        )
        self._worker.start()

    def _thread_work(self):
        self._stop_evt = threading.Event()
        self._queue = Queue(maxsize=1)
        self._worker = threading.Thread(
            target=_sampler_proc,
            args=(
                self._target_pid,
                self.sample_ms,
                self.include_children,
                self._stop_evt,
                self._queue,
            ),
            daemon=True,
        )
        self._worker.start()

    def __enter__(self):
        gc.collect()
        self._start = _mem_of(self._target_pid, self.include_children)
        if self.backend == "process":
            # process 백엔드(오버헤드↑, 간섭↓)
            self._proc_work()
        else:
            # thread 백엔드(오버헤드↓, 간섭↑)
            self._thread_work()
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop_evt.set()
        self._worker.join(timeout=2.0)

        # 종료 측정
        gc.collect()
        end = _mem_of(self._target_pid, self.include_children)

        try:
            msg = self._queue.get_nowait()
        except Exception as e:
            self.logger.warning(f"[MemScope]: unable to get stats from worker: {e}")
            msg = {}

        peak_rss = msg.get("peak_rss", None) or max(self._start["rss"], end["rss"])
        peak_uss = msg.get("peak_uss", None) or max(self._start["uss"], end["uss"])
        samples = msg.get("samples", None) or 0
        duration = msg.get("duration", None) or (time.perf_counter() - self._t0)

        self.stats = {
            "rss_start": self._start["rss"],
            "rss_end": end["rss"],
            "rss_delta": end["rss"] - self._start["rss"],
            "rss_peak_in_block": peak_rss,
            "rss_peak_over_start_delta": peak_rss - self._start["rss"],
            "uss_start": self._start["uss"],
            "uss_end": end["uss"],
            "uss_delta": end["uss"] - self._start["uss"],
            "uss_peak_in_block": peak_uss,
            "uss_peak_over_start_delta": peak_uss - self._start["uss"],
            "duration_s": duration,
            "samples": samples,
            "include_children": self.include_children,
            "backend": self.backend,
            "sample_ms": self.sample_ms,
        }

        def mib(x: int) -> float:
            return x / (1024 * 1024)

        log = (
            "[MemScope]\n"
            f"  RSS: start={mib(self.stats['rss_start']):.1f} MiB, "
            f"end={mib(self.stats['rss_end']):.1f} MiB, "
            f"delta={mib(self.stats['rss_delta']):+.1f} MiB, "
            f"peak={mib(self.stats['rss_peak_in_block']):.1f} MiB "
            f"(+{mib(self.stats['rss_peak_over_start_delta']):.1f} over start)\n"
            f"  USS: start={mib(self.stats['uss_start']):.1f} MiB, "
            f"end={mib(self.stats['uss_end']):.1f} MiB, "
            f"delta={mib(self.stats['uss_delta']):+.1f} MiB, "
            f"peak={mib(self.stats['uss_peak_in_block']):.1f} MiB "
            f"(+{mib(self.stats['uss_peak_over_start_delta']):.1f} over start)\n"
            f"  samples={self.stats['samples']}, "
            f"duration={self.stats['duration_s']:.2f}s, "
            f"backend={self.stats['backend']}, children={self.stats['include_children']}"
        )
        self.logger.info(log)

        return False


__all__ = ["MemScope"]
