from http import HTTPStatus

import pytest

from common.api.flask_ext.authentication import ServiceAccountAuth
from common.entities import ServiceAccountKey


@pytest.fixture
def sa_key_flask_app(flask_app):
    ServiceAccountAuth(flask_app)
    yield flask_app


@pytest.fixture
def sa_key_client(sa_key_flask_app):
    with sa_key_flask_app.test_client() as client:
        with sa_key_flask_app.app_context():
            yield client


@pytest.mark.integration
def test_valid_sa_key_request(sa_key_client, obs_api_sa_key, project):
    """When passed a valid SA key, endpoints should authenticate properly."""
    header = {ServiceAccountAuth.header_name: obs_api_sa_key.encoded_key}
    response = sa_key_client.get(f"/observability/v1/projects/{project.id}", headers=header)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.integration
def test_invalid_sa_key_request(sa_key_client, obs_api_sa_key, project):
    """When passed a valid SA key, endpoints should authenticate properly."""
    ServiceAccountKey.delete().where(ServiceAccountKey.id == obs_api_sa_key.key_entity.id).execute()
    response = sa_key_client.get(
        f"/observability/v1/projects/{project.id}", headers={ServiceAccountAuth.header_name: obs_api_sa_key.encoded_key}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_non_allowed_service_request(sa_key_client, events_api_sa_key, project):
    """When passed a valid SA key with non-allowed services, endpoints should not authenticate."""
    response = sa_key_client.get(
        f"/observability/v1/projects/{project.id}",
        headers={ServiceAccountAuth.header_name: events_api_sa_key.encoded_key},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
@pytest.mark.parametrize("header", [{ServiceAccountAuth.header_name: None}, None])
def test_empty_sa_key_request_401(sa_key_client, header, journey):
    """When request is sent with an empty key or missing header, endpoints should not authenticate."""
    response = sa_key_client.get(f"/observability/v1/journeys/{journey.id}", headers=header)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
