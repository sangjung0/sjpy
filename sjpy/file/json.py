from __future__ import annotations

import json

from typing import Any
from collections.abc import Mapping
from pathlib import Path
from datetime import datetime

from sjpy.collection import to_namespace

Metadata = object
Data = dict[str, Any]


class JsonSaver:
    def __init__(self, description: str):
        self.description: str = description

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
        self, data: Mapping[str, Any], filepath: Path | str, verbose: bool = True
    ) -> None:
        filepath = Path(filepath)

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
            json.dump(output, f, ensure_ascii=False, indent=4)


def load_json(filepath: Path) -> tuple[Metadata, Data]:
    data = read_json(filepath)
    metadata = to_namespace(data["metadata"])
    return metadata, data["data"]


def read_json(path: Path) -> dict[str, Any]:
    # 왜만들었지
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist.")
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


__all__ = [
    "JsonSaver",
    "load_json",
    "read_json",
]
