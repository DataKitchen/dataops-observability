import pytest
from marshmallow import Schema, ValidationError

from common.schemas.fields import NormalizedStr


@pytest.fixture
def normalized_str_data():
    return {"foo": "FOO", "bar": "bar", "baz": "BaZ"}


class TestSchema(Schema):
    foo = NormalizedStr()
    bar = NormalizedStr()
    baz = NormalizedStr()


@pytest.mark.unit
def test_normalized_str(normalized_str_data):
    ex = TestSchema().load(normalized_str_data)
    assert ex["foo"] == normalized_str_data["foo"].upper()
    assert ex["bar"] == normalized_str_data["bar"].upper()
    assert ex["baz"] == normalized_str_data["baz"].upper()


@pytest.mark.unit
def test_norm_str_none(normalized_str_data):
    normalized_str_data["foo"] = None
    # this hits the None condition
    result = TestSchema().dump(normalized_str_data)
    assert result["foo"] is None


@pytest.mark.unit
def test_norm_str_invalid_type(normalized_str_data):
    normalized_str_data["foo"] = ["list"]
    with pytest.raises(ValidationError) as e:
        TestSchema().load(normalized_str_data)
    assert e.value.args[0]["foo"] == ["Not a valid string."]


@pytest.mark.unit
@pytest.mark.parametrize(
    argnames=("invalid_unicode",),
    argvalues=((b"\xf0\x28\x8c\xbc",), (b"\xfc\xa1\xa1\xa1\xa1\xa1",)),
    ids=("invalid_4_octet_second_oct", "invalid_6_octet"),
)
def test_norm_str_invalid_unicode(normalized_str_data, invalid_unicode):
    normalized_str_data["foo"] = invalid_unicode
    with pytest.raises(ValidationError) as e:
        TestSchema().load(normalized_str_data)
    assert e.value.args[0]["foo"] == ["Not a valid utf-8 string."]
