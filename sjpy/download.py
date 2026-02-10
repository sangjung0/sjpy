from __future__ import annotations

import shutil

from pathlib import Path
from urllib.request import urlopen, Request

from tqdm import tqdm

from sjpy.file.temp import create_temp_path


def download(
    url: str,
    download_path: str | Path | None = None,
    chunk_size: int = 1024**2,
    verbose: bool = True,
) -> Path:
    if download_path is None:
        download_path = create_temp_path()
    else:
        download_path = Path(download_path)
        download_path.parent.mkdir(parents=True, exist_ok=True)
        if download_path.exists():
            raise FileExistsError(f"Download path already exists: {download_path}")

    req = Request(url, headers={"User-Agent": "python"})
    with urlopen(req) as resp:
        total = resp.headers.get("Content-Length")
        total = int(total) if total is not None else None

        if verbose:
            print(f"[download] {url} -> {download_path}")

        pbar_ctx = (
            tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=download_path.name,
                disable=not verbose,
            )
            if verbose
            else None
        )
        try:
            with open(download_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    if pbar_ctx is not None:
                        pbar_ctx.update(len(chunk))
        finally:
            if pbar_ctx is not None:
                pbar_ctx.close()

    if verbose:
        print(f"[download] done: {download_path}")

    return download_path


__all__ = ["download"]
