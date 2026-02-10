from __future__ import annotations

import tempfile
import zipfile

from pathlib import Path
from tqdm import tqdm


def extract_zip(
    zip_path: str | Path,
    extract_dir: str | Path | None = None,
    verbose: bool = True,
) -> Path:
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    extract_dir = (
        Path(extract_dir) if extract_dir is not None else Path(tempfile.gettempdir())
    )
    extract_dir.mkdir(parents=True, exist_ok=True)
    extract_dir_resolved = extract_dir.resolve()

    with zipfile.ZipFile(zip_path) as zf:
        members = zf.infolist()

        for m in members:
            member_path = Path(m.filename)

            if member_path.is_absolute() or ".." in member_path.parts:
                raise RuntimeError(f"Unsafe path in zip: {m.filename}")

            out_path = (extract_dir_resolved / member_path).resolve()
            if (
                out_path != extract_dir_resolved
                and extract_dir_resolved not in out_path.parents
            ):
                raise RuntimeError(f"Zip slip detected: {m.filename}")

        file_members = [m for m in members if not m.is_dir()]

        pbar = tqdm(
            total=len(file_members),
            desc=f"extract {zip_path.name}",
            unit="file",
            disable=not verbose,
        )

        try:
            for m in file_members:
                out_path = extract_dir / m.filename
                out_path.parent.mkdir(parents=True, exist_ok=True)

                zf.extract(m, path=extract_dir)
                pbar.update(1)
        finally:
            pbar.close()

    if verbose:
        print(f"[extract] {zip_path} -> {extract_dir}")

    return extract_dir


__all__ = ["extract_zip"]
