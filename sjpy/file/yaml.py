from __future__ import annotations

import yaml

from typing import Any
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path

from sjpy.file.algorithm import replace
from sjpy.collection import to_namespace

Metadata = object
Data = dict[str, Any]


class YamlSaver:
    def __init__(self, description: str):
        self.description = description

    def _get_current_time_dict(self) -> dict[str, int]:
        now = datetime.now()
        return {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
            "microsecond": now.microsecond,
        }

    def save(
        self, data: Mapping[Any, Any], filepath: Path, verbose: bool = True
    ) -> None:
        output: dict[str, Any] = {
            "metadata": {
                "description": self.description,
                "generated_date": self._get_current_time_dict(),
            },
            "data": data,
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)

        if verbose and filepath.exists():
            print(f"File {filepath} already exists. Overwriting...")

        with filepath.open("w", encoding="utf-8") as f:
            yaml.dump(output, f, allow_unicode=True, sort_keys=False)


def load_yaml(filepath: Path | str) -> tuple[Metadata, Data]:
    filepath = Path(filepath)
    data = read_yaml(filepath)
    metadata = to_namespace(data["metadata"])
    return metadata, data["data"]


def read_yaml(
    path: Path | str, replace_data: Mapping[str, str] | None = None
) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist.")
    with path.open("r", encoding="utf-8") as file:
        config: dict[str, Any] = yaml.safe_load(file)
    replace(config, replace_data)
    return config


def read_yaml_namespace(path: Path | str) -> object:
    config = read_yaml(path)
    return to_namespace(config)


__all__ = [
    "YamlSaver",
    "load_yaml",
    "read_yaml",
    "read_yaml_namespace",
]
