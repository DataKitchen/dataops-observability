__all__ = ["NormalizedStr", "strip_upper_underscore"]

from typing import Any, Callable, Mapping, Optional

from marshmallow.fields import Str
from marshmallow.utils import ensure_text_type


def strip_upper_underscore(value: str) -> str:
    return value.strip().upper().replace(" ", "_")


class NormalizedStr(Str):
    """
    This represents string data that we normalize. For now, that means that the strings
    are cast to an upper-case.

    Note: types of _serialize and _deserialize functions are inferred from the parent.
    """

    def __init__(self, normalizer: Callable[[str], str] = str.upper, **kwargs: Any):
        self.normalizer_func = normalizer
        super().__init__(**kwargs)

    def _serialize(self, value: Any, attr: Optional[str], obj: Any, **kwargs: object) -> Optional[str]:
        if value is None:
            return None
        str_field = ensure_text_type(value)
        return self.normalizer_func(str_field)

    def _deserialize(self, value: Any, attr: Optional[str], data: Optional[Mapping[str, Any]], **kwargs: object) -> Any:
        if not isinstance(value, (str, bytes)):
            raise self.make_error("invalid")
        try:
            str_field = ensure_text_type(value)
            return self.normalizer_func(str_field)
        except UnicodeDecodeError as error:
            raise self.make_error("invalid_utf8") from error
