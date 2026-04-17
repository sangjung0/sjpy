from __future__ import annotations

import os
import re

from typing import Any
from collections.abc import Mapping
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


PATTERN = re.compile(r"\$\{(\w+)(?::([^}]*))?\}")


def replace(
    data: dict[Any, Any],
    replace_data: Mapping[str, str] | None = None,
    *,
    inplace: bool = False,
) -> dict[Any, Any]:
    _replace_data = dict(replace_data or {})
    _replace_data.update(os.environ)

    def _replace(data: Any) -> Any:
        # nonlocal _replace_data, inplace

        if isinstance(data, dict):
            rd = data if inplace else {}  # pyright: ignore[reportUnknownVariableType]
            for k, v in data.items():  # pyright: ignore[reportUnknownVariableType]
                rd[k] = _replace(v)
            return rd  # pyright: ignore[reportUnknownVariableType]
        elif isinstance(data, list):
            rl = (  # pyright: ignore[reportUnknownVariableType]
                data if inplace else [*data]
            )
            for idx in range(len(data)):  # pyright: ignore[reportUnknownArgumentType]
                rl[idx] = _replace(data[idx])
            return rl  # pyright: ignore[reportUnknownVariableType]
        elif isinstance(data, str):
            return PATTERN.sub(lambda m: replacer(m, _replace_data), data)
        else:
            return data

    result = _replace(data)
    assert isinstance(result, dict)
    return result  # pyright: ignore[reportUnknownVariableType]


def replacer(match: re.Match[str], replace_data: Mapping[str, str]) -> str:
    key, default = match.group(1), match.group(2)

    if key in replace_data:
        return replace_data[key]
    if default is not None:
        return default
    return ""


def move_dir_contents(
    src_dir: str | Path, dst_dir: str | Path, *, overwrite: bool = False
) -> list[Path]:
    import shutil

    src = Path(src_dir)
    dst = Path(dst_dir)
    dst.mkdir(parents=True, exist_ok=True)

    moved: list[Path] = []
    for p in src.iterdir():
        target = dst / p.name

        if target.exists():
            if not overwrite:
                raise FileExistsError(f"Target already exists: {target}")
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()

        shutil.move(str(p), str(target))
        moved.append(target)

    return moved


__all__ = ["replace", "replacer", "move_dir_contents"]
