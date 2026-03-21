from __future__ import annotations

import os

from pathlib import Path
from typing import Any, Sequence

from sjpy.reference import get_top_package_root
from sjpy.file.yaml import read_yaml


def load_config(
    config_file_name: str,
    config_head: str,
    paths: Sequence[str | Path] | None = None,
) -> dict[str, Any]:
    if paths is None:
        config_paths = []
    else:
        config_paths: list[Path] = [Path(p) for p in paths]

    if env_path := os.getenv("CONFIG_PATH", None) is not None:
        config_paths.append(Path(str(env_path)))

    working_dir = Path.cwd()
    config_paths.append(working_dir / config_file_name)

    package_path = get_top_package_root()
    if package_path is not None:
        config_paths.append(package_path.parent / config_file_name)

    config = None
    for path in config_paths:
        if path and path.exists() and path.is_file():
            if config_head in (config := read_yaml(path)):
                config = config[config_head]
                break
    else:
        raise FileNotFoundError("No valid configuration file found.")

    return config


__all__ = ["load_config"]
