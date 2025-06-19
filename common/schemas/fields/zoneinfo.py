__all__ = ["ZoneInfo"]

import zoneinfo
from typing import Any
from collections.abc import Mapping

from marshmallow.fields import Str

from common.constants.validation_messages import INVALID_TIMEZONE


class ZoneInfo(Str):
    """
    Holds a String value that Represents a timezone. Any format `pytz` recognizes is valid.
    """

    default_error_messages = {"invalid_timezone": INVALID_TIMEZONE}

    def _deserialize(self, value: Any, attr: str | None, data: Mapping[str, Any] | None, **kwargs: object) -> Any:
        str_value = super(Str, self)._deserialize(value, attr, data, **kwargs)
        # Given ZoneInfo accepts a filesystem type as its constructor argument and we don't want to accept paths as
        # values for ZoneInfo fields, we validate the input before trying to build the ZoneInfo object
        if str_value not in zoneinfo.available_timezones():
            raise self.make_error("invalid_timezone")
        return zoneinfo.ZoneInfo(str_value)
