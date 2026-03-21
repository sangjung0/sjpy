from __future__ import annotations

import json

from typing import Any
from functools import wraps, lru_cache


def singleton(cls):
    implementation = None

    @wraps(cls)
    def get_instance(*args, **kwargs):
        nonlocal implementation
        if implementation is None:
            implementation = cls(*args, **kwargs)
        return implementation

    return get_instance


def lru_dict_cache(maxsize=128):
    def decorator(func):
        @lru_cache(maxsize=maxsize)
        def cached(
            *args: tuple,
            __cache__arg_idx__: tuple[int, ...],
            __cache__kwarg_keys__: tuple[str, ...],
            **kwargs: dict[str, Any],
        ):
            _args: list = list(args)
            for idx in __cache__arg_idx__:
                _args[idx] = json.loads(_args[idx])

            for key in __cache__kwarg_keys__:
                v = kwargs[key]
                assert isinstance(v, str)
                kwargs[key] = json.loads(v)

            # print(f"cache hit for {args} and {kwargs}")
            return func(*args, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs):
            new_args: list = []
            arg_idx: list = []
            for i, arg in enumerate(args):
                if isinstance(arg, dict):
                    arg = json.dumps(arg, sort_keys=True)
                    arg_idx.append(i)
                new_args.append(arg)
            _args: tuple = tuple(new_args)
            _arg_idx: tuple[int, ...] = tuple(arg_idx)

            new_kwargs: dict[str, Any] = {}
            kwarg_keys: list[str] = []
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    v = json.dumps(v, sort_keys=True)
                    kwarg_keys.append(k)
                new_kwargs[k] = v
            _kwargs: dict[str, Any] = new_kwargs
            _kwarg_keys: tuple[str, ...] = tuple(kwarg_keys)

            # print(
            # f"cache miss for {args} with {arg_idx} and {kwargs} with keys {kwarg_keys}"
            # )
            return cached(
                *args,
                __cache__arg_idx__=_arg_idx,
                __cache__kwarg_keys__=_kwarg_keys,
                **kwargs,
            )

        return wrapper

    return decorator


def generate_simple_decorator(key: str, obj: object):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key not in kwargs:
                kwargs[key] = obj
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["singleton", "lru_dict_cache", "generate_simple_decorator"]
