from dataclasses import MISSING, is_dataclass
from datetime import date, datetime, time
from enum import Enum
from json import JSONEncoder


class JsonExtendedEncoder(JSONEncoder):
    """
    Extend JSON encoder and fallback to string casting for unsupported types.

    Including the ability to add additional context to logging messages means there is less control over
    the what is passed TO log messages. This extended encoder ensures log messages can be emited as JSON
    without worrying about crashing (in most cases).

    Date, time and datetime instances are converted to strings in ISO8601 format.
    """

    def default(self, o: object) -> object:
        if isinstance(o, date | datetime | time):
            return o.isoformat()
        elif isinstance(o, tuple):
            return list(o)
        elif isinstance(o, set | frozenset):
            return sorted(o)  # Sorted returns a list
        elif isinstance(o, bytes | bytearray):
            try:
                return o.decode("utf-8")
            except UnicodeDecodeError:
                return o.hex()
        elif isinstance(o, Enum):
            return o.value
        elif is_dataclass(o) and not isinstance(o, type):
            return {x: getattr(o, x, MISSING) for x in o.__dataclass_fields__.keys()}
        else:
            return str(o)
