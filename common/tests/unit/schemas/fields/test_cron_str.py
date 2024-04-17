import pytest
from marshmallow import Schema, ValidationError

from common.schemas.fields import CronExpressionStr


@pytest.fixture
def schema():
    class TestSchema(Schema):
        f1 = CronExpressionStr()

    return TestSchema()


@pytest.mark.unit
@pytest.mark.parametrize("cron", ("* * * * *", "  12 13 14 * 5", "0 0 * * *   "))
def test_valid_cron(schema, cron):
    obj = schema.load({"f1": cron})
    assert obj["f1"] == cron


@pytest.mark.unit
@pytest.mark.parametrize("cron", ("not_a_cron", "42", ".", "* * * * ", "* * * * * *", "", None))
def test_invalid_cron(schema, cron):
    with pytest.raises(ValidationError):
        schema.load({"f1": cron})
