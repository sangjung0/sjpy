from functools import wraps


def deprecated(
    message: str = "This function is deprecated and will be removed in future versions.",
) -> None:
    """
    Decorator to mark a function as deprecated.

    Args:
        message (str): The deprecation message to display.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"WARNING: {message}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
