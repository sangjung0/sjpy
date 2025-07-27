def make_float_like(cls):
    def _binary(method_name):
        def method(self, other):
            return getattr(float(self.value), method_name)(other)

        return method

    def _reverse_binary(method_name):
        def method(self, other):
            return getattr(other, method_name)(float(self.value))

        return method

    def _unary(method_name):
        def method(self):
            return getattr(float(self.value), method_name)()

        return method

    bin_ops = [
        "__add__",
        "__sub__",
        "__mul__",
        "__truediv__",
        "__floordiv__",
        "__mod__",
        "__pow__",
    ]
    rbin_ops = [
        "__radd__",
        "__rsub__",
        "__rmul__",
        "__rtruediv__",
        "__rfloordiv__",
        "__rmod__",
        "__rpow__",
    ]
    unary_ops = ["__neg__", "__pos__", "__abs__"]
    cmp_ops = ["__lt__", "__le__", "__gt__", "__ge__", "__eq__", "__ne__"]

    for op in bin_ops:
        setattr(cls, op, _binary(op))
    for op in rbin_ops:
        setattr(cls, op, _reverse_binary(op))
    for op in unary_ops:
        setattr(cls, op, _unary(op))
    for op in cmp_ops:
        setattr(cls, op, _binary(op))

    cls.__float__ = lambda self: float(self.value)
    cls.__int__ = lambda self: int(self.value)
    cls.__repr__ = lambda self: f"{cls.__name__}({self.value})"

    return cls


def make_int_like(cls):
    def _binary(method_name):
        def method(self, other):
            return getattr(int(self.value), method_name)(other)

        return method

    def _reverse_binary(method_name):
        def method(self, other):
            return getattr(other, method_name)(int(self.value))

        return method

    def _unary(method_name):
        def method(self):
            return getattr(int(self.value), method_name)()

        return method

    bin_ops = [
        "__add__",
        "__sub__",
        "__mul__",
        "__truediv__",
        "__floordiv__",
        "__mod__",
        "__pow__",
        "__and__",
        "__or__",
        "__xor__",
    ]
    rbin_ops = [
        "__radd__",
        "__rsub__",
        "__rmul__",
        "__rtruediv__",
        "__rfloordiv__",
        "__rmod__",
        "__rpow__",
        "__rand__",
        "__ror__",
        "__rxor__",
    ]
    unary_ops = ["__neg__", "__pos__", "__abs__", "__invert__"]
    cmp_ops = ["__lt__", "__le__", "__gt__", "__ge__", "__eq__", "__ne__"]

    for op in bin_ops:
        setattr(cls, op, _binary(op))
    for op in rbin_ops:
        setattr(cls, op, _reverse_binary(op))
    for op in unary_ops:
        setattr(cls, op, _unary(op))
    for op in cmp_ops:
        setattr(cls, op, _binary(op))

    cls.__int__ = lambda self: int(self.value)
    cls.__float__ = lambda self: float(self.value)
    cls.__index__ = lambda self: int(self.value)  # for range(), list[a] 등
    cls.__repr__ = lambda self: f"{cls.__name__}({self.value})"

    return cls


__all__ = [
    "make_float_like",
    "make_int_like",
]
