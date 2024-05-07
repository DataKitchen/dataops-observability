from datetime import datetime, timezone
from enum import Enum, IntEnum
from zoneinfo import ZoneInfo

import pytest

from common.peewee_extensions.fields import (
    DomainField,
    EnumIntField,
    EnumStrField,
    JSONDictListField,
    JSONStrListField,
    UTCTimestampField,
    ZoneInfoField,
)

INVALID_DOMAINS: tuple[str, ...] = (
    "http://foo.com",  # Invalid because a full url
    "-foo.bar",  # Invalid for starting with a hypen
    "foo.bar-",  # Invalid for ending with a hypen
    "dog:cat",  # Invalid because : characters are not allowed
    ".happy",  # Invalid because domains cannot start with a .
    "happy.",  # Invalid because domains cannot end with a .
    "domain name",  # Invalid because domains cannot contain a space character
    "domain_name",  # Invalid because domains cannot contain an underscore
    "fa\u00dfbender",  # Invalid because \u00DF breaks IDNA compatibility
)

VALID_DOMAINS: tuple[str, ...] = (
    "127.0.0.1",  # Valid IP address
    "localhost",
    "domain.com",
    "a-hyphen.names",
    "long-names.with-hyphens.many-times",
    "test.domain.com",
    "longer.subdomain.than.normal",
    "t\u00fcrk",
    "\u00c7irkin",
    "\u0043\u0327irkin",
)


@pytest.mark.unit
@pytest.mark.parametrize("value", INVALID_DOMAINS)
def test_domain_field_invalid_db_value(value):
    """DomainField.db_value raises ValueError for invalid domain names."""
    f_inst = DomainField()
    with pytest.raises(ValueError):
        f_inst.db_value(value)


@pytest.mark.unit
@pytest.mark.parametrize("value", VALID_DOMAINS)
def test_domain_field_valid_db_value(value):
    """DomainField.db_value validation succeeds for valid domain names."""
    f_inst = DomainField()
    try:
        f_inst.db_value(value)
    except Exception:
        raise AssertionError(f"Value `{value}` is a valid domain and should not have raised an exception")


@pytest.mark.unit
def test_domain_field_normalization():
    """DomainField.db_value normalizes inputs."""
    decomposed = "\u0063\u0327"  # c followed by a combining cedillia
    composed = "\u00e7"  # the combined c + cedillia character
    assert decomposed != composed
    f_inst = DomainField()
    normalized = f_inst.db_value(decomposed)
    assert normalized == composed


@pytest.mark.unit
def test_domain_field_lowercase():
    """DomainField.db_value lowercases inputs."""
    f_inst = DomainField()
    lowered = f_inst.db_value("Test.Domain")
    assert lowered == "test.domain"


@pytest.mark.unit
def test_timestamp_to_utc():
    """UTCTimestampField.python_value returns timezone aware values."""
    expected_dt = datetime.now(timezone.utc)
    f_inst = UTCTimestampField()
    db_value = f_inst.db_value(expected_dt)
    result = f_inst.python_value(db_value)
    assert result.tzinfo is not None, "Converted value should have tzinfo"
    assert result == expected_dt


@pytest.mark.unit
def test_naive_to_utc():
    """UTCTimestampField.python_value returns timezone aware values even if input value was naive."""
    input_dt = datetime.utcnow()
    f_inst = UTCTimestampField()
    db_value = f_inst.db_value(input_dt)
    result = f_inst.python_value(db_value)
    assert result.tzinfo is not None, "Converted value should have tzinfo"
    assert result.year == input_dt.year
    assert result.month == input_dt.month
    assert result.day == input_dt.day
    assert result.hour == input_dt.hour
    assert result.minute == input_dt.minute
    assert result.second == input_dt.second
    assert result.resolution == input_dt.resolution


class ExampleEnum(Enum):
    """Simple enum for testing the EnumStrField."""

    RED = "R"
    BLUE = "B"
    GREEN = "G"


@pytest.mark.unit
def test_enum_str_field_python_value_valid():
    """EnumStrField.python_value yields an Enum instance for valid strings."""
    f_inst = EnumStrField(ExampleEnum)
    python_value = f_inst.python_value("B")
    assert python_value is ExampleEnum.BLUE


