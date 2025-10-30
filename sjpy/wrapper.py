from __future__ import annotations
from typing import TYPE_CHECKING

import operator

from functools import wraps
from typing import Any, Callable, Dict, Type

if TYPE_CHECKING:
    pass

# NOTE AI가 만듬 믿어선 안돼~!

_BINARY_OPS: Dict[str, Callable[[Any, Any], Any]] = {
    "__add__": operator.add,
    "__sub__": operator.sub,
    "__mul__": operator.mul,
    "__truediv__": operator.truediv,
    "__floordiv__": operator.floordiv,
    "__mod__": operator.mod,
    "__pow__": operator.pow,
    "__and__": operator.and_,
    "__or__": operator.or_,
    "__xor__": operator.xor,
}

_UNARY_OPS: Dict[str, Callable[[Any], Any]] = {
    "__neg__": operator.neg,
    "__pos__": operator.pos,
    "__abs__": operator.abs,
    "__invert__": operator.invert,
}

_CMP_OPS: Dict[str, Callable[[Any, Any], bool]] = {
    "__lt__": operator.lt,
    "__le__": operator.le,
    "__gt__": operator.gt,
    "__ge__": operator.ge,
    "__eq__": operator.eq,
    "__ne__": operator.ne,
}


def _make_numeric(cls: Type, caster: Callable[[Any], Any], *, is_int: bool) -> Type:
    """
    `cls.value`(원시 값)을 `caster`로 변환해 모든 숫자 연산을
    프록시하도록 메서드를 주입한다.
    """

    # ---------- 2-항 연산 ----------
    for name, op in _BINARY_OPS.items():

        @wraps(op)
        def f(self, other, _op=op):  # _op 디폴트 인수 trick으로 late-binding 방지
            return _op(caster(self.value), other)

        @wraps(op)
        def rf(self, other, _op=op):
            return _op(other, caster(self.value))

        setattr(cls, name, f)
        setattr(cls, f"__r{name[2:]}", rf)  # __add__ -> __radd__

    # ---------- 단항 연산 ----------
    for name, op in _UNARY_OPS.items():

        @wraps(op)
        def f(self, _op=op):
            return _op(caster(self.value))

        setattr(cls, name, f)

    # ---------- 비교 연산 ----------
    for name, op in _CMP_OPS.items():

        @wraps(op)
        def f(self, other, _op=op):
            return _op(caster(self.value), other)

        setattr(cls, name, f)

    # ---------- 기본 특수 메서드 ----------
    cls.__int__ = lambda self: int(self.value)
    cls.__float__ = lambda self: float(self.value)
    if is_int:
        cls.__index__ = lambda self: int(self.value)  # range(), list[x] 등에 필요
    cls.__repr__ = lambda self: f"{cls.__class__.__name__}({self.value})"

    return cls


def make_int_like(cls: Type) -> Type:
    """`int`처럼 동작하도록 메서드를 주입한다."""
    return _make_numeric(cls, int, is_int=True)


def make_float_like(cls: Type) -> Type:
    """`float`처럼 동작하도록 메서드를 주입한다."""
    return _make_numeric(cls, float, is_int=False)


__all__ = [
    "make_float_like",
    "make_int_like",
]
