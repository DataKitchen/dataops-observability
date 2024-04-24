from http import HTTPStatus
from unittest.mock import patch
from urllib.parse import urljoin

import pytest

from common.api.flask_ext.authentication import JWTAuth, ServiceAccountAuth
from testlib.fixtures.entities import *

BASE_URL = "/observability/v1/"


@pytest.fixture
def auth_flask_app(flask_app):
    """Test flask app configures with all authentication plugins"""
    ServiceAccountAuth(flask_app)
    JWTAuth(flask_app)
    with patch("common.api.flask_ext.authentication.jwt_plugin.get_domain", return_value="fakedomain.fake"):
        yield flask_app


@pytest.fixture
def auth_client(auth_flask_app):
    with auth_flask_app.test_client() as client:
        with auth_flask_app.app_context():
            yield client


@pytest.fixture
def sa_key_headers(obs_api_sa_key):
    return {"Content-Type": "application/json", ServiceAccountAuth.header_name: obs_api_sa_key.encoded_key}


@pytest.fixture
def jwt_headers(auth_client, admin_user):
    return {"Content-Type": "application/json", JWTAuth.header_name: JWTAuth.log_user_in(admin_user)}


@pytest.mark.integration
@pytest.mark.parametrize(
    "path,fixture",
    [
        ("batch-pipelines/{id}", "pipeline"),
        ("components/{id}", "component"),
        ("components/{id}/schedules", "component"),
        ("instances/{id}", "instance"),
        ("journeys/{id}", "journey"),
        ("journeys/{id}/rules", "journey"),
        ("projects/{id}", "project"),
        ("projects/{id}/alerts", "project"),
        ("rules/{id}", "rule"),
        ("runs/{id}", "run"),
        ("runs/{id}/tasks", "run"),
        ("test-outcomes/{id}", "test_outcome"),
    ],
)
def test_sa_key_auth_get_authorized(auth_client, sa_key_headers, path, fixture, request):
    """SAKey authorization allows GET request to endpoints within project scope."""
    endpoint = urljoin(BASE_URL, path.format(id=str(request.getfixturevalue(fixture).id)))
    response = auth_client.get(endpoint, headers=sa_key_headers)
    assert response.status_code == HTTPStatus.OK, response.json


@pytest.mark.integration
@pytest.mark.parametrize(
    "path,fixture",
    [
        ("components/{id}/schedules", "component"),
        ("journeys/{id}/instance-conditions", "journey"),
        ("journeys/{id}/rules", "journey"),
        ("projects/{id}/batch-pipelines", "project"),
        ("projects/{id}/journeys", "project"),
    ],
)
def test_sa_key_auth_post_authorized(auth_client, sa_key_headers, path, fixture, request):
    """SAKey authorization allows POST request to endpoints within project scope."""
    endpoint = urljoin(BASE_URL, path.format(id=str(request.getfixturevalue(fixture).id)))
    response = auth_client.post(endpoint, headers=sa_key_headers, json={})
    assert response.status_code not in (HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED), response.json


@pytest.mark.integration
@pytest.mark.parametrize(
    "path,fixture",
    [
        ("batch-pipelines/{id}", "pipeline"),
        ("components/{id}", "component"),
        ("journeys/{id}", "journey"),
        ("projects/{id}", "project"),
        ("rules/{id}", "rule"),
    ],
)
def test_sa_key_auth_patch_authorized(auth_client, sa_key_headers, path, fixture, request):
    """SAKey authorization allows PATCH request to endpoints within project scope."""
    endpoint = urljoin(BASE_URL, path.format(id=str(request.getfixturevalue(fixture).id)))
    response = auth_client.patch(endpoint, headers=sa_key_headers, json={})
    assert response.status_code not in (HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED), response.json


@pytest.mark.integration
@pytest.mark.parametrize(
    "path,fixture",
    [
        ("instance-conditions/{id}", "instance_rule_start"),
        ("journey-dag-edge/{id}", "journey_dag_edge"),
        ("journeys/{id}", "journey"),
        ("rules/{id}", "rule"),
        ("schedules/{id}", "batch_start_schedule"),
    ],
)
def test_sa_key_auth_delete_authorized(auth_client, sa_key_headers, path, fixture, request):
    """SAKey authorization allows DELETE request to endpoints within project scope."""
    endpoint = urljoin(BASE_URL, path.format(id=str(request.getfixturevalue(fixture).id)))
    response = auth_client.delete(endpoint, headers=sa_key_headers)
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json


out_of_scope_endpoints = pytest.mark.parametrize(
    "path, fixture, methods",
    [
        ("companies", None, ["GET"]),
        ("companies/{id}", "company", ["GET"]),
        ("companies/{id}/organizations", "company", ["GET"]),
        ("organizations/{id}", "organization", ["GET"]),
        ("organizations/{id}/projects", "organization", ["GET"]),
        ("users", None, ["GET"]),
        ("users/{id}", "user", ["GET"]),
        ("projects/{id}/service-account-key", "project", ["GET", "POST"]),
        ("service-account-key/{id}", "service_account_key", ["DELETE"]),
        ("instances", None, ["GET"]),
    ],
)


@pytest.mark.integration
@out_of_scope_endpoints
def test_sa_key_auth_beyond_project_scope_forbidden(auth_client, sa_key_headers, path, fixture, methods, request):
    """SAKey authorization is not allowed to any endpoints outside of project scope."""
    parent_id = str(request.getfixturevalue(fixture).id) if fixture else None
    endpoint = urljoin(BASE_URL, path.format(id=parent_id))
    for method in methods:
        if method == "GET":
            response = auth_client.get(endpoint, headers=sa_key_headers)
            assert response.status_code == HTTPStatus.FORBIDDEN, response.json
        elif method == "POST":
            response = auth_client.post(endpoint, headers=sa_key_headers, json={})
            assert response.status_code == HTTPStatus.FORBIDDEN, response.json
        elif method == "PATCH":
            response = auth_client.patch(endpoint, headers=sa_key_headers, json={})
            assert response.status_code == HTTPStatus.FORBIDDEN, response.json
        elif method == "DELETE":
            response = auth_client.delete(endpoint, headers=sa_key_headers)
            assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
@out_of_scope_endpoints
def test_admin_user_auth_beyond_project_scope_ok(auth_client, jwt_headers, path, fixture, methods, request):
    """Admin user's APIKey can access endpoints that are beyond project scope."""
    parent_id = str(request.getfixturevalue(fixture).id) if fixture else None
    endpoint = urljoin(BASE_URL, path.format(id=parent_id))
    for method in methods:
        if method == "GET":
            response = auth_client.get(endpoint, headers=jwt_headers)
            assert response.status_code == HTTPStatus.OK, response.json
        elif method == "POST":
            response = auth_client.post(endpoint, headers=jwt_headers, json={})
            assert response.status_code not in (HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED), response.json
        elif method == "PATCH":
            response = auth_client.patch(endpoint, headers=jwt_headers, json={})
            assert response.status_code not in (HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED), response.json
        elif method == "DELETE":
            response = auth_client.delete(endpoint, headers=jwt_headers)
            assert response.status_code == HTTPStatus.NO_CONTENT, response.json
