from enum import Enum

import pytest
from marshmallow import Schema, ValidationError

from common.schemas.fields import EnumStr


class SomeEnum(Enum):
    FOO = "foo"
    BAR = "bar"


class TestSchema(Schema):
    foo = EnumStr(enum=SomeEnum)
    bar = EnumStr(enum=SomeEnum)


class TestListSchema(Schema):
    foo = EnumStr(enum=["FOO", "BAR"])
    bar = EnumStr(enum=["FOO", "BAR"])


@pytest.fixture
def enum_str_data():
    return {"foo": "FOO", "bar": "bar"}


@pytest.fixture
def invalid_enum_data():
    return {"foo": "FOO", "bar": "baz"}


@pytest.mark.unit
def test_enum_str(enum_str_data):
    ex = TestSchema().load(enum_str_data)
    assert ex["foo"] == enum_str_data["foo"].upper()
    assert ex["bar"] == enum_str_data["bar"].upper()


@pytest.mark.unit
def test_enum_str_with_list(enum_str_data):
    ex = TestListSchema().load(enum_str_data)
    assert ex["foo"] == enum_str_data["foo"].upper()
    assert ex["bar"] == enum_str_data["bar"].upper()


@pytest.mark.unit
def test_enum_str_invalid_enum(invalid_enum_data):
    with pytest.raises(ValidationError):
        TestSchema().load(invalid_enum_data)


@pytest.mark.unit
def test_enum_str_dump(enum_str_data):
    ex = TestSchema().load(enum_str_data)
    expected = {"foo": "FOO", "bar": "BAR"}
    actual = TestSchema().dump(ex)
    assert expected == actual
