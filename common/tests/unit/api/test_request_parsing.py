from http import HTTPStatus
from unittest.mock import Mock

import pytest
from flask import url_for
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest

import common.api.request_parsing as ParsingModule
from common.api.request_parsing import get_bool_param, get_origin_domain, no_body_allowed


@pytest.mark.unit
def test_base_view_request_body_not_json_post(base_flask_app, client):
    response = client.post(
        url_for("request-body-endpoint"),
        headers={"Content-Type": "multipart/form-data"},
        data={"name": "foo"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.unit
def test_base_view_request_body_not_json_get(base_flask_app, client):
    response = client.get(
        url_for("request-body-endpoint"),
        headers={"Content-Type": "multipart/form-data"},
        data={"name": "foo"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.unit
def test_base_view_request_body_post(base_flask_app, client):
    data = {"name": "foo"}
    response = client.post(url_for("request-body-endpoint"), json=data)
    assert response.status_code == HTTPStatus.OK
    assert data == response.json.get("data")


@pytest.mark.unit
def test_base_view_request_body_get(base_flask_app, client):
    data = {"name": "foo"}
    response = client.get(url_for("request-body-endpoint"), json=data)
    assert response.status_code == HTTPStatus.OK
    assert data == response.json.get("data")


@pytest.mark.unit
def test_base_view_request_body_bad_data(base_flask_app, client):
    response = client.get(url_for("request-body-endpoint"), data="123'foo'")
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.unit
@pytest.mark.parametrize(
    "body,expected",
    (
        ({"foo": "true"}, True),
        ({"foo": "false"}, False),
        ({"foo": "True"}, True),
        ({"foo": "False"}, False),
        ({"foo": "TRUE"}, True),
        ({"foo": "FALSE"}, False),
        ({"foo": "no"}, "raises"),
        ({"foo": "yes"}, "raises"),
        ({"foo": "t"}, "raises"),
        ({"foo": "f"}, "raises"),
    ),
    ids=(
        "true_lower",
        "false_lower",
        "true_cased",
        "false_cased",
        "true_caps",
        "false_caps",
        "no_is_invalid",
        "yes_is_invalid",
        "t_is_invalid",
        "f_is_invalid",
    ),
)
def test_get_bool_param(body, expected):
    request = Mock()
    request.args = body
    if expected == "raises":
        with pytest.raises(ValidationError):
            get_bool_param(request, "foo")
    else:
        assert get_bool_param(request, "foo") == expected


@pytest.mark.unit
@pytest.mark.parametrize("default", (False, True), ids=("default_false", "default_true"))
def test_get_bool_param_different_default(default):
    request = Mock()
    request.args = {}
    assert get_bool_param(request, "foo", default=default) == default


@pytest.fixture
def mock_request():
    old_request = ParsingModule.request
    mock_request = Mock()
    mock_request.method = "GET"
    ParsingModule.request = mock_request
    yield mock_request
    ParsingModule.request = old_request


@pytest.mark.unit
def test_no_body_allowed(mock_request):
    mock_request.data = None

    @no_body_allowed
    def foo() -> bool:
        return True

    assert foo()


@pytest.mark.unit
@pytest.mark.parametrize("method,raises", (("PUT", True), ("GET", False)))
def test_no_body_allowed_custom_method(method, raises, mock_request):
    mock_request.method = method
    mock_request.data = "found"

    @no_body_allowed(methods=["PUT"])
    def foo() -> bool:
        return True

    if raises:
        with pytest.raises(BadRequest):
            foo()
    else:
        assert foo()


@pytest.mark.unit
def test_no_body_allowed_passes_params(mock_request):
    mock_request.data = None

    @no_body_allowed
    def foo(param: bool) -> bool:
        return param

    assert foo(True)
    assert not foo(param=False)


@pytest.mark.unit
def test_no_body_allowed_body_found(mock_request):
    mock_request.data = "some body"

    @no_body_allowed
    def foo():
        return True

    with pytest.raises(BadRequest):
        foo()


@pytest.mark.unit
def test_no_body_allowed_not_safe_method(mock_request):
    mock_request.method = "POST"
    mock_request.data = "some body"

    @no_body_allowed
    def get():
        return True

    assert get()


@pytest.mark.unit
def test_get_origin_domain_empty(mock_request):
    mock_request.headers = {}
    assert get_origin_domain() is None


@pytest.mark.unit
def test_get_origin_domain_invalid(mock_request):
    mock_request.headers = {"Origin": "asdf"}
    assert get_origin_domain() is None


@pytest.mark.unit
def test_get_origin_domain_ok(mock_request):
    mock_request.headers = {"Origin": "https://asdf.com"}
    assert get_origin_domain() == "asdf.com"
