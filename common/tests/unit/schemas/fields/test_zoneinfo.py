import zoneinfo

import pytest
from marshmallow import Schema, ValidationError

from common.schemas.fields import ZoneInfo


@pytest.fixture
def schema():
    class TestSchema(Schema):
        f1 = ZoneInfo()

    return TestSchema()


@pytest.mark.unit
@pytest.mark.parametrize("timezone", ("America/Phoenix", "America/New_York", "UTC", "Etc/GMT+4"))
def test_valid_timezone(schema, timezone):
    obj = schema.load({"f1": timezone})
    assert obj["f1"] == zoneinfo.ZoneInfo(timezone)


@pytest.mark.unit
@pytest.mark.parametrize("timezone", ("not_a_timezone", "42", "."))
def test_invalid_timezone(schema, timezone):
    with pytest.raises(ValidationError):
        schema.load({"f1": timezone})
