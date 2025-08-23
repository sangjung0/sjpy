import json

from datetime import datetime
from pathlib import Path

from sj_utils.collection import to_namespace


class JsonSaver:
    def __init__(self, description: str):
        self.description = description

    def _get_current_time_dict(self):
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

    def save(self, data: dict, filepath: Path, verbose: bool = True):
        output = {
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


def load_json(filepath: Path) -> tuple[object, dict]:
    data = read_json(filepath)
    metadata = to_namespace(data["metadata"])
    return metadata, data["data"]


def read_json(path: Path):
    # 왜만들었지
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist.")
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "JsonSaver",
    "load_json",
    "read_json",
]
