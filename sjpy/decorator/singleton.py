from __future__ import annotations


from threading import Lock
from typing import TypeVar, Any, overload, cast
from collections.abc import Callable

C = TypeVar("C", bound=type[Any])


class BaseSingletonMeta(type):
    _instances: dict[type, object] = {}
    _locks: dict[type, Lock] = {}
    _meta_lock: Lock = Lock()

    def _get_instance_lock(cls) -> Lock:
        with cls._meta_lock:
            if cls not in cls._locks:  # pyright: ignore[reportUnnecessaryContains]
                cls._locks[cls] = Lock()
            return cls._locks[cls]


class SingletonMeta(BaseSingletonMeta):
    def __call__(cls, *args: Any, **kwargs: Any) -> object:
        lock = cls._get_instance_lock()
        with lock:
            if cls not in cls._instances:  # pyright: ignore[reportUnnecessaryContains]
                cls._instances[cls] = type.__call__(cls, *args, **kwargs)
            return cls._instances[cls]


class StrictSingletonMeta(BaseSingletonMeta):
    _init_args: dict[type, tuple[tuple[Any, ...], dict[str, Any]]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> object:
        lock = cls._get_instance_lock()
        with lock:
            if cls not in cls._instances:  # pyright: ignore[reportUnnecessaryContains]
                obj = type.__call__(cls, *args, **kwargs)
                cls._instances[cls] = obj
                cls._init_args[cls] = (args, dict(kwargs))
                return obj

            old_args, old_kwargs = cls._init_args[cls]  # type: ignore[unused-ignore]
            if old_args != args or old_kwargs != kwargs:
                raise ValueError(
                    f"Singleton class {cls.__name__} already instantiated with "
                    f"different arguments: {old_args}, {old_kwargs} vs {args}, {kwargs}"
                )

            return cls._instances[cls]


@overload
def singleton(cls: C) -> C: ...
@overload
def singleton(*, strict_mode: bool = True) -> Callable[[C], C]: ...
def singleton(
    cls: C | None = None,
    *,
    strict_mode: bool = True,
) -> C | Callable[[C], C]:
    def wrap(target_cls: C) -> C:
        cls_base: Any = target_cls
        meta_base: Any = type(target_cls)

        if strict_mode:

            class CombinedMeta(  # pyright: ignore[reportRedeclaration]
                StrictSingletonMeta, meta_base  # type: ignore[misc]
            ):
                pass

        else:

            class CombinedMeta(SingletonMeta, meta_base):  # type: ignore[no-redef, misc]
                pass

        class SingletonWrapper(cls_base, metaclass=CombinedMeta):  # type: ignore[misc]
            __singleton_strict_args__ = strict_mode

        SingletonWrapper.__name__ = target_cls.__name__
        SingletonWrapper.__qualname__ = target_cls.__qualname__
        SingletonWrapper.__module__ = target_cls.__module__
        SingletonWrapper.__doc__ = target_cls.__doc__

        return cast(C, SingletonWrapper)

    if cls is None:
        return wrap

    return wrap(cls)


__all__ = ["singleton"]
