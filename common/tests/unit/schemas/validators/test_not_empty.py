import pytest
from marshmallow import Schema, ValidationError
from marshmallow.fields import Str

from common.schemas.validators import not_empty

_MAX_LENGTH: int = 10


class EmptyMinSchema(Schema):
    test = Str(validate=not_empty())


class EmptyMaxSchema(Schema):
    test = Str(validate=not_empty(max=_MAX_LENGTH))


@pytest.fixture
def valid_data():
    return {"test": "a"}


@pytest.mark.unit
def test_not_empty_empty():
    empty_data = {"test": ""}
    with pytest.raises(ValidationError):
        EmptyMinSchema().load(empty_data)
    with pytest.raises(ValidationError):
        EmptyMaxSchema().load(empty_data)


@pytest.mark.unit
def test_min_not_empty(valid_data):
    data = EmptyMinSchema().load(valid_data)
    assert data["test"] == valid_data["test"]


@pytest.mark.unit
def test_not_empty_with_max(valid_data):
    valid_data["test"] = "a" * _MAX_LENGTH
    data = EmptyMinSchema().load(valid_data)
    assert data["test"] == valid_data["test"]

    invalid_data = {"test": "a" * (_MAX_LENGTH + 1)}
    with pytest.raises(ValidationError):
        EmptyMaxSchema().load(invalid_data)
