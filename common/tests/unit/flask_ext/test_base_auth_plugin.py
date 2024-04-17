import flask
import pytest

from common.api.flask_ext.authentication.common import BaseAuthPlugin


@pytest.fixture
def test_plugin():
    class_ = type(
        "SomExtension",
        (BaseAuthPlugin,),
        {
            "header_name": "MyHeader",
            "header_prefix": "Prefix",
        },
    )
    return class_


@pytest.fixture
def request_mock():
    test_app = flask.Flask("test_flask_app")

    with test_app.test_request_context() as context_mock:
        context_mock.request.headers = {
            "MyHeader": "Prefix SomeData",
            "UnrelatedHeader": "NotUsefulData",
        }
        yield context_mock.request


@pytest.mark.unit
def test_get_header_data(test_plugin, request_mock):
    assert test_plugin.get_header_data() == "SomeData"


@pytest.mark.unit
def test_get_header_data_no_prefix(test_plugin, request_mock):
    test_plugin.header_prefix = None
    assert test_plugin.get_header_data() == "Prefix SomeData"


@pytest.mark.unit
def test_get_header_data_non_matching_prefix(test_plugin, request_mock):
    test_plugin.header_prefix = "Other"
    assert test_plugin.get_header_data() is None
