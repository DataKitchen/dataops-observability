__all__ = ["EnumStr"]

from enum import Enum, EnumMeta
from typing import Any, Union, cast
from collections.abc import Iterable

from marshmallow.utils import ensure_text_type
from marshmallow.validate import OneOf

from common.schemas.fields.normalized_str import NormalizedStr


class EnumStr(NormalizedStr):
    """
    This field is meant to represent a member of an enum. In our convention, those strings are always assumed to be
    upper-case, and so we will always upper-case these for the user.

    Note: types of _serialize and _deserialize functions are inferred from the parent.
    """

    def __init__(self, enum: Union[EnumMeta, list], **kwargs: object) -> None:
        if isinstance(enum, EnumMeta):
            allowed_values: list[str] = [e.name for e in cast(Iterable[Enum], enum)]
        else:
            allowed_values = enum

        if "validate" in kwargs:
            # There isn't a use case for them yet. Nothing is stopping us implementing them later though.
            raise NotImplementedError("Additional validators not supported.")

        super().__init__(validate=OneOf(allowed_values), **kwargs)  # type: ignore[arg-type]

    def _serialize(self, value: Any, attr: str | None, obj: Any, **kwargs: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, Enum):
            return ensure_text_type(value.value)
        else:
            return super()._serialize(value, attr, obj, **kwargs)
