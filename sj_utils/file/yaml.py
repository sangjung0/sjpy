import yaml

from datetime import datetime
from pathlib import Path

from sj_utils.file.service import replace
from sj_utils.collection import to_namespace


class YamlSaver:
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

    def save(self, data: dict, filepath: str, verbose: bool = True):
        output = {
            "metadata": {
                "description": self.description,
                "generated_date": self._get_current_time_dict(),
            },
            "data": data,
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        if verbose and filepath.exists():
            print(f"File {filepath} already exists. Overwriting...")

        with filepath.open("w", encoding="utf-8") as f:
            yaml.dump(output, f, allow_unicode=True, sort_keys=False)


def load_yaml(filepath: Path) -> tuple[object, dict]:
    data = read_yaml(filepath)
    metadata = to_namespace(data["metadata"])
    return metadata, data["data"]


def read_yaml(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist.")
    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    replace(config)
    return config


def read_yaml_namespace(path: Path):
    config = read_yaml(path)
    return to_namespace(config)


__all__ = [
    "YamlSaver",
    "load_yaml",
    "read_yaml",
    "read_yaml_namespace",
]
