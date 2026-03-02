from __future__ import annotations

from typing import Any
from types import SimpleNamespace


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
    "to_namespace",
    "namespace_to_dict",
]
