__all__ = ["DomainField", "EnumStrField", "JSONStrListField", "UTCTimestampField", "ZoneInfoField"]

import logging
import re
import socket
from datetime import datetime, timezone
from enum import Enum
from json import dumps as json_dumps
from json import loads as json_loads
from typing import Any, Optional, Pattern, Type, Union, cast
from unicodedata import normalize
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from peewee import CharField, IntegerField, TextField, TimestampField

from common.decorators import cached_property

LOG = logging.getLogger(__name__)


class UTCTimestampField(TimestampField):
    """TimestampField which always returns a timezone aware value."""

    def __init__(self, null: bool = False, defaults_to_now: bool = False, **kwargs: Any) -> None:
        if defaults_to_now:
            # This is a convenient method to ensure newly created objects will have a timezone-aware value. It doesn't
            # affect what is stored in the database.
            kwargs["default"] = lambda: datetime.utcnow().replace(tzinfo=timezone.utc)
        else:
            kwargs["default"] = None

        # 1_000_000 is the default resolution for a datetime object; setting this ensures we get the same object out as
        # we put in.
        super().__init__(null=null, utc=True, resolution=1_000_000, **kwargs)

    def python_value(self, value: Union[int, float]) -> Optional[datetime]:
        if isinstance(ret_val := super().python_value(value), datetime):
            return ret_val.replace(tzinfo=timezone.utc)
        else:
            return None


class DomainField(CharField):
    """A field which matches a valid domain name or, alternatively a valid IP address."""

    @cached_property
    def _domain_re(self) -> Pattern:
        """Regex that only matches a valid domain."""
        # Note that with lookaheads and lookbehinds, the cursor doesn't move when matching
        return re.compile(
            r"^(?=.{1,255}$)"  # Lookahead: validate a max length
            r"(?![.\-])"  # Negative lookahead: next character (first) can't be a period or dash
            r"([^\W_]|-){1,63}"  # Real start: match unicode word characters & underscore with max len 63
            r"(\.([^\W_]|-){1,63})*"  # Same as prev, but can start with a . and repeat many times (.bar.baz.bingle)
            r"(?<![.\-])$"  # Negative lookbehind: prev char cannot be - or .
        )

    def _validate_domain(self, value: str) -> None:
        """Ensure the given value is a valid domain name."""

        try:
            socket.inet_aton(value)
        except OSError:
            pass
        else:
            return None  # String was a valid IP address

        if not self._domain_re.match(value):
            raise ValueError(f"Invalid domain name: `{value}`")

        # If the decoded value differs from the encoded one then the original value had characters that are not IDNA
        # compatible.
        # NOTE: This is IDNA2003, there is an update IDNA2008 which supports more characters but isn't part of the
        # standard library. The odds that we'll encounter something that requires it are pretty low, but if we ever do,
        # we can switch to validating using the `idna` package on pypi.
        try:
            if value.encode("idna").decode("idna") != value:
                raise ValueError(f"Domain `{value}` contains invalid characters")
        except UnicodeEncodeError:
            raise ValueError(f"Domain `{value}` contains invalid characters")

    def db_value(self, value: str) -> str:
        """Converts a value before sending it to the DB."""
        value = value.lower()  # All domain names are inherently lowercase
        value = normalize("NFC", value)  # Perform a canonical decomposition + composition
        self._validate_domain(value)
        db_value: str = super().db_value(value)
        return db_value


def _enum_value_to_db_value(enum_class: Type[Enum], value: Union[str, Enum, None]) -> Optional[str | int]:
    """Converts a value before sending it to the DB."""
    if value is None:
        return None
    if isinstance(value, enum_class):
        return cast(str | int, value.value)  # Send the actual enum value rather than the enum instance
    else:
        if isinstance(value, Enum):
            raise ValueError("Got an enum value `%s` but was not of Enum type `%s`", value, enum_class)
        try:
            enum_class(value)
        except Exception as e:
            LOG.exception("Unable to convert value `%s` to an Enum of type `%s`", value, enum_class)
            raise ValueError from e
        else:
            return value


def _db_value_to_enum_value(enum_class: Type[Enum], value: str | int) -> Optional[Enum]:
    if value:
        try:
            return enum_class(value)
        except Exception as e:
            raise ValueError(f"Invalid value `{value}` for Enum of type `{enum_class}`") from e
    else:
        return None


class EnumStrField(CharField):
    """Field which accepts enum values and coerces them."""

    def __init__(self, enum_class: Type[Enum], **kwargs: Any) -> None:
        self.enum_class = enum_class
        super().__init__(**kwargs)

    def db_value(self, value: Union[str, Enum, None]) -> Optional[str]:
        """Converts a value before sending it to the DB."""
        db_value: str = super().db_value(_enum_value_to_db_value(self.enum_class, value))
        return db_value

    def python_value(self, value: str) -> Optional[Enum]:
        return _db_value_to_enum_value(self.enum_class, super().python_value(value))


