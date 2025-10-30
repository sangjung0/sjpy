import importlib.util
import inspect

from pathlib import Path

def get_top_package_root(depth: int = 1):
    frm = inspect.stack()[depth].frame
    mod = inspect.getmodule(frm)
    mod_name = mod.__name__

    if not mod_name:
        return None

    top_pkg_spec = None
    parent = mod_name
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

__all__ = ["get_top_package_root"]
