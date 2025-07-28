from http import HTTPStatus

import pytest

from common.api.flask_ext.cors import CORS, CORS_HEADERS

CORS_HEADER_TUPLE: tuple[str, ...] = tuple(CORS_HEADERS.keys())


@pytest.fixture
def flask_app(base_flask_app):
    CORS(base_flask_app)
    yield base_flask_app


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client


@pytest.mark.integration
def test_options_request(client):
    """OPTIONS request intercepted and given NO_CONTENT repsonse + CORS headers."""
    response = client.options("/test-endpoint", headers={"Origin": "https://xyz.com"})
    assert response.status_code == HTTPStatus.NO_CONTENT
    for header_name in CORS_HEADER_TUPLE:
        assert header_name in response.headers


@pytest.mark.integration
def test_options_request_404(client):
    """OPTIONS request returns a 404 for invalid url endpoints."""
    response = client.options("/bad-endpoint", headers={"Origin": "https://xyz.com"})
    assert response.status_code == HTTPStatus.NOT_FOUND


# NOTE: Pytest doesn't let you parameterize AND use a fixture at the same time, hence one for each of these


@pytest.mark.integration
def test_requests_get(client):
    """Served GET requests have proper headers."""
    response = client.get("/test-endpoint", headers={"Origin": "https://xyz.com"})
    assert response.status_code == HTTPStatus.OK
    for header_name in CORS_HEADER_TUPLE:
        assert header_name in response.headers


@pytest.mark.integration
def test_requests_put(client):
    """Served PUT requests have proper headers."""
    response = client.put("/test-endpoint", headers={"Origin": "https://xyz.com"})
    assert response.status_code == HTTPStatus.OK
    for header_name in CORS_HEADER_TUPLE:
        assert header_name in response.headers


@pytest.mark.integration
def test_requests_post(client):
    """Served POST requests have proper headers."""
    response = client.post("/test-endpoint", headers={"Origin": "https://xyz.com"})
    assert response.status_code == HTTPStatus.OK
    for header_name in CORS_HEADER_TUPLE:
        assert header_name in response.headers


@pytest.mark.integration
def test_requests_patch(client):
    """Served PATCH requests have proper headers."""
    response = client.patch("/test-endpoint", headers={"Origin": "https://xyz.com"})
    assert response.status_code == HTTPStatus.OK
    for header_name in CORS_HEADER_TUPLE:
        assert header_name in response.headers


@pytest.mark.integration
def test_requests_delete(client):
    """Served DELETE requests have proper headers."""
    response = client.delete("/test-endpoint", headers={"Origin": "https://xyz.com"})
    assert response.status_code == HTTPStatus.NO_CONTENT
    for header_name in CORS_HEADER_TUPLE:
        assert header_name in response.headers