@pytest.mark.unit
def test_enum_str_field_python_value_invalid():
    """EnumStrField.python_value raises a ValueError for invalid strings."""
    f_inst = EnumStrField(ExampleEnum)
    with pytest.raises(ValueError):
        f_inst.python_value("BADVALUE")


@pytest.mark.unit
def test_enum_str_field_db_value_valid_enum():
    """EnumStrField.db_value yields an appropriate string from a valid enum."""
    f_inst = EnumStrField(ExampleEnum)
    result = f_inst.db_value(ExampleEnum.GREEN)
    assert result == "G"


@pytest.mark.unit
def test_enum_str_field_db_value_valid_str():
    """EnumStrField.db_value yields the original string when given a valid string."""
    f_inst = EnumStrField(ExampleEnum)
    result = f_inst.db_value("G")
    assert result == "G"


@pytest.mark.unit
def test_enum_str_field_db_value_invalid_enum():
    """EnumStrField.db_value raises a ValueError when handed an invalid Enum."""
    f_inst = EnumStrField(ExampleEnum)

    class OtherEnum:
        YES: str = "Y"
        NO: str = "N"

    with pytest.raises(ValueError):
        f_inst.db_value(OtherEnum.NO)


@pytest.mark.unit
def test_enum_str_field_db_value_invalid_str():
    """EnumStrField.db_value raises a ValueError when handed an invalid string."""
    f_inst = EnumStrField(ExampleEnum)
    with pytest.raises(ValueError):
        f_inst.db_value("BADVALUE")


class ExampleIntEnum(IntEnum):
    """Simple enum for testing the EnumIntField."""

    ONE = 1
    TWO = 2


@pytest.mark.unit
def test_enum_int_field_python_value_valid():
    """EnumIntField.python_value yields an Enum instance for valid integers."""
    f_inst = EnumIntField(ExampleIntEnum)
    python_value = f_inst.python_value(1)
    assert python_value is ExampleIntEnum.ONE


@pytest.mark.unit
def test_enum_int_field_python_value_invalid():
    """EnumIntField.python_value raises a ValueError for invalid integer."""
    f_inst = EnumIntField(ExampleIntEnum)
    with pytest.raises(ValueError):
        f_inst.python_value(4)


@pytest.mark.unit
def test_enum_int_field_db_value_valid_enum():
    """EnumIntField.db_value yields an appropriate int from a valid enum."""
    f_inst = EnumIntField(ExampleIntEnum)
    result = f_inst.db_value(ExampleIntEnum.ONE)
    assert result == 1


@pytest.mark.unit
def test_enum_int_field_db_value_valid_int():
    """EnumIntField.db_value yields the original int when given a valid int."""
    f_inst = EnumIntField(ExampleIntEnum)
    result = f_inst.db_value(2)
    assert result == 2


@pytest.mark.unit
def test_enum_int_field_db_value_invalid_enum():
    """EnumIntField.db_value raises a ValueError when handed an invalid Enum."""
    f_inst = EnumIntField(ExampleIntEnum)

    class OtherEnum(IntEnum):
        YES = 4
        NO = 2

    with pytest.raises(ValueError):
        f_inst.db_value(OtherEnum.NO)


@pytest.mark.unit
def test_enum_int_field_db_value_invalid_int():
    """EnumIntField.db_value raises a ValueError when handed an invalid int."""
    f_inst = EnumIntField(ExampleEnum)
    with pytest.raises(ValueError):
        f_inst.db_value(5)


@pytest.mark.unit
def test_zoneinfo_field_value():
    f_inst = ZoneInfoField()
    str_value = "America/Buenos_Aires"
    zi_value = ZoneInfo(str_value)

    db_value = f_inst.db_value(zi_value)
    py_value = f_inst.python_value(str_value)

    assert db_value == str_value
    assert py_value == zi_value


@pytest.mark.unit
def test_json_str_list_field_python_value_valid():
    """JSONStrListField.python_value yields an list of strings for valid input."""
    f_inst = JSONStrListField()
    actual = f_inst.python_value('["a", "b", "c"]')
    expected = ["a", "b", "c"]
    assert expected == actual