class EnumIntField(IntegerField):
    """Field which accepts enum values and coerces them."""

    def __init__(self, enum_class: Type[Enum], **kwargs: Any) -> None:
        self.enum_class = enum_class
        super().__init__(**kwargs)

    def db_value(self, value: Union[str, Enum, None]) -> Optional[str]:
        """Converts a value before sending it to the DB."""
        db_value: str = super().db_value(_enum_value_to_db_value(self.enum_class, value))
        return db_value

    def python_value(self, value: str) -> Optional[Enum]:
        return _db_value_to_enum_value(self.enum_class, super().python_value(value))


class ZoneInfoField(CharField):
    """A field which matches a valid timezone name, as supported by `zoneinfo`."""

    def python_value(self, value: Any) -> Any:
        if value and isinstance(value, str):
            try:
                return ZoneInfo(value)
            except ZoneInfoNotFoundError:
                pass
        return value


class JSONStrListField(TextField):
    """
    A field for storing a list of strings in a JSON field.

    This field is expected to be used with databases which support a JSON field type. It is not compatible with
    JSONB fields in Postgresql or other similar implementations.
    """

    field_type = "JSON"

    def __init__(self, **kwargs: Any) -> None:
        """Ensure that `default` is always the list function or a function that returns a list."""
        if (default_func := kwargs.get("default", None)) not in (None, list):
            try:
                _result = default_func()
            except Exception as e:
                raise TypeError(
                    f"JSONStrListField `default` must be `list` or callable that returns a list. Got: {default_func}"
                ) from e
            if not isinstance(_result, list):
                raise TypeError("JSONStrListField `default` must be `list` or callable that returns a list.")
        else:
            kwargs["default"] = list
        super().__init__(**kwargs)

    def db_value(self, value: Optional[list[str]]) -> Optional[str]:
        """Dump a list of strings as a JSON string. Keeps key order consistent."""
        if value is not None:
            if not isinstance(value, list):
                raise ValueError(f"JSONStrListField only accepts a list of string values; got {type(value)}")
            for idx, item in enumerate(value):
                if not isinstance(item, str):
                    raise ValueError(f"Item value {item} at index {idx} is not a string value.")
            return json_dumps(value, sort_keys=True)
        else:
            return None

    def python_value(self, value: Optional[str]) -> Optional[list[str]]:
        """Load the text retrieved from the JSON field into a list."""
        if value is not None:
            try:
                str_list: list[str] = json_loads(value)
            except Exception as e:
                raise ValueError(f"Unable to load value `{value}` as json.") from e
            if not isinstance(str_list, list):
                raise ValueError(f"Invalid value `{value}`; does not deserialize into a list.")
            for idx, item in enumerate(str_list):
                if not isinstance(item, str):
                    raise ValueError(f"Item value {item} at index {idx} is not a string value.")
            return str_list
        else:
            return None


class JSONDictListField(TextField):
    """A field for storing a list of dicts in a JSON field."""

    field_type = "JSON"

    def __init__(self, **kwargs: Any) -> None:
        """Ensure that `default` is always the list function or a function that returns a list."""
        if (default_func := kwargs.get("default", None)) not in (None, list):
            try:
                _result = default_func()
            except Exception as e:
                raise TypeError(
                    f"JSONDictListField `default` must be `list` or callable that returns a list. Got: {default_func}"
                ) from e
            if not isinstance(_result, list):
                raise TypeError("JSONDictListField `default` must be `list` or callable that returns a list.")
        else:
            kwargs["default"] = list
        super().__init__(**kwargs)

    def db_value(self, value: Optional[list[dict]]) -> Optional[str]:
        """Dump a list of strings as a JSON string. Keeps key order consistent."""
        if value is not None:
            if not isinstance(value, list):
                raise ValueError(f"JSONDictListField only accepts a list of string values; got {type(value)}")
            for idx, item in enumerate(value):
                if not isinstance(item, dict):
                    raise ValueError(f"Item value {item} at index {idx} is not a mapping value.")
            return json_dumps(value, sort_keys=True)
        else:
            return None

    def python_value(self, value: Optional[str]) -> Optional[list[dict]]:
        """Load the text retrieved from the JSON field into a list."""
        if value is not None:
            try:
                dict_list: list[dict] = json_loads(value)
            except Exception as e:
                raise ValueError(f"Unable to load value `{value}` as json.") from e
            if not isinstance(dict_list, list):
                raise ValueError(f"Invalid value `{value}`; does not deserialize into a list.")
            for idx, item in enumerate(dict_list):
                if not isinstance(item, dict):
                    raise ValueError(f"Item value {item} at index {idx} is not a mapping value.")
            return dict_list
        else:
            return None
