import pytest
from marshmallow import Schema, ValidationError
from marshmallow.fields import Str

from common.schemas.validators.regexp import IsRegexp

_MAX_LENGTH: int = 10


class TestSchema(Schema):
    test = Str(validate=IsRegexp())


@pytest.fixture
def valid_data():
    return {"test": "a"}


@pytest.fixture
def invalid_data():
    return {"test": "(a"}


@pytest.mark.unit
def test_valid(valid_data):
    data = TestSchema().load(valid_data)
    assert data["test"] == "a"


@pytest.mark.unit
def test_invalid(invalid_data):
    with pytest.raises(ValidationError):
        TestSchema().load(invalid_data)
