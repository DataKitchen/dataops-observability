from http import HTTPStatus

import pytest

from common.api.flask_ext.authentication import ServiceAccountAuth
from common.auth.keys import service_key


@pytest.fixture
def flask_app(base_flask_app):
    ServiceAccountAuth(base_flask_app)
    yield base_flask_app


@pytest.fixture
def valid_sa_key(flask_app, project):
    sa_key = service_key.generate_key(allowed_services=[flask_app.config["SERVICE_NAME"]], project=project).encoded_key
    yield sa_key


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client


@pytest.mark.integration
def test_valid_request(client, valid_sa_key):
    """When passed a valid Service Account Key, endpoints should authenticate properly."""
    response = client.get("/test-endpoint", headers={ServiceAccountAuth.header_name: valid_sa_key})
    assert response.status_code == HTTPStatus.OK


@pytest.mark.integration
def test_invalid_request(client, valid_sa_key):
    """Invalid Service Account Keys in the header should yield a 401 unauthorized."""
    response = client.get("/test-endpoint", headers={ServiceAccountAuth.header_name: "Rk9PfEJBUnxCQVo="})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_invalid_service_name(client, project):
    """Invalid Service Account Keys in the header should yield a 401 unauthorized."""
    sa_key = service_key.generate_key(
        allowed_services=["wrong-name"], project=project
    ).encoded_key  # Valid for a different APP/API
    response = client.get("/test-endpoint", headers={ServiceAccountAuth.header_name: sa_key})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
