from __future__ import annotations

import importlib.util
import inspect

from pathlib import Path
from typing import Any, TypedDict, cast


def get_top_package_root(depth: int = 1) -> None | Path:
    frm = inspect.stack()[depth].frame
    mod = inspect.getmodule(frm)

    if not mod:
        return None

    top_pkg_spec = None
    parent = mod.__name__
    while True:
        if not parent:
            break
        pspec = importlib.util.find_spec(parent)
        if pspec and getattr(pspec, "submodule_search_locations", None):
            top_pkg_spec = pspec
        parent = parent.rpartition(".")[0]

    if top_pkg_spec and top_pkg_spec.submodule_search_locations:
        return Path(list(top_pkg_spec.submodule_search_locations)[0]).resolve()
    return None


class ImportData(TypedDict):
    module: str
    qualname: str


def import_from(data: ImportData) -> type[Any]:
    import sys
    from importlib import import_module
    from functools import reduce

    module, qual = data["module"], data["qualname"]
    if module in ("__main__", "__mp_main__"):
        m = sys.modules[module]
    else:
        m = import_module(module)
    _class = cast(type[Any], reduce(getattr, qual.split("."), m))
    return _class


__all__ = ["get_top_package_root", "import_from"]
