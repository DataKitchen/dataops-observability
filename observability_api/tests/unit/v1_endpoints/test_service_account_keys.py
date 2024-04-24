from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
from marshmallow.exceptions import ValidationError

from common.auth.keys.service_key import KeyPair
from common.constants.validation_messages import INVALID_INT_TYPE, MISSING_REQUIRED_FIELD, UNKNOWN_FIELD
from observability_api.endpoints.v1 import service_account_keys as ServiceAccountKeyRoutes
from observability_api.schemas.service_account_key_schemas import ServiceAccountKeySchema, ServiceAccountKeyTokenSchema


@pytest.fixture
def sa_key_model():
    model = Mock()
    ServiceAccountKeyRoutes.ServiceAccountKey = model
    yield model


@pytest.fixture
def project_model():
    model = Mock()
    ServiceAccountKeyRoutes.Project = model
    yield model


@pytest.fixture
def generate_sa_key():
    with patch("observability_api.endpoints.v1.service_account_keys.generate_key") as generate_key:
        yield generate_key


@pytest.mark.unit
@patch("observability_api.endpoints.entity_view.BaseEntityView.get_entity_or_fail")
def test_create_sa_key_with_invalid_request_throw_error(get_entity_or_fail, client, project):
    get_entity_or_fail.return_value = project
    with pytest.raises(ValidationError) as err:
        body = {"service_name": 123, "expires_after_days": "one"}
        response = client.post(
            f"/observability/v1/projects/{project.id}/service-account-key",
            headers={"Content-Type": "application/json"},
            json=body,
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

    get_entity_or_fail.assert_called_once()
    assert UNKNOWN_FIELD in str(err.value.messages["service_name"])
    assert INVALID_INT_TYPE in str(err.value.messages["expires_after_days"])
    assert MISSING_REQUIRED_FIELD in str(err.value.messages["name"])


@pytest.mark.unit
def test_sa_key_schema_dump(sa_key):
    res = ServiceAccountKeySchema().dump(sa_key)
    assert set(res.keys()) == {"id", "expires_at", "name", "description", "project", "allowed_services"}


@pytest.mark.unit
def test_sa_key_schema_token_dump(sa_key, generate_sa_key):
    generate_sa_key.return_value = KeyPair(sa_key, "abcxyz")
    res = ServiceAccountKeyTokenSchema().dump(generate_sa_key.return_value)
    assert set(res.keys()) == {"id", "expires_at", "name", "description", "project", "allowed_services", "token"}
