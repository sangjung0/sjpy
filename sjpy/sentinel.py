from __future__ import annotations

from typing import TypeAlias, Any
from typing_extensions import TypeIs
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema

from sjpy.decorator import singleton


@singleton
class _UnSet:
    __slots__ = ()

    def __repr__(self) -> str:
        return "UNSET"

    @classmethod
    def _validate(cls, value: Any) -> _UnSet:
        if is_unset(value):
            return UNSET
        raise ValueError(f"Expected UNSET, got {value!r}")

    @staticmethod
    def _serialize(value: _UnSet) -> str:
        return str(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        assert source is cls

        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.is_instance_schema(cls),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {
            "type": "object",
            "title": "UNSET",
            "description": "A special value indicating that a field is not set.",
        }


def is_unset(value: object) -> TypeIs[_UnSet]:
    return isinstance(value, _UnSet)


UNSET = _UnSet()
UnSet: TypeAlias = _UnSet

__all__ = ["UNSET", "UnSet", "is_unset"]
