import shutil
from http import HTTPStatus

import pytest
from flask import Flask, Response, make_response

from common.api.base_view import BaseView
from common.api.flask_ext.config import Config


class BasicTestEndpoint(BaseView):
    PERMISSION_REQUIREMENTS = ()

    def get(self) -> Response:
        return make_response({}, HTTPStatus.OK)

    def put(self) -> Response:
        return make_response({}, HTTPStatus.OK)

    def post(self) -> Response:
        return make_response({}, HTTPStatus.OK)

    def patch(self) -> Response:
        return make_response({}, HTTPStatus.OK)

    def delete(self) -> Response:
        return make_response({}, HTTPStatus.NO_CONTENT)


class RequestBodyEndpoint(BaseView):
    """Simple view that parses the request body."""

    PERMISSION_REQUIREMENTS = ()

    def get(self) -> Response:
        data = self.request_body
        return make_response({"data": data}, HTTPStatus.OK)

    def post(self) -> Response:
        data = self.request_body
        return make_response({"data": data}, HTTPStatus.OK)


@pytest.fixture
def flask_app():
    # create and configure a basic app
    app = Flask(__name__, instance_relative_config=True)
    app.config["ENV"] = "test"
    # nosemgrep: python.flask.security.audit.hardcoded-config.avoid_hardcoded_config_TESTING
    app.config["TESTING"] = True
    Config(app, config_module="observability_api.config")
    app.config["SERVICE_NAME"] = "test-app"
    app.config["SERVER_NAME"] = "dev.localhost"
    yield app
    shutil.rmtree(app.instance_path, ignore_errors=True)


@pytest.fixture
def base_flask_app(flask_app):
    test_view = BasicTestEndpoint.as_view("test-endpoint")
    flask_app.add_url_rule("/test-endpoint", view_func=test_view, methods=["GET", "PUT", "POST", "PATCH", "DELETE"])

    request_body_view = RequestBodyEndpoint.as_view("request-body-endpoint")
    flask_app.add_url_rule("/request-body-endpoint", view_func=request_body_view, methods=["GET", "POST"])
    yield flask_app


@pytest.fixture
def client(flask_app):
    with flask_app.app_context():
        with flask_app.test_client() as client:
            yield client
