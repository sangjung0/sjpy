from __future__ import annotations

import warnings

from typing import Literal, TypeVar, Any, cast, ParamSpec, TypedDict
from collections.abc import Callable, Sequence
from functools import wraps
from importlib.metadata import version, PackageNotFoundError
from packaging.specifiers import SpecifierSet
from packaging.version import Version

Action = Literal["error", "warn"]
P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
C = TypeVar("C", bound=type[Any])


class VersionRule(TypedDict, total=False):
    package_name: str
    allowed: str | None
    blocked: str | None
    action: Action


def _get_version(package_name: str) -> Version:
    try:
        return Version(version(package_name))
    except PackageNotFoundError as e:
        raise RuntimeError(f"Required package is not installed: {package_name}") from e


def check_version(
    package_name: str,
    *,
    allowed: str | None = None,
    blocked: str | None = None,
    action: Action = "error",
) -> None:
    installed = _get_version(package_name)

    messages: list[str] = []

    if allowed is not None and installed not in SpecifierSet(allowed):
        messages.append(
            f"{package_name}=={installed} is not supported. "
            f"Required: {package_name}{allowed}"
        )

    if blocked is not None and installed in SpecifierSet(blocked):
        messages.append(
            f"{package_name}=={installed} is blocked. "
            f"Blocked: {package_name}{blocked}"
        )

    if not messages:
        return

    message = "\n".join(messages)

    if action == "warn":
        warnings.warn(message, RuntimeWarning, stacklevel=3)
    elif action == "error":
        raise RuntimeError(message)
    else:
        raise ValueError(f"Unknown action: {action}")


def requires_versions(*rules: VersionRule) -> Callable[[T], T]:
    """
    Decorator for checking package versions before running a function
    or before initializing a class.

    Examples:
        @requires_versions({"package_name": "torch", "allowed": ">=2.1,<2.5"})
        def run(...):
            ...

        @requires_versions({"package_name": "torch", "blocked": "==2.3.0"})
        class MyModel:
            ...
    """

    def decorator(target: T) -> T:
        if isinstance(target, type):
            return cast(T, _decorate_class(target, rules))

        if callable(target):
            return cast(T, _decorate_function(target, rules))

        raise TypeError("Target must be a class or a callable")

    return decorator


def _decorate_class(cls: C, rules: Sequence[VersionRule]) -> C:
    original_init = cls.__init__

    @wraps(original_init)
    def wrapped_init(self: Any, *args: Any, **kwargs: Any) -> None:
        for rule in rules:
            check_version(**rule)
        original_init(self, *args, **kwargs)

    cls.__init__ = wrapped_init
    return cls


def _decorate_function(
    func: Callable[P, R], rules: Sequence[VersionRule]
) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        for rule in rules:
            check_version(**rule)
        return func(*args, **kwargs)

    return wrapper


__all__ = ["check_version", "requires_versions"]
