import logging
from array import array
from collections import OrderedDict
from dataclasses import is_dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum, IntEnum
from importlib import import_module
from io import BytesIO
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from types import MappingProxyType
from typing import Any, BinaryIO, Optional, TextIO, Union, cast
from collections.abc import Callable
from uuid import UUID

import msgpack
from boltons.dictutils import FrozenDict
from boltons.ioutils import SpooledBytesIO, SpooledStringIO
from msgpack import ExtType

from common.events.v2 import BatchPipelineStatus, MessageLog, MetricLog, TestOutcomes

path_order = [PurePath, PurePosixPath, PureWindowsPath, Path]
try:
    from pathlib import PosixPath
except ImportError:
    has_posixpath = False
else:
    has_posixpath = True
    path_order.append(PosixPath)
try:
    from pathlib import WindowsPath
except ImportError:
    has_windowspath = False
else:
    has_windowspath = True
    path_order.append(WindowsPath)

LOG = logging.getLogger(__name__)

FLO = Union[BinaryIO, BytesIO, SpooledBytesIO, SpooledStringIO, TextIO]
"""Files and file-like-objects."""


V2_EVENTS = FrozenDict(
    {
        1: MessageLog,
        2: MetricLog,
        3: BatchPipelineStatus,
        4: TestOutcomes,
    }
)
"""Registry of V2 Event IDs to Event classes."""

V2_EVENTS_REV_MAP = FrozenDict({v: k for k, v in V2_EVENTS.items()})
"""Registry of Event classes to Event ID's."""


class TypeID(IntEnum):
    TUPLE = 1
    DATETIME = 2
    DATE = 3
    TIME = 4
    DECIMAL = 5
    UUID = 6
    SLICE = 7
    RANGE = 8
    ARRAY = 9
    PATH = 10
    MAPPING_PROXY = 11
    DATACLASS = 12
    ORDERED_DICT = 13
    SET = 14
    FROZEN_SET = 15
    ENUM = 16
    V2_EVENT = 50


def import_string(import_name: str) -> Any:
    """
    Attempt to import a module or module attribute from a dot-notation string path.

    Example::

        >>> ret = import_string("datetime.date")
        >>> from datetime import date  # The string import should have simulated this import
        >>> ret is date
        True
    """
    try:
        return import_module(import_name)
    except ImportError as i:
        if "." in import_name:
            # It might be a module name attribute; simulate a "from" import
            module_name, value = import_name.rsplit(".", maxsplit=1)
            try:
                package = import_module(module_name)
            except ImportError as ie:
                raise ImportError(f"Unable to import `{import_name}`") from ie
            try:
                return getattr(package, value)
            except AttributeError as a:
                raise ImportError(f"Unable to import `{import_name}`") from a
        else:
            raise ImportError(f"Unable to import `{import_name}`") from i


def serialize_custom(value: object) -> object:
    """Encode types that are not part of the standard scalars."""
    match value:
        case tuple():
            return ExtType(TypeID.TUPLE.value, dumps(list(value)))
        case frozenset():
            return ExtType(TypeID.FROZEN_SET.value, dumps(tuple(value)))
        case set():
            return ExtType(TypeID.SET.value, dumps(tuple(value)))
        case OrderedDict():
            return ExtType(TypeID.ORDERED_DICT.value, dumps([(k, v) for k, v in value.items()]))
        case datetime():
            return ExtType(TypeID.DATETIME.value, value.isoformat().encode("utf-8"))
        case date():
            return ExtType(TypeID.DATE.value, value.toordinal().to_bytes(3, "little"))
        case time():
            return ExtType(TypeID.TIME.value, value.isoformat().encode("utf-8"))
        case Decimal():
            return ExtType(TypeID.DECIMAL.value, str(value).encode("utf-8"))
        case UUID():
            return ExtType(TypeID.UUID.value, value.int.to_bytes(128, "little"))
        case slice():
            return ExtType(TypeID.SLICE.value, dumps((value.start, value.stop, value.step)))
        case range():
            return ExtType(TypeID.RANGE.value, dumps((value.start, value.stop, value.step)))
        case array():
            return ExtType(TypeID.ARRAY.value, dumps((value.tobytes(), value.typecode)))
        case PurePath():
            for path_type in path_order[::-1]:
                if isinstance(value, path_type):
                    return ExtType(TypeID.PATH.value, dumps((path_type.__name__, str(value))))
            return value
        case MappingProxyType():
            return ExtType(TypeID.MAPPING_PROXY.value, dumps(dict(value)))
        case MessageLog():
            data = {x: getattr(value, x) for x in value.__dataclass_fields__.keys()}
            return ExtType(TypeID.V2_EVENT, dumps((V2_EVENTS_REV_MAP[MessageLog], data)))
        case MetricLog():
            data = {x: getattr(value, x) for x in value.__dataclass_fields__.keys()}
            return ExtType(TypeID.V2_EVENT, dumps((V2_EVENTS_REV_MAP[MetricLog], data)))
        case TestOutcomes():
            data = {x: getattr(value, x) for x in value.__dataclass_fields__.keys()}
            return ExtType(TypeID.V2_EVENT, dumps((V2_EVENTS_REV_MAP[TestOutcomes], data)))
        case BatchPipelineStatus():
            data = {x: getattr(value, x) for x in value.__dataclass_fields__.keys()}
            return ExtType(TypeID.V2_EVENT, dumps((V2_EVENTS_REV_MAP[BatchPipelineStatus], data)))
        case Enum():
            return ExtType(
                TypeID.ENUM, dumps((f"{value.__class__.__module__}.{value.__class__.__name__}", value.value))
            )
        case _:
            if is_dataclass(value) and not isinstance(value, type):
                data = {x: getattr(value, x) for x in value.__dataclass_fields__.keys()}
                return ExtType(
                    TypeID.DATACLASS, dumps((f"{value.__class__.__module__}.{value.__class__.__name__}", data))
                )
            else:
                return value


