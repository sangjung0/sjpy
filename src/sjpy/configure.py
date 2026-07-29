from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from sjpy.file.yaml import read_yaml
from sjpy.reference import get_top_package_root


def load_config(
    config_file_name: str,
    config_head: str,
    paths: Sequence[str | Path] | None = None,
) -> dict[str, Any]:
    config_paths: list[Path] = []
    if paths is not None:
        config_paths = [Path(p) for p in paths]

    if env_path := os.getenv("CONFIG_PATH", None) is not None:
        config_paths.append(Path(str(env_path)))

    working_dir = Path.cwd()
    config_paths.append(working_dir / config_file_name)

    package_path = get_top_package_root()
    if package_path is not None:
        config_paths.append(package_path.parent / config_file_name)

    config: dict[str, Any] | None = None
    for path in config_paths:
        if path and path.exists() and path.is_file():
            if config_head in (config := read_yaml(path)):
                config = config[config_head]
                break

    if config is None:
        raise FileNotFoundError("No valid configuration file found.")

    return config


__all__ = ["load_config"]
