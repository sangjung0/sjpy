from functools import wraps


def singleton(cls):
    implementation = None

    @wraps(cls)
    def get_instance(*args, **kwargs):
        nonlocal implementation
        if implementation is None:
            implementation = cls(*args, **kwargs)
        return implementation

    return get_instance


__all__ = ["singleton"]
