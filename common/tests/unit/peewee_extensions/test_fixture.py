import pytest
from peewee import BlobField, BooleanField, CharField, IntegerField, UUIDField

from common.peewee_extensions import fixtures


@pytest.mark.unit
def test_jinja_filter_bool():
    true_data = {
        "field_instance": BooleanField(),
        "value": True,
    }
    assert fixtures.toml_value(true_data) == "true"

    false_data = {
        "field_instance": BooleanField(),
        "value": False,
    }
    assert fixtures.toml_value(false_data) == "false"


@pytest.mark.unit
def test_jinja_filter_bytes():
    data = {
        "field_instance": BlobField(),
        "value": "foo\u2014bar\u2013baz".encode(),
    }
    assert fixtures.toml_value(data) == '"Zm9v4oCUYmFy4oCTYmF6"'


@pytest.mark.unit
def test_jinja_filter_memoryview():
    data = {
        "field_instance": BlobField(),
        "value": memoryview("foo\u2014bar\u2013baz".encode()),
    }
    assert fixtures.toml_value(data) == '"Zm9v4oCUYmFy4oCTYmF6"'


@pytest.mark.unit
def test_jinja_filter_str():
    data = {
        "field_instance": CharField(),
        "value": "foobar",
    }
    assert fixtures.toml_value(data) == '"foobar"'


@pytest.mark.unit
def test_jinja_filter_int():
    data = {
        "field_instance": IntegerField(),
        "value": 1,
    }
    assert fixtures.toml_value(data) == "1"


@pytest.mark.unit
def test_jinja_filter_uuid_str():
    """UUID values should always dump as hyphenated version."""
    data = {
        "field_instance": UUIDField(),
        "value": "5cf02a7e752e45f090d5f4d7bbb7a31e",
    }
    assert fixtures.toml_value(data) == '"5cf02a7e-752e-45f0-90d5-f4d7bbb7a31e"'
