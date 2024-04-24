import pytest
from marshmallow.exceptions import ValidationError

from common.constants.validation_messages import MISSING_REQUIRED_FIELD, NULL_FIELD
from common.entities.authentication import Service
from observability_api.schemas.service_account_key_schemas import ServiceAccountKeyCreateSchema


@pytest.mark.unit
def test_sa_key_create_schema_load_with_seven_expires_after_days_value():
    res = ServiceAccountKeyCreateSchema().load(
        {"expires_after_days": 7, "name": "My Key Bruh", "allowed_services": [Service.EVENTS_API.value]}
    )
    assert res["expires_after_days"] == 7


@pytest.mark.unit
def test_sa_key_create_schema_load_with_none_expires_after_days_value():
    with pytest.raises(ValidationError) as err:
        ServiceAccountKeyCreateSchema().load(
            {"expires_after_days": None, "name": "My Key Bruh", "allowed_services": [Service.EVENTS_API.value]}
        )
    assert err.value.messages["expires_after_days"][0] == NULL_FIELD


@pytest.mark.unit
def test_sa_key_create_schema_load_without_expires_after_days_key():
    with pytest.raises(ValidationError) as err:
        ServiceAccountKeyCreateSchema().load({"name": "My Key Bruh", "allowed_services": [Service.EVENTS_API.value]})
    assert err.value.messages["expires_after_days"][0] == MISSING_REQUIRED_FIELD


@pytest.mark.unit
def test_sa_key_create_schema_load_allowed_services():
    res = ServiceAccountKeyCreateSchema().load(
        {
            "expires_after_days": 7,
            "name": "My Key Bruh",
            "allowed_services": [Service.EVENTS_API.name],
        }
    )
    assert res["allowed_services"] == [Service.EVENTS_API]


@pytest.mark.unit
@pytest.mark.parametrize(
    "service", [["events-api"], [""], [], None], ids=["invalid value", "empty string", "empty list", "none value"]
)
def test_sa_key_create_schema_load_invalid_allowed_services(service):
    payload = {"expires_after_days": 7, "name": "My Key Bruh", "allowed_services": service}
    with pytest.raises(ValidationError):
        ServiceAccountKeyCreateSchema().load(payload)
