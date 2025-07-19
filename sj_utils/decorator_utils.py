import json

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
            __cache__arg_idx__: tuple,
            __cache__kwarg_keys__: tuple,
            **kwargs: dict,
        ):
            args = list(args)
            for idx in __cache__arg_idx__:
                args[idx] = json.loads(args[idx])

            for key in __cache__kwarg_keys__:
                kwargs[key] = json.loads(kwargs[key])

            # print(f"cache hit for {args} and {kwargs}")
            return func(*args, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs):
            new_args = []
            arg_idx = []
            for i, arg in enumerate(args):
                if isinstance(arg, dict):
                    arg = json.dumps(arg, sort_keys=True)
                    arg_idx.append(i)
                new_args.append(arg)
            args = tuple(new_args)
            arg_idx = tuple(arg_idx)

            new_kwargs = {}
            kwarg_keys = []
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    v = json.dumps(v, sort_keys=True)
                    kwarg_keys.append(k)
                new_kwargs[k] = v
            kwargs = new_kwargs
            kwarg_keys = tuple(kwarg_keys)

            # print(
                # f"cache miss for {args} with {arg_idx} and {kwargs} with keys {kwarg_keys}"
            # )
            return cached(
                *args,
                __cache__arg_idx__=arg_idx,
                __cache__kwarg_keys__=kwarg_keys,
                **kwargs,
            )

        return wrapper

    return decorator


__all__ = ["singleton", "lru_dict_cache"]
