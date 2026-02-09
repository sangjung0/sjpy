from typing import Any
from types import SimpleNamespace
from typing_extensions import override
from collections import OrderedDict
from collections.abc import Mapping


class SafetyDict(dict):
    def __init__(self, data: Mapping[str, Any] | None = None):
        super().__init__()

        if data is not None:
            self.update(self._to_safety(dict(data)))

    @override
    def __missing__(self, key: Any) -> Any:
        return dict.get(self, "default", None)

    def _to_safety(self, d: dict[str, Any]) -> dict[str, Any]:
        for k, v in list(d.items()):
            if isinstance(v, dict):
                d[k] = SafetyDict(data=v)
            elif isinstance(v, list):
                d[k] = [SafetyDict(data=x) if isinstance(x, dict) else x for x in v]
        return d


class LRUDict(OrderedDict):
    def __init__(self, *args, capacity: int = 128, **kwargs):
        self._capacity = capacity
        super().__init__(*args, **kwargs)

    @property
    def capacity(self) -> int:
        return self._capacity

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


def namespace_to_dict(ns: Any):
    if isinstance(ns, SimpleNamespace):
        return {k: namespace_to_dict(v) for k, v in ns.__dict__.items()}
    elif isinstance(ns, list):
        return [namespace_to_dict(i) for i in ns]
    else:
        return ns


__all__ = [
    "SafetyDict",
    "LRUDict",
    "to_namespace",
    "namespace_to_dict",
]
