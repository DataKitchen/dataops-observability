import os
import shutil
from unittest.mock import Mock

import pytest
from flask import Flask

from common.api.flask_ext.exception_handling import ExceptionHandling
from common.api.flask_ext.health import Health
from testlib.fixtures.entities import *
from testlib.fixtures.v2_events import *


@pytest.fixture
def readiness_check_callback():
    yield Mock()


@pytest.fixture
def flask_app(readiness_check_callback):
    # create and configure the app. Astute readers will note that we are not configuring the database,
    # as currently these tests does not use it. See observability_api's test suite to see how that may
    # be done.
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    ExceptionHandling(app)
    Health(app, prefix="test", readiness_callback=readiness_check_callback)
    yield app
    shutil.rmtree(app.instance_path, ignore_errors=True)


@pytest.fixture
def client(flask_app):
    yield flask_app.test_client()
