from http import HTTPStatus

import pytest
from flask import g

from common.api.flask_ext.htmx import HTMX


@pytest.fixture()
def flask_app(base_flask_app):
    HTMX(base_flask_app)
    yield base_flask_app


@pytest.fixture()
def client(flask_app):
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client


@pytest.mark.integration
def test_header_no_htmx_headers(client):
    """Test default values are set when no htmx headers are present."""
    response = client.get("/test-endpoint", headers={})
    assert response.status_code == HTTPStatus.OK

    # Boolean values default to False
    assert g.is_htmx is False
    assert g.is_async is False
    assert g.hx_boosted is False
    assert g.hx_history_restore_request is False

    # String values default to empty strings
    assert g.hx_current_url == ""
    assert g.hx_prompt == ""
    assert g.hx_target == ""
    assert g.hx_trigger == ""
    assert g.hx_trigger_name == ""


@pytest.mark.integration
def test_header_hx_request(client):
    """HX-Request header sets g.is_htmx"""
    response = client.get("/test-endpoint", headers={"HX-Request": "true"})
    assert response.status_code == HTTPStatus.OK
    assert g.is_htmx is True


@pytest.mark.integration
def test_header_hx_boosted(client):
    """HX-Boost header sets g.hx_boosted"""
    response = client.get("/test-endpoint", headers={"HX-Boosted": "true"})
    assert response.status_code == HTTPStatus.OK
    assert g.hx_boosted is True


@pytest.mark.integration
def test_header_hx_history_restore_request(client):
    """HX-History-Restore-Request header sets g.hx_history_restore_request"""
    response = client.get("/test-endpoint", headers={"HX-History-Restore-Request": "true"})
    assert response.status_code == HTTPStatus.OK
    assert g.hx_history_restore_request is True


@pytest.mark.integration
def test_header_is_async_true(client):
    """Presence HX-Request header and absence of HX-Boost header sets g.is_async to True"""
    response = client.get("/test-endpoint", headers={"HX-Request": "true"})
    assert response.status_code == HTTPStatus.OK
    assert g.is_async is True


@pytest.mark.integration
def test_header_is_async_false(client):
    """Presence HX-Request header and presence of HX-Boost header sets g.is_async to False"""
    response = client.get("/test-endpoint", headers={"HX-Request": "true", "HX-Boosted": "true"})
    assert response.status_code == HTTPStatus.OK
    assert g.is_async is False


@pytest.mark.integration
def test_header_hx_current_url(client):
    """HX-Current-URL header sets g.hx_current_url attribute"""
    response = client.get("/test-endpoint", headers={"HX-Current-URL": "/test-endpoint"})
    assert response.status_code == HTTPStatus.OK
    assert g.hx_current_url == "/test-endpoint"


@pytest.mark.integration
def test_header_hx_prompt(client):
    """HX-Prompt header sets g.hx_prompt attribute"""
    response = client.get("/test-endpoint", headers={"HX-Prompt": "Do a thing"})
    assert response.status_code == HTTPStatus.OK
    assert g.hx_prompt == "Do a thing"


@pytest.mark.integration
def test_header_hx_target(client):
    """HX-Target header sets g.hx_target attribute"""
    response = client.get("/test-endpoint", headers={"HX-Target": "/test-endpoint"})
    assert response.status_code == HTTPStatus.OK
    assert g.hx_target == "/test-endpoint"


@pytest.mark.integration
def test_header_hx_trigger(client):
    """HX-Trigger header sets g.hx_trigger attribute"""
    response = client.get("/test-endpoint", headers={"HX-Trigger": "someval"})
    assert response.status_code == HTTPStatus.OK
    assert g.hx_trigger == "someval"


@pytest.mark.integration
def test_header_hx_trigger_name(client):
    """HX-Trigger-Name header sets g.hx_trigger_name attribute"""
    response = client.get("/test-endpoint", headers={"HX-Trigger-Name": "someval"})
    assert response.status_code == HTTPStatus.OK
    assert g.hx_trigger_name == "someval"
