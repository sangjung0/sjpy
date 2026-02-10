from __future__ import annotations

import os
import tarfile
from pathlib import Path
from typing import Optional, Callable

from tqdm import tqdm


def _is_within_directory(base: Path, target: Path) -> bool:
    try:
        base_resolved = base.resolve()
        target_resolved = target.resolve()
        return (
            base_resolved == target_resolved or base_resolved in target_resolved.parents
        )
    except Exception:
        return False


def extract_tar(
    archive_path: str | Path,
    dest_dir: str | Path,
    *,
    verbose: bool = True,
    overwrite: bool = False,
    keep_permissions: bool = True,
    keep_mtime: bool = True,
    progress_desc: Optional[str] = None,
    on_member: Optional[Callable[[tarfile.TarInfo], None]] = None,
) -> list[Path]:
    """
    Extract a .tar.gz (or any tar.* supported by tarfile) with tqdm progress and a verbose toggle.

    Args:
        archive_path: path to .tar.gz
        dest_dir: extraction directory (created if not exists)
        verbose: show tqdm progress bar
        overwrite: if False, skip files that already exist; if True, overwrite
        keep_permissions: if True, preserve mode bits when possible (tarfile usually does)
        keep_mtime: if True, preserve mtime (tarfile usually does); set False to skip utime
        progress_desc: tqdm description text
        on_member: optional callback invoked per TarInfo before extraction

    Returns:
        List of extracted Paths (files/dirs/links that were processed).
    """

    archive_path = Path(archive_path)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    extracted: list[Path] = []

    mode = "r:*"  # auto-detect compression (gz, bz2, xz, etc.)
    with tarfile.open(archive_path, mode) as tf:
        members = tf.getmembers()

        pbar = None
        if verbose:
            pbar = tqdm(
                total=len(members),
                unit="file",
                desc=progress_desc or f"Extracting {archive_path.name}",
                dynamic_ncols=True,
            )

        for m in members:
            if on_member is not None:
                on_member(m)

            target_path = dest_dir / m.name

            if m.name.startswith(("/", "\\")) or ".." in Path(m.name).parts:
                if verbose and pbar:
                    pbar.write(f"Skip suspicious member path: {m.name}")
                if pbar:
                    pbar.update(1)
                continue

            if not _is_within_directory(dest_dir, target_path):
                if verbose and pbar:
                    pbar.write(f"Skip (path traversal): {m.name}")
                if pbar:
                    pbar.update(1)
                continue

            if target_path.exists() and m.isfile() and not overwrite:
                if pbar:
                    pbar.update(1)
                extracted.append(target_path)
                continue

            tf.extract(m, path=dest_dir, set_attrs=keep_permissions)

            if (not keep_mtime) and target_path.exists():
                try:
                    st = target_path.stat()
                    os.utime(
                        target_path, (st.st_atime, st.st_mtime), follow_symlinks=False
                    )
                except Exception:
                    pass

            extracted.append(target_path)

            if pbar:
                pbar.update(1)

        if pbar:
            pbar.close()

    return extracted


__all__ = ["extract_tar"]
