from typing import Any
from types import SimpleNamespace
from collections import OrderedDict


class SafetyDict(dict):
    def __init__(
        self,
        data: dict = {},
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if data:
            self.__dict_to_safety(data)
            self.update(data)

    def __getitem__(self, key):
        return super().get(key, self.get("default", None))

    def __dict_to_safety(self, d: dict):
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = SafetyDict(value)


class LRUDict(OrderedDict):
    def __init__(self, capacity: int = 128, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capacity = capacity

    def __getitem__(self, key):
        val = super().__getitem__(key)
        self.move_to_end(key)
        return val

    def __setitem__(self, key, value):
        if key in self:
            super().__setitem__(key, value)
            self.move_to_end(key)
        else:
            super().__setitem__(key, value)
            if len(self) > self.capacity:
                self.popitem(last=False)

    def get(self, key, default=None, *, touch=True):
        if key in self:
            v = super().__getitem__(key)
            if touch:
                self.move_to_end(key)
            return v
        return default


def to_namespace(d: Any):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [to_namespace(i) for i in d]
    else:
        return d


__all__ = [
    "SafetyDict",
    "LRUDict",
    "to_namespace",
]
