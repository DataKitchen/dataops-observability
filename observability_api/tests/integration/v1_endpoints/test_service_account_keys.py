import uuid
from datetime import datetime, timezone, UTC
from http import HTTPStatus

import pytest

from common.auth.keys.service_key import generate_key
from common.constants import INVALID_INT_TYPE, MISSING_REQUIRED_FIELD, NULL_FIELD
from common.datetime_utils import datetime_iso8601
from common.entities import Service, ServiceAccountKey
from observability_api.tests.integration.v1_endpoints.conftest import TIMESTAMP_FORMAT


@pytest.fixture
def sa_key_data():
    return {"expires_after_days": 7, "name": "Mah Keyz", "allowed_services": [Service.EVENTS_API.name]}


@pytest.fixture
def sa_key(client, project):
    sa_key = generate_key(allowed_services=[Service.EVENTS_API.name], name="Test Key", project=project.id)
    yield sa_key


@pytest.mark.integration
def test_create_sa_key_success(client, g_user, project, sa_key_data):
    today = datetime.now(UTC)
    response = client.post(
        f"/observability/v1/projects/{project.id}/service-account-key",
        headers={"Content-Type": "application/json"},
        json=sa_key_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json

    expires_at_datetime = datetime.strptime(data["expires_at"], TIMESTAMP_FORMAT)
    assert len(data["id"]) > 0
    assert (expires_at_datetime - today).days == sa_key_data["expires_after_days"]
    assert data["allowed_services"] == sa_key_data["allowed_services"]
    assert data["project"] == str(project.id)
    assert data["name"] == sa_key_data["name"]
    assert len(data["token"]) > 0
    assert "digest" not in data


@pytest.mark.integration
def test_create_sa_key_with_name_and_description(client, g_user, project, sa_key_data):
    sa_key_data["description"] = "Whoa man, I'm just using this for auth"
    today = datetime.now(UTC)
    response = client.post(
        f"/observability/v1/projects/{project.id}/service-account-key",
        headers={"Content-Type": "application/json"},
        json=sa_key_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json

    expires_at_datetime = datetime.strptime(data["expires_at"], TIMESTAMP_FORMAT)

    assert len(data["id"]) > 0
    assert (expires_at_datetime - today).days == sa_key_data["expires_after_days"]
    assert len(data["token"]) > 0
    assert "digest" not in data
    assert data["name"] == sa_key_data["name"]
    assert data["description"] == sa_key_data["description"]


@pytest.mark.integration
def test_create_sa_key_forbidden(client, g_user_2, project, sa_key_data):
    response = client.post(
        f"/observability/v1/projects/{project.id}/service-account-key",
        headers={"Content-Type": "application/json"},
        json=sa_key_data,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.integration
def test_create_sa_key_conflict(client, g_user, project):
    body_1 = {"expires_after_days": 7, "name": "key-1", "allowed_services": [Service.EVENTS_API.value]}
    response_1 = client.post(
        f"/observability/v1/projects/{project.id}/service-account-key",
        headers={"Content-Type": "application/json"},
        json=body_1,
    )
    assert response_1.status_code == HTTPStatus.CREATED

    # Try creating a new key with the same name in the same project
    body_2 = {"expires_after_days": 17, "name": "key-1", "allowed_services": [Service.EVENTS_API.value]}
    response_2 = client.post(
        f"/observability/v1/projects/{project.id}/service-account-key",
        headers={"Content-Type": "application/json"},
        json=body_2,
    )
    assert response_2.status_code == HTTPStatus.CONFLICT


@pytest.mark.integration
def test_create_sa_key_project_not_found(client, g_user, sa_key_data):
    response = client.post(
        f"/observability/v1/projects/{uuid.uuid4()}/service-account-key",
        headers={"Content-Type": "application/json"},
        json=sa_key_data,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_create_sa_key_invalid_value_type(client, g_user, project):
    # Expect expires_after_days to be int not datetime
    body = {"expires_after_days": datetime.now()}
    response = client.post(
        f"/observability/v1/projects/{project.id}/service-account-key",
        headers={"Content-Type": "application/json"},
        json=body,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
    err = response.json["details"]
    assert err["expires_after_days"][0] == INVALID_INT_TYPE


@pytest.mark.integration
def test_create_sa_key_with_none_expires_after_days(client, g_user, project):
    body = {"expires_after_days": None}
    response = client.post(
        f"/observability/v1/projects/{project.id}/service-account-key",
        headers={"Content-Type": "application/json"},
        json=body,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json["details"]["expires_after_days"][0] == NULL_FIELD


@pytest.mark.integration
def test_create_sa_key_with_missing_expires_after_days(client, g_user, project):
    response = client.post(
        f"/observability/v1/projects/{project.id}/service-account-key",
        headers={"Content-Type": "application/json"},
        json={},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json["details"]["expires_after_days"][0] == MISSING_REQUIRED_FIELD


@pytest.mark.integration
def test_list_service_account_key(client, g_user, sa_key, project):
    response = client.get(f"/observability/v1/projects/{project.id}/service-account-key")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 1
    assert data["total"] == 1
    assert data["entities"][0] == {
        "id": str(sa_key.key_entity.id),
        "description": sa_key.key_entity.description,
        "name": sa_key.key_entity.name,
        "project": str(sa_key.key_entity.project.id),
        "expires_at": datetime_iso8601(sa_key.key_entity.expiry),
        "allowed_services": sa_key.key_entity.allowed_services,
    }
    assert "digest" not in data["entities"][0]


@pytest.mark.integration
def test_list_service_account_key_search(client, g_user, sa_key, project):
    response_1 = client.get(f"/observability/v1/projects/{project.id}/service-account-key?search=key")
    data_1 = response_1.json
    assert data_1["total"] == 1, "Expected search for text 'key' to return 1 result"

    response_2 = client.get(f"/observability/v1/projects/{project.id}/service-account-key?search=notakeyname")
    data_2 = response_2.json
    assert data_2["total"] == 0, "Expected search for text 'notakeyname' to return 0 results"


@pytest.mark.integration
def test_delete_service_account_key(client, g_user, sa_key):
    response = client.delete(f"/observability/v1/service-account-key/{sa_key.key_entity.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json


@pytest.mark.integration
def test_delete_service_account_key_forbidden(client, g_user_2, sa_key):
    response = client.delete(f"/observability/v1/service-account-key/{sa_key.key_entity.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_delete_service_account_key_not_found(client, g_user):
    response = client.delete(f"/observability/v1/service-account-key/{uuid.uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json
    assert list(ServiceAccountKey.select()) == []
