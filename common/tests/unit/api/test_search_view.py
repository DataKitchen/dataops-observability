from http import HTTPStatus
from unittest.mock import Mock
from uuid import uuid4

import pytest
from marshmallow import Schema
from marshmallow.fields import UUID, List, Str
from werkzeug.datastructures import MultiDict

from common.api.base_view import BaseView, SearchableView
from common.api.flask_ext.exception_handling import ExceptionHandling
from common.api.search_view import SearchView, add_route_with_search


@pytest.fixture
def test_view_mock():
    return Mock()


class TestFilterSchema(Schema):
    uuid_array = List(UUID())
    string_field = Str()


@pytest.fixture
def test_view_class(test_view_mock):
    class TestView(BaseView, SearchableView):
        PERMISSION_REQUIREMENTS = ()
        FILTERS_SCHEMA = TestFilterSchema

        def get(self, **kwargs):
            return test_view_mock(view_args=kwargs, search_args=self.args)

    yield TestView


@pytest.fixture
def test_view(test_view_class):
    yield test_view_class.as_view("test_view")


@pytest.fixture
def blueprint():
    mock = Mock()
    mock.add_url_rule = Mock()
    yield mock


@pytest.mark.unit
def test_add_route_with_search(blueprint, test_view, test_view_class):
    ret = add_route_with_search(blueprint, "/test", test_view, methods=["GET"])

    assert blueprint.add_url_rule.call_count == 2

    rule1, rule2 = blueprint.add_url_rule.call_args_list
    assert rule1[0][0] == "/test"
    assert rule1[1]["methods"] == ["GET"]
    assert rule1[1]["view_func"] == test_view

    assert rule2[0][0] == "/test/search"
    assert rule2[1]["view_func"] == ret
    assert issubclass(rule2[1]["view_func"].view_class, SearchView)
    assert issubclass(rule2[1]["view_func"].view_class, test_view_class)
    assert rule2[1]["methods"] == ["POST"]


@pytest.mark.unit
def test_search_view_valid_request(flask_app, client, test_view, test_view_mock):
    add_route_with_search(flask_app, "/test/<arg>/", test_view, methods=["GET"])
    resp_data = {"data": "response"}
    test_view_mock.return_value = resp_data
    params = {
        "string_field": "1",
        "uuid_array": [str(uuid4()), str(uuid4())],
    }
    resp = client.post(
        "/test/some_value/search",
        json={
            "params": params,
        },
    )

    assert resp.status_code == HTTPStatus.OK, resp.json
    assert resp.json == resp_data
    test_view_mock.assert_called_once_with(view_args={"arg": "some_value"}, search_args=MultiDict(params))


@pytest.mark.unit
@pytest.mark.parametrize(
    "request_data",
    (
        {
            "uuid_array": uuid4(),
        },
        {
            "string_field": ["a", "b"],
        },
    ),
)
def test_search_view_invalid_request(flask_app, client, test_view, test_view_mock, request_data):
    ExceptionHandling(flask_app)
    add_route_with_search(flask_app, "/test/<arg>/", test_view, methods=["GET"])
    test_view_mock.return_value = {}

    resp = client.post(
        "/test/some_value/search",
        json={"params": request_data},
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST, resp.json
    assert list(request_data.keys())[0] in resp.json["error"]
