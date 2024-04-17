import json
from dataclasses import dataclass
from datetime import date, datetime, time
from enum import Enum
from uuid import UUID

import pytest

from common.json_encoder import JsonExtendedEncoder


@pytest.mark.unit
def test_json_extended_encoder():
    """JsonExtendedEncoder can handle arbitrary data types."""
    data = {
        "bytes": b"some\xe2\x80\x94value",
        "time": time(10, 42, 59, 746471),
        "datetime": datetime(2021, 11, 8, 10, 42, 59, 746471),
        "date": date(2021, 11, 8),
        "tuple": ("a", "b", "c"),
        "set": {"a", "b", "c"},
        "frozenset": frozenset(("a", "b", "c")),
        "uuid": UUID("f73170b8-b893-4627-a8d1-b0102f3bb03b"),
    }
    expected = """{"bytes": "some\\u2014value", "date": "2021-11-08", "datetime": "2021-11-08T10:42:59.746471", "frozenset": ["a", "b", "c"], "set": ["a", "b", "c"], "time": "10:42:59.746471", "tuple": ["a", "b", "c"], "uuid": "f73170b8-b893-4627-a8d1-b0102f3bb03b"}"""
    assert json.dumps(data, cls=JsonExtendedEncoder, sort_keys=True) == expected


@pytest.mark.unit
def test_dump_object_with_default():
    """JsonExtendedEncoder can dump a custom class instance."""

    class TestObj:
        def __init__(self, o: str):
            self.o = o

    expected = "test_dump_object_with_default.<locals>.TestObj object"
    actual = json.dumps(TestObj("flipper"), cls=JsonExtendedEncoder)
    assert expected in actual


@pytest.mark.unit
def test_dump_enum_value():
    """JsonExtendedEncoder can dump enums when they are `value` attributes."""

    class BasicEnum(Enum):
        a = "A"
        b = "B"

    data = {"key": BasicEnum.a}
    expected = '{"key": "A"}'
    actual = json.dumps(data, cls=JsonExtendedEncoder)
    assert expected == actual


@pytest.mark.unit
def test_dump_dataclass():
    """JsonExtendedEncoder can dump dataclasses."""

    @dataclass
    class SomeThing:
        a: str
        b: str

    data = SomeThing("foo", "bar")
    expected = '{"a": "foo", "b": "bar"}'
    actual = json.dumps(data, cls=JsonExtendedEncoder, sort_keys=True)
    assert expected == actual


@pytest.mark.unit
def test_dump_dict_with_dataclass_value():
    """JsonExtendedEncoder can dump data where a nested value is an instance of a dataclass."""

    @dataclass
    class SomeThing:
        a: str
        b: str

    some_thing = SomeThing("foo", "bar")
    data = {"thing": some_thing}
    expected = '{"thing": {"a": "foo", "b": "bar"}}'
    actual = json.dumps(data, cls=JsonExtendedEncoder, sort_keys=True)
    assert expected == actual


@pytest.mark.unit
def test_dump_bytes_hex():
    """JsonExtendedEncoder dumps arbitrary non-text bytes as hex."""
    data = {"bytes": b"\xde\xad\xbe\xef"}
    expected = '{"bytes": "deadbeef"}'
    actual = json.dumps(data, cls=JsonExtendedEncoder)
    assert expected == actual


@pytest.mark.unit
def test_dump_bytearray_hex():
    """JsonExtendedEncoder dumps arbitrary non-text bytearrays as hex."""
    data = {"bytes": bytearray(b"\xde\xad\xbe\xef")}
    expected = '{"bytes": "deadbeef"}'
    actual = json.dumps(data, cls=JsonExtendedEncoder)
    assert expected == actual
