from typing import Any
from types import SimpleNamespace


class SafetyDict(dict):
    def __init__(
        self,
        data: dict = {},
        default_value: Any = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.__DEFAULT_VALUE = default_value
        if data:
            self.update(self.__upload(data))

    def __getitem__(self, key):
        if key not in self:
            print(f"Key '{key}' not found in SafetyDict. Returning default value.")
        return super().get(key, self.__DEFAULT_VALUE)

    def __upload(self, d: dict):
        default = d["default"] if "default" in d else None
        bucket = SafetyDict(default_value=default)
        for key, value in d.items():
            if isinstance(value, dict):
                super(SafetyDict, bucket).__setitem__(key, self.__upload(value))
            else:
                super(SafetyDict, bucket).__setitem__(key, value)
        return bucket


def to_namespace(d: Any):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [to_namespace(i) for i in d]
    else:
        return d


__all__ = [
    "SafetyDict",
    "to_namespace",
]
