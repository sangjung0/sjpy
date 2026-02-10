import os
import re

from dotenv import load_dotenv
from pathlib import Path

PATTERN = re.compile(r"\$\{(\w+)(?::([^}]*))?\}")

load_dotenv()


def replace(d: dict, replace_data: dict = None):
    replace_data = replace_data or {}
    replace_data.update(os.environ)

    for k, v in d.items():
        if isinstance(v, dict):
            replace(v, replace_data)
        elif isinstance(v, list):
            for idx in range(len(v)):
                if isinstance(v[idx], dict):
                    replace(v[idx], replace_data)
                elif isinstance(v[idx], str):
                    v[idx] = PATTERN.sub(lambda m: replacer(m, replace_data), v[idx])
        elif isinstance(v, str):
            d[k] = PATTERN.sub(lambda m: replacer(m, replace_data), v)


def replacer(match: re.Match[str], replace_data: dict) -> str:
    return replace_data.get(match.group(1), match.group(2))


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