@pytest.mark.unit
@pytest.mark.parametrize("badval", ["BADVALUE", "{}", "", "[1, 2]"])
def test_json_str_list_field_python_value_invalid(badval):
    """JSONStrListField.python_value raises a ValueError for invalid input."""
    f_inst = JSONStrListField()
    with pytest.raises(ValueError):
        f_inst.python_value(badval)


@pytest.mark.unit
def test_json_str_list_field_db_value_valid_input():
    """JSONStrListField.db_value yields an appropriate db value from a list of strings."""
    f_inst = JSONStrListField()
    expected = '["a", "b", "c"]'
    actual = f_inst.db_value(["a", "b", "c"])
    assert expected == actual


@pytest.mark.unit
@pytest.mark.parametrize("badval", [object(), tuple(), [1, 2]])
def test_json_str_list_field_db_value_invalid(badval):
    """JSONStrListField.db_value raises a ValueError for invalid input."""
    f_inst = JSONStrListField()
    with pytest.raises(ValueError):
        f_inst.db_value(badval)


def _bad_default():
    """A function which does not return a list (used to test JSONStrListField default argument)."""
    return ("a", "b", "c")


@pytest.mark.unit
@pytest.mark.parametrize("default", [dict, _bad_default, ["a", "b", "c"], object()])
def test_json_str_list_field_invalid_default(default):
    """JSONStrListField raises a TypeError when given an invalid default argument."""
    with pytest.raises(TypeError):
        JSONStrListField(default=default)


def _good_default():
    """A function which does return a list (used to test JSONStrListField default argument)."""
    return ["a", "b", "c"]


@pytest.mark.unit
@pytest.mark.parametrize("default", [list, _good_default])
def test_json_str_list_field_valid_default(default):
    """JSONStrListField does not raise a TypeError when given a valid default argument."""
    try:
        JSONStrListField(default=default)
    except TypeError:
        raise AssertionError(f"The default: `{default}` should have been a valid default argument")


@pytest.mark.unit
def test_json_dict_list_field_python_value_valid():
    """JSONDictListField.python_value yields an list of strings for valid input."""
    f_inst = JSONDictListField()
    actual = f_inst.python_value('[{"a": 1}, {"a": 4}]')
    expected = [{"a": 1}, {"a": 4}]
    assert expected == actual


@pytest.mark.unit
@pytest.mark.parametrize("badval", ["BADVALUE", "{}", "", "[1, 2]"])
def test_json_dict_list_field_python_value_invalid(badval):
    """JSONDictListField.python_value raises a ValueError for invalid input."""
    f_inst = JSONDictListField()
    with pytest.raises(ValueError):
        f_inst.python_value(badval)


@pytest.mark.unit
def test_json_dict_list_field_db_value_valid_input():
    """JSONDictListField.db_value yields an appropriate db value from a list of strings."""
    f_inst = JSONDictListField()
    expected = '[{"a": 1}, {"a": 4}]'
    actual = f_inst.db_value([{"a": 1}, {"a": 4}])
    assert expected == actual


@pytest.mark.unit
@pytest.mark.parametrize("badval", [object(), tuple(), [1, 2]])
def test_json_dict_list_field_db_value_invalid(badval):
    """JSONDictListField.db_value raises a ValueError for invalid input."""
    f_inst = JSONDictListField()
    with pytest.raises(ValueError):
        f_inst.db_value(badval)


def _bad_dict_list_default():
    """A function which does not return a list (used to test JSONDictListField default argument)."""
    return ({"a": 1}, {"a": 4})


@pytest.mark.unit
@pytest.mark.parametrize("default", [dict, _bad_dict_list_default, [{"a": 1}, {"a": 4}], object()])
def test_json_dict_list_field_invalid_default(default):
    """JSONDictListField raises a TypeError when given an invalid default argument."""
    with pytest.raises(TypeError):
        JSONDictListField(default=default)


def _good_dict_list_default():
    """A function which does return a list of dicts (used to test JSONDictListField default argument)."""
    return [{"a": 1}, {"a": 4}]


@pytest.mark.unit
@pytest.mark.parametrize("default", [list, _good_dict_list_default])
def test_json_dict_list_field_valid_default(default):
    """JSONDictListField does not raise a TypeError when given a valid default argument."""
    try:
        JSONDictListField(default=default)
    except TypeError:
        raise AssertionError(f"The default: `{default}` should have been a valid default argument")