def decode_ext(code: int, data: bytes) -> object:
    """Decode ExtTypes into their original object representation."""
    match code:
        case TypeID.TUPLE:
            loaded_data = loads(data)
            if isinstance(loaded_data, list):
                return tuple(loaded_data)
            elif isinstance(loaded_data, tuple):
                return loaded_data
            else:
                LOG.warning("Got extended type %s but loaded data was not a list or tuple", code)
                return ExtType(code, data)
        case TypeID.FROZEN_SET:
            loaded_data = cast(tuple, loads(data))
            return frozenset(loaded_data)
        case TypeID.SET:
            loaded_data = cast(tuple, loads(data))
            return set(loaded_data)
        case TypeID.ORDERED_DICT:
            unsorted_dict = cast(tuple[tuple[object, object]], loads(data))
            return OrderedDict(unsorted_dict)
        case TypeID.DATE:
            ordinal = int.from_bytes(data, "little")
            return date.fromordinal(ordinal)
        case TypeID.DATETIME:
            return datetime.fromisoformat(data.decode("utf-8"))
        case TypeID.TIME:
            return time.fromisoformat(data.decode("utf-8"))
        case TypeID.DECIMAL:
            return Decimal(data.decode("utf-8"))
        case TypeID.RANGE:
            start, stop, step = cast(tuple[int, int, int], loads(data))
            return range(start, stop, step)
        case TypeID.SLICE:
            start, stop, step = cast(tuple[int, int, int], loads(data))
            return slice(start, stop, step)
        case TypeID.ARRAY:
            array_data = cast(tuple[bytes, str], loads(data))
            array_bytes = array_data[0]
            array_typecode = array_data[1]
            array_val = array(array_typecode)
            array_val.frombytes(array_bytes)
            return array_val
        case TypeID.UUID:
            uuid_int = int.from_bytes(data, "little")
            return UUID(int=uuid_int)
        case TypeID.MAPPING_PROXY:
            mapping_dict = cast(dict, loads(data))
            return MappingProxyType(mapping_dict)
        case TypeID.PATH:
            path_data = cast(tuple[str, str], loads(data))
            path_type: str = path_data[0]
            path_str: str = path_data[1]
            if path_type == "PurePath":
                return PurePath(path_str)
            elif path_type == "PurePosixPath":
                return PurePosixPath(path_str)
            elif path_type == "PureWindowsPath":
                return PureWindowsPath(path_str)
            elif path_type == "Path":
                return Path(path_str)
            elif path_type == "PosixPath":
                if has_posixpath is True:
                    return PosixPath(path_str)
                else:
                    return PurePosixPath(path_str)  # Best we can do if moving between systems
            elif path_type == "WindowsPath":
                if has_windowspath is True:
                    return WindowsPath(path_str)
                else:
                    return PureWindowsPath(path_str)  # Best we can do if moving between systems
            else:
                LOG.error("Path type: %s no match", path_type)
                return Path(path_str)  # Last result fallback
        case TypeID.V2_EVENT:
            event_data = cast(tuple[int, dict], loads(data))
            event_id = event_data[0]
            event_map = event_data[1]
            EventKlass = V2_EVENTS[event_id]
            return EventKlass(**event_map)
        case TypeID.ENUM:
            enum_data = cast(tuple[str, object], loads(data))
            enum_module = enum_data[0]
            enum_value = enum_data[1]
            enum_klass = import_string(enum_module)
            return enum_klass(enum_value)
        case TypeID.DATACLASS:
            dataclass_data = cast(tuple[str, dict], loads(data))
            dataclass_module = dataclass_data[0]
            dataclass_map = dataclass_data[1]
            dataklass = import_string(dataclass_module)
            return dataklass(**dataclass_map)
        case _:
            return ExtType(code, data)


def dump(value: object, flo: FLO, hook: Optional[Callable] = None) -> None:
    """
    Serialize as msgpack and write the result to a file-like-object.

    Usage::

        dump(my_data, flo)
    """
    if hook is None:
        hook = serialize_custom
    msgpack.pack(
        value,
        flo,
        default=hook,
        use_bin_type=True,
        datetime=False,
        strict_types=True,
    )


def dumps(value: object, hook: Optional[Callable] = None) -> bytes:
    """
    Serialize object to msgpack and return resulting messagepack bytes.

    Usage::

        bytes_value = dumps(my_data)
    """
    if hook is None:
        hook = serialize_custom
    result: bytes = msgpack.packb(value, default=hook, use_bin_type=True, datetime=False, strict_types=True)
    return result


def load(flo: FLO, object_hook: Optional[Callable] = None) -> Any:
    """
    Deserialize a msgpack file-like-object.

    Usage::

        my_data = load(some_flo)
    """
    orig = flo.tell()
    flo.seek(0)
    result = msgpack.unpack(
        flo,
        ext_hook=decode_ext,
        object_hook=object_hook,
        raw=False,
        strict_map_key=False,
        use_list=True,
    )
    flo.seek(orig)
    return result


def loads(stream: bytes, object_hook: Optional[Callable] = None) -> Any:
    """
    Deserialize msgpack bytes

    Usage::

        my_data = loads(some_bytes)
    """
    return msgpack.unpackb(
        stream,
        ext_hook=decode_ext,
        object_hook=object_hook,
        raw=False,
        strict_map_key=False,
        use_list=True,
    )
