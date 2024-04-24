import shutil
from http import HTTPStatus

import pytest
from flask import Flask, Response, make_response
from flask.views import MethodView

from common.api.flask_ext.config import Config
from conf import init_db


class TestEndpoint(MethodView):
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


@pytest.fixture
def base_flask_app():
    # create and configure a basic app
    app = Flask(__name__, instance_relative_config=True)
    app.config["ENV"] = "test"
    # nosemgrep: python.flask.security.audit.hardcoded-config.avoid_hardcoded_config_TESTING
    app.config["TESTING"] = True
    Config(app, config_module="observability_api.config")
    app.config["SERVICE_NAME"] = "TEST_APP"
    app.config["SERVER_NAME"] = "dev.localhost"
    init_db()
    test_view = TestEndpoint.as_view("test-endpoint")
    app.add_url_rule("/test-endpoint", view_func=test_view, methods=["GET", "PUT", "POST", "PATCH", "DELETE"])
    yield app
    shutil.rmtree(app.instance_path, ignore_errors=True)
