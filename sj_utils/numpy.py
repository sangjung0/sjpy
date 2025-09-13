import numpy as np
import base64


def numpy_to_base64(array: np.ndarray) -> str:
    if array is None:
        return ""
    return base64.b64encode(array.tobytes()).decode("utf-8")


def base64_to_numpy(
    encoded_str: str, dtype: np.dtype = np.float32, shape: tuple | None = None
) -> np.ndarray | None:
    if not encoded_str:
        return None
    byte_data = base64.b64decode(encoded_str.encode("utf-8"))
    array = np.frombuffer(byte_data, dtype=dtype)
    if shape is not None:
        array = array.reshape(shape)
    return array


__all__ = ["numpy_to_base64", "base64_to_numpy"]
