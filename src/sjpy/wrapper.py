# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownMemberType=false, reportUnknownLambdaType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations
from typing import TYPE_CHECKING

import operator

from functools import wraps
from typing import Any, Type
from collections.abc import Callable

if TYPE_CHECKING:
    pass

# NOTE AI가 만듦 믿어선 안돼~!

_BINARY_OPS: dict[str, Callable[[Any, Any], Any]] = {
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

_UNARY_OPS: dict[str, Callable[[Any], Any]] = {
    "__neg__": operator.neg,
    "__pos__": operator.pos,
    "__abs__": operator.abs,
    "__invert__": operator.invert,
}

_CMP_OPS: dict[str, Callable[[Any, Any], bool]] = {
    "__lt__": operator.lt,
    "__le__": operator.le,
    "__gt__": operator.gt,
    "__ge__": operator.ge,
    "__eq__": operator.eq,
    "__ne__": operator.ne,
}


def _make_numeric(
    cls: Type[Any], caster: Callable[[Any], Any], *, is_int: bool
) -> Type[Any]:
    """
    `cls.value`(원시 값)을 `caster`로 변환해 모든 숫자 연산을
    프록시하도록 메서드를 주입한다.
    """

    # ---------- 2-항 연산 ----------
    for name, op in _BINARY_OPS.items():

        @wraps(op)
        def f0(  # type: ignore[no-untyped-def]
            self, other: Any, _op: Callable[[Any, Any], Any] = op
        ) -> Any:  # _op 디폴트 인수 trick으로 late-binding 방지
            return _op(caster(self.value), other)

        @wraps(op)
        def rf(self, other: Any, _op: Callable[[Any, Any], Any] = op) -> Any:  # type: ignore[no-untyped-def]
            return _op(other, caster(self.value))

        setattr(cls, name, f0)
        setattr(cls, f"__r{name[2:]}", rf)  # __add__ -> __radd__

    # ---------- 단항 연산 ----------
    for name, op in _UNARY_OPS.items():  # type: ignore[assignment]

        @wraps(op)
        def f1(self, _op: Callable[[Any], Any] = op) -> Any:  # type: ignore[assignment, no-untyped-def]
            return _op(caster(self.value))

        setattr(cls, name, f1)

    # ---------- 비교 연산 ----------
    for name, op in _CMP_OPS.items():

        @wraps(op)
        def f2(self, other: Any, _op: Callable[[Any, Any], bool] = op) -> bool:  # type: ignore[no-untyped-def]
            return _op(caster(self.value), other)

        setattr(cls, name, f2)

    # ---------- 기본 특수 메서드 ----------
    cls.__int__ = lambda self: int(self.value)
    cls.__float__ = lambda self: float(self.value)
    if is_int:
        cls.__index__ = lambda self: int(self.value)  # range(), list[x] 등에 필요
    cls.__repr__ = lambda self: f"{cls.__class__.__name__}({self.value})"  # type: ignore[assignment, misc]

    return cls


def make_int_like(cls: Type[Any]) -> Type[Any]:
    """`int`처럼 동작하도록 메서드를 주입한다."""
    return _make_numeric(cls, int, is_int=True)


def make_float_like(cls: Type[Any]) -> Type[Any]:
    """`float`처럼 동작하도록 메서드를 주입한다."""
    return _make_numeric(cls, float, is_int=False)


__all__ = [
    "make_float_like",
    "make_int_like",
]
