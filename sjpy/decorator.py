from __future__ import annotations

import json

from threading import Lock
from typing import TypeVar, Any, overload, cast
from collections.abc import Callable
from functools import wraps, lru_cache

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


def lru_dict_cache(
    maxsize: int = 128,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @lru_cache(maxsize=maxsize)
        def cached(
            *args: Any,
            __cache__arg_idx__: tuple[int, ...],
            __cache__kwarg_keys__: tuple[str, ...],
            **kwargs: Any,
        ) -> Any:
            _args: list[Any] = list(args)
            for idx in __cache__arg_idx__:
                _args[idx] = json.loads(_args[idx])

            for key in __cache__kwarg_keys__:
                v = kwargs[key]
                assert isinstance(v, str)
                kwargs[key] = json.loads(v)

            # print(f"cache hit for {args} and {kwargs}")
            value: Any = func(*args, **kwargs)
            return value

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            new_args: list[Any] = []
            arg_idx: list[Any] = []
            for i, arg in enumerate(args):
                if isinstance(arg, dict):
                    arg = json.dumps(arg, sort_keys=True)
                    arg_idx.append(i)
                new_args.append(arg)
            _args: tuple[Any, ...] = tuple(new_args)
            _arg_idx: tuple[int, ...] = tuple(arg_idx)

            new_kwargs: dict[str, Any] = {}
            kwarg_keys: list[str] = []
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    _v = json.dumps(v, sort_keys=True)
                    kwarg_keys.append(k)
                else:
                    _v = v
                new_kwargs[k] = _v
            _kwargs: dict[str, Any] = new_kwargs
            _kwarg_keys: tuple[str, ...] = tuple(kwarg_keys)

            # print(
            # f"cache miss for {args} with {arg_idx} and {kwargs} with keys {kwarg_keys}"
            # )
            value: Any = cached(
                *_args,
                __cache__arg_idx__=_arg_idx,
                __cache__kwarg_keys__=_kwarg_keys,
                **_kwargs,
            )
            return value

        return wrapper

    return decorator


def generate_simple_decorator(
    key: str, obj: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if key not in kwargs:
                kwargs[key] = obj
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["singleton", "lru_dict_cache", "generate_simple_decorator"]
